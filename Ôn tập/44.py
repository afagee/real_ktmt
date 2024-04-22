# Phát triển một mô hình thang máy mô phỏng điều khiển cho một tòa nhà 4 tầng, sử dụng bo mạch thực hành.
# Mô hình sẽ tích hợp các nút bấm để gọi thang, một động cơ DC để mô phỏng việc thang máy di chuyển lên/xuống,
# một động cơ RC servo để mô phỏng cửa thang mở/đóng và sử dụng LED matrix cùng màn hình LCD để hiển thị
# thông tin về vị trí hiện tại và trạng thái của thang máy. Mô tả chi tiết: Tích hợp 4 nút bấm tương ứng với mỗi tầng
# trong tòa nhà. Khi một nút được nhấn, hệ thống sẽ xử lý yêu cầu và di chuyển thang máy đến tầng đó.
# Sử dụng động cơ DC để mô phỏng việc thang máy di chuyển lên hoặc xuống. Chiều quay của động cơ sẽ thay đổi tùy theo
# hướng di chuyển của thang máy. Sử dụng động cơ RC servo để mô phỏng việc mở và đóng cửa thang máy.
# Đảm bảo có thời gian chờ trước khi cửa đóng để mô phỏng việc chờ khách. Sử dụng LED matrix để hiển thị
# số tầng hiện tại của thang máy. Sử dụng màn hình LCD để hiển thị trạng thái hoạt động của thang máy,
# bao gồm các thông báo như: "đang chờ", "đang di chuyển lên", "đang di chuyển xuống", và "cửa mở".
from PIL import Image, ImageDraw, ImageFont
import spidev
import time
import numpy as np
import RPi.GPIO as GPIO

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)

    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)


def lcd_display_string(message, line):
    lcd_clear()
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10000000
spi.mode = 0x00


def max7219_write(register, data):
    spi.xfer2([register, data])


def max7219_init():
    max7219_write(0x0C, 0x01)
    max7219_write(0x0B, 0x07)
    max7219_write(0x09, 0x00)
    max7219_write(0x0A, 0x00)
    max7219_write(0x0F, 0x00)


def create_text_image(text, width, height):
    image = Image.new('1', (width, height), 0)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_size = 1
    text_position = (1, -1)
    draw.text(text_position, text, font=font, fill=1)
    return image


def display_image(image):
    pixels = np.array(image)
    for y in range(8):
        row_data = 0
        for x in range(8):
            if pixels[y, x]:
                row_data |= 1 << x
            max7219_write(y + 1, row_data)


def clear_matrix():
    max7219_write(0x0c, 0x00)


def LED_matrix(floor):
    max7219_init()
    while True:
        text = floor
        width, height = 8, 8
        image = create_text_image(text, width, height)
        display_image(image)
        time.sleep(0.1)


PWM = 24
DIR = 25
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm_dir = GPIO.PWM(PWM, 1000)
pwm_dir.start(0)
speed = 0
direction = 0

def motor_control():
    global speed, direction
    GPIO.output(DIR, direction)
    speed1 = speed
    if direction != 0:
        speed1 = 100 - speed
    pwm_dir.ChangeDutyCycle(speed1)


SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm_servo = GPIO.PWM(SERVO, 50)
pwm_servo.start(0)


def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO, True)
    pwm_servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm_servo.ChangeDutyCycle(0)


current_floor = 1

def display_floor(floor):
    text = str(floor)
    width, height = 8, 8
    image = create_text_image(text, width, height)
    flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    display_image(flipped_image)

def button_pressed(floor):
    global current_floor, speed, direction
    if current_floor - floor == 0:
        return
    speed = 50
    direction = 0 if current_floor - floor > 0 else 1

    if direction == 1:
        lcd_display_string("Dang di len", 1)
    else:
        lcd_display_string("Dang di xuong", 1)

    motor_control()
    time.sleep(1.5)
    if current_floor < floor:
        for i in range(current_floor + 1, floor + 1, 1):
            display_floor(i)
            time.sleep(1.5)
    else:
        for i in range(current_floor - 1, floor - 1, -1):
            display_floor(i)
            time.sleep(1.5)
    speed = 0
    motor_control()
    time.sleep(0.15)

    lcd_display_string("Mo cua", 1)
    set_servo_angle(180)
    time.sleep(1)
    lcd_display_string("Dong cua", 1)
    set_servo_angle(0)
    time.sleep(0.15)
    lcd_clear()

    current_floor = floor


def main():
    clear_matrix()
    lcd_init()
    lcd_clear()
    max7219_init()
    motor_control()

    display_floor(1)
    while True:
        if GPIO.input(BT1) == GPIO.LOW:
            button_pressed(1)
        if GPIO.input(BT2) == GPIO.LOW:
            button_pressed(2)
        if GPIO.input(BT3) == GPIO.LOW:
            button_pressed(3)
        if GPIO.input(BT4) == GPIO.LOW:
            button_pressed(4)
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    clear_matrix()
    spi.close()
    GPIO.cleanup()

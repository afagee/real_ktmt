# Xây dựng một mô hình điều khiển tự động cho camera hành trình và cảm biến phát hiện va chạm của ô tô trên Bo mạch
# thực hành, kết hợp với chức năng điều khiển động cơ để mô phỏng chế độ lùi, tiến và điều chỉnh tốc độ. Mô tả chi tiết:
# Khi bấm button 1, kích hoạt camera ở chế độ livestream và cảm biến siêu âm để đo khoảng cách đến vật cản. Lúc này động
# cơ quay theo một chiều, mô phỏng việc lùi xe, nếu khoảng cách nhỏ hơn ngưỡng xác định, camera chuyển sang chế độ quay
# video. Hiển thị chế độ và khoảng cách đến vật cản lên màn hình LCD. Khi bấm button 2, sẽ vô hiệu hóa camera và cảm
# biến siêu âm, động cơ quay theo chiều ngược lại, mô phỏng việc tiến xe. Trong cả hai quá trình, khi giữ button 3,
# tốc độ động cơ tăng thêm 10% theo mỗi giây, khi thả button 3, động cơ sẽ quay theo quán tính. Khi bấm button 4,
# động cơ sẽ dừng ngay lập tức.
import RPi.GPIO as GPIO
import time
from multiprocessing import Value, Process

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

BT_1 = 21
BT_2 = 26
BT_3 = 20
PWM = 24
DIR = 25
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


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
    lcd_byte(LCD_LINE1 if line == 1 else LCD_LINE2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


pwm = GPIO.PWM(PWM, 1000)
pwm.start(0)

speed = 0
direction = 0


def motor_control():
    global speed, direction
    GPIO.output(DIR, direction)
    speed1 = speed
    if direction != 0:
        speed1 = 100 - speed
    pwm.ChangeDutyCycle(speed1)
    lcd_state()


def handle_BT1():

    pass

def lcd_state():
    global direction, speed
    pass

def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    current_time = 0
    time_from = time.time()
    time_end = time.time()
    global speed
    while True:
        motor_control()
        time_end = time.time()
        current_time += time_end - time_from
        time_from = time.time()


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
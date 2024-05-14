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
import cv2
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
BT_4 = 19
PWM = 24
DIR = 25
TRIG = 15
ECHO = 4

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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


def main():
    global speed, direction
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)

    pressed_button = 0
    direction = 0

    GPIO.output(DIR, 0)
    cap = cv2.VideoCapture(0)
    out = cv2.VideoWriter('output.avi', fourcc=cv2.VideoWriter_fourcc(*'MJPG'), fps=20.0, frameSize=(640, 490))
    cv2.namedWindow('Camera')

    time_end = 0
    time_from = 0
    current_time = 0
    pulse_end = 0
    pulse_start = 0

    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            cv2.namedWindow('Camera')
            pressed_button = 1

            speed = 20
            direction = 0
            motor_control()

        if GPIO.input(BT_2) == GPIO.LOW:
            lcd_display_string("Mode 2", 1)
            pressed_button = 2
            cv2.destroyAllWindows()

            speed = 20
            direction = 1
            motor_control()

        if GPIO.input(BT_3) == GPIO.LOW:
            time_end = time.time()
            current_time = 0
            time_from = time.time()
            while GPIO.input(BT_3) == GPIO.LOW:
                time_end = time.time()
                current_time += time_end - time_from
                time_from = time.time()
                if current_time >= 1:
                    speed += 10
                    if speed >= 100:
                        speed = 100
                    current_time -= 1
                motor_control()
                time.sleep(0.1)
        else:
            time_end = time.time()
            current_time += time_end - time_from
            time_from = time.time()
            if current_time >= 1:
                speed -= 10
                if speed >= 20:
                    speed = 20
                current_time -= 1

        if GPIO.input(BT_4) == GPIO.LOW:
            speed = 0
            motor_control()

        if pressed_button == 1:

            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()
            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()
            pulse_duration = pulse_end - pulse_start
            dis = pulse_duration * 17150
            dis = round(dis, 2)
            distance = dis
            # cd_display_string(str(distance.value), 1)
            if distance > 30:
                lcd_clear()
            time.sleep(0.1)
            lcd_display_string("Mode 1", 1)
            lcd_display_string("Dis:" + str(distance), 2)

            _, scr = cap.read()
            cv2.imshow('Camera', scr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                continue
            if distance < 10:
                out.write(scr)



try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
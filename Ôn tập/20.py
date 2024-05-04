# Viết chương trình điều khiển tốc độ động cơ DC theo kịch bản sau.
# Ban đầu động cơ đứng yên. Bấm button 1 và giữ, động cơ quay theo một chiều bất kỳ
# với tốc độ tăng dần 10% theo mỗi giây và khi đạt đến tốc độ 100% thì duy trì tốc độ này,
# khi thả button 1 thì động cơ sẽ quay theo quán tính và dừng hẳn. Bấm button 3 và giữ,
# động cơ sẽ quay theo chiều ngược lại với tốc độ tăng dần 10% theo mỗi giây và khi đạt
# đến tốc độ 100% thì duy trì tốc độ này, khi thả button 2 thì động cơ sẽ quay theo quán
# tính và dừng hẳn. Trong quá trình động cơ đang quay, nếu bấm button 2 động cơ
# ngay lập tức dừng lại hẳn. Hiển thị trạng thái của động cơ gồm:
# chiều quay, tốc độ lên màn hình LCD.
# Viết chương trình điều khiển tốc độ động cơ DC theo kịch bản sau.
# Ban đầu động cơ đứng yên, bấm button 1 lần 1 động cơ quay theo một
# chiều bất kỳ tốc độ 20%, bấm button 1 lần 2 động cơ tăng tốc lên 40%,
# bấm button 1 lần 3 động cơ tăng tốc lên 100%, bấm button 1 lần 4 động
# cơ dừng quay. Tương tự khi bấm button 2 nhưng động cơ đảo chiều quay.

import RPi.GPIO as GPIO
import time

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


def button_1_pressed():
    global speed, direction
    direction = 0
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control()
    print(speed)


def button_2_pressed():
    global speed, direction
    direction = 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control()
    print(speed)


def button_3_pressed():
    global speed
    speed = 0
    motor_control()
    print(speed)


def button_no_pressed():
    global speed
    speed -= 10
    speed = max(0, speed)
    motor_control()
    print(speed)


def lcd_state():
    global direction, speed

    direction_state = str("Phai") if direction else str("Trai")
    speed_state = str(speed)

    lcd_display_string("Chieu quay:" + direction_state, 1)
    lcd_display_string("Toc do:" + speed_state, 2)


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
        if GPIO.input(BT_1) == GPIO.LOW:
            print("1")
            button_1_pressed()
            while GPIO.input(BT_1) == GPIO.LOW:
                print("1")
                time_end = time.time()
                current_time += time_end - time_from
                time_from = time.time()
                if current_time >= 1:
                    button_1_pressed()
                    current_time -= 1
                time.sleep(0.1)

        elif GPIO.input(BT_2) == GPIO.LOW:
            print("2")
            button_2_pressed()
            while GPIO.input(BT_2) == GPIO.LOW:
                print("2")
                time_end = time.time()
                current_time += time_end - time_from
                time_from = time.time()
                if current_time >= 1:
                    button_2_pressed()
                    current_time -= 1
                time.sleep(0.1)

        elif GPIO.input(BT_3) == GPIO.LOW:
            print("3")
            button_3_pressed()

        else:
            if current_time >= 1:
                button_no_pressed()
                current_time -= 1
        time.sleep(0.15)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
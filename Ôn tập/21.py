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

Led = 13
BT_1 = 21
BT_2 = 26
BT_3 = 20
PWM = 24
DIR = 25
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Led, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
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
    GPIO.output(Led, GPIO.HIGH if speed >= 80 else GPIO.LOW)


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

def main():
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

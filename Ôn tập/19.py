# Viết chương trình điều khiển tốc độ động cơ DC theo kịch bản sau.
# Ban đầu động cơ đứng yên, bấm button 1 lần 1 động cơ quay theo một
# chiều bất kỳ tốc độ 20%, bấm button 1 lần 2 động cơ tăng tốc lên 40%,
# bấm button 1 lần 3 động cơ tăng tốc lên 100%, bấm button 1 lần 4 động
# cơ dừng quay. Tương tự khi bấm button 2 nhưng động cơ đảo chiều quay.
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BT_1 = 21
BT_2 = 26
PWM = 24
DIR = 25
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm = GPIO.PWM(PWM, 1000)
pwm.start(0)

speed = 0
count = 0
count1 = 0
direction = 0

def motor_control(speed_, direction_):
    GPIO.output(DIR, direction_)
    if direction_ != 0:
        speed_ = 100 - speed_
    pwm.ChangeDutyCycle(speed_)


def button_1_pressed():
    global speed, count
    count += 1
    speed += 20
    if count == 4:
        speed = 0
        count = 0

    if speed >= 100:
        speed = 100
    motor_control(speed, 0)


def button_2_pressed():
    global speed, count1
    count1 += 1
    speed += 20
    if count1 == 4:
        speed = 0
        count1 = 0

    if speed >= 100:
        speed = 100
    motor_control(speed, 0)


def main():
    motor_control(0, 0)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_1_pressed()
            print(f"so lan bam: {count}")
            time.sleep(0.25)
        if GPIO.input(BT_2) == GPIO.LOW:
            button_2_pressed()
            print(f"so lan bam: {count1}")
            time.sleep(0.25)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

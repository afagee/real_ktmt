# Viết chương trình lặp đi lặp lại theo kịch bản sau: Bấm button 1 động cơ RC servo quay góc 20 độ, bấm button 2 động cơ
# RC servo quay góc 60 độ, bấm button 3 động cơ RC servo quay góc 160 độ
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

buttons = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20}
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)


def set_servo_angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm.ChangeDutyCycle(0)

def main():
    while True:
        if GPIO.input(buttons['BT_1']) == GPIO.LOW:
            set_servo_angle(20)
        if GPIO.input(buttons['BT_2']) == GPIO.LOW:
            set_servo_angle(60)
        if GPIO.input(buttons['BT_3']) == GPIO.LOW:
            set_servo_angle(160)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

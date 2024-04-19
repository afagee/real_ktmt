# Viết chương thực hiện quay động cơ RC servo theo các vị trí góc 20 độ và góc 160 độ, lặp đi lặp lại liên tục theo chu kỳ 1 giây.
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)


def set_servo_angle(angle):
    duty = angle / 18 + 2 #chuyen doi xung nhip
    GPIO.output(SERVO, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm.ChangeDutyCycle(0)

def main():
    while True:
        set_servo_angle(20)
        set_servo_angle(160)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

# Viết chương trình điều khiển tốc độ động cơ DC quay theo một chiều bất kỳ với tốc độ 50% so với tốc độ tối đa.
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PWM = 24
DIR = 25
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
pwm = GPIO.PWM(PWM, 1000)
pwm.start(0)

def motor_control(speed, direction):
    GPIO.output(DIR, direction)
    pwm.ChangeDutyCycle(speed)

def main():
    while True:
        motor_control(50, 0)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

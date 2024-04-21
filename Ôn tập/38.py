# Viết chương trình bấm button 1 sẽ thực hiện chụp 1 ảnh từ camera và hiện ảnh lên màn hình.
import cv2
import RPi.GPIO as GPIO
import time

nameWindow = "Camera User"


def main():
    BT_1 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    global nameWindow

    capture = cv2.VideoCapture(0)
    print("Capture ready")
    while True:
        ret, frame = capture.read()
        if GPIO.input(BT_1) == GPIO.LOW:
            while True:
                cv2.imshow("Camera picture", frame)
                cv2.waitKey()
                cv2.destroyWindow("Camera picture")
                break


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyWindow(nameWindow)

# Viết chương trình bấm button 1 sẽ xuất hiện cửa sổ hiện stream camera, và cửa sổ khác lọc hết những đối tượng khác,
# chỉ giữ lại những vật có màu đỏ. Bấm button 2 thì vẽ đường bao màu đỏ lên các đối tượng màu đỏ.
import cv2
import numpy as np
import copy
import RPi.GPIO as GPIO

def nothing(x):
    pass


def main():
    BT_1 = 21
    BT_2 = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    cap = cv2.VideoCapture(0)
    print("Camera ready")
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            print("Press BT_1")
            cv2.namedWindow('image')
            while True:
                _, scr = cap.read()
                hsv = cv2.cvtColor(scr, cv2.COLOR_BGR2HSV)
                lower_red = np.array([30, 150, 50])
                upper_red = np.array([255, 255, 180])
                mask = cv2.inRange(hsv, lower_red, upper_red)
                result = cv2.bitwise_or(scr, scr, mask=mask)
                cv2.imshow('image', result)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    GPIO.cleanup()
                    break

        if GPIO.input(BT_2) == GPIO.LOW:
            print("Press BT_2")
            cv2.namedWindow('image')
            while True:
                _, scr = cap.read()
                hsv = cv2.cvtColor(scr, cv2.COLOR_BGR2HSV)
                lower_red = np.array([0, 100, 100])
                upper_red = np.array([10, 255, 255])
                mask = cv2.inRange(hsv, lower_red, upper_red)

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(scr, contours, -1, (0, 0, 255), 2)

                cv2.imshow('Red contours', scr)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    GPIO.cleanup()
                    break



try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyAllWindows()

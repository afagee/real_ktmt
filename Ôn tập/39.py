# Viết chương trình bấm button 1 sẽ thực hiện quay video clip từ camera, khi không
# bấm button 1 sẽ dừng quay, video clip sẽ tự động lưu vào thư mục chứa tên bài tập khi
# dừng quay.
import cv2
import RPi.GPIO as GPIO
import time

name_window = "Camera User"


def main():
    BT_1 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    global name_window
    capture = cv2.VideoCapture(0)
    print("Capture da ok")
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640, 480))
    cap_video = False
    while True:
        ret, frame = capture.read()
        if GPIO.input(BT_1) == GPIO.LOW:
            print("Press BT_1")
            cv2.imshow(name_window, frame)
            out.write(frame)
            print("video luu")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                GPIO.cleanup()
                cv2.destroyWindow(name_window)
                break
            continue
        if cap_video:
            cv2.imshow(name_window, frame)
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            GPIO.cleanup()
            cv2.destroyWindow(name_window)
            break


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyWindow(name_window)

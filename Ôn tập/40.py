# Viết chương trình bấm button 1 lần 1 sẽ thực hiện quay video clip từ camera, bấm
# button 1 lần 2 sẽ dừng quay và lưu video clip vào trong thư mục chứa bài tập.
import cv2
import RPi.GPIO as GPIO
import time


def main():
    BT_1 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    name_window = "Camera User"
    capture = cv2.VideoCapture(0)
    print("Capture da ok")
    out = cv2.VideoWriter('output.avi', fourcc=cv2.VideoWriter_fourcc(*'MJPG'), fps=20.0, frameSize=(640, 490))
    cap_video = False
    button_pressed = False
    while True:
        ret, frame = capture.read()
        button_state = GPIO.input(BT_1)
        if button_state == GPIO.LOW and not button_pressed:
            button_pressed = True
            cap_video = not cap_video
            if not cap_video:
                cv2.destroyWindow(name_window)
                time.sleep(0.3)
        elif button_state == GPIO.HIGH:
            button_pressed = False
        if cap_video:
            cv2.imshow(name_window, frame)
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    out.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyAllWindows()

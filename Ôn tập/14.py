import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19
LED = 13
RELAY_1 = 16
RELAY_2 = 12
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE1 = 0x80
LCD_LINE2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)

def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)


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
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_display_state(message, state):
    message_1 = state[0] + message[0]
    message_2 = state[1] + message[1]
    print(message_1)
    print(message_2)
    lcd_display_string(message_1, LCD_LINE1)
    lcd_display_string(message_2, LCD_LINE2)

def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    message0 = ['Menu chinh', '']
    message1 = ['Menu 1', 'Menu 2']
    message2 = ['Menu 1_1', '']
    message3 = ['Menu 2_2', '']
    message4 = ['Bat LED', '']
    message5 = ['Relay 1', 'Relay 2']

    choice_0 = ['*', '']
    choice_1 = ['', '*']

    menu = [message0, message1, message2, message3, message4, message5]
    choice = [choice_0, choice_1]

    menu_state = 0
    choice_state = 0
    LED_state = GPIO.LOW
    RELAY_1_state = GPIO.LOW
    RELAY_2_state = GPIO.LOW

    while True:
        lcd_clear()
        lcd_display_state(menu[menu_state], choice[choice_state])
        if menu_state == 0:
            if GPIO.input(BT4) == GPIO.LOW:
                menu_state = 1
                choice_state = 0
                time.sleep(0.05)
                continue

        if menu_state == 1:
            if GPIO.input(BT1) == GPIO.LOW:
                menu_state = 0
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT2) == GPIO.LOW:
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT3) == GPIO.LOW:
                choice_state = 1
                time.sleep(0.05)
                continue
            if GPIO.input(BT4) == GPIO.LOW:
                if choice_state == 0:
                    menu_state = 2
                    choice_state = 0
                    time.sleep(0.05)

                if choice_state == 1:
                    menu_state = 3
                    choice_state = 0
                    time.sleep(0.05)
                continue

        if menu_state == 2:
            if GPIO.input(BT1) == GPIO.LOW:
                menu_state = 1
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT4) == GPIO.LOW:
                menu_state = 4
                choice_state = 0
                time.sleep(0.05)
                continue

        if menu_state == 3:
            if GPIO.input(BT1) == GPIO.LOW:
                menu_state = 1
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT4) == GPIO.LOW:
                menu_state = 5
                choice_state = 0
                time.sleep(0.05)
                continue

        if menu_state == 4:
            if GPIO.input(BT1) == GPIO.LOW:
                menu_state = 2
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT4) == GPIO.LOW:
                GPIO.output(LED, not LED_state)
                LED_state = not LED_state
                time.sleep(0.05)
                continue

        if menu_state == 5:
            if GPIO.input(BT1) == GPIO.LOW:
                menu_state = 3
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT2) == GPIO.LOW:
                choice_state = 0
                time.sleep(0.05)
                continue
            if GPIO.input(BT3) == GPIO.LOW:
                choice_state = 1
                time.sleep(0.05)
                continue
            if GPIO.input(BT4) == GPIO.LOW:
                if choice_state == 0:
                    GPIO.output(RELAY_1, not RELAY_1_state)
                    RELAY_1_state = not RELAY_1_state
                    time.sleep(0.05)
                if choice_state == 1:
                    GPIO.output(RELAY_2, not RELAY_2_state)
                    RELAY_2_state = not RELAY_2_state
                    time.sleep(0.05)
                continue

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()

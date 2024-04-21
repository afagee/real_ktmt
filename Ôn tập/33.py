# Viết chương trình hiển thị chữ Hello-world chạy từ phải qua trái trên LED matrix.
from PIL import Image, ImageDraw, ImageFont
import spidev
import time
import numpy as np
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10000000
spi.mode = 0b00

def max7219_write(register, data):
    spi.xfer2([register, data])

def max7219_init():
    max7219_write(0x0C, 0x01)
    max7219_write(0x0B, 0x07)
    max7219_write(0x09, 0x00)
    max7219_write(0x0A, 0x00)
    max7219_write(0x0F, 0x00)

def create_text_image(text, width, height):
    image = Image.new('1', (width, height), 0)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_size = 1
    text_position = (0, -1)
    draw.text(text_position, text, font=font, fill=1)
    return image

def display_image(image):
    pixels = np.array(image)
    for y in range(8):
        row_data = 0
        for x in range(8):
            if pixels[y, x]:
                row_data |= 1 << x
        max7219_write(y + 1, row_data)


def clear_matrix():
    max7219_write(0x0c, 0x00)

def main():
    max7219_init()
    while True:
        text = "hello world"
        width, height = 8 * len(text), 8
        image = create_text_image(text, width, height)
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        for x in range(0, width - 9, 1):
            cropped_image = flipped_image.crop((x, 0, x + 8, 8))
            display_image(cropped_image)
            time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    clear_matrix()
    spi.close()


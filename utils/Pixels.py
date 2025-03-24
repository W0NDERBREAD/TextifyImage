import logging
import math


def get_pixels(image):
    return list(image.getdata())


def brightness_less_than_threshold(pixel, max_threshold_brightness):
    return get_pixel_brightness(pixel) < max_threshold_brightness

1
def get_pixel_brightness(pixel):
    r, g, b = pixel
    return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))

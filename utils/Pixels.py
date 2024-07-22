import logging
import math

def get_pixels(image):
    return list(image.getdata())


def should_paint_pixel(pixel, max_threshold_brightness):
    return get_pixel_brightness(pixel) < max_threshold_brightness


def get_pixel_brightness(pixel):
    r, g, b, x = pixel
    return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))
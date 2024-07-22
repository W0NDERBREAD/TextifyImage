import argparse
import logging
import math
import sys

from PIL import Image

from utils.Pixels import should_paint_pixel

def scale_image_to_text(text, image, font_size, threshold):
    """
    Returns an image that has been scaled to account for the font ratio and so that every character of the text can
    be represented by a single pixel above the given threshold.

    Args:
        text: The text to scale to.
        image: The image to be scaled.
        font_size: The (x, y) pixel size of the font where x is the width and y is the height.
        threshold: The value representing the maximum brightness that will be represented by text.

    Returns:
        An image scaled so every character of text can be represented by a single pixel.
    """
    logging.info("scaling image to match text length")
    logging.info('using font_size: [%s], threshold: [%s]', font_size, threshold)
    logging.debug("original - width: [%s] height: [%s] pixels: [%s]: text[%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1], len(text))

    image = scale_for_font_ratio(image, font_size)
    logging.debug("scaled for font ratio - width: [%s] height: [%s] pixels: [%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1])

    image = scale_pixel_count_to_text_count(image, text, threshold)
    logging.debug("account for empty space - width: [%s] height: [%s]: pixels: [%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1])

    return image


def scale_for_font_ratio(image, font_size: tuple[int, int]):
    """
    Returns a resized image so that when all 'square' pixels are converted to rectangular characters the size of the image
    will stay the same.
    """
    font_pixel_ratio = font_size[1] / font_size[0]
    return image.resize((math.ceil(image.size[0] * font_pixel_ratio), image.size[1]))


def scale_pixel_count_to_text_count(image, text, threshold):
    """
    Resize the image so every pixel of the image can be represented by a single character from the text.  A pixel that 
    is below the given brightness threshold will be skipped and not represented by a character.

    Returns a resized image.
    """
    pixels = list(image.getdata())
    empty_pixels_count = get_empty_pixel_count(pixels, threshold)
    empty_pixel_ratio = empty_pixels_count / len(pixels)
    text_length = len(text)
    width, height = image.size
    logging.debug('text length: [%s] original width: [%s] height: [%s] empty pixel ratio: [%s]', text_length, width,
                  height, empty_pixel_ratio)

    # scale width/hight up or down until all of the characters can be represented by a single pixel above the brightness threshold
    # It's unlikely that the amount of charaters will match exactly so stop if the texts runs out on the last line or if adding
    # one more line would use up the rest of the text.
    while True:
        scalar = math.sqrt((width * height) / (text_length + (width * height * empty_pixel_ratio)))
        logging.debug("scaling by [%s]", scalar)
        old_width = width
        old_height = height
        width = math.ceil(width / scalar)
        height = math.ceil(height / scalar)
        logging.debug('new width: [%s] height: [%s]', width, height)

        new_area = width * height
        colored_pixels = new_area - (new_area * empty_pixel_ratio)
        text_difference = text_length - colored_pixels
        logging.debug('text difference: [%s]', text_difference)
        if math.fabs(text_difference) < width or (old_width == width and old_height == height):
            break

    # Add one extra line if there is some text left over
    if text_difference > 0:
        if width > height:
            logging.debug('adding 1 pixel to the height to account for missing text')
            height += 1
        else:
            logging.debug('adding 1 pixel to the width to account for missing text')
            width += 1

    logging.debug("unpainted pixels: [%s] painted pixels: [%s]", empty_pixels_count,
                  image.size[0] * image.size[1] - empty_pixels_count)

    return image.resize((width, height))


def get_empty_pixel_count(pixels, threshold):
    """
    Returns the number of pixels that should not be painted with a character.  A pixel shouldn't be painted if it's brightness falls below the given threshold.
    """
    empty_pixel_counter = 0
    for pixel in pixels:
        if not should_paint_pixel(pixel, threshold):
            empty_pixel_counter += 1
    return empty_pixel_counter
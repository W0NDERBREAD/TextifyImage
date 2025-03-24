import argparse
import logging
import math
import sys
import pprint

from PIL import Image

from utils.Pixels import brightness_less_than_threshold


def scale_image_to_text(text, image, font_size, should_paint_pixel_func, min_threshold):
    """
    Returns an image that has been scaled to account for the font ratio and so that every character of the text can
    be represented by a single pixel above the given threshold.

    Args:
        text: The text to scale to.
        image: The image to be scaled.
        font_size: The (x, y) pixel size of the font where x is the width and y is the height.
        should_paint_pixel_func: The method should be implemented by the processor and is used to determine if a pixel will result in a character being painted or skipped.

    Returns:
        An image scaled so every character of text can be represented by a single pixel.
    """
    logging.info("scaling image to match text length")
    logging.info('using font_size: [%s]', font_size)
    logging.debug("original - width: [%s] height: [%s] pixels: [%s]: text[%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1], len(text))

    image = scale_for_font_ratio(image, font_size)
    logging.debug("scaled for font ratio - width: [%s] height: [%s] pixels: [%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1])

    image = scale_pixel_count_to_text_count(
        image, text, should_paint_pixel_func, min_threshold)
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


def scale_pixel_count_to_text_count(image, text, should_paint_pixel_func, min_threshold):
    """
    Resize the image so every pixel of the image can be represented by a single character from the text.  A pixel that
    is below the given brightness threshold will be skipped and not represented by a character.

    Returns a resized image.
    """
    text_length = len(text)
    max_loop = 40
    counter = 0
    margin = text_length * .0001
    seen = {}

    logging.debug('text length: [%s]', text_length)

    # scale width/hight up or down until all of the characters can be represented by a single painted pixel as determined by the processors should_paint_pixel_func
    # It's unlikely that the amount of charaters will match exactly so get as close to an exact match without cutting off any characters.
    while True:
        counter += 1
        colored_pixel_count, width, height, diff = get_image_dimensions(
            image, should_paint_pixel_func, text_length, counter, margin, min_threshold)
        seen[str(width) + ',' + str(height)] = diff

        if counter > max_loop or (text_length < colored_pixel_count and abs(diff) < margin):
            break

        scalar = math.sqrt(abs(text_length / colored_pixel_count))
        logging.debug("scaling by [%s]", scalar)
        new_width = round(width * scalar)
        new_height = round(height * scalar)
        logging.debug(
            'new width: [%s] new height: [%s]', new_width, new_height)

        if str(new_width) + ',' + str(new_height) in seen:
            new_width += int(1 * diff / abs(diff))
            new_height += int(1 * diff / abs(diff))
            if str(new_width) + ',' + str(new_height) in seen:
                break
            logging.debug(
                'single pixel adjusted new width: [%s] and new height: [%s]', new_width, new_height)

        image = image.resize((new_width, new_height))

    filtered = {k: v for k, v in seen.items() if v < 0}
    closest = max(filtered, key=lambda k: filtered[k])
    logging.debug("closeset looping attempt: [%s]", str(closest))

    # Allow for the image ratio to be off by one pixel in either direction to see if we can get a little closer
    closest_width = int(closest.split(",")[0])
    closest_height = int(closest.split(",")[1])

    image = image.resize((closest_width+1, closest_height))
    colored_pixel_count, width, height, diff = get_image_dimensions(
        image, should_paint_pixel_func, text_length, counter, margin, min_threshold)
    seen[str(width) + ',' + str(height)] = diff

    image = image.resize((closest_width, closest_height+1))
    colored_pixel_count, width, height, diff = get_image_dimensions(
        image, should_paint_pixel_func, text_length, counter, margin, min_threshold)
    seen[str(width) + ',' + str(height)] = diff

    filtered = {k: v for k, v in seen.items() if v < 0}
    closest = max(filtered, key=lambda k: filtered[k])
    logging.debug("closeset after ratio wiggle: [%s]", str(closest))
    closest_width = int(closest.split(",")[0])
    closest_height = int(closest.split(",")[1])

    return image.resize((closest_width, closest_height))


def get_image_dimensions(image, should_paint_pixel_func, text_length, counter, margin, min_threshold):
    pixels = list(image.getdata())
    colored_pixel_count = get_colored_pixel_count(
        pixels, should_paint_pixel_func, min_threshold)
    width, height = image.size
    diff = text_length - colored_pixel_count

    logging.debug('\n\n[%s] - width: [%s] height: [%s] pixels: [%s] colored_pixels: [%s] text: [%s] diff: [%s] margin: [%s]',
                  counter, width, height, len(pixels), colored_pixel_count, text_length, diff, margin)

    return colored_pixel_count, width, height, diff


def get_colored_pixel_count(pixels, should_paint_pixel_func, min_threshold):
    """
    Returns the number of pixels that should not be painted with a character.  A pixel shouldn't be painted if it's brightness falls below the given threshold.
    """
    count = 0
    for pixel in pixels:
        if should_paint_pixel_func(pixel, min_threshold):
            count += 1
    return count

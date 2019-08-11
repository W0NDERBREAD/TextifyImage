import argparse
import logging
import math
import sys

from PIL import Image


def scale_image_to_text(text, image, font_size: (int, int) = (9, 19), threshold: float = 250.0):
    """
    Returns an image that has been scaled to account for the font ratio and so that every character of the text can
    be represented by a single pixel above the given threshold

    Args:
        text: The text to scale to
        image: The image to be scaled
        font_size: The (x, y) pixel size of the font where x is the width and y is the height
        threshold: The value representing the maximum brightness that will be represented by text

    Returns:
        An image scaled so every character of text can be represented by a single pixel
    """
    logging.info("scaling image to match text length")
    logging.info('using font_size: [%s], threshold: [%s]', font_size, threshold)
    logging.debug("original - width: [%s] height: [%s] pixels: [%s]: text[%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1], len(text))

    image = account_for_font_ratio(image, font_size)
    logging.debug("scaled for font ratio - width: [%s] height: [%s] pixels: [%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1])

    image = account_for_empty_space(image, text, threshold)
    logging.debug("account for empty space - width: [%s] height: [%s]: pixels: [%s]", image.size[0], image.size[1],
                  image.size[0] * image.size[1])

    empty_pixels = get_empty_pixel_count(list(image.getdata()), threshold)
    logging.debug("unpainted pixels: [%s] painted pixels: [%s]", empty_pixels,
                  image.size[0] * image.size[1] - empty_pixels)

    return image


def account_for_font_ratio(image, font_size: (int, int)):
    """Resize image so that when all 'square' pixels are converted to rectangular characters the size of the image
    will stay the same
    """
    font_pixel_ratio = font_size[1] / font_size[0]
    return image.resize((math.ceil(image.size[0] * font_pixel_ratio), image.size[1]))


def account_for_empty_space(image, text, threshold):
    pixels = list(image.getdata())
    empty_pixels_count = get_empty_pixel_count(pixels, threshold)
    empty_pixel_ratio = empty_pixels_count / len(pixels)
    text_length = len(text)
    width, height = image.size
    logging.debug('text length: [%s] original width: [%s] height: [%s] empty pixel ratio: [%s]', text_length, width,
                  height, empty_pixel_ratio)

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

    if text_difference > 0:
        if width > height:
            logging.debug('adding 1 pixel to the height to account for missing text')
            height += 1
        else:
            logging.debug('adding 1 pixel to the width to account for missing text')
            width += 1

    return image.resize((width, height))


def get_empty_pixel_count(pixels, threshold):
    empty_pixel_counter = 0
    for pixel in pixels:
        if not should_paint_pixel(pixel, threshold):
            empty_pixel_counter += 1
    return empty_pixel_counter


# TODO: Make common method
def should_paint_pixel(pixel, threshold):
    return get_pixel_brightness(pixel) < threshold


# TODO: Make common method
def get_pixel_brightness(pixel):
    """Pixel brightness value between 0 and 255 where white = 255 and black = 0"""
    r, g, b, x = pixel
    return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))


def get_text(filename):
    logging.info("retrieving text from [%s]", filename)
    text = ""
    try:
        file = open(filename, encoding='UTF-8')
        for line in file:
            text += line.replace('\n', ' ')
    except UnicodeDecodeError as ex:
        logging.critical("Unable to process: " + filename + "\n\t{0}".format(ex))
        sys.exit()
    finally:
        file.close()
    return text


def set_logging_level(log_level):
    if log_level == 'CRITICAL':
        logging.basicConfig(level=logging.CRITICAL)
    elif log_level == 'ERROR':
        logging.basicConfig(level=logging.ERROR)
    elif log_level == 'WARNING':
        logging.basicConfig(level=logging.WARNING)
    elif log_level == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Scales an image to fit the size of the text')
    parser.add_argument('-t', '--text_location', help='The text file to be used', required=True)
    parser.add_argument('-i', '--image_location', help='The image file to be used', required=True)
    parser.add_argument('-x', '--font_width', default=9, help='The width of the font in pixels')
    parser.add_argument('-y', '--font_height', default=19, help='The height of the font in pixels')
    parser.add_argument('-b', '--brightness_threshold', type=float, default=250.0,
                        help='The brightness value (float) to which each pixel must be below to have a character '
                             'drawn to represent it')
    parser.add_argument('-o', '--output_name', help='The location and name of the image to output')
    parser.add_argument('-l', '--log_level', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                  'CRITICAL] (default: INFO)')
    args = parser.parse_args()

    set_logging_level(args.log_level)

    image = Image.open(args.image_location).convert("RGBA")
    text = get_text(args.text_location)

    image = scale_image_to_text(text, image, (args.font_width, args.font_height), args.brightness_threshold)

    logging.info("saving image to [%s]", args.output_name)
    image.save(args.output_name)


if __name__ == '__main__':
    main()

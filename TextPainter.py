import argparse
import logging
import sys

from PIL import Image, ImageFont

from text_painter import ImageScaler, Painter


def get_text_image(text, image, font, font_size: (int, int) = (9, 19), margin: (int, int) = (0, 0),
                   threshold: float = 250.0):
    """
    Creates an image where each pixel of a picture is represented by a single character from the text.  The color of
    the pixel is preserved and only pixels with a brightness above the given threshold will not be represented by a
    character.

    Args:
        text: The text to use when replacing pixels
        image: The image to paint
        font: An ImageFont (should be monospaced)
        font_size: The (x, y) pixel size of the font where x is the width and y is the height
        margin: A margin to add a border of the image
        threshold: The value representing the maximum brightness that will be represented by text

    Returns:
        An image made of text
    """
    logging.info('processing text into image')

    scaled_image = ImageScaler.scale_image_to_text(text, image, font_size, threshold)
    text_image = Painter.get_image_of_text(text, scaled_image, font, font_size, margin, threshold)

    return text_image


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
    parser = argparse.ArgumentParser(description='Creates image ')
    parser.add_argument('-t', '--text_location', help='The text file to be used', required=True)
    parser.add_argument('-i', '--image_location', help='The image file to be used', required=True)
    parser.add_argument('--x_margin', default=0, type=int, help='The number of pixels to add as a horizontal border')
    parser.add_argument('--y_margin', default=0, type=int, help='The number of pixels to add as a vertical border')
    parser.add_argument('--font_width', default=9, type=int, help='The width of the font in pixels')
    parser.add_argument('--font_height', default=19, type=int, help='The height of the font in pixels')
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
    font = ImageFont.truetype('c:/Windows/Fonts/Arial/LTYPE.TTF', 15)

    image = get_text_image(text, image, font, (args.font_width, args.font_height), (args.x_margin, args.y_margin),
                           args.brightness_threshold)

    logging.info("saving image to [%s]", args.output_name)
    image.save(args.output_name)


if __name__ == '__main__':
    main()

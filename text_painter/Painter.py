import argparse
import logging
import math
import sys

from PIL import Image, ImageFont, ImageDraw


def get_image_of_text(text, image, font, font_size: (int, int) = (9, 19), margin: (int, int) = (0, 0),
                      threshold: float = 250.0):
    """
    Returns an image where each pixel is represented by a character from text

    Args:
        text: The text to use when replacing pixels
        image: The image to paint
        font: An ImageFont
        font_size: The (x, y) pixel size of the font where x is the width and y is the height
        margin: A margin to add a border of the image
        threshold: The value representing the maximum brightness that will be represented by text

    Returns:
        An image made of text
    """
    logging.info('converting text to image')
    logging.info('using margin: [%s], threshold: [%s]', margin, threshold)
    width, height = image.size
    text_size = len(text)
    logging.debug('original width: [%s] height: [%s]', width, height)
    final_image = Image.new('RGBA',
                            (width * font_size[0] + margin[0] * 2, math.ceil(height * font_size[1]) + margin[1] * 2),
                            (255, 255, 255, 255))
    s_width, s_height = final_image.size
    logging.debug('scaled for character width: [%s] height: [%s]', s_width, s_height)
    d = ImageDraw.Draw(final_image)
    x = margin[0]
    y = margin[1]
    pixel_count = 0
    text_count = 0
    logging.info('painting text to canvas (this could take a while)')
    for pixel in get_pixels(image):
        if should_paint_pixel(pixel, threshold):
            d.text((x, y), text[text_count % text_size], font=font, fill=pixel)
            text_count += 1
        x += font_size[0]
        pixel_count += 1
        if pixel_count % width == 0:
            x = margin[0]
            y += font_size[1]

    logging.info('painting finished')
    return final_image


def get_pixels(image):
    return list(image.getdata())


# TODO: Make common
def should_paint_pixel(pixel, threshold_brightness):
    return get_pixel_brightness(pixel) < threshold_brightness


# TODO: Make common
def get_pixel_brightness(pixel):
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
    parser.add_argument('--x_margin', default=0, help='The width of the font in pixels')
    parser.add_argument('--y_margin', default=0, help='The height of the font in pixels')
    parser.add_argument('--font_width', default=9, help='The width of the font in pixels')
    parser.add_argument('--font_height', default=19, help='The height of the font in pixels')
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

    image = get_image_of_text(text, image, font, (args.font_width, args.font_height), (args.x_margin, args.y_margin),
                              args.brightness_threshold)

    logging.info("saving image to [%s]", args.output_name)
    image.save(args.output_name)


if __name__ == '__main__':
    main()

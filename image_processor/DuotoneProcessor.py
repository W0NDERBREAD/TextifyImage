import argparse
import ast
import logging
import math

from PIL import Image


def process(image, arguments):
    """
    Converts an image into a duotone image consisting of a primary and secondary color.  Each pixel is converted to
    the primary color if it is above a given brightness threshold and the secondary color otherwise.  By default the
    threshold is the average color of the picture, the primary color is black and the secondary color is white

    Args:
        image: The image to process
        arguments: A list of arguments [threshold, is_above, primary_color, secondary_color].  Omitting a value or
                   passing None will use the default value
            threshold: The brightness threshold used to decide the pixel color. default: average color brightness
            is_above: Weather or not to use the primary color when the pixel brightness is above or below the
                      threshold. default: False
            primary_color: The RGB value of the primary color. default: (0, 0, 0)
            secondary_color: The RGB value of the secondary color. default: (255, 255, 255)

    Returns:
        A duotone image
    """

    threshold, is_above, primary_color, secondary_color = get_arguments(arguments)
    logging.info(
        'processing image with arguments - threshold: [%s] is_above: [%s] primary_color: [%s] secondary_color: [%s]',
        threshold, is_above, primary_color, secondary_color)

    average_color = get_average_color(image)
    logging.debug("average color: [%s] average color brightness: [%s]", average_color,
                  get_pixel_brightness(average_color))

    pixels = get_pixels(image)
    new_pixels = []
    for pixel in pixels:
        if should_paint_pixel(pixel, average_color, threshold, is_above):
            new_pixels.append(primary_color)
        else:
            new_pixels.append(secondary_color)
    processed_image = Image.new(image.mode, image.size)
    processed_image.putdata(new_pixels)

    return processed_image


def get_average_color(image):
    temp_image = image.resize((1, 1), Image.ANTIALIAS)
    return temp_image.getpixel((0, 0))


def should_paint_pixel(pixel, average_color, threshold, is_above):
    color_brightness = threshold if threshold is not None else get_pixel_brightness(average_color)
    pixel_brightness = get_pixel_brightness(pixel)
    return pixel_brightness > color_brightness if is_above else pixel_brightness < color_brightness


def get_pixel_brightness(pixel):
    r, g, b, x = pixel
    return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))


def get_pixels(image):
    return list(image.getdata())


def get_arguments(arguments):
    arguments = [] if arguments is None else arguments
    default_threshold = None
    default_is_above = False
    default_primary_color = (0, 0, 0)
    default_secondary_color = (255, 255, 255)

    arguments += ['None'] * (4 - len(arguments))

    return default_or_argument(arguments[0], default_threshold), \
           default_or_argument(arguments[1], default_is_above), \
           default_or_argument(arguments[2], default_primary_color), \
           default_or_argument(arguments[3], default_secondary_color)


def default_or_argument(argument, default):
    argument = ast.literal_eval(argument)
    return default if argument is None else argument


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
    parser.add_argument('-i', '--image_location', help='The image file to be used', required=True)
    parser.add_argument('-a', '--arguments', nargs='*', help='a list of arguments to be passed to the processor')
    parser.add_argument('-o', '--output_name', help='The location and name of the image to output')
    parser.add_argument('-l', '--log_level', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                  'CRITICAL] (default: INFO)')
    args = parser.parse_args()

    set_logging_level(args.log_level)

    image = Image.open(args.image_location).convert("RGBA")

    image = process(image, args.arguments)

    logging.info("saving image to [%s]", args.output_name)
    image.save(args.output_name)


if __name__ == '__main__':
    main()

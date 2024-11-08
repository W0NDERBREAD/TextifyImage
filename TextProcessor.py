import argparse
import importlib
import logging
import os
import sys

from PIL import Image, ImageFont

import text_painter.TextPainter as TextPainter
import text_painter.ImageScaler as ImageScaler


def main():
    parser = argparse.ArgumentParser(description='Converts the image to an image of text')
    parser.add_argument('-i', '--image', help='The image file to be used', required=True)
    parser.add_argument('-t', '--text', help='The text file to be used', required=True)
    parser.add_argument('-o', '--output', help='Filename to save the processed image to.', required=True)
    parser.add_argument('-f', '--font', nargs=3, default=[os.path.join('.', 'fonts', 'JetBrainsMono', '2.304', 'fonts', 'ttf','JetBrainsMono-Regular.ttf'), 9, 15], help='Font to be used.  Must include Filename of a TrueType (.ttf) font, font width in pixels when rendered at 15px, and height when rendered at 15px (which should be 15). (default: (JetBrainsMono-Regular.ttf, 9, 15))')
    parser.add_argument('-m', '--margin', type=int, nargs=2, default=[0,0], help='The number of pixels to add as a margin around the final image. Must include both a width and a height (default: 0 0)')
    parser.add_argument('-c', '--char_threshold', type=float, default=250.0, help='A brightness threshold between 0 (black) and 255 (white).  Pixels below this threshold wont be replaced by a character and will be left blank.  (default: 250)')
    parser.add_argument('-b', '--background_color', type=int, nargs=3, default=[255,255,255], help='The RGB values of the color to use for the background of the image (default: 255 255 255)')
    parser.add_argument('-p', '--processor', default='DuotoneProcessor',
                        help='pre-process the image using the given processor')
    parser.add_argument('-a', '--processor_arguments', nargs='*',
                        help='a list of arguments to be passed to the processor')
    parser.add_argument('--processor_only', action=argparse.BooleanOptionalAction, help='Only run the processor without converting to characters. Useful for testing custom processors.')
    parser.add_argument('--logging', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                'CRITICAL] (default: INFO)')
    args = normalize_args(parser.parse_args())

    logging.info("getting image from [%s] and text from [%s]", args.image, args.text)
    image = Image.open(args.image).convert("RGBA")
    text = get_text(args.text)
    font = (ImageFont.truetype(args.font[0], 15), int(args.font[1]), int(args.font[2]))

    image = process(image, text, font, (args.margin[0], args.margin[1]), float(args.char_threshold), args.background_color, args.processor, args.processor_arguments, args.processor_only)

    logging.info("saving image to [%s]", args.output)
    image.save(args.output)
    logging.info("processing complete")


def normalize_args(args):
    set_logging_level(args.logging)

    return args


def process(image, text, font, margin, char_threshold, background_color, processor_name, processor_arguments, processor_only):
    """
    Converts an image to a text image where each pixel is replaced by a single character.  By default the image will
    be turned into a duotone image, but a different processor can be supplied.

    Args:
        image: The image.
        text: The text.
        font:  A tuple containing (An ImageFont (should be monospaced), font pixel width, font pixel height).
        margin: A tuple (margin width, margin height) containing the pixel margin to add a border of the image.
        char_threshold: A brightness threshold between 0 (black) and 255 (white).  Pixels below this threshold wont be replaced by a character and will be left blank.
        background_color: A tuple containing the RGB values to be used for the background color of the image.
        processor_name: The processor used to process the image.  Must be located in image_processor/processors and must
            extend image_processor.Processor.py. default: DuotoneProcessor
        processor_arguments: A list of arguments to be passed to the processor.
        processor_only: Only run the processor and save the image without converting to characters. default: False

    Returns:
        An image made out of the text.
    """

    if not processor_only:
        image = ImageScaler.scale_image_to_text(text, image, (font[1], font[2]), char_threshold)

    processor_module = importlib.import_module("image_processor.processors." + processor_name)
    processor = getattr(processor_module, processor_name)

    image = processor.process(processor, image, processor_arguments)

    if not processor_only:
        image = TextPainter.get_text_image(text, image, font, margin, char_threshold, background_color)

    return image

    
def get_text(filename):
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


def write_to_file(text_image, text_file):
    try:
        file = open(text_file, mode='wt', encoding='UTF-8')
        file.write(text_image)
        logging.info('writing text image to file: [%s]', os.path.abspath(file.name))
    except UnicodeDecodeError as ex:
        logging.critical("unable to process: " + text_file + "\n\t{0}".format(ex))
        sys.exit()
    finally:
        file.close()


if __name__ == '__main__':
    main()

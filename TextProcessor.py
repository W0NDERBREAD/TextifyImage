import argparse
import logging
import os
import sys

from PIL import Image, ImageFont

from image_processor import DuotoneProcessor
import TextPainter


def main():
    parser = argparse.ArgumentParser(description='Converts the image to an image of text')
    parser.add_argument('-i', '--image', help='The image file to be used', required=True)
    parser.add_argument('-t', '--text', help='The text file to be used', required=True)
    parser.add_argument('-o', '--output_location', help='Name of the directory to be used for output', required=True)
    parser.add_argument('-n', '--output_name', help='Name of the file to be used for the text and image file.  Do not '
                                                    'include the extension', required=True)
    parser.add_argument('-m', '--margin', type=int, default=0, help='The number of pixels to add as a margin around the'
                                                                    ' final image (default: 0)')
    parser.add_argument('-p', '--processor', help='pre-process the image using the given processor')
    parser.add_argument('-a', '--processor_arguments', nargs='*',
                        help='a list of arguments to be passed to the processor')
    parser.add_argument('-l', '--logging', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                'CRITICAL] (default: INFO)')
    args = massage_args(parser.parse_args())

    process(args.image, args.text, args.output_location, args.output_name, args.margin, args.processor,
            args.processor_arguments)


def massage_args(args):
    log_arg = args.logging
    if log_arg == 'CRITICAL':
        logging.basicConfig(level=logging.CRITICAL)
    elif log_arg == 'ERROR':
        logging.basicConfig(level=logging.ERROR)
    elif log_arg == 'WARNING':
        logging.basicConfig(level=logging.WARNING)
    elif log_arg == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    args.margin = 0 if args.margin < 0 else args.margin

    return args


def process(image_location, text_location, output_location, name, margin, processor, processor_arguments):
    """
    Converts an image to a text image where each pixel is replaced by a single character.  By default the image will
    be turned into a duotone image, but a different processor can be supplied

    Args:
        image_location: The location of the image
        text_location: The location of the text
        output_location: The location to save the new image
        name: The name used to save the new image (Should not include an extension i.e. jpeg)
        margin: The number of pixels used to add an empty border around the image.  default: 0
        processor: The processor used to process the image.  default: DuotoneProcessor
        processor_arguments: A list of arguments to be passed to the processor

    Returns:
        An image made out of the text
    """
    logging.info("getting image from [%s]", image_location)
    image = Image.open(image_location).convert("RGBA")
    text = get_text(text_location)
    # TODO: pass font location as an argument
    font = ImageFont.truetype('c:/Windows/Fonts/Arial/LTYPE.TTF', 15)

    # TODO: use the supplied processor
    image = DuotoneProcessor.process(image, processor_arguments)

    image = TextPainter.get_text_image(text, image, font, margin=(margin, margin))

    if not os.path.exists(output_location):
        os.makedirs(output_location)

    logging.info("saving image to [%s]", output_location + '\\' + name + '.png')
    image.save(output_location + '\\' + name + '.png')
    logging.info("processing complete")


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

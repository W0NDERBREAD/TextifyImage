import argparse
import ast
import logging

from PIL import Image


class Processor:
    """Process an image"""

    def process(self, image, arguments):
        pass

    @staticmethod
    def get_pixels(image):
        """Returns a list of pixels from a given image"""
        return list(image.getdata())

    def get_arguments(self, arguments, defaults):
        arguments = [] if arguments is None else arguments
        arguments += ['None'] * (len(defaults))

        processed_arguments = []
        for i in range(len(defaults)):
            processed_arguments.append(self._default_or_argument(arguments[i], defaults[i]))

        return processed_arguments

    @staticmethod
    def _default_or_argument(argument, default):
        argument = ast.literal_eval(argument)
        return default if argument is None else argument

    @staticmethod
    def _set_logging_level(log_level):
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

    def main(self):
        parser = argparse.ArgumentParser(description='Creates image ')
        parser.add_argument('-i', '--image_location', help='The image file to be used', required=True)
        parser.add_argument('-a', '--arguments', nargs='*', help='a list of arguments to be passed to the processor')
        parser.add_argument('-o', '--output_name', help='The location and name of the image to output')
        parser.add_argument('-l', '--log_level', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                      'CRITICAL] (default: INFO)')
        args = parser.parse_args()

        self._set_logging_level(args.log_level)

        image = Image.open(args.image_location).convert("RGBA")

        image = self.process(image, args.arguments)

        logging.info("saving image to [%s]", args.output_name)
        image.save(args.output_name)

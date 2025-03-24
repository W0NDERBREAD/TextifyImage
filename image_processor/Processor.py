import argparse
import ast
import logging

from PIL import Image


class Processor:
    """Process an image"""

    def __init__(self, image, arguments):
        """Init method called by TextProcessor to setup processor variables.  This method needs to be implemented by custom processors."""
        pass

    def process(self):
        """Method called by TextProcessor to process the given image.  This method needs to be implemented by custom processors."""
        pass

    def should_paint_pixel(self, pixel, min_threshold):
        """Method called during image scaling to determine if a pixel will paint a character or skip.  This method needs to be implemented by custom processors."""
        pass

    def get_arguments(self, arguments, defaults):
        """Returns the list of arguments where default values are used if an argument value is not provided."""
        arguments = [] if arguments is None else arguments
        arguments += ['None'] * (len(defaults))

        processed_arguments = []
        for i in range(len(defaults)):
            processed_arguments.append(
                self._default_or_argument(arguments[i], defaults[i]))

        return processed_arguments

    @staticmethod
    def _default_or_argument(argument, default):
        argument = ast.literal_eval(argument)
        return default if argument is None else argument

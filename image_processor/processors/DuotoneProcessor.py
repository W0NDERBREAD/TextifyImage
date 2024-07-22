import logging
import math

from PIL import Image  # type: ignore

from image_processor.Processor import Processor
from utils.Pixels import get_pixel_brightness, get_pixels


class DuotoneProcessor(Processor):
    """
        Processes an image into a duotone image consisting of a primary and secondary color.  Each pixel is converted to
        the primary color if it is below a given brightness threshold and the secondary color otherwise.  By default the
        threshold is the average color of the picture, the primary color is black and the secondary color is white.
    """

    def process(self, image, arguments):
        """
        Processes an image into a duotone image.

        Args:
            image: The image to process.
            arguments: A list of arguments [threshold, primary_color, secondary_color].  Omitting a value or
                       passing None will use the default value.
                primary_color: The RGB value of the primary color. default: (0, 0, 0)
                secondary_color: The RGB value of the secondary color. default: (255, 255, 255)
                threshold: Pixels with a brightness below threshold will be considered primary. default: average color brightness of image

        Returns:
            A duotone image
        """
        default_args = [(0, 0, 0), (255, 255, 255),
                        get_pixel_brightness(self._get_average_color(image))]
        primary_color, secondary_color, threshold = self.get_arguments(
            self, arguments, default_args)
        logging.info('processing image using [%s] with arguments - threshold: [%s] primary_color: [%s] '
                     'secondary_color: [%s]', __name__, threshold, primary_color, secondary_color)

        new_pixels = []
        for pixel in get_pixels(image):
            if self._is_primary_color(pixel, threshold):
                new_pixels.append(primary_color)
            else:
                new_pixels.append(secondary_color)
        processed_image = Image.new(image.mode, image.size)
        processed_image.putdata(new_pixels)

        return processed_image

    @staticmethod
    def _get_average_color(image):
        temp_image = image.resize((1, 1), Image.LANCZOS)
        return temp_image.getpixel((0, 0))

    @staticmethod
    def _is_primary_color(pixel, threshold):
        """
        A pixel is considered the primary color if it's brightness is below the given threshold.

        Returns:
            true if the pixel should be the primary color, false otherwise.
        """
        pixel_brightness = get_pixel_brightness(pixel)
        return pixel_brightness < threshold

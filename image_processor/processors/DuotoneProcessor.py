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

    def __init__(self, image, arguments):
        """Initialize the DuotoneProcessor.

        Args:
            image: The image to process.
            arguments: A list of arguments [threshold, primary_color, secondary_color].  Omitting a value or
                       passing None will use the default value.
                primary_color: The RGB value of the primary color. default: (0, 0, 0)
                secondary_color: The RGB value of the secondary color. default: (255, 255, 255)
                threshold: Pixels with a brightness below threshold will be considered primary. default: average color brightness of image
        """
        default_args = [(0, 0, 0), (255, 255, 255),
                        get_pixel_brightness(self._get_average_color(image))]
        self.primary_color, self.secondary_color, self.threshold = self.get_arguments(
            arguments, default_args)
        self.image = image

    def process(self):
        """
        Processes an image into a duotone image.

        Returns:
            A duotone image
        """
        logging.info('processing image using [%s] with arguments - threshold: [%s] primary_color: [%s] '
                     'secondary_color: [%s]', __name__, self.threshold, self.primary_color, self.secondary_color)

        new_pixels = []
        colored_pixel = white_pixel = 0
        for pixel in get_pixels(self.image):
            if self._is_primary_color(pixel, self.threshold):
                new_pixels.append(self.primary_color)
                colored_pixel += 1
            else:
                new_pixels.append(self.secondary_color)
                white_pixel += 1
        processed_image = Image.new(self.image.mode, self.image.size)
        processed_image.putdata(new_pixels)

        logging.debug(
            'processor - colored_pixel: [%s] white_pixel: [%s]', colored_pixel, white_pixel)

        self.image = processed_image

    def should_paint_pixel(self, pixel):
        """Method called during image scaling to determine if a pixel will paint a character or skip.  This method needs to be implemented by custom processors."""
        return self._is_primary_color(pixel, self.threshold)

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

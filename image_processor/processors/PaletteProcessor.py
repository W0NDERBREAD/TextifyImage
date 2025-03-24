import logging
import math

from PIL import Image  # type: ignore

from image_processor.Processor import Processor
from utils.Pixels import get_pixel_brightness, get_pixels, brightness_less_than_threshold


class PaletteProcessor(Processor):
    """
        Processes an image by converting each pixel to the closest pixel from a given list.
    """

    def __init__(self, image, arguments):
        """
        Initialize the PaletteProcessor.

        Args:
            image: The image to process.
            arguments: A list of arguments [palette].  Omitting a value or passing None will use the default value.
                palette: A list of RGB values to make up the palette. default: [(0, 0, 0), (255, 255, 255)]
        """
        palette_string = '[0 0 0,255 255 255]' if arguments[0] is None else arguments[0]
        self.palette = self._string_to_tuple_list(palette_string)
        self.image = image

    def process(self):
        """
        Processes an image into an image made up only of colors from a given palette.

        Returns:
            An image using on the palette
        """
        calculated_colors = {}
        logging.info(
            'processing image using [%s] with arguments - palette: [%s]', __name__, self.palette)

        new_pixels = []
        new_pixel = None
        for pixel in get_pixels(self.image):
            if pixel in calculated_colors:
                new_pixel = calculated_colors[pixel]
            else:
                new_pixel = self._find_closest_color(
                    (pixel[0], pixel[1], pixel[2]), self.palette)
                calculated_colors[pixel] = new_pixel
            new_pixels.append(new_pixel)
        processed_image = Image.new(self.image.mode, self.image.size)
        processed_image.putdata(new_pixels)

        self.image = processed_image

    def should_paint_pixel(self, pixel, min_threshold):
        """Method called during image scaling to determine if a pixel will paint a character or skip.  This method needs to be implemented by custom processors."""
        return brightness_less_than_threshold(self._find_closest_color((pixel[0], pixel[1], pixel[2]), self.palette), min_threshold)

    @staticmethod
    def _string_to_tuple_list(s):
        """
        Converts a string of comma-separated space-delimited numbers 
        (representing RGB values) into a list of tuples.

        Args:
            string: The input string.

        Returns:
            A list of tuples, where each tuple represents an RGB color.
        """

        s = s.strip('[]')
        color_strings = s.split(',')
        tuple_list = []

        for color_string in color_strings:
            rgb_values = color_string.split()
            rgb_values = [int(value) for value in rgb_values]
            tuple_list.append(tuple(rgb_values))

        return tuple_list

    @staticmethod
    def _color_distance(color1, color2):
        """
        Calculates the Euclidean distance between two RGB colors.

        Args:
            color1: A tuple of 3 integers representing the RGB values of the first color.
            color2: A tuple of 3 integers representing the RGB values of the second color.

        Returns:
            The Euclidean distance between the two colors.
        """

        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    def _find_closest_color(self, pixel_color, color_list):
        """
        Finds the color in the given list that is closest to the pixel color.

        Args:
            pixel_color: A tuple of 3 integers representing the RGB values of the pixel.
            color_list: A list of tuples, where each tuple represents the RGB values of a color.

        Returns:
            The closest color in the list to the pixel color, as a tuple of RGB values.
        """
        closest_color = color_list[0]
        min_distance = self._color_distance(pixel_color, closest_color)

        for color in color_list[1:]:
            distance = self._color_distance(pixel_color, color)
            if distance < min_distance:
                min_distance = distance
                closest_color = color

        return closest_color

import logging
import math

from PIL import Image # type: ignore

from image_processor.Processor import Processor


class DuotoneProcessor(Processor):
    """
        Processes an image into a duotone image consisting of a primary and secondary color.  Each pixel is converted to
        the primary color if it is above a given brightness threshold and the secondary color otherwise.  By default the
        threshold is the average color of the picture, the primary color is black and the secondary color is white.
    """

    def process(self, image, arguments):
        """
        Processes an image into a duotone image

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
        default_args = [None, False, (0, 0, 0), (255, 255, 255)]
        threshold, is_above, primary_color, secondary_color = Processor.get_arguments(self, arguments, default_args)
        logging.info('processing image using [%s] with arguments - threshold: [%s] is_above: [%s] primary_color: [%s] '
                     'secondary_color: [%s]', __name__, threshold, is_above, primary_color, secondary_color)

        average_color = self.get_average_color(image)
        logging.debug("average color: [%s] average color brightness: [%s]", average_color,
                      self.get_pixel_brightness(average_color))

        pixels = Processor.get_pixels(image)
        new_pixels = []
        for pixel in pixels:
            if self.should_paint_pixel(self, pixel, average_color, threshold, is_above):
                new_pixels.append(primary_color)
            else:
                new_pixels.append(secondary_color)
        processed_image = Image.new(image.mode, image.size)
        processed_image.putdata(new_pixels)

        return processed_image

    @staticmethod
    def get_average_color(image):
        temp_image = image.resize((1, 1), Image.LANCZOS)
        return temp_image.getpixel((0, 0))

    def should_paint_pixel(self, pixel, average_color, threshold, is_above):
        color_brightness = threshold if threshold is not None else self.get_pixel_brightness(average_color)
        pixel_brightness = self.get_pixel_brightness(pixel)
        return pixel_brightness > color_brightness if is_above else pixel_brightness < color_brightness

    @staticmethod
    def get_pixel_brightness(pixel):
        r, g, b, x = pixel
        return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))

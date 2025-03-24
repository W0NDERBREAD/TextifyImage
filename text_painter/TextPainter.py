import logging
import math

from PIL import Image, ImageDraw  # type: ignore

from utils.Pixels import get_pixels, brightness_less_than_threshold


def get_text_image(text, image, font, margin, threshold, background_color):
    """
    Creates an image where each pixel of the image is represented by a single character from the text.  The color of
    the pixel is preserved and only pixels with a brightness above the given threshold will not be represented by a
    character.

    Args:
        text: The text to use when replacing pixels.
        image: The image to paint.
        font: A tuple containing (An ImageFont (should be monospaced), font pixel width, font pixel height).
        margin: A tuple (margin width, margin height) containing the pixel margin to add a border of the image.
        threshold: The value representing the maximum brightness that will be represented by text.
        background_color: A tuple containing the RGB values to be used for the background color of the image.

    Returns:
        An image made of text.
    """
    logging.info('converting text to image')
    logging.info('using margin: [%s], threshold: [%s], font_size: [%s]',
                 margin, threshold, (font[1], font[2]))
    width, height = image.size
    text_size = len(text)
    logging.debug('original width: [%s] height: [%s]', width, height)
    final_image = Image.new('RGBA',
                            (width * font[1] + margin[0] * 2,
                             math.ceil(height * font[2]) + margin[1] * 2),
                            (background_color[0], background_color[1], background_color[2], 255))
    s_width, s_height = final_image.size

    logging.debug(
        'scaled for character width: [%s] height: [%s]', s_width, s_height)
    d = ImageDraw.Draw(final_image)
    x, y = margin
    pixel_count, text_count = (0, 0)

    white_pixels = 0

    logging.info('painting text to canvas (this could take a while)')
    for pixel in get_pixels(image):
        if brightness_less_than_threshold(pixel, threshold):
            d.text((x, y), text[text_count %
                   text_size], font=font[0], fill=pixel)
            text_count += 1
        else:
            white_pixels += 1
        x += font[1]
        pixel_count += 1
        if pixel_count % width == 0:
            x = margin[0]
            y += font[2]

    logging.debug(
        'painter - painted_pixels: [%s] white_pixels: [%s]', text_count, white_pixels)

    logging.info('painting finished')
    return final_image

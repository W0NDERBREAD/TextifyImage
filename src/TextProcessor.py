import argparse
import logging
import os, sys, math
from PIL import Image, ImageFilter, ImageFont, ImageDraw
from pip._vendor.msgpack.fallback import xrange


def is_pixel_below_average(pixel, color):
    return get_pixel_brightness(pixel) < get_pixel_brightness(color)


def pre_process(image):
    image.filter(ImageFilter.SMOOTH_MORE)
    return image


def enough_text_for_edge(edge_size, leftover_text):
    return leftover_text - edge_size >= 0


def main():
    parser = argparse.ArgumentParser(description='Converts the image to an image of text')
    parser.add_argument('-i', '--image', help='The image file to be used', required=True)
    parser.add_argument('-t', '--text', help='The text file to be used', required=True)
    parser.add_argument('-o', '--output_location', help='Name of the directory to be used for output', required=True)
    parser.add_argument('-n', '--output_name', help='Name of the file to be used for the text and image file.  Do not '
                                                    'include the extension', required=True)
    parser.add_argument('-m', '--margin', type=int, default=0, help='The number of pixels to add as a margin around the'
                                                                    ' final image (default: 0)')
    parser.add_argument('-p', '--preview', action='store_true', help='Preview the image after applying the color '
                                                                     'transformation (default: false)')
    parser.add_argument('--threshold', type=float, help='The brightness value (float) to which each pixel must be'
                                                        ' above to have a character drawn to represent it')
    parser.add_argument('--above', action='store_false', help='When true will paint the pixel if it is above the'
                                                              ' average brightness or threshold (default: true)')
    parser.add_argument('-l', '--logging', help='Logging level possible values: [DEBUG, INFO, WARNING, ERROR, '
                                                'CRITICAL] (default: INFO)')
    args = parser.parse_args()

    massage_args(args)

    process(args.image, args.text, args.output_location, args.output_name, args.margin, args.preview, args.threshold,
            args.above)


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


def process(image_location, text_location, output, name, margin, preview, threshold, is_above):
    logging.info("getting image from [%s]", image_location)
    image = Image.open(image_location).convert("RGBA")
    average_color = get_average_color(image)
    logging.debug("pictures average color: %s", average_color)
    logging.debug("pictures average brightness: %s", get_pixel_brightness(average_color))

    if preview:
        generate_preview(image, average_color, output, name, threshold, is_above)
        sys.exit()

    text = get_text(text_location)
    image = scale_img_to_text(image, text, average_color, threshold, is_above)
    text_image = get_text_image(text, image, average_color, threshold, is_above)
    if not os.path.exists(output):
        os.makedirs(output)
    write_to_file(text_image, output + '\\' + name + '.txt')
    image = get_image_of_text(text_image, image, margin)
    logging.info("saving image to [%s]", output + '\\' + name + '.png')
    image.save(output + '\\' + name + '.png')
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


def get_average_color(image):
    temp_image = image.resize((1, 1), Image.ANTIALIAS)
    return temp_image.getpixel((0, 0))


def generate_preview(image, average_color, output, name, threshold, is_above):
    logging.info('generating preview')
    pixels = get_pixels(image)
    new_pixels = []
    for pixel in pixels:
        if should_paint_pixel(pixel, average_color, threshold, is_above):
            new_pixels.append((255, 255, 255))
        else:
            new_pixels.append((0, 0, 0))
    preview = Image.new(image.mode, image.size)
    preview.putdata(new_pixels)
    output_file = output + '\\' + name + '_preview.png'
    preview.save(output_file)
    logging.info('saved preview to [%s]', output_file)


def scale_img_to_text(image, text, average_color, threshold, is_above):
    logging.info("scaling image to match text length")
    logging.debug("original - width: [%s] and height: [%s]", image.size[0], image.size[1])
    image = account_for_font_ratio(image)
    logging.debug("scaled for font ratio - width: [%s] height: [%s]", image.size[0], image.size[1])
    image = account_for_empty_space(image, text, average_color, threshold, is_above)
    logging.debug("account for empty space - width: [%s] height: [%s]", image.size[0], image.size[1])
    return image


def account_for_font_ratio(image):
    """Resize image so that when all 'square' pixels are converted to rectangular characters the size of the image
    will stay the same
    """
    font_pixel_ratio = 19 / 9
    return image.resize((math.ceil(image.size[0] * font_pixel_ratio), image.size[1]))


def account_for_empty_space(image, text, average_color, threshold, is_above):
    pixels = get_pixels(image)
    empty_pixels_count = get_empty_pixel_area(pixels, average_color, threshold, is_above)
    empty_pixel_ratio = empty_pixels_count / len(pixels)
    text_length = len(text)
    width, height = image.size
    logging.debug('text length: [%s] original width: [%s] height: [%s] empty pixel ratio: [%s]', text_length, width,
                  height, empty_pixel_ratio)

    while True:
        scalar = math.sqrt((width * height) / (text_length + (width * height * empty_pixel_ratio)))
        logging.debug("scaling by [%s]", scalar)
        width = math.ceil(width / scalar)
        height = math.ceil(height / scalar)
        logging.debug('new width: [%s] height: [%s]', width, height)

        new_area = width * height
        colored_pixels = new_area - (new_area * empty_pixel_ratio)
        text_difference = text_length - colored_pixels
        logging.debug('text difference: [%s]', text_difference)
        if math.fabs(text_difference) < width:
            break

    if text_difference > 0:
        if width > height:
            logging.debug('adding 1 pixel to the height to account for missing text')
            height += 1
        else:
            logging.debug('adding 1 pixel to the width to account for missing text')
            width += 1

    return image.resize((width, height))


def get_pixels(image):
    return list(image.getdata())


def get_empty_pixel_area(pixels, average_color, threshold, is_above):
    empty_pixel_counter = 0
    for pixel in pixels:
        if should_paint_pixel(pixel, average_color, threshold, is_above):
            empty_pixel_counter += 1
    return empty_pixel_counter


def should_paint_pixel(pixel, average_color, threshold, is_above):
    color_brightness = threshold if threshold is not None else get_pixel_brightness(average_color)
    pixel_brightness = get_pixel_brightness(pixel)
    return pixel_brightness > color_brightness if is_above else pixel_brightness < color_brightness


def get_pixel_brightness(pixel):
    r, g, b, x = pixel
    return math.sqrt(.241 * math.pow(r, 2) + .691 * math.pow(g, 2) + .068 * math.pow(b, 2))


def get_text_image(text, image, average_color, threshold, is_above):
    logging.info("converting image to text")
    text_image = ""
    width, height = image.size
    pixels = get_pixels(image)
    line_counter = 0
    text_counter = 0
    for pixel in pixels:
        line_counter += 1
        if should_paint_pixel(pixel, average_color, threshold, is_above):
            text_image += ' '
        else:
            if text_counter < len(text):
                text_image += text[text_counter]
                text_counter += 1
            else:
                logging.warning("more pixels [%s] than text [%s]", len(pixels), len(text))
                break

        if line_counter == width:
            text_image += '\n'
            line_counter = 0
    return text_image


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


def get_image_of_text(text_image, image, margin):
    logging.info('converting text to image')
    width, height = image.size
    logging.debug('original width: [%s] height: [%s]', width, height)
    txt_img = Image.new('RGBA', (width * 9 + margin * 2, math.ceil(height * 19) + margin * 2), (255, 255, 255, 255))
    logging.debug('scaled for character width: [%s] height: [%s]', txt_img.size[0], txt_img.size[1])
    fnt = ImageFont.truetype('c:/Windows/Fonts/Arial/LTYPE.TTF', 15)
    d = ImageDraw.Draw(txt_img)
    logging.info('painting text to canvas (this could take a while)')
    d.text((margin, margin), str(text_image), font=fnt, fill=(0, 0, 0, 255))
    logging.info('painting finished')
    return txt_img


if __name__ == '__main__':
    main()

import logging

from PIL import ImageFilter # type: ignore

from image_processor.Processor import Processor


class SmoothingProcessor(Processor):
    """
        Processes an image by smoothing it.
    """

    def process(self, image, arguments):
        """
        Processes an image using Pillows built in smooth-filter
        https://pythontic.com/image-processing/pillow/smooth-filter

        Args:
            image: The image to process
            arguments: A list of arguments [more_smooth].  Omitting a value or passing None will use the default value
                smooth_level: Whether to use more smoothing.  default: False

        Returns:
            A smoothed image
        """
        default_args = [False]
        more_smoothing = Processor.get_arguments(self, arguments, default_args)
        logging.info('processing image using [%s] with arguments - more_smoothing: [%s] ', __name__, more_smoothing)

        return image.filter(ImageFilter.SMOOTH_MORE) if more_smoothing else image.filter(ImageFilter.SMOOTH)

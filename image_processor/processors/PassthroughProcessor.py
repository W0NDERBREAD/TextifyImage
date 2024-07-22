import logging
import math

from PIL import Image

from image_processor.Processor import Processor


class PassthroughProcessor(Processor):
    """
        Just returns the image.
    """

    def process(self, image, arguments):
        """
        Returns the image.

        Args:
            image: The image to process.
            arguments: None

        Returns:
            The original Image
        """

        logging.info(
            'processing image using [%s] with arguments - None', __name__)

        return image

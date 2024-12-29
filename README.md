# TextifyImage

A Python project to convert images to be made up of characters from a given text file.

![Alice's Adventures in Wonderland](/examples/outputs/AAiW-basic.png)

## Flags

Name                | Flag                    | Short Flag | Required | Default                        | Details
--------------------|-------------------------|------------|----------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------
Image               | `--image`               | `-i`       | True     | None                           | A path to the image to convert
Text                | `--text`                | `-t`       | True     | None                           | A path to the text to convert.  Should be a plain .txt file
Output              | `--output`              | `-o`       | True     | None                           | A path to the file to save the converted image to
Font                | `--font`                | `-f`       | False    | JetBrainsMono-Regular.ttf 9 15 | 3 fields to use a custom font - A path to the font (must be TrueType .ttf font), width in pixels of the font, height in pixels of the font
Margin              | `--margin`              | `-m`       | False    | 0 0                            | 2 fields to define margins for the converted image - The number of pixels for the left and right margin, the number of pixels for the top and bottom margin
Character Threshold | `--char_threshold`      | `-c`       | False    | 250                            | A brightness threshold between 0 (black) and 255 (white). Pixels below this threshold won't be replaced by a character and will be left blank.
Background Color    | `--background_color`    | `-b`       | False    | 255 255 255 (white)            | The RGB values of the color to use for the background of the image
Processor           | `--processor`           | `-p`       | False    | `DuotoneProcessor`             | The name of a Processor used to pre-process the image before converting it to characters.  Processors must be stored in `/image_processor/processors` and must extend image_processor.Processor.py
Processor Arguments | `--processor_arguments` | `-a`       | False    | None                           | Arguments to be passed to the given Processor. All processor fields have default values and can be safely omitted. Use `None` to omit an argument that is not the last argument.
Processor Only      | `--processor_only`      |            | False    | False                          | Only runs the processor and does not convert the final image to text.  Useful for quickly previewing processor flags or debugging processors
Logging              | `--logging`             |            | False    | INFO                           | Set the logging level.  Possible values are DEBUG, INFO, WARNING, ERROR, CRITICAL

## Examples

Below are a few examples of different TextProcessor commands to give you and idea of how it can be used.  All inputs and outputs can be found in the `/examples` directory.

### Basic Usage

Out of the box by only supplying the required fields, `TextProcessor` will produce a black and white duotone image.  This should produce a pretty good result for simple images.  For busier images with lots of different colors or details you can then start tweaking the `Character Threshold` field to hone in on bringing out the details you want.

```shell
python .\TextProcessor.py -i .\examples\images\AAiW-white-rabbit.png -t .\examples\text\AAiW.txt -o .\examples\outputs\AAiW-basic.png
```

### Custom Colors

Custom colors can be passed to the `Duotone` processor to use colors other than black and white.

```shell
python .\TextProcessor.py -i .\examples\images\AAiW-white-rabbit.png -t .\examples\text\AAiW.txt -o .\examples\outputs\AAiW-custom-colors.png -p DuotoneProcessor -a 237,185,109 138,229,253
```

### All the Fields

An example using all of the fields

```shell
python .\TextProcessor.py -i .\examples\images\AAiW-white-rabbit.png -t .\examples\text\AAiW.txt -o .\examples\outputs\AAiW-all.png -f .\fonts\JetBrainsMono\2.304\fonts\ttf\JetBrainsMono-Bold.ttf 9 15 -m 50 50 -c 255 -b 24 62 12 -p DuotoneProcessor -a 237,185,109 138,229,253 255
```

### Processor Only

The `--processor_only` flag is a good way to quickly see what the image might look like after being processed but not converted to characters.

```shell
python .\TextProcessor.py -i .\examples\images\AAiW-white-rabbit.png -t .\examples\text\AAiW.txt -o .\examples\outputs\AAiW-processor-only.png -p DuotoneProcessor -a 237,185,109 138,229,253  --processor_only
```

## Processors

A processor is responsible for pre-processing an image before each pixel is converted to a character.  More information about each processor can be found below.  New processors can be added as long as they are put in the `/image_processor/processors/` directory and extend `image_processor.Processor.py`

### Duotone

The Duotone processor Converts a given image to an image made up of only 2 colors. By default it will create a black and white image by converting each pixel to black or white based on the "average" color of the image.

#### Arguments

Name                | `processor_arguments` position                    | Default                        | Details
--------------------|-------------------------|--------------------------------|------------------------------------------------
Primary Color | 0 | 0,0,0 | The RGB value of the color to be used when a pixel is below the `threshold`
Secondary Color | 1 | 255,255,255 | The RGB value of the color to be used when a pixel is above the `threshold`
Threshold | 2 | "average" color of the image | Defines the threshold value in terms of the brightness of a pixel where 0 is black and 255 is white.  Pixels below this threshold will be converted to the Primary Color and pixels above or equal will be converted to the Secondary Color

### Passthrough

The Passthrough processor does nothing to the image.  This can be useful if you want to do all of the processing of an image in your favorite image editor and simply convert the image to characters.

#### Arguments

None
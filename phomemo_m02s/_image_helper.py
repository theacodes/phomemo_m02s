# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

import math

import PIL
import PIL.Image
import PIL.ImageOps

def preprocess_image(src, width=512, save=False):
    src_w, src_h = src.size
    aspect = src_w / src_h
    new_size = (width, math.floor(width / aspect))
    resized = src.resize(new_size)
    converted = PIL.ImageOps.invert(resized.convert("RGB")).convert("1")

    if save:
        converted.save("converted.png")

    return converted

def split_image(image, padding_top):
    chunks = image.height // 255

    # Yield one "empty" chunk as a workaround for the printer not printing
    # the first couple lines
    yield _make_padding(image.width, padding_top)

    for chunk in range(chunks + 1):
        i = image.crop((0, chunk * 255, image.width, chunk * 255 + 255))
        yield i

def image_to_bits(image, threshold=127):
    return [
        bytearray(
            [
                1 if image.getpixel((x, y)) > threshold else 0
                for x in range(image.width)
            ]
        )
        for y in range(image.height)
    ]

def _make_padding(width, height):
    return PIL.Image.new("L", (width, height), color=0)

# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

import argparse
import sys

import PIL.Image
import PIL.ImageDraw

import phomemo_m02s.printer
import phomemo_m02s._image_helper


def _make_test_image(width):
    img = PIL.Image.new("RGB", (width, 30), (255, 255, 255))
    d = PIL.ImageDraw.Draw(img)
    d.rectangle((10, 10, img.width - 10, img.height - 10), fill=(0, 0, 0))
    d.rectangle((0, 0, img.width - 1, img.height - 1), outline=(0, 0, 0))

    img.save("test.png")

    return "test.png"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument(
        "--width", type=int, default=phomemo_m02s.printer.Printer.MAX_WIDTH
    )
    parser.add_argument("--test", action="store_true", default=False)
    parser.add_argument("--convert-only", action="store_true", default=False)
    parser.add_argument("--port", default="/dev/tty.M02S")
    parser.add_argument("--mac", default=None)
    parser.add_argument("--channel", default=6)

    args = parser.parse_args()

    if args.test:
        args.image = _make_test_image(args.width)

    if args.convert_only:
        phomemo_m02s._image_helper.preprocess_image(
            args.image, width=args.width, save=True
        )
        sys.exit(0)

    printer = phomemo_m02s.printer.Printer(args.port, args.mac, args.channel)
    printer.initialize()
    printer.reset()
    print("Serial number:", printer.get_serial_number())
    print("Firmware:", printer.get_firmware_version())
    print("Paper state:", printer.get_paper_state())
    print("Energy:", printer.get_energy())

    printer.initialize()
    printer.align_center()

    printer.print_image(args.image, width=args.width)

    printer.reset()

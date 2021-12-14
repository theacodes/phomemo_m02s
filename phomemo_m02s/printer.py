# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

import PIL
import serial
import socket

from phomemo_m02s import _image_helper

FF = 0x0C
NAK = 0x15
CAN = 0x18
ESC = 0x1B
GS = 0x1D
US = 0x1F


class BluSerial:
    def __init__(self, mac, port):
        self.sock = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        self.sock.connect((mac, port))

    def write(self, b):
        if type(b) is list:
            b = bytes(b)
        self.sock.send(b)

    def read(self, size):
        return self.sock.recv(size)

    def flush(self):
        pass


class Printer:
    # Figured out empirically
    MAX_WIDTH = 576

    def __init__(self, port_name="/dev/tty.M02S", mac=None):
        if mac is not None:
            # the channel can be found by running `sdptool browse` but should be the same
            self.port = BluSerial(mac, 6)

        else:
            self.port = serial.Serial(port_name, timeout=10)

    def write(self, bytes):
        self.port.write(bytes)
        self.port.flush()

    def read(self, count):
        return self.port.read(size=count)

    # These commands are in the same order as in PrinterUtils.java
    # from the Android app.

    def set_concentration(self, val=2):
        self.write(bytes([ESC, 0x4E, 0x04, val]))

    def set_device_timer(self, val):
        self.write(bytes([ESC, 0x4E, 0x07, val]))

    def get_serial_number(self):
        # PrinterUtils uses NAK, but it doesn't seem to work for some reason.
        # However, apparently US works.
        self.write(bytes([US, 0x11, 0x13]))
        return int.from_bytes(
            self.read(3)[2:],
            byteorder="little",
        )

    def get_firmware_version(self):
        self.write([US, 0x11, 0x07])
        response = self.read(5)
        return f"{response[4]}.{response[3]}.{response[2]}"

    def get_energy(self):
        self.write(bytes([US, 0x11, 0x08]))
        return int.from_bytes(self.read(3)[2:], byteorder="little")

    def get_device_timer(self):
        self.write(bytes([US, 0x11, 0x0E]))
        return int.from_bytes(self.read(3)[2:], byteorder="little")

    def get_paper_state(self):
        self.write(bytes([US, 0x11, 0x11]))
        return int.from_bytes(
            self.read(3)[2:],
            byteorder="little",
        )

    def initialize(self):
        self.write(bytes([ESC, 0x40]))

    def print_line_feed(self):
        self.write(bytes([0x0A]))

    def emphasized_on(self):
        self.write(bytes([ESC, 0x45, 1]))

    def emphasized_off(self):
        self.write(bytes([ESC, 0x45, 0]))

    def align_left(self):
        self.write(bytes([ESC, 0x61, 0]))

    def align_center(self):
        self.write(bytes([ESC, 0x61, 1]))

    def align_right(self):
        self.write(bytes([ESC, 0x61, 2]))

    def feed_paper_cut(self):
        self.write(bytes([GS, 0x56, 1]))

    def feed_paper_cut_partial(self):
        self.write(bytes([GS, 0x56, 0x42, 0]))

    # Note: not sure what the difference is between
    # set_concentration and print_concentration, although
    # this one seems to use non-standard commands.
    def print_concentration(self, val):
        self.write(bytes([NAK, 0x11, 0x02, val]))

    # These commands are in the same order as PrintCommands.java,
    # except for the ones already above.

    def print_feed_lines(self, num):
        self.write(bytes([ESC, 0x64, num]))

    def print_feed_paper(self, num):
        self.write(bytes([ESC, 0x4A, num]))

    def reset(self):
        self.write(bytes([ESC, 0x40, 0x02]))

    def print_raster_bit_image(self, lines: list[bytearray]):
        """The lowest level print image command.

        lines must be a list of bytearrays representing the lines to
        print. The line length must be a multiple of 8 and the number of lines
        must be less than 256. The "pixels" should be either a 0 or 1.

        For the M02S, a fullwidth image is 512 pixels width.
        """
        mode = 0
        # CS v 0
        output = bytearray([GS, 0x76, 0x30, mode])

        width = len(lines[0])
        height = len(lines)

        if width % 8 != 0:
            raise ValueError("Width isn't a multiple of 8")

        byte_width = width // 8

        output.extend(byte_width.to_bytes(2, byteorder="little"))

        if height > 255:
            raise ValueError("Height must be less than 256")

        output.extend(height.to_bytes(2, byteorder="little"))

        for line in range(height):
            for byte_num in range(byte_width):
                byte = 0
                for bit in range(8):
                    pixel = lines[line][byte_num * 8 + bit]
                    byte |= (pixel & 0x01) << (7 - bit)

                output.append(byte)

        self.write(output)

    # These are custom. :3
    def print_image(printer, filename_or_image, width=512, padding_top=5):
        with PIL.Image.open(filename_or_image) as src:
            image = _image_helper.preprocess_image(src, width)

        for chunk in _image_helper.split_image(image, padding_top=padding_top):
            printer.print_raster_bit_image(_image_helper.image_to_bits(chunk))

        printer.feed_paper_cut()

# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

"""This is a basic Python library for controlling the Phomemo M02S bluetooth thermal printer."""

__version__ = "0.0.0a0"

from phomemo_m02s.printer import Printer

__all__ = [
    "Printer",
]

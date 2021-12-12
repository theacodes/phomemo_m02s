# Phomemo M02S Python library

This is a basic Python library for controlling the [Phomemo M02S](https://phomemo.com/collections/phomemo-m02s) bluetooth thermal printer.

It probably only works on Mac & Linux, and it was really only made for me, but if you find it useful that's great!

This isn't published to PyPI, so if you want to install it you can use:

```
pip install git+https://github.com/theacodes/phomemo_m02s.git
```

## Usage

You'll need to connect your computer to the printer via Bluetooth, this library just uses the Bluetooth serial port to communicate with the printer and therefore avoids any complicated Bluetooth stuff.

The whole library is designed around just printing images through the printer. Although it's totally possible to use the text features, it's just not important to me so I haven't really bothered. To print an image use:

```python
python3 -m phomemo_m02s /path/to/image.png
```

You can use any format supported by `Pillow`. There are a few other options available, run `python3 -m phomemo_m02s --help` to see the full list.


## Contributing

While I don't really expect anyone else to try to use this, by all means, contributions are welcome. File an issue or reach out to us before you write code, so we can make sure it's something that'll be beneficial for all of us. :)

## License

Wintertools is published under the [MIT License](LICENSE)

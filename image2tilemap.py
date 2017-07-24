#!/usr/bin/env python3

import itertools as it
from PIL import Image

def rgba_iaverage(iterable):
    """Takes an iterable, which will be consumed in groups of 3 (so the iterable
    should have a length divisible by 3). This function is a generator of the
    average of these RGB values.
    """
    try:
        iterable = iter(iterable)
        while True:
            r = next(iterable)
            g = next(iterable)
            b = next(iterable)
            a = next(iterable)
            yield (r + g + b) // 3
    except StopIteration:
        raise StopIteration

def rgb_i2bit(iterable):
    """Consumes an iterable of byte values and generates pairs of bytes
    representing 8 pixels.
    """
    try:
        iterable = iter(iterable)
        while True:
            hi = 0
            lo = 0
            for i in range(8):
                c = next(iterable) // 64
                hi |= (c >> 1) << (7 - i)
                lo |= (c & 1) << (7 - i)
            yield hi
            yield lo
    except StopIteration:
        raise StopIteration

def imageto2bit(filename):
    img = Image.open(filename)
    width = img.width
    height = img.height
    print(width, height)
    width_tiles = width // 8
    height_tiles = height // 8
    img_bytes = img.tobytes()
    if img.mode == 'RGBA':
        img_bytes = bytes(rgba_iaverage(img_rgba_bytes))
    assert len(img_bytes) == width_tiles*height_tiles*8*8
    tiles = []
    for i in range(width_tiles*height_tiles):
        tile = []
        tx = (i % width_tiles) * 8
        ty = (i // width_tiles) * 8
        for j in range(8):
            y = ty + j
            print(y*width+tx, y*width+tx+8)
            row = img_bytes[y*width+tx:y*width+tx+8]
            print(len(row))
            tile.extend(row)
        tiles.append(tile)

    encoded = []
    for tile in tiles:
        assert len(tile) == 8*8
        encoded.extend(rgb_i2bit(tile))

    return encoded

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=(
        'Convert an image to a GameBoy tilemap (2-bit color).'
        ))
    parser.add_argument('in_file', type=str,
            help='An image (any format supported by Pillow) to be converted')
    parser.add_argument('out_file', type=str,
            help='A writable output file.')
    parser.add_argument('--asm', action='store_true',
            help='Output in Z80 assembly instead of binary data.')

    args = parser.parse_args()
    try:
        rgb2_bytes = bytes(imageto2bit(args.in_file))
    except IOError:
        parser.print_help()
        sys.exit()

    if args.asm:
        with open(args.out_file, 'w') as f:
            for i, b in enumerate(rgb2_bytes):
                f.write('db %{:08b}\n'.format(b))
                if i & 0x7 == 0x7:
                    f.write('\n')
    else:
        with open(args.out_file, 'wb') as f:
            f.write(rgb2_bytes)
    print('Wrote output to {}'.format(args.out_file))

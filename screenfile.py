"""screenfile.py

One-off script for building an input file to displayscreen.py."""

import argparse
from PIL import Image
#from image2tilemap import imageto2bit
from gfx import RGBTileset
import json
import sys

parser = argparse.ArgumentParser(description='One-off script for building an input file to displayscreen.py')
parser.add_argument('tile_image', type=str,
        help='256x256 image containing 8x8 tiles')
parser.add_argument('tilemap', type=argparse.FileType('r'),
        help='Tiled JSON containing the BG and FG maps (layers 0 and 1)')
parser.add_argument('outfile', type=argparse.FileType('wb'),
        help='Output is written to this file')
args = parser.parse_args()

"""The following sprite flags are described in the pandocs. At the time of this
writing, they have no effect and default to 0.
"""
SPRITE_PRIO = (1 << 0)
SPRITE_YFLIP = (1 << 1)
SPRITE_XFLIP = (1 << 2)
SPRITE_PALLETTE1 = (1 << 3)
# y-16, x-8, tileid, flags
SPRITE_TABLE = [
        32, 32, 9, 0, # y=48,x=40,tileid=9,flags=0
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        ]
img = Image.open(args.tile_image).convert(mode='L')
tileset = RGBTileset(img.tobytes(), img.size, (8, 8))
#tiles = imageto2bit(img, (8, 8))
palette = [0xff, 0xc0, 0x40, 0x00]
tiles = tileset.to_gb(palette).data
tiled_json = json.loads(args.tilemap.read())
sub1 = lambda x: x - 1 if x > 0 else 0
bgmap = bytes(map(sub1, tiled_json['layers'][0]['data']))
fgmap = bytes(map(sub1, tiled_json['layers'][1]['data']))
sprite_table = bytes(SPRITE_TABLE)

assert len(tiles) == (256 // 8) * (256 * 2)
assert len(bgmap) == 1024
assert len(fgmap) == 1024
assert len(SPRITE_TABLE) == 40*4

args.outfile.write(tiles)
args.outfile.write(bgmap)
args.outfile.write(fgmap)
args.outfile.write(sprite_table)

args.outfile.close()
print('wrote output to {}'.format(args.outfile.name))

"""displayscreen.py

Takes a tileset image and a tilemap from Tiled and draws it like a GameBoy
screen—160x144.
"""


import argparse
from collections import defaultdict
import functools as ft
import itertools as it
from math import sqrt
from PIL import Image
import sdl2.ext
from sdl2.ext import Color
import sdl2.events

from gfx import GBTileset, RGBTileset
from display2bit import i2bitdecode, split_tiles


SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
BACKGROUND_WIDTH = 256
BACKGROUND_HEIGHT = 256
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 144
SPRITE_WIDTH = 8
SPRITE_HEIGHT = 8
#SPRITE_HEIGHT = 16


bgpalette = [
    Color(0xff, 0xff, 0xff, 0xff),
    Color(0x55, 0x55, 0x55, 0xff),
    Color(0xaa, 0xaa, 0xaa, 0xff),
    Color(0x00, 0x00, 0x00, 0xff),
]

fgpalette = [
    Color(0xff, 0xff, 0xff, 0x00),
    Color(0x55, 0x55, 0x55, 0xff),
    Color(0xaa, 0xaa, 0xaa, 0xff),
    Color(0x00, 0x00, 0x00, 0xff),
]


parser = argparse.ArgumentParser(description='Display a static GB screen')
parser.add_argument('tileset', type=str,
                    help='Tileset image (expecting 256x256).')
parser.add_argument('tilemap', type=argparse.FileType('r'),
                    help='Tiled JSON with the BG and FG maps (layers 0, 1).')
parser.add_argument('--scx', type=int,
                    help='Background scroll x.')
parser.add_argument('--scy', type=int,
                    help='Background scroll y.')
parser.add_argument('--wcx', type=int,
                    help='Window x position')
parser.add_argument('--wcy', type=int,
                    help='Window y position')
args = parser.parse_args()

tileset = Image.open(args.tileset).convert('L')
rgbtileset = RGBTileset(tileset.tobytes(), tileset.size, (8, 8))
encode_palette = [0xff, 0x55, 0xaa, 0x00]
gbtileset = GBTileset.from_rgb(rgbtileset, encode_palette)

tile_data = gbtileset.data
tiled_json = json.loads(args.tilemap.read())
sub1 = lambda x: x - 1 if x > 0 else 0
bgmap = bytes(map(sub1, tiled_json['layers'][0]['data']))
fgmap = bytes(map(sub1, tiled_json['layers'][1]['data']))
sprite_table = [
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

assert len(tile_data) == 32*32*16
assert len(bgmap) == 32*32
assert len(fg_tmap) == 32*32
assert len(sprite_table) == 40*4

window = sdl2.ext.Window('GB screen', (BACKGROUND_WIDTH, BACKGROUND_HEIGHT))
window.show()
renderer = sdl2.ext.Renderer(window)
width = SCREEN_WIDTH
height = SCREEN_HEIGHT
tile_width = 8
tile_height = 8
tile_size = tile_width, tile_height
width_tiles = width // tile_width
height_tiles = height // tile_height
bgwidth_tiles = BACKGROUND_WIDTH // tile_width
bgheight_tiles = BACKGROUND_HEIGHT // tile_height


bgtiles = split_tiles(tile_data, (256, 256), (tile_size))


def bg_tile_visible(tileid: int, sc: Tuple[int, int]) -> bool:
    tx = (tileid % width_tiles) * tile_width
    ty = (tileid // width_tiles) * tile_height
    scx, scy = sc
    if tx + tile_width < scx:
        return False
    elif tx > SCREEN_WIDTH + scx:
        return False
    elif ty + tile_height < scy:
        return False
    elif ty > SCREEN_HEIGHT + scy:
        return False
    else:
        return True


def draw_tile(renderer, tile, point):
    x, y = point
    for i, c in enumerate(tile):
        xoff = i % tile_width
        yoff = i // tile_width
        point = (x+xoff, y+yoff)
        renderer.draw_point(point, c)

def draw_screen(renderer, sc: Tuple[int, int]):
    # draw background
    bgwidth_tiles = BACKGROUND_WIDTH // tile_width
    bgheight_tiles = BACKGROUND_HEIGHT // tile_height
    for i, tid in enumerate(bgmap):
        x = (i % bgwidth_tiles) * tile_width
        y = (i // bgwidth_tiles) * tile_height
        draw_tile(renderer, bgtiles[tid], (x, y))

    # foreground
    fgwidth_tiles = WINDOW_WIDTH // tile_width
    fgheight_tiles = WINDOW_HEIGHT // tile_height
    for i, tid in enumerate(fg_tmap):
        x = (i*8) % width
        y = (i*8) // width
        draw_tile(renderer, fgtiles[tid], (x, y))

    # sprites
    for i in range(40):
        sy = sprite_table[i*4] - 16
        sx = sprite_table[i*4+1] - 8
        tileid = sprite_table[i*4+2]
        flags = sprite_table[i*4+3]
        draw_tile(renderer, bgtiles[tileid], (sx, sy))

renderer.present()

running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.events.SDL_QUIT:
            running = False
            break
    sdl2.SDL_Delay(100)


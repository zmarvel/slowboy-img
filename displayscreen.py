"""displayscreen.py

This script takes a file with a special binary format.

0x0000-0x0fff: 8x8x2 tile data (256 tiles at 16 B/tile)
0x1000-0x13ff: 32x32 byte background tile map (1 B/tile)
0x1400-0x17ff: 32x32 byte window tile map
0x1800-0x189f: 40 sprite table entries (4 B each)
"""


import argparse
from collections import defaultdict
import functools as ft
import itertools as it
from math import sqrt
import sdl2.ext
from sdl2.ext import Color
import sdl2.events

bgpalette = [
        Color(0, 0, 0, 255),
        Color(64, 64, 64, 255),
        Color(192, 192, 192, 255),
        Color(255, 255, 255, 255),
        ]
fgpalette = [
        Color(0, 0, 0, 0),
        Color(64, 64, 64, 255),
        Color(192, 192, 192, 255),
        Color(255, 255, 255, 255),
        ]
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
BACKGROUND_WIDTH = 256
BACKGROUND_HEIGHT = 256
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 144
SPRITE_WIDTH = 8
SPRITE_HEIGHT = 8
#SPRITE_HEIGHT = 16

def i2bitdecode(iterator, palette):
    iterator = iter(iterator)
    try:
        while True:
            hi = next(iterator)
            lo = next(iterator)
            for i in range(8):
                c = (lo >> (7-i)) & 1
                c |= ((hi >> (7-i)) & 1) << 1
                color = palette[c]
                yield color
    except StopIteration:
        raise StopIteration()

def test_i2bitdecode():
    encoded = [
            0b00110011,
            0b01010101,
            0b11001100,
            0b10101010,
            0b00110011,
            0b01010101,
            0b11001100,
            0b10101010,
            ]
    decoded = list(i2bitdecode(encoded, bgpalette))
    decoded_expected = [
            bgpalette[0], bgpalette[1], bgpalette[2], bgpalette[3], bgpalette[0], bgpalette[1], bgpalette[2], bgpalette[3],
            bgpalette[3], bgpalette[2], bgpalette[1], bgpalette[0], bgpalette[3], bgpalette[2], bgpalette[1], bgpalette[0],
            bgpalette[0], bgpalette[1], bgpalette[2], bgpalette[3], bgpalette[0], bgpalette[1], bgpalette[2], bgpalette[3],
            bgpalette[3], bgpalette[2], bgpalette[1], bgpalette[0], bgpalette[3], bgpalette[2], bgpalette[1], bgpalette[0],
            ]
    assert decoded == decoded_expected

parser = argparse.ArgumentParser(description='Display a static GB screen')
parser.add_argument('screenfile', type=argparse.FileType('rb'),
        help='Binary file format described at the top of the script.')
parser.add_argument('--scx', type=int,
        help='Background scroll x.')
parser.add_argument('--scy', type=int,
        help='Background scroll y.')
parser.add_argument('--wcx', type=int,
        help='Window x position')
parser.add_argument('--wcy', type=int,
        help='Window y position')

args = parser.parse_args()

test_i2bitdecode()

tile_data = args.screenfile.read(0x1000)
bg_tmap = args.screenfile.read(0x400)
fg_tmap = args.screenfile.read(0x400)
sprite_table = args.screenfile.read(0xa0)

assert len(tile_data) == 128*8*8*2 // 4
assert len(bg_tmap) == 32*32
assert len(fg_tmap) == 32*32
assert len(sprite_table) == 40*4

bgtiles = []
fgtiles = []
for i in range(0, 256):
    off = 16*i
    encoded = tile_data[off:off+16]
    bgtile = list(i2bitdecode(encoded, bgpalette))
    fgtile = list(i2bitdecode(encoded, fgpalette))
    assert len(bgtile) == 8*8
    assert len(fgtile) == 8*8
    bgtiles.append(bgtile)
    fgtiles.append(fgtile)

window = sdl2.ext.Window('GB screen', (SCREEN_WIDTH, SCREEN_HEIGHT))
window.show()
renderer = sdl2.ext.Renderer(window)
width = SCREEN_WIDTH
height = SCREEN_HEIGHT

twidth, theight = 8, 8
def draw_tile(renderer, tile, point):
    x, y = point
    for i, c in enumerate(tile):
        xoff = i % twidth
        yoff = i // twidth
        renderer.draw_point((x+xoff, y+yoff), c)

for i, tid in enumerate(it.islice(bg_tmap, 0, 32)):
    x = (i*8) % width
    y = (i // width) * 8
    draw_tile(renderer, bgtiles[tid], (x, y))

# draw background
#for i, tid in enumerate(bg_tmap):
#    x = (i*8) % width
#    y = (i*8) // width
#    draw_tile(renderer, bgtiles[tid], (x, y))

# foreground
#for i, tid in enumerate(fg_tmap):
#    x = (i*8) % width
#    y = (i*8) // width
#    draw_tile(renderer, fgtiles[tid], (x, y))

# sprites
#for i in range(40):
#    sy = sprite_table[i*4] - 16
#    sx = sprite_table[i*4+1] - 8
#    tileid = sprite_table[i*4+2]
#    flags = sprite_table[i*4+3]
#    draw_tile(renderer, bgtiles[tileid], (sx, sy))


renderer.present()

running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.events.SDL_QUIT:
            running = False
            break
    sdl2.SDL_Delay(100)


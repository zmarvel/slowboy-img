"""displayscreen.py

Takes a tileset image and a tilemap from Tiled and draws it like a GameBoy
screen—160x144.
"""


import argparse
from collections import defaultdict
from typing import Tuple
import functools as ft
import itertools as it
from math import sqrt
from PIL import Image
import sdl2.ext
from sdl2.ext import Color
import sdl2.events
from sdl2 import (SDL_CreateRGBSurfaceWithFormatFrom,
                  SDL_CreateTextureFromSurface,
                  SDL_FreeSurface,
                  SDL_Texture,
                  SDL_CreateRGBSurfaceWithFormat,
                  SDL_BlitSurface,
                  SDL_ConvertSurfaceFormat,
                 )
import sdl2
import json

from gfx import GBTileset, RGBTileset

bgpalette = [
    0x00,
    0x40,
    0xc0,
    0xff,
]
#bgpalette = [
#    Color(0, 0, 0, 255),
#    Color(64, 64, 64, 255),
#    Color(192, 192, 192, 255),
#    Color(255, 255, 255, 255),
#]
#bgpalette = [
#    0x000000ff,
#    0x404040ff,
#    0xc0c0c0ff,
#    0xffffffff,
#]

fgpalette = [
    0x00,
    0x40,
    0xc0,
    0xff,
]
#fgpalette = [
#    Color(0, 0, 0, 0),
#    Color(64, 64, 64, 255),
#    Color(192, 192, 192, 255),
#    Color(255, 255, 255, 255),
#]



SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
#SCREEN_WIDTH = 256
#SCREEN_HEIGHT = 256
BACKGROUND_WIDTH = 256
BACKGROUND_HEIGHT = 256
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 144
SPRITE_WIDTH = 8
SPRITE_HEIGHT = 8
#SPRITE_HEIGHT = 16


#bgpalette = [
#    Color(0xff, 0xff, 0xff, 0xff),
#    Color(0x55, 0x55, 0x55, 0xff),
#    Color(0xaa, 0xaa, 0xaa, 0xff),
#    Color(0x00, 0x00, 0x00, 0xff),
#]
#
#fgpalette = [
#    Color(0xff, 0xff, 0xff, 0x00),
#    Color(0x55, 0x55, 0x55, 0xff),
#    Color(0xaa, 0xaa, 0xaa, 0xff),
#    Color(0x00, 0x00, 0x00, 0xff),
#]

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


#test_i2bitdecode()

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
#encode_palette = [0xff, 0x55, 0xaa, 0x00]
gbtileset = GBTileset.from_rgb(rgbtileset, bgpalette)

tile_data = gbtileset.data
tiled_json = json.loads(args.tilemap.read())
sub1 = lambda x: x - 1 if x > 0 else 0
bgmap = bytes(map(sub1, tiled_json['layers'][0]['data']))
fgmap = bytes(tiled_json['layers'][1]['data'])
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
#assert len(fg_tmap) == 32*32
assert len(sprite_table) == 40*4

width = BACKGROUND_WIDTH
height = BACKGROUND_HEIGHT
tile_width = 8
tile_height = 8
tile_size = tile_width, tile_height
width_tiles = width // tile_width
height_tiles = height // tile_height

tileset = GBTileset(tile_data, (256, 256), tile_size)
bgtiles = list(tileset.to_rgb(bgpalette).split_tiles())
fgtiles = list(tileset.to_rgb(fgpalette).split_tiles())

class RenderError(Exception):
    def __init__(self, message):
        self.message = message

def get_tile_surfaces(tiles):
    rgb_tile = bytearray(tile_width*tile_height*3)
    for tile in tiles:
        for i in range(len(tile)):
            rgb_tile[3*i] = tile[i]
            rgb_tile[3*i+1] = tile[i]
            rgb_tile[3*i+2] = tile[i]

        surf = SDL_CreateRGBSurfaceWithFormatFrom(bytes(rgb_tile), tile_width,
                                                  tile_height, 24, 3*tile_width,
                                                  sdl2.SDL_PIXELFORMAT_RGB24)
        if not surf:
            raise RenderError('SDL_CreateRGBSurfaceWithFormatFrom returned null')
        else:
            yield SDL_ConvertSurfaceFormat(surf, sdl2.SDL_PIXELFORMAT_RGBA32, 0)
            SDL_FreeSurface(surf)

def get_tile_textures(renderer, tiles):
    for surf in get_tile_surfaces(tiles):
        text = SDL_CreateTextureFromSurface(renderer, surf)
        SDL_FreeSurface(surf)
        if not text:
            raise RenderError('SDL_CreateTextureFromSurface returned null')
        else:
            yield text.contents

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


def draw_tile(renderer, texture: SDL_Texture, pos: Tuple[int, int]) -> None:
    x, y = pos
    src = (0, 0, tile_width, tile_height)
    dest = (x, y, tile_width, tile_height)
    renderer.copy(texture, src, dest)

from ctypes import byref

bgsurfaces = list(get_tile_surfaces(bgtiles))
def draw_screen(renderer, sc: Tuple[int, int]):
    # draw background
    bgsurface = SDL_CreateRGBSurfaceWithFormat(0, BACKGROUND_HEIGHT, BACKGROUND_HEIGHT,
                                     32, sdl2.SDL_PIXELFORMAT_RGBA32)
    for i, tid in enumerate(bgmap):
        x = (i % width_tiles) * tile_width
        y = (i // width_tiles) * tile_height
        src = sdl2.SDL_Rect(0, 0, tile_width, tile_height)
        dst = sdl2.SDL_Rect(x, y, tile_width, tile_height)
        if SDL_BlitSurface(bgsurfaces[tid], src, bgsurface, dst) < 0:
            raise sdl2.SDL_Error()
    bgtexture = SDL_CreateTextureFromSurface(renderer.sdlrenderer, bgsurface)
    SDL_FreeSurface(bgsurface)
    if not bgtexture:
        raise sdl2.SDL_Error()
    scx, scy = sc
    src = (scx, scy, SCREEN_WIDTH, SCREEN_HEIGHT)
    dst = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    renderer.copy(bgtexture.contents, src, dst)

    # foreground
    #fgwidth_tiles = WINDOW_WIDTH // tile_width
    #fgheight_tiles = WINDOW_HEIGHT // tile_height
    #fgtextures = list(get_tile_textures(renderer.sdlrenderer, fgtiles))
    #for i, tid in enumerate(fgmap):
    #    if tid > 0:
    #        x = (i % width_tiles) * tile_width
    #        y = (i // width_tiles) * tile_height
    #        draw_tile(renderer, fgtextures[tid-1], (x, y))

    ## sprites
    #for i in range(40):
    #    sy = sprite_table[i*4] - 16
    #    sx = sprite_table[i*4+1] - 8
    #    tileid = sprite_table[i*4+2]
    #    flags = sprite_table[i*4+3]
    #    draw_tile(renderer, bgtiles[tileid], (sx, sy))

    renderer.present()

window = sdl2.ext.Window('GB screen', (SCREEN_WIDTH, SCREEN_HEIGHT))
window.show()
renderer = sdl2.ext.Renderer(window)

running = True
scx = 0
scy = 0
draw_screen(renderer, (scx, scy))
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.events.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == sdl2.SDLK_DOWN:
                scy += 1
                scy = min(BACKGROUND_HEIGHT-SCREEN_HEIGHT, scy)
            elif event.key.keysym.sym == sdl2.SDLK_UP:
                scy -= 1
                scy = max(0, scy)
            elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                scx += 1
                scx = min(BACKGROUND_WIDTH-SCREEN_WIDTH, scx)
            elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                scx -= 1
                scx = max(0, scx)
            draw_screen(renderer, (scx, scy))

    sdl2.SDL_Delay(100)


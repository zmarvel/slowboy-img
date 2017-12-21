
import sys
import sdl2.ext
from sdl2.ext import Color
import sdl2.events
from gfx import RGBTileset, GBTileset


palette = [
        Color(0x00, 0x00, 0x00, 0xff),
        Color(0x55, 0x55, 0x55, 0xff),
        Color(0xaa, 0xaa, 0xaa, 0xff),
        Color(0xff, 0xff, 0xff, 0xff),
        ]

decode_palette = [
    0x00,
    0x55,
    0xaa,
    0xff,
]


if __name__ == '__main__':
    import argparse as ap

    parser = ap.ArgumentParser('Decode and display a 2-bit image with SDL2.')
    parser.add_argument('image', type=ap.FileType('rb'),
                        help='Image to show.')
    parser.add_argument('--width', type=int, default=256,
                        help='Image width (default=256).')
    parser.add_argument('--height', type=int, default=256,
                        help='Image height (default=256).')
    parser.add_argument('--tile-width', type=int, default=8,
                        help='Tile width (default=8).')
    parser.add_argument('--tile-height', type=int, default=8,
                        help='Tile height (default=8).')
    args = parser.parse_args()

    tset = args.image.read()

    size = (args.width, args.height)
    width, height = size
    tsize = (args.tile_width, args.tile_height)
    twidth, theight = tsize
    gbtileset = GBTileset(tset, size, tsize)
    rgbtileset = RGBTileset.from_gb(gbtileset, decode_palette)
    width_tiles = width // twidth
    height_tiles = height // theight

    window = sdl2.ext.Window('display2bit', size)
    window.show()
    renderer = sdl2.ext.Renderer(window)

    for i, b in enumerate(rgbtileset.data):
        x = i % width
        y = i // width
        c = palette[decode_palette.index(b)]
        renderer.draw_point((x, y), color=c)

    renderer.present()

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.events.SDL_QUIT:
                running = False
                break
        sdl2.SDL_Delay(100)



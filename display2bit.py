
import sys
import sdl2.ext
from sdl2.ext import Color
import sdl2.events

palette = [
        Color(255, 255, 255, 255),
        Color(192, 192, 192, 255),
        Color(64, 64, 64, 255),
        Color(0, 0, 0, 255),
        ]


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


def main():
    if len(sys.argv) < 2:
        sys.exit('USAGE: {} <tilemap>')

    with open(sys.argv[1], 'rb') as f:
        tmap = f.read()

    width = 128
    height = 48
    print(width, height)

    tiles = []
    width_tiles = width // 8
    height_tiles = height // 8
    for i in range(width_tiles*height_tiles):
        tile = tmap[i*16:(i+1)*16]
        tiles.append(list(i2bitdecode(tile, palette)))

    window = sdl2.ext.Window('display2bit', (width, height))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    for tid, tile in enumerate(tiles):
        tx = tid % width_tiles
        ty = tid // width_tiles
        for i, c in enumerate(tile):
            x = tx*8 + (i % 8)
            y = ty*8 + (i // 8)
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


if __name__ == '__main__':
    main()

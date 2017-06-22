
import sys
from collections import defaultdict
from math import sqrt
import sdl2.ext
from sdl2.ext import Color
import sdl2.events

palette = [
        Color(0, 0, 0, 255),
        Color(64, 64, 64, 255),
        Color(192, 192, 192, 255),
        Color(255, 255, 255, 255),
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

    tilecolors = list(i2bitdecode(tmap, palette))
    width = int(sqrt(len(tilecolors)))
    height = width
    width = 256
    height = 128
    print(width, height)

    window = sdl2.ext.Window('display2bit', (width, height))
    window.show()
    renderer = sdl2.ext.Renderer(window)
    for i, c in enumerate(tilecolors):
        #x = i % 256
        #x = i & 0xff
        x = i % width
        y = i // width
        renderer.draw_point((x, y), color=c)
        x += 1
        if x >= width:
            x = 0
            y += 1

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


# slowboy-img

Just some scripts for exploring GameBoy graphics.

## image2tilemap

`image2tilemap.py` converts an image file (anything Pillow supports) into a
2-bit grayscale binary file like the GameBoy might use.

## display2bit

`display2bit.py` uses PySDL2 to decode a 2-bit grayscale image and draw it.

## screenfile

`screenfile.py` is a helper script for `displayscreen.py`, which accepts a
special binary format. This script accepts the components of the input to
`displayscreen.py` and prepares the binary file.

## displayscreen

`displayscreen.py`, as mentioned, takes a special binary format. It contains:

- Some tiles in 2-bit grayscale
- A tilemap for the background
- A tilemap for the window
- A sprite attribute table

Its command-line options will eventually specify the background scroll and the
window position.

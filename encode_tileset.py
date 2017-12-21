
import argparse as ap
from PIL import Image
from gfx import GBTileset, RGBTileset

palette = [
    0x00,
    0x55,
    0xaa,
    0xff,
]

parser = ap.ArgumentParser('Convert an image to a 2-bit grayscale.')
parser.add_argument('image', type=str, help='Input RGB image')
parser.add_argument('outfile', type=ap.FileType('wb+'), help='Output 2-bit image')
args = parser.parse_args()

img = Image.open(args.image).convert('L')
rgbtileset = RGBTileset(img.tobytes(), img.size, (8, 8))
gbtileset = GBTileset.from_rgb(rgbtileset, palette)
args.outfile.write(gbtileset.data)
print('Wrote {} bytes'.format(len(gbtileset.data)))

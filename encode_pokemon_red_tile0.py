

INFILE = "pokemon_red_tile0_bytes.txt"
OUTFILE = "pokemon_red_tile0.bin"

lines = []
with open(INFILE, 'r') as f:
    lines.extend(f)

print('read {} lines from {}'.format(len(lines), INFILE))

lines = map(lambda s: s.rstrip(), lines)
encoded = bytearray(32*32*16)
i = 0
for line in lines:
    for byte in line.split(' '):
        encoded[i] = int(byte, 16)
        i += 1

with open(OUTFILE, 'wb') as f:
    f.write(encoded)
print('wrote {} bytes to {}'.format(len(encoded), OUTFILE))

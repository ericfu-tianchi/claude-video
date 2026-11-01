import sys, glob
from PIL import Image
shots = sys.argv[1].split(','); n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
ims = []
for s in shots:
    fs = sorted(glob.glob(f'frames/{s}/*.png'))
    step = max(1, len(fs) // n)
    ims += [Image.open(f).resize((480, 270)) for f in fs[::step][:n]]
cols = n
c = Image.new('RGB', (480 * cols, 270 * ((len(ims) + cols - 1) // cols)))
for i, im in enumerate(ims): c.paste(im, ((i % cols) * 480, (i // cols) * 270))
c.save('cs.png')

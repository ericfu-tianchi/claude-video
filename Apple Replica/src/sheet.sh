#!/bin/zsh
# sheet.sh "t1,t2,..." name  -> stills (output time) + contact sheet
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Apple Replica/src"
rm -rf out/st_$2; node render.mjs stills "$1" out/st_$2 2>&1 | grep -v "^$" | head -5
python3 - "$2" <<'PY'
import sys,glob
from PIL import Image, ImageDraw
n=sys.argv[1]; fs=sorted(glob.glob(f'out/st_{n}/*.png'))
ims=[Image.open(f).resize((640,360)) for f in fs]
cols=4; c=Image.new('RGB',(640*cols,360*((len(ims)+cols-1)//cols)),'white'); d=ImageDraw.Draw(c)
for i,(f,im) in enumerate(zip(fs,ims)): c.paste(im,((i%cols)*640,(i//cols)*360)); d.text(((i%cols)*640+6,(i//cols)*360+4),f.split('/')[-1][:-4],fill=(255,0,0))
c.save(f'out/sheet_{n}.png')
PY

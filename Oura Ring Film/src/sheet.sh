#!/bin/zsh
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Oura Ring Film/src"
rm -rf out/st_$2; node render.mjs stills "$1" out/st_$2 2>&1 | grep -iE "error|fail" | head -5
python3 - "$2" "${3:-4}" <<'PY'
import sys,glob
from PIL import Image, ImageDraw
n=sys.argv[1]; cols=int(sys.argv[2]); fs=sorted(glob.glob(f'out/st_{n}/*.png'))
w=1920//cols*1 if cols>2 else 960; w=min(640,1920//cols*2); h=w*9//16
c=Image.new('RGB',(w*cols,h*((len(fs)+cols-1)//cols)),'white'); d=ImageDraw.Draw(c)
for i,f in enumerate(fs): c.paste(Image.open(f).resize((w,h)),((i%cols)*w,(i//cols)*h)); d.text(((i%cols)*w+6,(i//cols)*h+4),f.split('/')[-1][:-4],fill=(255,0,0))
c.save(f'out/sheet_{n}.png')
PY

#!/bin/zsh
# rt.sh SHOT "t1,t2,..."  -> quick half-res stills + contact sheet build/sheet_SHOT.png
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Shanghai Stop-Motion/src"
S=$1; T=$2; SC=${3:-0.5}
rm -rf build/t_$S
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P render.py -- $S build/t_$S --scale $SC --samples 32 --still $T 2>&1 | grep -E "Error|Traceback|line [0-9]|Exception" 
python3 - "$S" <<'PY'
import sys,glob
from PIL import Image
S=sys.argv[1]; fs=sorted(glob.glob(f'build/t_{S}/*.png'))
ims=[Image.open(p) for p in fs]
if not ims: sys.exit()
w,h=ims[0].size; cols=2 if len(ims)>1 else 1; rows=(len(ims)+1)//2
c=Image.new('RGB',(w*cols,h*rows))
for i,im in enumerate(ims): c.paste(im,((i%cols)*w,(i//cols)*h))
c.save(f'build/sheet_{S}.png')
PY

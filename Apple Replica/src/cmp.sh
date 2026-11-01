#!/bin/zsh
# cmp.sh "T1,T2,..." name -> side-by-side (mine | reference at mapped source time)
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Apple Replica/src"
V="../../References/apple_ad.MP4"
rm -rf out/st_$2; node render.mjs stills "$1" out/st_$2 2>&1 | grep -iE "error|fail" | head -5
mkdir -p out/ref
for T in ${(s:,:)1}; do
  S=$(python3 -c "T=$T; print(1.6+T if T<35.4 else 84.0+T-35.4)")
  [ -f out/ref/$S.png ] || ffmpeg -v error -y -ss $S -i $V -frames:v 1 -vf "crop=2096:1180:230:0,scale=640:360" out/ref/$S.png
done
python3 - "$1" "$2" <<'PY'
import sys,glob
from PIL import Image, ImageDraw
Ts=[float(x) for x in sys.argv[1].split(',')]; n=sys.argv[2]
fs=sorted(glob.glob(f'out/st_{n}/*.png'))
rows=len(Ts); c=Image.new('RGB',(1290,365*rows),'white'); d=ImageDraw.Draw(c)
for i,(T,f) in enumerate(zip(sorted(Ts),fs)):
    S=1.6+T if T<35.4 else 84.0+T-35.4
    c.paste(Image.open(f).resize((640,360)),(0,i*365)); c.paste(Image.open(f'out/ref/{S}.png'),(650,i*365))
    d.text((6,i*365+4),f'T={T} src={S:.1f}',fill=(255,0,0))
c.save(f'out/cmp_{n}.png')
PY

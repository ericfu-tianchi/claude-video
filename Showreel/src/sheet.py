import sys,glob
from PIL import Image, ImageDraw
d=sys.argv[1]; cols=int(sys.argv[2]) if len(sys.argv)>2 else 3
fs=sorted(glob.glob(d+'/*.png')); w,h=640,360
rows=(len(fs)+cols-1)//cols
c=Image.new('RGB',(w*cols,h*rows),'#333')
for i,f in enumerate(fs):
    im=Image.open(f).convert('RGB').resize((w,h),Image.LANCZOS)
    ImageDraw.Draw(im).text((8,8),f.split('/')[-1][:-4],fill='#f0f')
    c.paste(im,((i%cols)*w,(i//cols)*h))
c.save(d+'_sheet.png')

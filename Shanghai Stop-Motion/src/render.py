"""Usage: blender -b -P render.py -- SHOT OUTDIR [--scale 0.5] [--samples 32] [--frames a:b:step] [--still t]"""
import sys, os, time, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
argv = sys.argv[sys.argv.index('--') + 1:]
shot, out = argv[0], argv[1]
opts = {'--scale': '1.0', '--samples': '64', '--frames': None, '--still': None}
i = 2
while i < len(argv):
    opts[argv[i]] = argv[i + 1]; i += 2

import lib
import shots
lib.reset()
dur, update = shots.SHOTS[shot]()
s = bpy.context.scene
s.render.resolution_x = int(1920 * float(opts['--scale']))
s.render.resolution_y = int(1080 * float(opts['--scale']))
s.eevee.taa_render_samples = int(opts['--samples'])
os.makedirs(out, exist_ok=True)
N = int(round(dur * 12))
if opts['--still'] is not None:
    frames = [int(round(float(t) * 12)) for t in opts['--still'].split(',')]
elif opts['--frames']:
    a, b, st = (opts['--frames'].split(':') + ['1'])[:3]
    frames = range(int(a), min(N, int(b)), int(st))
else:
    frames = range(N)
t0 = time.time()
for f in frames:
    path = os.path.join(out, f'{f:04d}.png')
    if opts['--still'] is None and os.path.exists(path):
        continue
    s.frame_set(f)
    update(f, f / 12.0)
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f'FRAME {shot} {f}/{N} {time.time() - t0:.1f}s', flush=True)
print('DONE', shot, N, f'{time.time() - t0:.1f}s')

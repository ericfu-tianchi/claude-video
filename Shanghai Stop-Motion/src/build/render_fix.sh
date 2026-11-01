#!/bin/zsh
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Shanghai Stop-Motion/src"
for S in $(cat build/fixups.txt); do
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P render.py -- $S build/frames/$S --scale 1.0 --samples 64 2>&1 | grep -E "DONE|Error|Traceback"
done
echo FIXDONE

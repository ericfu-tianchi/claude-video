#!/bin/zsh
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Shanghai Stop-Motion/src"
for S in p1_desk p2_popup p3_arrive p4_title l1_lane_wide l2_laundry l3_stall l4_cat b1_river_wide b2_bund_claude b3_ferry d1_lights d2_night_claude e1_desk_back e2_lamp_off; do
  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P render.py -- $S build/frames/$S --scale 1.0 --samples 64 2>&1 | grep -E "DONE|Error|Traceback"
done
echo ALLDONE

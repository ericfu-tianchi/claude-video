#!/bin/zsh
cd "/Users/tianchifu/Desktop/Playground:Inspiration/Claude Video/Oura Ring Film/src/ring3d"
B=/Applications/Blender.app/Contents/MacOS/Blender
need() { case $1 in silver) echo 181;; *) echo 71;; esac }
for T in silver brushed; do
  S=600; A=90; [ $T != silver ] && S=300 && A=35
  for try in 1 2 3 4 5 6; do
    n=$(ls ../sprites | grep -c "^${T}_")
    [ $n -ge $(need $T) ] && break
    $B -b --factory-startup -P ring_sprites.py -- $T $S $A ../sprites > /dev/null 2>&1
  done
  echo $T $(ls ../sprites | grep -c "^${T}_")
done
echo SPRITESDONE

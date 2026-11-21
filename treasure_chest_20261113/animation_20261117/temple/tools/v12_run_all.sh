#!/bin/zsh
# Version 12: render the four pieces of the reveal and put the videos in Downloads. Safe to run again: frames that
# exist are kept (delete render/v12_frames/<piece> to redo one). PCT and SAMPLES set the quality.
# Order: arrival, waiting, ending, reveal (the reveal last, so the mist can bake meanwhile); each piece's video is written as soon as its frames are done.
cd /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117
B=/Applications/Blender.app/Contents/MacOS/Blender
PCT=${PCT:-70}; SAMPLES=${SAMPLES:-24}
R=render/v12_frames
D=/Users/antonioperedo/Downloads
count() { ls $R/$1 2>/dev/null | grep -c png }
enc() { local extra=(); [ -n "$3" ] && extra=(-frames:v $3); ffmpeg -y -loglevel error -framerate 30 -i "$1/%04d.png" "${extra[@]}" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart "$2" }
render() {  # piece, frames needed, optional list of frames to render
  for try in 1 2 3 4; do
    [ "$(count $1)" -ge "$2" ] && break
    echo "$(date +%H:%M) render $1 try $try ($(count $1) of $2)"
    PIECE=$1 OUT=$R/$1 PCT=$PCT SAMPLES=$SAMPLES SKIP_DONE=1 ONLY=$3 $B -b chest_reveal_v12_full.blend --python tools/v12_render.py 2>&1 | grep -E "V12 DONE|Traceback|Error: " | sed 's/(.*//' | sort | uniq -c | head -4
  done
  echo "$(date +%H:%M) $1: $(count $1) of $2 frames"
}
render arrival 124
enc $R/arrival "$D/Chest reveal 1 arrival.mp4"
# Waiting loop: between rattles the chest is at rest and the picture depends only on the place in the 2.5 second
# beat, so those 45 frames are rendered once (first beat) and reused for the second and third.
if [ "$(count waiting)" -lt 225 ]; then
  render waiting 135 "$(/usr/local/bin/python3 -c "print(','.join(str(i) for i in list(range(0, 105)) + list(range(150, 180))))")"
  for i in $(seq 105 149); do ln -f $R/waiting/$(printf %04d $((i-75))).png $R/waiting/$(printf %04d $i).png; done
  for i in $(seq 180 224); do ln -f $R/waiting/$(printf %04d $((i-150))).png $R/waiting/$(printf %04d $i).png; done
fi
echo "$(date +%H:%M) waiting: $(count waiting) of 225 frames"
enc $R/waiting "$D/Chest reveal 2 waiting loop three rattles.mp4"
enc $R/waiting "$D/Chest reveal 2 waiting loop one rattle.mp4" 75
render ending 114
/usr/local/bin/python3 temple/tools/loop_join.py $R/ending $R/ending_loop 90 24
enc $R/ending_loop "$D/Chest reveal 4 ending loop.mp4"
# the reveal reads the mist simulation: if that is still baking (it can run beside the pieces above), wait for it
while pgrep -f v12_bake_mist.py >/dev/null; do /bin/sleep 15; done
REVEAL=$(/usr/local/bin/python3 -c "import re; s=open('tools/v12_story.py').read(); print(int(re.search(r'STORY_END\", (\d+)', s).group(1)) - 49)")
render reveal $REVEAL
enc $R/reveal "$D/Chest reveal 3 reveal.mp4"
# the whole thing as a person would see it: arrival, one round of waiting, reveal, then the ending three times
rm -rf $R/whole && mkdir -p $R/whole
n=0
add() { for f in $(ls $1 | grep png | sort | sed -n "${2:-1},${3:-9999}p"); do ln -f $1/$f $R/whole/$(printf %05d $n).png; n=$((n+1)); done }
add $R/arrival; add $R/waiting; add $R/reveal; add $R/ending 1 90; add $R/ending_loop; add $R/ending_loop
ffmpeg -y -loglevel error -framerate 30 -i $R/whole/%05d.png -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart "$D/Chest reveal whole scene preview.mp4"
echo "$(date +%H:%M) ALL DONE $n frames in the whole preview"
ls -la $D | grep "Chest reveal"

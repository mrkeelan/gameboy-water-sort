"""Refresh baked bottle previews from GB Studio scene events; preserve scenery.

Save your GB Studio changes first. Run this only when you want the saved scene
images to reflect changed bottle configurations. Gameplay already uses events.
"""
from pathlib import Path
import re,json,itertools
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
raw=[int(v) for v in re.findall(r'\d+',re.search(r'ws_tiles\[\].*?\{(.*?)\}',(ROOT/'plugins/water-sort/engine/include/states/water_tiles.h').read_text(),re.S).group(1))]
def decode(s):
 result=[]
 for m in re.finditer(r'([0-9a-f]{2})(!|([0-9a-f]+)\+)',s):result.extend([int(m[1],16)]*(1 if m[2]=='!' else int(m[3],16)))
 return result
mono=[(224,248,207),(134,192,108),(48,104,80),(7,24,33)]
backgrounds={}
for path in (ROOT/'assets/backgrounds').rglob('*.gbsres'):
 data=json.loads(path.read_text());backgrounds[data['id']]=(path,data)
for path in (ROOT/'project/scenes').rglob('scene.gbsres'):
 scene=json.loads(path.read_text());events=[e for e in scene.get('script',[]) if e['command']=='EVENT_WATER_SORT_CONFIGURE']
 if not events:continue
 args=events[0]['args'];meta,bg=backgrounds[scene['backgroundId']]
 png=meta.parent/bg['filename'];im=Image.open(png).convert('RGB');pixels=im.load();attrs=decode(bg['tileColors']) or [0]*360
 def put(x,y,t,p=0):
  attrs[y*20+x]=p
  for py in range(8):
   lo,hi=raw[t*16+py*2:t*16+py*2+2]
   for px in range(8):pixels[x*8+px,y*8+py]=mono[((lo>>(7-px))&1)+2*((hi>>(7-px))&1)]
 for b in range(6):
  x=2+b%3*6;y=5 if b<3 else 11
  for j in range(6):
   for k in range(4):put(x+k,y-1+j,0)
  if b>=int(args['count']):continue
  p=6 if b==0 else 5;put(x+1,y-1,17+b,p)
  if b==0:put(x,y-1,ord('>')-32,6)
  for j in range(4):
   put(x,y+j,59,p);put(x+3,y+j,60,p)
   color=int(args.get(f'b{b}l{3-j}',0));put(x+1,y+j,63+color if color else 0,color);put(x+2,y+j,63+color if color else 0,color)
  for k,t in enumerate([61,62,62,63]):put(x+k,y+4,t,p)
 im.save(png)
 bg['tileColors']=''.join(f'{value:02x}'+('!' if len(group)==1 else f'{len(group):x}+') for value,items in itertools.groupby(attrs) for group in [list(items)])
 meta.write_text(json.dumps(bg,indent=2)+'\n')
 print('Updated preview:',scene['name'])

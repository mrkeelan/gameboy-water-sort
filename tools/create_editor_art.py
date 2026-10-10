"""Create the initial native scene images and the GB Studio resource manifest."""
import json,re,uuid,itertools
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
INC=ROOT/'plugins/water-sort/engine/include/states'
def ident(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'water-sort/editor/'+name))
def array(name,file):
 text=file.read_text();body=re.search(name+r'[^=]*=\{(.*?)\};',text,re.S).group(1)
 return [int(n) for n in re.findall(r'\d+',body)]
raw=array('ws_tiles',INC/'water_tiles.h')+array('ws_theme_tiles',INC/'water_themes.h')
tiles=[]
for i in range(0,len(raw),16):
 tile=[]
 for y in range(8):
  lo,hi=raw[i+y*2:i+y*2+2];tile.append([((lo>>(7-x))&1)+2*((hi>>(7-x))&1) for x in range(8)])
 tiles.append(tile)
themes=(INC/'water_themes.h').read_text()
names=re.findall(r'"([A-Z ]+)"',re.search(r'ws_theme_names.*?\};',themes,re.S).group(0))
maps=array('ws_theme_maps',INC/'water_themes.h')
def rgb(hex5):return ''.join(f'{(v*255+15)//31:02X}' for v in hex5)
theme_palettes=[tuple(map(int,m)) for m in re.findall(r'RGB\((\d+),(\d+),(\d+)\)',re.search(r'ws_theme_palettes.*?\};',themes,re.S).group(0))]
source=(ROOT/'plugins/water-sort/engine/src/states/watersort.c').read_text()
base=[tuple(map(int,m)) for m in re.findall(r'RGB\((\d+),(\d+),(\d+)\)',re.search(r'ws_colors.*?\};',source,re.S).group(0))]
levels=json.loads((ROOT/'tools/levels.json').read_text())
manifest={'commonPalettes':[], 'levels':[]}
for p in range(1,8):manifest['commonPalettes'].append({'id':ident('palette-'+str(p)),'name':['','Red Dots','Blue Stripes','Yellow Diagonals','Green Grid','Bottle Glass','Cursor Gold','Selected Aqua'][p],'colors':[rgb(c) for c in base[p*4:p*4+4]]})
for level,puzzle in enumerate(levels):
 m=maps[level*360:(level+1)*360].copy();attrs=[0]*360
 def put(x,y,t,p=0):m[y*20+x]=t;attrs[y*20+x]=p
 def text(x,y,s,p=0):
  for c in s:
   if x<20:put(x,y,ord(c)-32,p)
   x+=1
 for y in list(range(4))+[16,17]:
  for x in range(20):put(x,y,0)
 text(5,0,'WATER SORT',6);text(1,1,f'LEVEL {level+1}/8',5);text(11,1,'MOVES',5);text(17,1,'000')
 text(2,2,'A - PICK A BOTTLE',0);text(2,3,names[level])
 args={'level':level+1,'count':len(puzzle['bottles'])}
 for b in range(6):
  water=(puzzle['bottles'][b] if b<len(puzzle['bottles']) else [])
  for l in range(4):args[f'b{b}l{l}']=water[l] if l<len(water) else 0
  x=2+(b%3)*6;y=5 if b<3 else 11;p=6 if b==0 else 5
  for j in range(6):
   for k in range(4):put(x+k,y-1+j,0)
  if b>=len(puzzle['bottles']):continue
  put(x+1,y-1,17+b,p)
  if b==0:put(x,y-1,ord('>')-32,6)
  for j in range(4):
   put(x,y+j,59,p);put(x+3,y+j,60,p)
   color=water[3-j] if 3-j<len(water) else 0
   put(x+1,y+j,63+color if color else 0,color);put(x+2,y+j,63+color if color else 0,color)
  for k,t in enumerate([61,62,62,63]):put(x+k,y+4,t,p)
 text(1,16,'B CANCEL  SEL UNDO',5);text(1,17,'DPAD MOVE START RST',5)
 png=ROOT/f'assets/backgrounds/levels/level_{level+1:02d}.png'
 im=Image.new('RGB',(160,144));pixels=im.load();mono=[(224,248,207),(134,192,108),(48,104,80),(7,24,33)]
 for y in range(18):
  for x in range(20):
   for py in range(8):
    for px in range(8):pixels[x*8+px,y*8+py]=mono[tiles[m[y*20+x]][py][px]]
 im.save(png)
 compressed=''.join(f'{value:02x}'+('!' if len(group)==1 else f'{len(group):x}+') for value,items in itertools.groupby(attrs) for group in [list(items)])
 manifest['levels'].append({'name':f'{level+1:02d} - {names[level].title()}', 'sceneId':'12f07015-0a42-504a-8d39-3f689e13ad3a' if level==0 else ident('scene-'+str(level+1)), 'backgroundId':ident('background-'+str(level+1)), 'palette':{'id':ident('theme-'+str(level+1)),'name':names[level].title()+' Background','colors':[rgb(c) for c in theme_palettes[level*4:level*4+4]]}, 'path':str(png.relative_to(ROOT)), 'tileColors':compressed,'args':args})
(ROOT/'tools/editor_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Created eight 160x144 scene backgrounds and editor configurations.')

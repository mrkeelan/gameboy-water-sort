"""Hand-author low-contrast tiled scenery for each puzzle level."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plugins/water-sort/engine/include/states/water_themes.h'
themes=[
 ('MOONLIT SKY',(2,3,9),(6,8,17)),
 ('FERN GROVE',(2,6,4),(5,12,7)),
 ('BRICK COURTYARD',(7,3,4),(13,7,7)),
 ('CORAL TIDE',(1,6,9),(3,12,17)),
 ('DESERT DUSK',(9,4,3),(17,9,5)),
 ('SNOWFALL',(5,8,12),(11,15,20)),
 ('CRYSTAL CAVE',(5,2,9),(12,5,17)),
 ('NEON LAB',(2,7,8),(4,15,14))]
tiles=[];maps=[]
for level in range(8):
 for variant in range(4):
  p=[[0]*8 for _ in range(8)]
  def dot(x,y):
   if 0<=x<8 and 0<=y<8:p[y][x]=1
  if level==0:
   if variant!=0:
    dot(2+variant,2);dot(2+variant,3);dot(1+variant,3);dot(3+variant,3);dot(2+variant,4)
  elif level==1:
   for y in range(2,8):
    dot(3,y)
    if y%2==variant%2:dot(2,y-1);dot(1,y-2);dot(4,y-1);dot(5,y-2)
  elif level==2:
   for x in range(8):dot(x,7)
   for y in range(8):dot((variant%2)*4,y)
  elif level==3:
   for x in range(8):dot(x,3+((x+variant*2)//2)%3)
  elif level==4:
   for x in range(8):
    y=7-abs(x-3) if variant%2==0 else 4+abs(x-3)//2
    dot(x,y)
  elif level==5:
   if variant:
    for d in range(-2,3):dot(3+d,3);dot(3,3+d)
    dot(2,2);dot(4,4);dot(2,4);dot(4,2)
  elif level==6:
   for y in range(8):dot(3-y//2,y);dot(3+y//2,y)
   for x in range(8):dot(x,7)
  else:
   for x in range(8):dot(x,variant+2)
   for y in range(variant+2,8):dot(4,y)
   dot(3,6);dot(5,6);dot(4,5);dot(4,7)
  tiles.append(p)
 m=[]
 for y in range(18):
  for x in range(20):
   v=(x*3+y*5)%4
   if level in (0,5):v=0 if (x+y*3)%5 else 1+(x+y)%3
   m.append(68+level*4+v if 3<=y<=15 else 0)
 maps.append(m)
data=[]
for tile in tiles:
 for row in tile:data.extend([sum(c<<(7-x) for x,c in enumerate(row)),0])
OUT.write_text('static const unsigned char ws_theme_tiles[]={'+','.join(map(str,data))+'};\n'+
 'static const unsigned char ws_theme_maps[8][360]={\n'+',\n'.join('{'+','.join(map(str,m))+'}' for m in maps)+'\n};\n'+
 'static const char * const ws_theme_names[]={'+','.join('"'+t[0]+'"' for t in themes)+'};\n'+
 'static const unsigned short ws_theme_palettes[8][4]={\n'+',\n'.join('{RGB('+','.join(map(str,t[1]))+'),RGB('+','.join(map(str,t[2]))+'),RGB(27,29,28),RGB(12,19,23)}' for t in themes)+'\n};\n')
print('Created eight native background themes with 32 additional tiles.')

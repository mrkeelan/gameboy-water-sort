"""Author exact 8x8 tiles and deterministic, solver-verified puzzle levels."""
from pathlib import Path
import random, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plugins/water-sort/engine/include/states'
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
'/':['00001','00001','00010','00100','01000','10000','10000'],
'>':['10000','01000','00100','00010','00100','01000','10000'],
'!':['00100','00100','00100','00100','00100','00000','00100'],
}
tiles=[]
for ascii in range(32,91):
    rows=FONT.get(chr(ascii),['00000']*7)
    tiles.append([[0]*8]+[[0]+[2 if c=='1' else 0 for c in row]+[0,0] for row in rows])
tiles += [
 [[0,0,0,2,3,0,0,0] for y in range(8)],
 [[0,0,0,3,2,0,0,0] for y in range(8)],
 [[0,0,0,2,3,0,0,0] if y<3 else [0,0,0,0,2,2,2,2] if y==3 else [0]*8 for y in range(8)],
 [[2]*8 if y==3 else [0]*8 for y in range(8)],
 [[0,0,0,3,2,0,0,0] if y<3 else [2,2,2,2,0,0,0,0] if y==3 else [0]*8 for y in range(8)],
]
for pattern in range(4):
    tiles.append([[2 if ([(x%4==1 and y%4==1),(y%4==1),(x+y)%4==0,(x%4==1 or y%4==1)][pattern]) else 1 for x in range(8)] for y in range(8)])
data=[]
for tile in tiles:
    for row in tile:
        data.extend([sum((c&1)<<(7-x) for x,c in enumerate(row)),sum(((c>>1)&1)<<(7-x) for x,c in enumerate(row))])
OUT.joinpath('water_tiles.h').write_text('static const unsigned char ws_tiles[]={\n'+','.join(map(str,data))+'\n};\n#define WS_TILE_COUNT '+str(len(tiles))+'\n')

def pour(state,a,b):
    src,dst=state[a],state[b]
    if a==b or not src or len(dst)==4 or (dst and dst[-1]!=src[-1]): return None
    n=1
    while n<len(src) and src[-1-n]==src[-1]: n+=1
    n=min(n,4-len(dst))
    out=list(state);out[a]=src[:-n];out[b]=dst+src[-n:]
    return tuple(out)
def solved(state):return all(not b or len(b)==4 and len(set(b))==1 for b in state)
def solve(state):
    seen=set()
    def dfs(s,depth):
        if solved(s):return []
        if depth>45:return None
        key=tuple(sorted(s))
        if key in seen:return None
        seen.add(key)
        options=[]
        for a,src in enumerate(s):
            if not src or len(src)==4 and len(set(src))==1:continue
            used_empty=False
            for b,dst in enumerate(s):
                if not dst:
                    if used_empty or len(set(src))==1:continue
                    used_empty=True
                out=pour(s,a,b)
                if out is not None: options.append((0 if dst else 1,a,b,out))
        for _,a,b,out in sorted(options):
            result=dfs(out,depth+1)
            if result is not None:return [(a,b)]+result
        return None
    return dfs(state,0)
levels=[]
for idx,colors in enumerate([2,2,3,3,4,4,4,4]):
    rng=random.Random(700+idx)
    while True:
        balls=[c for c in range(1,colors+1) for _ in range(4)];rng.shuffle(balls)
        state=tuple(tuple(balls[i*4:(i+1)*4]) for i in range(colors))+((),())
        answer=solve(state)
        if answer and len(answer)>=4:break
    levels.append({'colors':colors,'bottles':[list(b) for b in state],'solution':answer})
OUT.joinpath('water_levels.h').write_text('#define WS_LEVEL_COUNT 8\nstatic const unsigned char ws_counts[]={'+','.join(str(l['colors']+2) for l in levels)+'};\nstatic const unsigned char ws_levels[8][6][4]={\n'+',\n'.join('{'+','.join('{'+','.join(map(str,b+[0]*(4-len(b))))+'}' for b in l['bottles']+[[]]*(6-len(l['bottles'])))+'}' for l in levels)+'\n};\n')
ROOT.joinpath('tools/levels.json').write_text(json.dumps(levels,indent=2)+'\n')
print('Authored',len(tiles),'tiles and',len(levels),'solvable levels; solutions:',[len(l['solution']) for l in levels])

#pragma bank 255
#include <gbdk/platform.h>
#include <gb/cgb.h>
#include <string.h>
#include "states/watersort.h"
#include "states/water_model.h"
#include "states/water_tiles.h"
#include "states/water_levels.h"
#include "states/water_themes.h"
#include "input.h"
#include "actor.h"
#include "palette.h"
#include "camera.h"
#include "data_manager.h"
#include "vm.h"

static ws_state ws_game, ws_initial, ws_history[8];
static UBYTE ws_next_bank;
static UBYTE *ws_next_script;
static UBYTE ws_history_start, ws_history_count;
static UBYTE ws_level, ws_count, ws_cursor, ws_source, ws_ready, ws_win;
static UBYTE ws_from, ws_to, ws_remaining, ws_timer, ws_message;
static UBYTE ws_map[360], ws_palette_pass;
static const UWORD ws_colors[32]={
    RGB(2,4,8), RGB(8,13,19), RGB(27,29,28), RGB(12,19,23),
    RGB(2,4,8), RGB(28,8,12), RGB(31,18,19), RGB(15,3,7),
    RGB(2,4,8), RGB(5,16,29), RGB(16,26,31), RGB(2,7,19),
    RGB(2,4,8), RGB(29,20,3), RGB(31,29,15), RGB(18,11,1),
    RGB(2,4,8), RGB(8,23,16), RGB(21,31,23), RGB(2,13,8),
    RGB(2,4,8), RGB(8,13,19), RGB(16,22,25), RGB(4,8,13),
    RGB(2,4,8), RGB(26,19,4), RGB(31,28,13), RGB(18,12,3),
    RGB(2,4,8), RGB(8,23,25), RGB(19,31,30), RGB(3,14,17)
};

static void ws_put(UBYTE x, UBYTE y, UBYTE tile, UBYTE pal) {
    UWORD p=(UWORD)y*20+x;
    ws_map[p]=ws_palette_pass?pal:tile+128;
}
static void ws_text(UBYTE x, UBYTE y, const char *text, UBYTE pal) {
    while (*text && x<20) ws_put(x++,y,(UBYTE)(*text++-32),pal);
}
static void ws_number(UBYTE x, UBYTE y, UWORD number, UBYTE digits) {
    while (digits) { ws_put(x+--digits,y,16+number%10,0); number/=10; }
}
static void ws_sound(UBYTE good) {
    NR52_REG=0x80; NR50_REG=0x77; NR51_REG=0x11;
    NR10_REG=0; NR11_REG=0x80; NR12_REG=0x82;
    NR13_REG=good?0xC0:0x10; NR14_REG=good?0x87:0x84;
}
static void ws_draw(void) {
    UBYTE i,j,x,y,p,color,t;
    for (ws_palette_pass=0;ws_palette_pass<2;ws_palette_pass++) {
    MemcpyBanked(ws_map,ws_palette_pass?image_attr_ptr:image_ptr,sizeof(ws_map),ws_palette_pass?image_attr_bank:image_bank);
    for (y=0;y<3;y++) for (x=0;x<20;x++) ws_put(x,y,0,0);
    for (y=16;y<18;y++) for (x=0;x<20;x++) ws_put(x,y,0,0);
    /* All six bottle footprints belong to the live board, including unused slots. */
    for (i=0;i<6;i++) {
        x=2+(i%3)*6;y=i<3?5:11;
        for(j=0;j<6;j++) for(t=0;t<4;t++) ws_put(x+t,y-1+j,0,0);
    }
    for (x=0;x<20;x++) ws_put(x,3,0,0);
    ws_text(2,3,ws_theme_names[ws_level],0);
    ws_text(5,0,"WATER SORT",6);
    ws_text(1,1,"LEVEL",5);ws_number(7,1,ws_level+1,1);ws_text(8,1,"/8",5);
    ws_text(11,1,"MOVES",5);ws_number(17,1,ws_game.moves,3);
    if (ws_win) ws_text(0,2,ws_level==7?"ALL SORTED! A REPLAY":"SORTED! A NEXT LEVEL",0);
    else if (ws_remaining) ws_text(5,2,"POURING...",0);
    else if (ws_message==1) ws_text(2,2,"COLORS MUST MATCH",1);
    else if (ws_message==2) ws_text(4,2,"BOTTLE IS FULL",1);
    else if (ws_message==3) ws_text(3,2,"BOTTLE IS EMPTY",5);
    else if (ws_message==4) ws_text(4,2,"NOTHING TO UNDO",5);
    else ws_text(ws_source==255?2:0,2,ws_source==255?"A - PICK A BOTTLE":"A - PICK DESTINATION",0);
    for (i=0;i<ws_count;i++) {
        x=2+(i%3)*6; y=i<3?5:11;
        for (j=0;j<6;j++) {
            ws_put(x,y-1+j,0,0);ws_put(x+1,y-1+j,0,0);
            ws_put(x+2,y-1+j,0,0);ws_put(x+3,y-1+j,0,0);
        }
        p=i==ws_source?0:i==ws_cursor?6:5;
        ws_put(x+1,y-1,16+i+1,p);
        if (i==ws_cursor) ws_put(x,y-1,'>'-32,6);
        if (i==ws_source) ws_put(x+2,y-1,'A'-32,0);
        for (j=0;j<4;j++) {
            ws_put(x,y+j,59,p);ws_put(x+3,y+j,60,p);
            color=ws_game.water[i][3-j];
            t=color?63+color:0;
            ws_put(x+1,y+j,t,color);ws_put(x+2,y+j,t,color);
        }
        ws_put(x,y+4,61,p);ws_put(x+1,y+4,62,p);ws_put(x+2,y+4,62,p);ws_put(x+3,y+4,63,p);
    }
    ws_text(1,16,"B CANCEL  SEL UNDO",5);
    ws_text(1,17,"DPAD MOVE START RST",5);
    VBK_REG=ws_palette_pass;set_bkg_tiles(0,0,20,18,ws_map);
    }
    VBK_REG=0;
}
static void ws_load(void) {
    memcpy(&ws_game,&ws_initial,sizeof(ws_game));
    ws_cursor=0;ws_source=255;ws_win=0;ws_message=0;ws_remaining=0;
    ws_history_start=0;ws_history_count=0;
}
void ws_configure(SCRIPT_CTX *THIS) OLDCALL BANKED {
    UBYTE b,l,c;
    UWORD packed;
    ws_next_script=*(UBYTE **)VM_REF_TO_PTR(-1);
    ws_next_bank=*(UWORD *)VM_REF_TO_PTR(-2);
    ws_count=*(UWORD *)VM_REF_TO_PTR(-9);
    ws_level=*(UWORD *)VM_REF_TO_PTR(-10);
    memset(&ws_initial,0,sizeof(ws_initial));
    for (b=0;b<ws_count;b++) {
        packed=*(UWORD *)VM_REF_TO_PTR(-8+b);
        for(l=0;l<4;l++) {
            c=(packed>>(l*3))&7;
            ws_initial.water[b][l]=c;
            if(c)ws_initial.height[b]++;
        }
    }
    ws_load();
    ws_ready=0;
}
static void ws_remember(void) {
    UBYTE slot;
    if (ws_history_count==8) {
        ws_history_start=(ws_history_start+1)&7;ws_history_count--;
    }
    slot=(ws_history_start+ws_history_count)&7;
    memcpy(&ws_history[slot],&ws_game,sizeof(ws_state));ws_history_count++;
}
void watersort_init(void) BANKED {
    ws_ready=0;
    PLAYER.flags|=ACTOR_FLAG_HIDDEN;
    camera_offset_x=0;camera_offset_y=0;
}
void watersort_update(void) BANKED {
    UBYTE key, color, amount;
    ws_state candidate;
    HIDE_SPRITES;
    if (!ws_ready) {
        VBK_REG=0;set_bkg_data(128,WS_TILE_COUNT,ws_tiles);
        ws_ready=1;ws_draw();return;
    }
    if (ws_remaining) {
        if (--ws_timer) return;
        color=ws_game.water[ws_from][ws_game.height[ws_from]-1];
        ws_game.water[ws_from][--ws_game.height[ws_from]]=0;
        ws_game.water[ws_to][ws_game.height[ws_to]++]=color;
        ws_remaining--;ws_timer=8;ws_sound(1);
        if (!ws_remaining) {ws_game.moves++;ws_win=ws_solved(&ws_game,ws_count);}
        ws_draw();return;
    }
    key=joy_pressed;
    if (!key) return;
    ws_message=0;
    if (key&J_START) {ws_load();ws_sound(1);ws_draw();return;}
    if (key&J_SELECT) {
        if (ws_history_count) {
            ws_history_count--;
            memcpy(&ws_game,&ws_history[(ws_history_start+ws_history_count)&7],sizeof(ws_state));
            ws_source=255;ws_win=0;ws_sound(1);
        } else ws_message=4;
        ws_draw();return;
    }
    if (ws_win) {
        if ((key&J_A) && ws_next_script) {script_execute(ws_next_bank,ws_next_script,0,0);ws_sound(1);}
        ws_draw();return;
    }
    if (key&J_LEFT) ws_cursor=ws_cursor?ws_cursor-1:ws_count-1;
    else if (key&J_RIGHT) ws_cursor=(ws_cursor+1)%ws_count;
    else if (key&(J_UP|J_DOWN)) {
        if (ws_cursor>=3) ws_cursor-=3;
        else if (ws_cursor+3<ws_count) ws_cursor+=3;
    }
    else if (key&J_B) ws_source=255;
    else if (key&J_A) {
        if (ws_source==255) {
            if (ws_game.height[ws_cursor]) {ws_source=ws_cursor;ws_sound(1);}
            else {ws_message=3;ws_sound(0);}
        } else if (ws_cursor==ws_source) ws_source=255;
        else {
            memcpy(&candidate,&ws_game,sizeof(ws_state));
            amount=ws_pour(&candidate,ws_source,ws_cursor,ws_count);
            if (amount) {
                ws_remember();ws_from=ws_source;ws_to=ws_cursor;
                ws_remaining=amount;ws_timer=8;ws_source=255;
            } else {ws_message=ws_game.height[ws_cursor]==4?2:1;ws_sound(0);}
        }
    }
    ws_draw();
}

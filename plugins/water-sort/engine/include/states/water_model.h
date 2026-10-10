#ifndef WATER_MODEL_H
#define WATER_MODEL_H
#include <string.h>
#define WS_CAP 4
#define WS_BOTTLES 6
typedef struct {
    unsigned char water[WS_BOTTLES][WS_CAP];
    unsigned char height[WS_BOTTLES];
    unsigned short moves;
} ws_state;
static unsigned char ws_pour(ws_state *s, unsigned char from, unsigned char to, unsigned char count) {
    unsigned char color, amount = 1, i;
    if (from >= count || to >= count || from == to || !s->height[from] || s->height[to] == WS_CAP) return 0;
    color = s->water[from][s->height[from] - 1];
    if (s->height[to] && s->water[to][s->height[to]-1] != color) return 0;
    while (amount < s->height[from] && s->water[from][s->height[from]-1-amount] == color) amount++;
    if (amount > WS_CAP-s->height[to]) amount = WS_CAP-s->height[to];
    for (i=0; i<amount; i++) {
        s->water[to][s->height[to]++] = color;
        s->water[from][--s->height[from]] = 0;
    }
    s->moves++;
    return amount;
}
static unsigned char ws_solved(const ws_state *s, unsigned char count) {
    unsigned char i,j;
    for (i=0; i<count; i++) {
        if (!s->height[i]) continue;
        if (s->height[i] != WS_CAP) return 0;
        for (j=1; j<WS_CAP; j++) if (s->water[i][j] != s->water[i][0]) return 0;
    }
    return 1;
}
#endif

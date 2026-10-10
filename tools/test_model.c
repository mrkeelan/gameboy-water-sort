#include <assert.h>
#include <stdio.h>
#include "../plugins/water-sort/engine/include/states/water_model.h"
int main(void) {
    ws_state s={0}, before;
    s.water[0][0]=1;s.water[0][1]=2;s.water[0][2]=2;s.water[0][3]=2;s.height[0]=4;
    s.water[1][0]=2;s.water[1][1]=2;s.water[1][2]=2;s.height[1]=3;
    before=s;
    assert(ws_pour(&s,0,1,4)==1); /* Only available capacity, even for a block of three. */
    assert(s.height[0]==3 && s.height[1]==4 && s.moves==1);
    assert(ws_pour(&s,0,1,4)==0); /* Full target. */
    assert(ws_pour(&s,0,0,4)==0); /* Self-pour. */
    assert(ws_pour(&s,3,2,4)==0); /* Empty source. */
    assert(ws_pour(&s,0,6,4)==0); /* Invalid index. */
    s=before;
    s.water[2][0]=1;s.height[2]=1;
    assert(ws_pour(&s,0,2,4)==0); /* Different top colors. */
    assert(ws_pour(&s,0,3,4)==3); /* Move the whole contiguous top block. */
    assert(s.height[0]==1 && s.height[3]==3 && !ws_solved(&s,4));
    memset(&s,0,sizeof(s));
    s.height[0]=4;memset(s.water[0],1,4);
    assert(ws_solved(&s,4)); /* Uniform full bottles plus empty spare bottles. */
    s.height[1]=1;s.water[1][0]=2;assert(!ws_solved(&s,4));
    puts("Pour rules, capacity limits, invalid input, and win detection passed.");
    return 0;
}

const fields = [
  { key: "level", label: "Level number", type: "number", min: 1, max: 8, defaultValue: 1 },
  { key: "count", label: "Number of bottles", type: "number", min: 3, max: 6, defaultValue: 4 },
  { type: "label", label: "Layers are listed from bottom to top. Use Empty only above filled layers. Each color needs four layers in total." },
];
for (let bottle = 0; bottle < 6; bottle++) {
  fields.push({ type: "label", label: `Bottle ${bottle + 1}` });
  for (let layer = 0; layer < 4; layer++) fields.push({
    key: `b${bottle}l${layer}`, label: ["Bottom", "Lower middle", "Upper middle", "Top"][layer],
    type: "select", defaultValue: 0,
    options: [[0,"Empty"],[1,"Red dots"],[2,"Blue stripes"],[3,"Yellow diagonals"],[4,"Green grid"]],
  });
}
fields.push({key:"script",label:"On solved: next level / replay",type:"events",allowedContexts:["global","entity"]});
module.exports = {
  id: "EVENT_WATER_SORT_CONFIGURE",
  name: "Configure Water Sort Puzzle",
  description: "Sets this scene's starting bottles. The scene background and palettes are used directly by the game. Put a Switch Scene event in On solved to choose the next level.",
  groups: ["EVENT_GROUP_MISC"], sceneTypes: ["watersort"], fields,
  allowedBeforeInitFade: true,
  compile(input, helpers) {
    const { _stackPushConst, _callNative, _stackPop, _compileSubScript } = helpers;
    const count = Math.max(3, Math.min(6, Number(input.count) || 4));
    const level = Math.max(1, Math.min(8, Number(input.level) || 1));
    const totals=[0,0,0,0,0], packed=[];
    for (let b=0;b<6;b++) {
      let value=0, empty=false;
      for (let l=0;l<4;l++) {
        const color=Number(input[`b${b}l${l}`])||0;
        if(color<0||color>4||!Number.isInteger(color))throw new Error(`Bottle ${b+1}: invalid color`);
        if(b<count){
          if(!color)empty=true;
          else {if(empty)throw new Error(`Bottle ${b+1}: filled layer above an empty layer`);totals[color]++;}
        } else if(color)throw new Error(`Bottle ${b+1} is outside the bottle count`);
        value |= color << (l*3);
      }
      packed.push(value);
    }
    if(!totals.some((n,i)=>i&&n))throw new Error("The puzzle has no water");
    for(let c=1;c<=4;c++)if(totals[c]&&totals[c]!==4)throw new Error(`Color ${c} must have exactly four layers`);
    const script = _compileSubScript("state", input.script || [], "water_sort_next");
    _stackPushConst(level-1);_stackPushConst(count);
    packed.forEach(value=>_stackPushConst(value));
    _stackPushConst(`___bank_${script}`);_stackPushConst(`_${script}`);
    _callNative("ws_configure");_stackPop(10);
  },
};

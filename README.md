# Water Sort

A Game Boy Color puzzle with eight fixed, solver-verified levels. Sort the patterned colored water into full bottles of one color, leaving spare bottles empty.

Each level is a real GB Studio scene with its own editable background PNG and palette resources: Moonlit Sky, Fern Grove, Brick Courtyard, Coral Tide, Desert Dusk, Snowfall, Crystal Cave, and Neon Lab. The Game World canvas shows the actual starting board for every level.

## Play

- D-pad: move between bottles.
- A: select a source, then select its destination. After winning, advance to the next level; the final level offers replay.
- B: cancel the source selection.
- Select: undo, up to eight moves.
- Start: restart the current level.

Pour only into an empty bottle or onto matching water, and only while space remains. Each move transfers as much of the contiguous top color as fits. The move counter counts successful pours. Progress is session-only.

In the browser, use arrows, Z for A, X for B, P for Select, and Enter for Start.

## Edit and build

Open project.gbsproj in GB Studio 4.3.2. Select a named level from the Scenes list. In On Init, expand **Configure Water Sort Puzzle**. Its dropdowns set each bottle's four layers, ordered from bottom to top. Use Empty only above filled layers, leave bottles beyond Number of bottles empty, and use exactly four layers of each included color. These event fields are the source of truth for the played puzzle; they no longer require C edits. The compiler rejects gaps and incorrect color totals. Solvability still needs a playtest after changing a puzzle.

Expand **On solved: next level / replay** inside the configuration event to change its normal **Switch Scene** event. Each scene links to the next, and level eight links back to level one. GB Studio's Run Scene also uses that scene's own configuration.

Background art lives in assets/backgrounds/levels/level_01.png through level_08.png. Use GB Studio's Backgrounds view to open the images in an image editor, and Colorize to change tile palette assignments. These are manual-color assets: use only #e0f8cf, #86c06c, #306850, and #071821; scene palettes supply the displayed colors. Edits to scenery outside the six bottle footprints and interface rows appear in the ROM. The live board redraws those reserved regions for selection, pouring, and messages. Palette resources such as Moonlit Sky Background and Bottle Glass can be edited in GB Studio.

After changing the bottle dropdowns, the played level updates on your next build. The canvas background is a saved initial-board image, not a live evaluation of script events. To refresh its bottle illustration, save the project and run tools/sync_scene_previews.py with the prepared Python environment, or ask Codex to refresh the scene previews. That helper preserves scenery outside bottle footprints. Do not rerun create_editor_art.py or the original generate_assets.py/generate_themes.py bootstrap scripts over an edited project.

The Water Sort Puzzle scene type and configuration event are supplied by the included project-local extension in plugins/water-sort. The extension still implements the pouring rules in C, while levels, progression, scene artwork, and scene palettes are editable through native GB Studio resources. Keep the whole project folder together; no engine ejection is needed.

The genuine Color-only cartridge is build/water-sort.gbc. The official browser export is build/web.

## Validation

The C rule model checks capacity-limited pours, contiguous color transfer, mismatched colors, empty sources, full destinations, invalid indices, and win detection. The native PyBoy playtest solved all eight scene-based levels, compared each resulting bottle against the expected model after every pour, and checked undo, cancel, restart, empty-source rejection, full-target rejection, actual scene transitions, and final replay. GB Studio 4.3.2 was opened to verify all eight scene canvases, palettes, and the custom event's dropdown fields. Current evidence is in build/test-results.json, build/level-1.png through build/level-8.png, and build/screenshot.png. The older build/playtest.jsonl records the original prototype, rather than this scene-based revision.

Created using the ModRetro Chromatic plugin and the official GB Studio build pipeline. The extension uses GB Studio's documented custom scene type format: https://www.gbstudio.dev/docs/extending-gbstudio/plugins/

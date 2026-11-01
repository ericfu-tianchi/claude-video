# claude-video

When Claude Opus 5.5 came out I heard it was unusually good at making video **with code**, so I tried it on a few short films. No image or video generation models were used: every frame, the 3D, the motion, and the music were written as code by Claude, then rendered frame by frame.

| Film | Length | What it is |
|---|---|---|
| [Oura Ring 5 — Subtle Power](Oura%20Ring%20Film/) | 60 s | An Apple-style product film for the Oura Ring. The ring is rendered in 3D; one circle carries the whole film (ring → moon → a night of sleep). |
| [Claude眼中的上海 · Shanghai Stop-Motion](Shanghai%20Stop-Motion/) | 2:09 | A clay-and-paper stop-motion of Shanghai, built and animated in Blender with Python: 15 shots, 1,500 frames at 12 fps. |
| [Tianchi Fu · Showreel ’26](Showreel/) | 43 s | My personal showreel: 9 scenes, 2,580 frames at 60 fps, music synthesized in code. |
| [Apple Replica — Wonderful Tools](Apple%20Replica/) | 46 s | A study that rebuilds the grammar of Apple's "Give people wonderful tools" ad in code. |

Each folder has the film, a contact sheet, the source (`src/`), and most have a `幕后制作.html` page explaining how it was made (open it next to the video so the embedded player works).

**Full-quality masters** of the Shanghai film and the showreel are larger than GitHub allows in a repo; download them from [Releases](../../releases).

## Notes
- Rendered frames (`src/build`, `src/out`) are not committed; re-run the render scripts to regenerate them.
- The Oura film uses Apple's SF Pro font, which is not redistributable and is not included. Install it from Apple to re-render.
- The Apple Replica and the Oura film are non-commercial studies. Oura and Apple are trademarks of their owners; this project is not affiliated with either.

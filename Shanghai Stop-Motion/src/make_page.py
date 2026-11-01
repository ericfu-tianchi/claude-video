"""Builds 幕后制作.html: a one-page, plain-language walkthrough of how the film was made."""
import base64, io, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')


def jpg(path, w=640, crop=None):
    im = Image.open(path).convert('RGB')
    if crop: im = im.crop(crop)
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

S = {k: jpg(os.path.join(B, 'stills', f'{k}.png')) for k in ['desk', 'lane', 'bund', 'dusk', 'end', 'raw', 'graded']}

html = f'''<title>微缩上海幕后</title>
<style>
/* Layout: one narrow reading column; the pipeline is a single vertical track, chapters are a film strip. */
:root {{
  --bg: #15110e; --panel: #1e1915; --line: #3a3029; --fg: #efe6d8; --muted: #a8998a; --lamp: #e9a95b; --clay: #d97757;
  --serif: "Noto Serif SC", "Songti SC", "STSong", serif;
  --sans: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
  color-scheme: dark;
}}
html, body {{ background: var(--bg); color: var(--fg); }}
body {{ font: 15px/1.75 var(--sans); padding-inline: 20px; padding-block: 48px 72px; }}
.wrap {{ max-width: 760px; margin: 0 auto; display: flex; flex-direction: column; gap: 56px; }}
h1, h2 {{ font-family: var(--serif); font-weight: 600; text-wrap: balance; margin: 0; }}
h1 {{ font-size: clamp(30px, 6vw, 44px); line-height: 1.2; letter-spacing: .02em; }}
h2 {{ font-size: 22px; }}
p {{ margin: 0; }}
.eyebrow {{ font: 500 12px/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--lamp); }}
.lede {{ color: var(--muted); font-size: 16px; max-width: 34em; }}
header {{ display: flex; flex-direction: column; gap: 16px; }}
.hero {{ border-radius: 6px; overflow: hidden; border: 1px solid var(--line); }}
.hero img {{ display: block; width: 100%; height: auto; }}
.facts {{ display: flex; flex-wrap: wrap; gap: 10px 28px; font: 13px/1.4 var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }}
.facts b {{ color: var(--fg); font-weight: 500; }}
section {{ display: flex; flex-direction: column; gap: 20px; }}
.track {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }}
.step {{ display: grid; grid-template-columns: 44px 1fr; gap: 0 16px; }}
.rail {{ display: flex; flex-direction: column; align-items: center; }}
.dot {{ width: 30px; height: 30px; border-radius: 50%; border: 1px solid var(--lamp); color: var(--lamp);
        font: 500 13px/28px var(--mono); text-align: center; flex: none; }}
.step:last-child .stem {{ display: none; }}
.stem {{ width: 1px; flex: 1; background: var(--line); margin-block: 6px; }}
.body {{ padding-bottom: 28px; min-width: 0; display: flex; flex-direction: column; gap: 6px; }}
.body h3 {{ margin: 3px 0 0; font: 600 17px/1.4 var(--serif); }}
.body p {{ color: var(--muted); }}
.tag {{ align-self: flex-start; font: 12px/1 var(--mono); color: var(--fg); border: 1px solid var(--line); border-radius: 3px; padding: 5px 8px; }}
.loop {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 22px; display: flex; flex-direction: column; gap: 14px; }}
.cycle {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font: 14px/1.3 var(--sans); }}
.cycle span {{ border: 1px solid var(--lamp); color: var(--lamp); border-radius: 999px; padding: 6px 12px; }}
.cycle i {{ font-style: normal; color: var(--muted); }}
.loop ul {{ margin: 0; padding-left: 1.1em; color: var(--muted); display: flex; flex-direction: column; gap: 4px; }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
figure {{ margin: 0; display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
figure img {{ width: 100%; height: auto; display: block; border-radius: 4px; border: 1px solid var(--line); }}
figcaption {{ font: 12px/1.5 var(--mono); color: var(--muted); }}
.strip {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
.strip figcaption b {{ display: block; color: var(--fg); font: 600 14px/1.4 var(--serif); }}
.files {{ font: 13px/1.8 var(--mono); color: var(--muted); overflow-wrap: anywhere; }}
.files b {{ color: var(--fg); font-weight: 500; }}
@media (max-width: 620px) {{
  .strip {{ grid-template-columns: 1fr 1fr; }}
  .pair {{ grid-template-columns: 1fr; }}
}}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600&family=Noto+Sans+SC:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">

<div class="wrap">
  <header>
    <div class="eyebrow">幕后 · Behind the film</div>
    <h1>Claude 眼中的上海</h1>
    <p class="lede">一部 2 分钟的定格动画。没有用任何图像或视频生成模型：场景、灯光、动作、配乐和字幕，每一样都是 Claude 写代码做出来的。</p>
    <div class="hero"><img src="{S['dusk']}" alt="黄昏的陆家嘴，灯一盏一盏亮起来"></div>
    <div class="facts">
      <span><b>2:09</b> 时长</span><span><b>15</b> 个镜头</span><span><b>1,500</b> 帧逐帧渲染</span><span><b>12</b> 帧/秒 定格节奏</span><span><b>0</b> 个生成模型</span>
    </div>
  </header>

  <section>
    <h2>从一个想法到成片</h2>
    <ol class="track">
      <li class="step"><div class="rail"><div class="dot">1</div><div class="stem"></div></div><div class="body">
        <h3>写故事</h3>
        <p>先定视角：Claude 从没去过上海，只读过人们写下的它。于是它在书桌上，用这些句子搭一座小城。再拆成 4 章、15 个镜头，每个镜头配一句中英字幕。</p>
        <span class="tag">剧本 · 分镜表</span></div></li>
      <li class="step"><div class="rail"><div class="dot">2</div><div class="stem"></div></div><div class="body">
        <h3>用代码搭微缩场景</h3>
        <p>在 Blender 里用 Python 一块块“摆”出书桌、立体书、石库门弄堂、外滩和陆家嘴。材质模仿黏土、卡纸、毛毡和树脂水面；尺寸按真实微缩模型来，一栋弄堂房子约 17 厘米高，所以景深会像真的桌面拍摄一样虚化。</p>
        <span class="tag">Blender + Python</span></div></li>
      <li class="step"><div class="rail"><div class="dot">3</div><div class="stem"></div></div><div class="body">
        <h3>让它动起来</h3>
        <p>小角色的走路、跳跃、眨眼、回头，还有晾衣、蒸汽、轮渡、亮灯，都写成随时间变化的规则。画面按每秒 12 帧走，并故意加一点逐帧的轻微抖动和灯光闪烁，像手工一帧帧摆出来的。</p>
        <span class="tag">定格动画节奏</span></div></li>
      <li class="step"><div class="rail"><div class="dot">4</div><div class="stem"></div></div><div class="body">
        <h3>逐帧渲染</h3>
        <p>每一帧由电脑算出光线、阴影、反射和景深。在一台 M3 Pro 笔记本上本地完成，约 1,500 帧，每帧 3 到 7 秒。</p>
        <span class="tag">本地渲染 · 约 2 小时</span></div></li>
      <li class="step"><div class="rail"><div class="dot">5</div><div class="stem"></div></div><div class="body">
        <h3>作曲和音效</h3>
        <p>配乐同样由代码合成：八音盒、钢琴和弦乐铺底，随章节变化。音效贴着画面：台灯开关、纸片弹起、黏土小脚步、鸟叫、生煎滋滋声、轮渡汽笛。</p>
        <span class="tag">声音合成</span></div></li>
      <li class="step"><div class="rail"><div class="dot">6</div><div class="stem"></div></div><div class="body">
        <h3>剪辑、调色、字幕</h3>
        <p>把镜头接起来，章节之间用溶解转场；统一暖色调，加光晕、暗角和胶片颗粒；最后叠上中英字幕，和配乐合成 1080p 成片。</p>
        <span class="tag">剪辑 · 调色 · 合成</span></div></li>
    </ol>
  </section>

  <section>
    <h2>打磨：每个镜头至少过两轮</h2>
    <div class="loop">
      <div class="cycle"><span>渲一张小图</span><i>→</i><span>Claude 自己看图挑毛病</span><i>→</i><span>改代码</span><i>→</i><span>再渲</span></div>
      <ul>
        <li>镜头卡进了墙里、树冠里，画面一片模糊：挪机位。</li>
        <li>路人刚好站在主角位置，把它挡住：把路人请走。</li>
        <li>夜景窗户太亮，像填字游戏：调暗、调暖，减少亮灯的窗。</li>
        <li>河面和桌面重叠，水不见了：把水面抬高 2 毫米。</li>
      </ul>
    </div>
    <div class="pair">
      <figure><img src="{S['raw']}" alt="渲染出的原始画面"><figcaption>渲染原片</figcaption></figure>
      <figure><img src="{S['graded']}" alt="调色并加字幕后的画面"><figcaption>调色、光晕、颗粒、字幕之后</figcaption></figure>
    </div>
  </section>

  <section>
    <h2>四个章节</h2>
    <div class="strip">
      <figure><img src="{S['desk']}" alt="书桌上的立体书"><figcaption><b>书桌</b>立体书里弹出一座纸上海</figcaption></figure>
      <figure><img src="{S['lane']}" alt="清晨的石库门弄堂"><figcaption><b>清晨弄堂</b>晾衣、生煎、猫</figcaption></figure>
      <figure><img src="{S['bund']}" alt="外滩和黄浦江"><figcaption><b>外滩与江</b>老房子、渡轮、黄昏亮灯</figcaption></figure>
      <figure><img src="{S['end']}" alt="台灯熄灭后发光的纸城"><figcaption><b>回到书桌</b>台灯熄了，纸城还亮着</figcaption></figure>
    </div>
  </section>

  <section>
    <h2>文件在哪</h2>
    <div class="files">
      <div><b>成片</b>　Claude Video/Shanghai Stop-Motion/Claude眼中的上海.mp4</div>
      <div><b>源码</b>　Claude Video/Shanghai Stop-Motion/src/（场景 shots.py · 道具 props.py · 配乐 music.py · 后期 post.py）</div>
    </div>
  </section>
</div>
'''
open(os.path.join(ROOT, '幕后制作.html'), 'w').write(html)
print('ok', len(html) // 1024, 'KB')

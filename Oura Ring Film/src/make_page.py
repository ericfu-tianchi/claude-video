"""Builds ../幕后制作.html — a self-contained behind-the-scenes page (images embedded, video linked relatively)."""
import base64, io, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = sys.argv[1]   # folder with f_<t>.png stills, apple.png, sprite.png


def jpg(name, w=720, png=False):
    im = Image.open(os.path.join(SRC, name))
    if png:
        im.thumbnail((w, w)); buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
        return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    im = im.convert('RGB'); im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


CHAIN = [('0:02', '戒指随心跳出场', '2.0'), ('0:09', '戒指化作月亮，画出睡眠', '9.0'), ('0:11', '天亮前，月亮变成太阳', '11.4'),
         ('0:15', '每一拍写出一次心跳', '15.5'), ('0:21', '体温曲线收成一点', '21.8'), ('0:26', '在重拍上炸开成三个分数', '26.0'),
         ('0:37', '压力线卷成周期', '37.0'), ('0:41', '侧过来：2.28 mm', '41.6'),
         ('0:44', '每拍充一格电', '44.0'), ('0:49', '六种表面处理', '49.2'),
         ('0:53', '戒指变成句号', '53.8'), ('0:57', 'Oura Ring 5', '57.0')]

chain_html = '\n'.join(
    f'<figure><img src="{jpg("f_" + f + ".png", 480)}" alt="{c}" loading="lazy"><figcaption><span class="tc">{t}</span>{c}</figcaption></figure>'
    for t, c, f in CHAIN)

html = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Oura Ring 5 幕后</title>
<style>
/* Layout: one calm reading column, the film first; the morph chain is the only wide grid. */
:root {{
  --bg: #ecebee; --surface: #f6f5f7; --line: #d6d5da; --ink: #1d1d1f; --muted: #6e6e73;
  --accent: #b9772a;            /* the warm amber of the film's sun and temperature line */
  --sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  --display: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{ --bg: #141416; --surface: #1c1c1f; --line: #2e2e33; --ink: #f2f2f4; --muted: #9a9aa1; --accent: #e3a35a; color-scheme: dark; }}
}}
:root[data-theme="dark"] {{ --bg: #141416; --surface: #1c1c1f; --line: #2e2e33; --ink: #f2f2f4; --muted: #9a9aa1; --accent: #e3a35a; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--bg); color: var(--ink); }}
body {{ font: 16px/1.7 var(--sans); padding-inline: 20px; padding-block: 64px 96px; -webkit-font-smoothing: antialiased; }}
.wrap {{ max-width: 760px; margin: 0 auto; display: flex; flex-direction: column; gap: 88px; }}
h1, h2, h3 {{ font-family: var(--display); margin: 0; text-wrap: balance; }}
h1 {{ font-size: clamp(36px, 7vw, 56px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.08; }}
h2 {{ font-size: 28px; font-weight: 600; letter-spacing: -0.01em; }}
h3 {{ font-size: 18px; font-weight: 600; }}
p {{ margin: 0; }}
.eyebrow {{ font: 600 12px/1 var(--sans); letter-spacing: .22em; text-transform: uppercase; color: var(--accent); }}
.lede {{ font-size: 19px; color: var(--muted); max-width: 32em; }}
section, header {{ display: flex; flex-direction: column; gap: 24px; }}
.head {{ display: flex; flex-direction: column; gap: 10px; }}
video, .media img {{ width: 100%; height: auto; display: block; border-radius: 10px; background: #000; }}
.note {{ font-size: 13px; color: var(--muted); }}
.facts {{ display: flex; flex-wrap: wrap; gap: 12px 36px; padding-top: 8px; border-top: 1px solid var(--line); }}
.facts div {{ display: flex; flex-direction: column; }}
.facts b {{ font: 300 30px/1.2 var(--display); letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }}
.facts span {{ font-size: 13px; color: var(--muted); }}
.pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
figure {{ margin: 0; display: flex; flex-direction: column; gap: 8px; min-width: 0; }}
figure img {{ width: 100%; height: auto; display: block; border-radius: 8px; border: 1px solid var(--line); }}
figcaption {{ font-size: 13px; color: var(--muted); line-height: 1.5; }}
.rules {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }}
.rules li {{ background: var(--surface); padding: 18px 20px; display: flex; flex-direction: column; gap: 4px; }}
.rules li b {{ font-weight: 600; }}
.rules li span {{ color: var(--muted); font-size: 14px; }}
.steps {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }}
.steps li {{ display: grid; grid-template-columns: 48px 1fr; gap: 0 12px; padding: 22px 0; border-top: 1px solid var(--line); }}
.steps li:last-child {{ border-bottom: 1px solid var(--line); }}
.n {{ font: 300 28px/1 var(--display); color: var(--accent); font-variant-numeric: tabular-nums; }}
.steps .body {{ display: flex; flex-direction: column; gap: 6px; min-width: 0; }}
.steps p {{ color: var(--muted); }}
.chain {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 18px 14px; }}
.tc {{ display: block; font: 500 12px/1.6 var(--mono); color: var(--accent); }}
.tools {{ display: flex; flex-direction: column; }}
.tools div {{ display: grid; grid-template-columns: 180px 1fr; gap: 16px; padding: 14px 0; border-top: 1px solid var(--line); }}
.tools div:last-child {{ border-bottom: 1px solid var(--line); }}
.tools b {{ font-weight: 600; }}
.tools span {{ color: var(--muted); }}
.log {{ display: flex; flex-direction: column; }}
.log div {{ display: grid; grid-template-columns: 56px 1fr; gap: 12px; padding: 12px 0; border-top: 1px solid var(--line); }}
.log div:last-child {{ border-bottom: 1px solid var(--line); }}
.log code {{ font: 500 14px/1.7 var(--mono); color: var(--accent); }}
.log span {{ color: var(--muted); }}
.log b {{ color: var(--ink); font-weight: 600; }}
.sprite {{ display: grid; grid-template-columns: 200px 1fr; gap: 24px; align-items: center; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 20px; }}
.sprite img {{ width: 100%; height: auto; display: block; }}
.sprite p {{ color: var(--muted); font-size: 15px; }}
footer {{ font-size: 13px; color: var(--muted); }}
@media (max-width: 620px) {{
  .pair, .rules {{ grid-template-columns: 1fr; }}
  .tools div {{ grid-template-columns: 1fr; gap: 2px; }}
  .sprite {{ grid-template-columns: 1fr; }}
  .sprite img {{ max-width: 200px; }}
}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="head">
    <div class="eyebrow">幕后 · Behind the film</div>
    <h1>Oura Ring 5<br>Subtle. Power.</h1>
  </div>
  <p class="lede">一支 60 秒的苹果风格产品片。没有用任何图像或视频生成模型：画面、3D 戒指和配乐，全部由 Claude 写代码做出来。</p>
  <div class="media">
    <video src="Oura Ring 5 — Subtle Power.mp4" controls playsinline preload="metadata" poster="{jpg('f_57.0.png', 1280)}"></video>
  </div>
  <p class="note">视频需要和本页放在同一个文件夹里才能播放。</p>
  <div class="facts">
    <div><b>60 s</b><span>时长</span></div>
    <div><b>1080p · 60 fps</b><span>画质</span></div>
    <div><b>96 BPM</b><span>全片节拍</span></div>
    <div><b>6</b><span>版迭代</span></div>
    <div><b>0</b><span>个生成模型</span></div>
  </div>
</header>

<section>
  <div class="head"><div class="eyebrow">01 · 参考</div><h2>从一支苹果广告学语法</h2></div>
  <p>参考的是苹果那支 “Give people wonderful tools” 广告。我逐帧拆了它，没有照抄任何画面，只学它的四条规则；产品信息则全部来自 Oura 官网。</p>
  <div class="pair">
    <figure><img src="{jpg('apple.png', 720)}" alt="苹果广告中的指纹画面"><figcaption>苹果广告：一个产品的标志性细节，变形成下一个</figcaption></figure>
    <figure><img src="{jpg('f_9.0.png', 720)}" alt="Oura 片中的睡眠阶段画面"><figcaption>Oura 片：戒指变成月亮，再画出一整夜的睡眠</figcaption></figure>
  </div>
  <ul class="rules">
    <li><b>一个形状贯穿全片</b><span>苹果用产品轮廓，这里用的是戒指这个圆</span></li>
    <li><b>上一个变成下一个</b><span>不切镜头，每个功能都从上一个画面长出来</span></li>
    <li><b>动作落在节拍上</b><span>每一次变形都踩在音乐的鼓点或重拍上</span></li>
    <li><b>最后只留一句话</b><span>收尾用 Oura 官网自己的口号 “Subtle. Power.”</span></li>
  </ul>
</section>

<section>
  <div class="head"><div class="eyebrow">02 · 做法</div><h2>六步，从一首曲子开始</h2></div>
  <ol class="steps">
    <li><div class="n">1</div><div class="body"><h3>查清楚产品</h3><p>读 Oura 官网和评测：Ring 5 有哪些功能、真实参数（2.28 mm、6–9 天续航、100 米防水、六种表面处理），以及哪些话不能说，比如它不是医疗设备、没有屏幕。</p></div></li>
    <li><div class="n">2</div><div class="body"><h3>先写音乐，再排画面</h3><p>用代码合成配乐，定在每分钟 96 拍。整片的时间轴按拍子切好：哪一拍出月亮、哪个重拍炸开分数，都提前写进节拍表。</p></div></li>
    <li><div class="n">3</div><div class="body"><h3>用代码画出变形链</h3><p>每个画面都是一段“随时间变化”的绘图程序：线怎么卷成圆、点怎么炸开、月亮怎么在天亮前变成太阳。程序按节拍表驱动，所以画面和音乐天然同步。</p></div></li>
    <li><div class="n">4</div><div class="body"><h3>在 Blender 里做 3D 戒指</h3><p>按官方尺寸建模，内圈带三颗传感器凸点，打上影棚光渲染钛金属质感。</p></div></li>
    <li><div class="n">5</div><div class="body"><h3>逐帧渲染、合成</h3><p>用浏览器把 3,600 帧一帧帧画出来，每帧叠 4 个瞬间做运动模糊，再和配乐合成 1080p 成片。</p></div></li>
    <li><div class="n">6</div><div class="body"><h3>审片、修改、再审</h3><p>每一版都渲染成缩略图逐秒检查，再用程序测量画面动作和音乐重拍的时间差。人看完提意见，再改下一版。</p></div></li>
  </ol>
  <div class="sprite">
    <img src="{jpg('sprite.png', 400, png=True)}" alt="Blender 渲染的 Oura Ring 5 钛金属戒指">
    <p><b style="color:var(--ink)">3D 戒指是怎么放进 2D 片子里的？</b><br>戒指每转 1 度，就在 Blender 里渲染一张透明底的图：银色 181 张，其余五种颜色各 71 张。片子里戒指转到哪个角度，就取那一张，相邻两张之间再做平滑过渡，所以转起来是连续的。</p>
  </div>
</section>

<section>
  <div class="head"><div class="eyebrow">03 · 变形链</div><h2>一个圆，讲完一整天</h2></div>
  <div class="chain">
{chain_html}
  </div>
</section>

<section>
  <div class="head"><div class="eyebrow">04 · 工具</div><h2>用到的工具</h2></div>
  <div class="tools">
    <div><b>Claude Code</b><span>写全部代码：画面、动画、建模脚本、作曲、审片程序</span></div>
    <div><b>Blender</b><span>建模并渲染 3D 钛金属戒指，六种表面处理</span></div>
    <div><b>浏览器 Canvas</b><span>用 JavaScript 逐帧绘制所有 2D 图形和文字</span></div>
    <div><b>Playwright</b><span>自动打开浏览器，一帧帧截取画面</span></div>
    <div><b>Python（NumPy / SciPy）</b><span>从零合成配乐：鼓、贝斯、和弦、旋律、音效</span></div>
    <div><b>FFmpeg</b><span>把画面帧和音乐合成为 MP4，并生成审片缩略图</span></div>
    <div><b>SF Pro</b><span>苹果的系统字体，用于全片文字</span></div>
  </div>
</section>

<section>
  <div class="head"><div class="eyebrow">05 · 迭代</div><h2>六个版本，每版改了什么</h2></div>
  <div class="log">
    <div><code>v1</code><span><b>跑通整条变形链。</b>扁平图形，配轻氛围音乐。</span></div>
    <div><code>v2</code><span><b>换上节奏更强的配乐</b>，让每个变形都踩在节拍上，加运动模糊。</span></div>
    <div><code>v3</code><span><b>戒指换成 Blender 渲染的 3D 版本。</b></span></div>
    <div><code>v4</code><span><b>改字体和排版</b>，换成真正的 SF Pro；去掉不必要的随拍抖动，修好戒指转动卡顿。</span></div>
    <div><code>v5</code><span><b>月亮在天亮前就变成太阳</b>；去掉放射线；理顺太阳到心跳的衔接。</span></div>
    <div><code>v6</code><span><b>温度曲线多停一会儿</b>，再收成一点，在重拍上炸开。定稿。</span></div>
  </div>
</section>

<footer>Oura 和 Oura Ring 是 ŌURA 的商标。本片为个人学习作品，非官方广告；片中参数来自 Oura 官网公开信息。</footer>

</div>
</body>
</html>
'''
out = os.path.join(ROOT, '幕后制作.html')
open(out, 'w').write(html)
print('wrote', out, len(html) // 1024, 'KB')

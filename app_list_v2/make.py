"""Render 四個 app images in the app_list style.
Background is rebuilt from an old app_list image (same colors), icons from icons/<slug>.png.
Usage: python3 make.py  -> writes app_list_v2/<id>.jpg for every entry in POSTS."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, '..', 'app_list')
W, H = 1800, 680
CENTERS = [285, 695, 1105, 1515]
TOP, SIZE, RAD = 174, 250, 56
LATIN = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', 40)
CJK = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 40)


def background(old_id, seed):
    a = np.asarray(Image.open(f'{OLD}/{old_id}.jpg').convert('RGB')).astype(float)
    top = a[20:130].mean(0)          # rows above icons, per column
    bot = a[560:660].mean(0)         # rows below labels
    t = np.linspace(0, 1, H)[:, None, None]
    grad = top[None] * (1 - t) + bot[None] * t
    img = Image.fromarray(grad.clip(0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(40))
    rng = np.random.default_rng(seed)
    g = np.asarray(img).astype(float) + rng.normal(0, 5, (H, W, 1))
    img = Image.fromarray(g.clip(0, 255).astype('uint8'))
    # soft snow dots like the originals
    dots = Image.new('L', (W, H), 0); d = ImageDraw.Draw(dots)
    r = random.Random(seed)
    for _ in range(45):
        x, y, s = r.randint(0, W), r.randint(0, H), r.choice([4, 5, 6, 8, 14, 22])
        d.ellipse((x - s, y - s, x + s, y + s), fill=r.randint(60, 150) if s < 10 else r.randint(25, 45))
    dots = dots.filter(ImageFilter.GaussianBlur(2))
    white = Image.new('RGB', (W, H), 'white')
    return Image.composite(white, img, dots)


def rounded_mask(size, rad):
    m = Image.new('L', (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), rad * 4, fill=255)
    return m.resize((size, size), Image.LANCZOS)


def text_w(s):
    return sum((CJK if ord(ch) > 0x2E80 else LATIN).getlength(ch) for ch in s)


def draw_label(img, cx, y, s):
    sh = Image.new('L', img.size, 0); ds = ImageDraw.Draw(sh)
    x = cx - text_w(s) / 2
    for pass_ in ('shadow', 'text'):
        xx = x
        for ch in s:
            f = CJK if ord(ch) > 0x2E80 else LATIN
            if pass_ == 'shadow':
                ds.text((xx, y + 2), ch, font=f, fill=110)
            else:
                ImageDraw.Draw(img).text((xx, y), ch, font=f, fill=(255, 255, 255))
            xx += f.getlength(ch)
        if pass_ == 'shadow':
            sh = sh.filter(ImageFilter.GaussianBlur(4))
            img.paste((40, 30, 40), (0, 0), sh)


def render(out, old_id, apps, seed=1):
    img = background(old_id, seed)
    mask = rounded_mask(SIZE, RAD)
    shadow = Image.new('L', (W, H), 0)
    centers = CENTERS if len(apps) == 4 else [390, 900, 1410]
    for cx in centers:
        shadow.paste(mask, (cx - SIZE // 2, TOP + 8))
    img.paste((30, 20, 30), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 0.35))
    for cx, (slug, label) in zip(centers, apps):
        ic = Image.open(f'{HERE}/icons/{slug}.png').convert('RGBA')
        x0 = cx - SIZE // 2
        if slug == 'okie':   # crop keeps the LINE badge: 275x276 from the icon's top-left
            badge = Image.new('L', ic.size, 0)
            badge.paste(mask, (0, 0))
            ImageDraw.Draw(badge).ellipse((205, 185, 272, 252), fill=255)
            badge = badge.filter(ImageFilter.GaussianBlur(0.8))
            img.paste(ic.convert('RGB'), (x0, TOP), badge)
        else:
            ic = ic.resize((SIZE, SIZE), Image.LANCZOS)
            img.paste(ic.convert('RGB'), (x0, TOP), mask)
        draw_label(img, cx, TOP + SIZE + 30, label)
    img.save(out, quality=92)


POSTS = {}
if __name__ == '__main__':
    import posts
    for pid, (old_id, apps) in posts.POSTS.items():
        render(f'{HERE}/{pid}.jpg', old_id, apps, seed=sum(map(ord, pid)))
        print('wrote', pid)

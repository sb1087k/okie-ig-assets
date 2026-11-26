"""Bigger, sharper 四個 app images (Paul 11/26: icons too small; reference = his iPhone home-screen crop).
Changes vs app_list_v2/make.py: 1024px App Store icons instead of 250px, icon 330px (18% of width, was 250 / 14%),
tighter canvas 1800x600 (was 680), iOS-style labels (SF + PingFang) at 52px (was 40), no snow dots.
Optional jiggle-mode minus badges like the reference (--jiggle).
Usage: python3 make_big.py OUTDIR [--jiggle] [IDS...]"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "app_list_v2"))
import posts  # noqa: E402

OLD = os.path.join(HERE, "app_list")
HI = os.path.join(HERE, "hires")
OKIE = "/Users/paul/okie-social/okie_icon/final3/okie_icon_badge_full.png"
W, H = 1800, 600
SIZE = 330
RAD = round(SIZE * 0.2237)
PITCH = 430
TOP = 92
LAB = 50
LATIN = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", LAB)
CJK = ImageFont.truetype(
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc",
    LAB, index=2)  # PingFang TC Regular
try:
    LATIN.set_variation_by_name("Medium")
except Exception:
    pass
SLUG_ID = {
    "ecbo": 1443707795, "safetytips": 858357174, "wamazing": 1181315839, "go": 1254341709,
    "tabelog": 6752922875, "payke": 1040452788, "uber": 368677368, "bounce": 1444570755, "airalo": 1475911720,
    "klook": 961850126, "flighty": 1358823008, "polarsteps": 947925763, "what3words": 657878530,
    "organicmaps": 1567437057, "wowpass": 1626691440, "namane": 1533784467, "creatrip": 1221245620,
    "funliday": 905768387, "splitwise": 458023433, "timetree": 952578473, "citymapper": 469463298,
    "navermap": 311867728, "googlemaps": 585027354, "perplexity": 1668000334, "gemininotebook": 6737527615,
    "wanderlog": 1476732439, "welcomesuica": 6738336566, "googletranslate": 414706506, "voicetra": 581137577,
    "papago": 1147874819, "mstranslator": 1018949559, "mofa": 511243885, "findmy": 1514844621,
    "thim": 6759272559, "muvmi": 1410088538, "bolt": 675033630, "grab": 647268330, "trainline": 334235181,
    "flixbus": 778437357, "kride": 6474654222, "catchtable": 1639046576,
}


def background(old_id, seed):
    """Same colours as the old app_list image (top and bottom bands), smooth, light grain, no dots."""
    src = Image.open(f"{OLD}/{old_id}.jpg").convert("RGB")
    top = src.crop((0, 20, src.width, 130)).resize((W, 1), Image.BOX)
    bot = src.crop((0, 560, src.width, 660)).resize((W, 1), Image.BOX)
    grad = Image.new("RGB", (W, H))
    for y in range(H):
        grad.paste(Image.blend(top, bot, y / (H - 1)), (0, y))
    grad = grad.filter(ImageFilter.GaussianBlur(40))
    noise = Image.effect_noise((W, H), 12).convert("RGB")
    return Image.blend(grad, noise, 0.04)


def mask(size):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), RAD * 4, fill=255)
    return m.resize((size, size), Image.LANCZOS)


def font(ch):
    return CJK if ord(ch) > 0x2E80 else LATIN


def text_w(s):
    return sum(font(ch).getlength(ch) for ch in s)


def label(img, cx, y, s):
    x0 = cx - text_w(s) / 2
    sh = Image.new("L", img.size, 0)
    ds, dt = ImageDraw.Draw(sh), ImageDraw.Draw(img)
    x = x0
    for ch in s:
        ds.text((x, y + 2), ch, font=font(ch), fill=120)
        x += font(ch).getlength(ch)
    img.paste((30, 22, 30), (0, 0), sh.filter(ImageFilter.GaussianBlur(5)))
    x = x0
    for ch in s:
        dt.text((x, y), ch, font=font(ch), fill=(255, 255, 255))
        x += font(ch).getlength(ch)


def minus_badge(img, x, y):
    r = 46
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 185, 160, 235))
    d.rounded_rectangle((x - 22, y - 4, x + 22, y + 4), 4, fill=(20, 20, 20, 255))
    img.paste(layer, (0, 0), layer)


def render(out, old_id, apps, seed=1, jiggle=False):
    img = background(old_id, seed)
    m = mask(SIZE)
    n = len(apps)
    centers = [W / 2 + (i - (n - 1) / 2) * PITCH for i in range(n)]
    shadow = Image.new("L", (W, H), 0)
    for cx in centers:
        shadow.paste(m, (round(cx - SIZE / 2), TOP + 10))
    img.paste((30, 20, 30), (0, 0), shadow.filter(ImageFilter.GaussianBlur(18)).point(lambda v: v * 0.28))
    for cx, (slug, name) in zip(centers, apps):
        x0 = round(cx - SIZE / 2)
        if slug == "okie":  # 1187px file: the icon square is 0..1023, the LINE badge hangs off the corner
            ic = Image.open(OKIE).convert("RGBA")
            s = round(ic.width * SIZE / 1024)
            ic = ic.resize((s, s), Image.LANCZOS)
            img.paste(ic, (x0, TOP), ic)
        else:
            ic = Image.open(f"{HI}/{SLUG_ID[slug]}.png").convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
            img.paste(ic, (x0, TOP), m)
        if jiggle:
            minus_badge(img, x0 + 18, TOP + 18)
        label(img, cx, TOP + SIZE + 26, name)
    img.save(out, quality=94)


if __name__ == "__main__":
    out = sys.argv[1]
    jig = "--jiggle" in sys.argv
    ids = [a for a in sys.argv[2:] if not a.startswith("--")] or list(posts.POSTS)
    os.makedirs(out, exist_ok=True)
    for pid in ids:
        old_id, apps = posts.POSTS[pid]
        render(f"{out}/{pid}.jpg", old_id, apps, seed=sum(map(ord, pid)), jiggle=jig)
        print("wrote", pid)

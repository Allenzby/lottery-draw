# -*- coding: utf-8 -*-
"""生成 icon.ico（多尺寸）与窗口用 icon.png"""
import base64
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SIZES = [16, 24, 32, 48, 64, 128, 256]
FONT = r"C:\Windows\Fonts\arialbd.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render(size):
    s = 8  # 超采样，保证小尺寸也圆滑
    S = size * s
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 蓝色渐变圆角方块背景
    top, bottom = (84, 130, 255), (29, 63, 208)
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        gd.line([(0, y), (S, y)], fill=lerp(top, bottom, y / (S - 1)) + (255,))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1],
                                           radius=int(S * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    # 2. 白色号球
    cx, cy = S / 2, S / 2
    r = S * 0.335
    # 球下方投影
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - r, cy - r + S * 0.045,
                                cx + r, cy + r + S * 0.045],
                               fill=(10, 25, 80, 90))
    img.alpha_composite(sh)
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255),
                 outline=(214, 226, 255, 255), width=max(1, int(S * 0.012)))
    # 球面高光
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([cx - r * 0.72, cy - r * 0.78,
                                cx + r * 0.28, cy - r * 0.12],
                               fill=(255, 255, 255, 110))
    img.alpha_composite(hl)
    draw = ImageDraw.Draw(img)

    # 3. 球上的数字 8（蓝色）
    font = ImageFont.truetype(FONT, int(r * 1.18))
    draw.text((cx, cy), "8", font=font, fill=(47, 84, 235, 255), anchor="mm")

    # 4. 右上角红色小圆点（点缀，增加辨识度）
    dr = S * 0.10
    dx, dy = S * 0.79, S * 0.20
    draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr],
                 fill=(239, 68, 68, 255), outline=(255, 255, 255, 255),
                 width=max(1, int(S * 0.022)))

    return img.resize((size, size), Image.LANCZOS)


def inject_into_app(b64):
    """把窗口图标的 base64 数据写进 app.py 的占位符"""
    app_path = os.path.join(OUT_DIR, "app.py")
    with open(app_path, "r", encoding="utf-8") as f:
        src = f.read()
    marker = 'ICON_PNG_B64 = "'
    i = src.find(marker)
    if i < 0:
        print("app.py 中未找到占位符，跳过注入")
        return
    j = src.find('"', i + len(marker))
    src = src[:i + len(marker)] + b64 + src[j:]
    with open(app_path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("已注入 app.py")


def render_android(size):
    """安卓启动图标：留一点内边距，避免被启动器裁切"""
    inner = int(round(size * 0.88))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    art = render(inner)
    off = (size - inner) // 2
    canvas.paste(art, (off, off), art)
    return canvas


def write_android_icons():
    """生成 android/res/mipmap-*/ic_launcher.png"""
    sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    base = os.path.join(OUT_DIR, "android", "res")
    if not os.path.isdir(base):
        print("未找到 android/res，跳过安卓图标")
        return
    for dpi, px in sizes.items():
        folder = os.path.join(base, "mipmap-" + dpi)
        os.makedirs(folder, exist_ok=True)
        render_android(px).save(os.path.join(folder, "ic_launcher.png"))
    print("已生成安卓图标（5 个密度）")


def main():
    images = [render(s) for s in SIZES]
    ico_path = os.path.join(OUT_DIR, "icon.ico")
    images[-1].save(ico_path, format="ICO",
                    sizes=[(s, s) for s in SIZES])
    print("ico:", ico_path)

    png_path = os.path.join(OUT_DIR, "icon.png")
    render(64).save(png_path, format="PNG")
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    print("png base64 length:", len(b64))
    inject_into_app(b64)
    write_android_icons()


if __name__ == "__main__":
    main()

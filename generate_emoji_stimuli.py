"""
生成 CFF 范式用 emoji 刺激图片
- 黄色背景
- 线条为红绿相间（静态帧）或纯红/纯绿（闪烁帧）
- 三种表情：开心、中性、难过
"""

import os
import math
from PIL import Image, ImageDraw

# ── 参数 ──────────────────────────────────────────────
SIZE = 512
BG_COLOR = (255, 255, 0)       # 黄色背景
RED = (255, 0, 0)
GREEN = (0, 200, 0)
LINE_W = 8
OUT_DIR = os.path.join(os.path.dirname(__file__), "stimuli")
os.makedirs(OUT_DIR, exist_ok=True)

CX, CY = SIZE // 2, SIZE // 2
FACE_R = 180
EYE_Y = CY - 50
EYE_X_OFF = 55
EYE_R = 22
MOUTH_Y = CY + 60


def _draw_face_outline(draw, color_fn):
    """绘制面部轮廓（红绿相间）"""
    n_segments = 72
    for i in range(n_segments):
        a1 = 2 * math.pi * i / n_segments
        a2 = 2 * math.pi * (i + 1) / n_segments
        c = color_fn(i)
        x1 = CX + FACE_R * math.cos(a1)
        y1 = CY + FACE_R * math.sin(a1)
        x2 = CX + FACE_R * math.cos(a2)
        y2 = CY + FACE_R * math.sin(a2)
        draw.line([(x1, y1), (x2, y2)], fill=c, width=LINE_W)


def _draw_eyes(draw, color_fn, start_idx=0):
    """绘制双眼（红绿相间）"""
    for side, ex in enumerate([CX - EYE_X_OFF, CX + EYE_X_OFF]):
        n = 24
        for i in range(n):
            a1 = 2 * math.pi * i / n
            a2 = 2 * math.pi * (i + 1) / n
            idx = start_idx + side * n + i
            c = color_fn(idx)
            x1 = ex + EYE_R * math.cos(a1)
            y1 = EYE_Y + EYE_R * math.sin(a1)
            x2 = ex + EYE_R * math.cos(a2)
            y2 = EYE_Y + EYE_R * math.sin(a2)
            draw.line([(x1, y1), (x2, y2)], fill=c, width=LINE_W)


def _draw_arc_mouth(draw, color_fn, start_angle, end_angle, start_idx=0):
    """绘制弧形嘴巴（红绿相间）"""
    mouth_r = 80
    n = 36
    for i in range(n):
        t1 = start_angle + (end_angle - start_angle) * i / n
        t2 = start_angle + (end_angle - start_angle) * (i + 1) / n
        c = color_fn(start_idx + i)
        x1 = CX + mouth_r * math.cos(t1)
        y1 = MOUTH_Y + mouth_r * math.sin(t1)
        x2 = CX + mouth_r * math.cos(t2)
        y2 = MOUTH_Y + mouth_r * math.sin(t2)
        draw.line([(x1, y1), (x2, y2)], fill=c, width=LINE_W)


def _draw_line_mouth(draw, color_fn, start_idx=0):
    """绘制直线嘴巴（中性表情）"""
    half = 70
    n = 20
    for i in range(n):
        t1 = -half + 2 * half * i / n
        t2 = -half + 2 * half * (i + 1) / n
        c = color_fn(start_idx + i)
        draw.line([(CX + t1, MOUTH_Y), (CX + t2, MOUTH_Y)], fill=c, width=LINE_W)


def _alt_color(idx):
    """红绿相间着色函数"""
    return RED if idx % 2 == 0 else GREEN


def _solid_color(color):
    """纯色着色函数"""
    def fn(idx):
        return color
    return fn


def draw_emoji(emotion, color_mode="alternate"):
    """
    绘制 emoji
    emotion: 'happy' | 'neutral' | 'sad'
    color_mode: 'alternate' | 'red' | 'green'
    """
    img = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)

    if color_mode == "alternate":
        cf = _alt_color
    elif color_mode == "red":
        cf = _solid_color(RED)
    else:
        cf = _solid_color(GREEN)

    _draw_face_outline(draw, cf)
    _draw_eyes(draw, cf, start_idx=72)

    if emotion == "happy":
        # 微笑弧（下半圆）
        _draw_arc_mouth(draw, cf, math.pi * 0.15, math.pi * 0.85, start_idx=120)
    elif emotion == "neutral":
        _draw_line_mouth(draw, cf, start_idx=120)
    elif emotion == "sad":
        # 皱眉弧（上半圆）
        _draw_arc_mouth(draw, cf, math.pi * 1.15, math.pi * 1.85, start_idx=120)

    return img


def main():
    emotions = ["happy", "neutral", "sad"]
    labels = {"happy": "开心", "neutral": "中性", "sad": "难过"}

    print("生成 CFF emoji 刺激图片 …")
    for emo in emotions:
        # 红绿相间静态图
        img_alt = draw_emoji(emo, "alternate")
        path_alt = os.path.join(OUT_DIR, f"{emo}_alternate.png")
        img_alt.save(path_alt)
        print(f"  [{labels[emo]}] 红绿相间 → {path_alt}")

        # CFF 闪烁用：纯红帧 / 纯绿帧
        for mode in ("red", "green"):
            img = draw_emoji(emo, mode)
            path = os.path.join(OUT_DIR, f"{emo}_{mode}.png")
            img.save(path)
            print(f"  [{labels[emo]}] {mode} 帧 → {path}")

    # 生成预览拼图
    preview = Image.new("RGB", (SIZE * 3, SIZE * 2), (200, 200, 200))
    for col, emo in enumerate(emotions):
        preview.paste(draw_emoji(emo, "alternate"), (col * SIZE, 0))
        preview.paste(draw_emoji(emo, "red"), (col * SIZE, SIZE))
    preview.save(os.path.join(OUT_DIR, "preview.png"))
    print(f"\n预览图 → {os.path.join(OUT_DIR, 'preview.png')}")
    print("完成！")


if __name__ == "__main__":
    main()

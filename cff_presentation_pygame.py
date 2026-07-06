"""
CFF 无意识表情呈现范式 — Pygame 轻量版
无需 PsychoPy，仅需 pygame + pillow

用法:
    python cff_presentation_pygame.py
    python cff_presentation_pygame.py --emotion sad --hz 55
    python cff_presentation_pygame.py --demo
"""

import os
import sys
import argparse
import pygame

STIM_DIR = os.path.join(os.path.dirname(__file__), "stimuli")
EMOTIONS = ["happy", "neutral", "sad"]
EMOTION_LABELS = {"happy": "开心", "neutral": "中性", "sad": "难过"}
BG_COLOR = (255, 255, 0)   # 黄色
WIN_SIZE = 800
STIM_SIZE = 512


def load_stimuli(emotion):
    red = pygame.image.load(os.path.join(STIM_DIR, f"{emotion}_red.png"))
    green = pygame.image.load(os.path.join(STIM_DIR, f"{emotion}_green.png"))
    red = pygame.transform.scale(red, (STIM_SIZE, STIM_SIZE))
    green = pygame.transform.scale(green, (STIM_SIZE, STIM_SIZE))
    return red, green


def draw_fixation(screen, font):
    txt = font.render("+", True, (0, 0, 0))
    screen.blit(txt, (WIN_SIZE // 2 - txt.get_width() // 2,
                      WIN_SIZE // 2 - txt.get_height() // 2))


def run_cff(emotion="happy", flicker_hz=50.0, duration_sec=2.0,
            isi_sec=1.0, n_trials=3):
    pygame.init()
    screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
    pygame.display.set_caption(
        f"CFF 范式 — {EMOTION_LABELS[emotion]} @ {flicker_hz} Hz"
    )
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 48)

    red_img, green_img = load_stimuli(emotion)
    offset = (WIN_SIZE - STIM_SIZE) // 2

    print(f"按 SPACE 开始 | Q 退出 | 表情: {EMOTION_LABELS[emotion]} | {flicker_hz} Hz")

    # 等待空格
    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    waiting = False
                elif ev.key == pygame.K_q:
                    pygame.quit()
                    return
        screen.fill(BG_COLOR)
        hint = pygame.font.SysFont("Arial", 20).render(
            "按 SPACE 开始，按 Q 退出", True, (0, 0, 0))
        screen.blit(hint, (WIN_SIZE // 2 - hint.get_width() // 2, WIN_SIZE - 40))
        draw_fixation(screen, font)
        pygame.display.flip()

    frame_ms = 1000.0 / flicker_hz  # 每帧毫秒

    for trial in range(n_trials):
        # ISI 固定点
        t_end = pygame.time.get_ticks() + int(isi_sec * 1000)
        while pygame.time.get_ticks() < t_end:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_q):
                    pygame.quit()
                    return
            screen.fill(BG_COLOR)
            draw_fixation(screen, font)
            pygame.display.flip()

        # CFF 闪烁
        t_start = pygame.time.get_ticks()
        t_end = t_start + int(duration_sec * 1000)
        frame_idx = 0
        while pygame.time.get_ticks() < t_end:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_q):
                    pygame.quit()
                    return

            screen.fill(BG_COLOR)
            img = red_img if frame_idx % 2 == 0 else green_img
            screen.blit(img, (offset, offset))
            pygame.display.flip()

            frame_idx += 1
            clock.tick(flicker_hz)

        print(f"  试次 {trial + 1}/{n_trials} 完成 ({frame_idx} 帧)")

    pygame.quit()
    print("呈现结束。")


def run_demo(flicker_hz=50.0, duration_sec=2.0, isi_sec=1.5):
    for emo in EMOTIONS:
        print(f"\n>>> {EMOTION_LABELS[emo]}")
        run_cff(emo, flicker_hz, duration_sec, isi_sec, n_trials=1)


def main():
    parser = argparse.ArgumentParser(description="CFF 范式 (Pygame 版)")
    parser.add_argument("--emotion", choices=EMOTIONS, default="happy")
    parser.add_argument("--hz", type=float, default=50.0)
    parser.add_argument("--duration", type=float, default=2.0)
    parser.add_argument("--isi", type=float, default=1.0)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    stim_missing = not os.path.exists(
        os.path.join(STIM_DIR, f"{args.emotion}_red.png"))
    if stim_missing:
        print("刺激文件不存在，正在生成 …")
        import generate_emoji_stimuli
        generate_emoji_stimuli.main()

    if args.demo:
        run_demo(args.hz, args.duration, args.isi)
    else:
        run_cff(args.emotion, args.hz, args.duration, args.isi, args.trials)


if __name__ == "__main__":
    main()

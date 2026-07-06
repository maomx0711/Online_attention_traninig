"""
CFF 无意识表情呈现范式
利用红绿线条在黄色背景上快速交替闪烁，使 emoji 在意识层面"消失"，
实现阈下（无意识）情绪刺激呈现。

依赖: psychopy, pillow
"""

import os
import sys
import argparse

try:
    from psychopy import visual, core, event, data, gui
    import numpy as np
except ImportError:
    print("请先安装依赖: pip install psychopy numpy pillow")
    sys.exit(1)

STIM_DIR = os.path.join(os.path.dirname(__file__), "stimuli")
EMOTIONS = ["happy", "neutral", "sad"]
EMOTION_LABELS = {"happy": "开心", "neutral": "中性", "sad": "难过"}


def check_stimuli():
    """确保刺激文件存在"""
    missing = []
    for emo in EMOTIONS:
        for color in ("red", "green"):
            p = os.path.join(STIM_DIR, f"{emo}_{color}.png")
            if not os.path.exists(p):
                missing.append(p)
    if missing:
        print("缺少刺激文件，正在生成 …")
        import generate_emoji_stimuli
        generate_emoji_stimuli.main()


def run_cff(
    emotion="happy",
    flicker_hz=50.0,
    duration_sec=2.0,
    isi_sec=1.0,
    n_trials=3,
    fullscreen=False,
):
    """
    运行 CFF 呈现

    Parameters
    ----------
    emotion      : 'happy' | 'neutral' | 'sad'
    flicker_hz   : 红绿交替频率 (Hz)，建议 40–60 Hz
    duration_sec : 每次刺激呈现时长 (秒)
    isi_sec      : 试次间隔 (秒)
    n_trials     : 重复次数
    fullscreen   : 是否全屏
    """
    check_stimuli()

    win = visual.Window(
        size=[800, 800],
        fullscr=fullscreen,
        color=[1, 1, 0],          # 黄色背景 (PsychoPy: -1~1 → 此处用 RGB 0~1)
        units="pix",
        allowGUI=not fullscreen,
    )
    # PsychoPy color 范围 -1~1，黄色 = (1, 1, -1)
    win.colorSpace = "rgb"
    win.color = (1, 1, -1)

    # 加载红/绿帧
    red_path = os.path.join(STIM_DIR, f"{emotion}_red.png")
    green_path = os.path.join(STIM_DIR, f"{emotion}_green.png")

    stim_red = visual.ImageStim(win, image=red_path, size=(512, 512))
    stim_green = visual.ImageStim(win, image=green_path, size=(512, 512))

    # 固定十字（试次间隔）
    fixation = visual.TextStim(win, text="+", color=(-1, -1, -1), height=40)

    # 说明文字
    info = visual.TextStim(
        win,
        text=f"CFF 范式 | 表情: {EMOTION_LABELS[emotion]} | 频率: {flicker_hz} Hz\n"
             f"按空格开始，按 Q 退出",
        color=(-1, -1, -1),
        height=18,
        pos=(0, -350),
    )

    frame_interval = 1.0 / flicker_hz  # 每帧间隔（秒）
    clock = core.Clock()

    # ── 等待开始 ──
    info.draw()
    win.flip()
    event.waitKeys(keyList=["space", "q"])
    if "q" in [k[0] for k in event.getKeys()]:
        win.close()
        return

    trial_data = []
    for trial in range(n_trials):
        # 固定点
        fixation.draw()
        win.flip()
        core.wait(isi_sec)

        # CFF 闪烁呈现
        clock.reset()
        frame_idx = 0
        while clock.getTime() < duration_sec:
            if frame_idx % 2 == 0:
                stim_red.draw()
            else:
                stim_green.draw()
            win.flip()
            core.wait(frame_interval)
            frame_idx += 1

        trial_data.append({
            "trial": trial + 1,
            "emotion": emotion,
            "flicker_hz": flicker_hz,
            "duration_sec": duration_sec,
            "total_frames": frame_idx,
        })

        if "q" in event.getKeys():
            break

    win.close()
    print(f"\n完成 {len(trial_data)} 个试次:")
    for d in trial_data:
        print(f"  试次 {d['trial']}: {EMOTION_LABELS[d['emotion']]}, "
              f"{d['flicker_hz']} Hz, {d['total_frames']} 帧")
    return trial_data


def run_demo_all(flicker_hz=50.0, duration_sec=2.0, isi_sec=1.5):
    """依次呈现三种表情的 CFF 刺激"""
    for emo in EMOTIONS:
        print(f"\n{'='*40}")
        print(f"即将呈现: {EMOTION_LABELS[emo]}")
        run_cff(emotion=emo, flicker_hz=flicker_hz,
                duration_sec=duration_sec, isi_sec=isi_sec, n_trials=1)


def main():
    parser = argparse.ArgumentParser(description="CFF 无意识表情呈现范式")
    parser.add_argument("--emotion", choices=EMOTIONS, default="happy",
                        help="表情类型 (默认: happy)")
    parser.add_argument("--hz", type=float, default=50.0,
                        help="红绿闪烁频率 Hz (默认: 50)")
    parser.add_argument("--duration", type=float, default=2.0,
                        help="刺激呈现时长 秒 (默认: 2.0)")
    parser.add_argument("--isi", type=float, default=1.0,
                        help="试次间隔 秒 (默认: 1.0)")
    parser.add_argument("--trials", type=int, default=3,
                        help="重复次数 (默认: 3)")
    parser.add_argument("--fullscreen", action="store_true",
                        help="全屏呈现")
    parser.add_argument("--demo", action="store_true",
                        help="依次演示三种表情")
    args = parser.parse_args()

    if args.demo:
        run_demo_all(flicker_hz=args.hz, duration_sec=args.duration, isi_sec=args.isi)
    else:
        run_cff(
            emotion=args.emotion,
            flicker_hz=args.hz,
            duration_sec=args.duration,
            isi_sec=args.isi,
            n_trials=args.trials,
            fullscreen=args.fullscreen,
        )


if __name__ == "__main__":
    main()

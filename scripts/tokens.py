#!/usr/bin/env python3
"""ai-ui-forge: 从风格预设生成 design-tokens.json

用法：
    python scripts/tokens.py --list
    python scripts/tokens.py --preset neutral-pro -o design-tokens.json
    python scripts/tokens.py --preset calm-wellness --primary "#2F6B4F" -o design-tokens.json

设计原则：
  - 语义命名（bg/surface/text/primary…），不出现 #hex 硬编码在组件里
  - light / dark 两套并列，同一个 token 名
  - 间距只允许 8pt 刻度；圆角只有 3 档
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STYLES = ROOT / "references" / "styles.json"

SPACE = [4, 8, 12, 16, 24, 32, 48, 64, 96]
BREAKPOINTS = {"sm": 640, "md": 768, "lg": 1024, "xl": 1280}


def load():
    with STYLES.open(encoding="utf-8") as f:
        return json.load(f)


def build(preset: dict, primary: str | None = None) -> dict:
    light = dict(preset["light"])
    dark = dict(preset["dark"])
    if primary:
        light["primary"] = primary
        light["accent"] = primary
        dark["primary"] = light_shift_for_dark(primary)
        dark["accent"] = dark["primary"]
    return {
        "$schema": "internal://ai-ui-forge/tokens-1",
        "meta": {
            "preset": preset["id"],
            "presetName": preset["name"],
            "density": preset["density"],
            "generatedBy": "ai-ui-forge/scripts/tokens.py",
            "rule": "组件只允许消费这里的 token，不许写死 hex / px",
        },
        "color": {"light": light, "dark": dark},
        "typography": preset["typography"],
        "space": {f"s{i + 1}": v for i, v in enumerate(SPACE)},
        "radius": preset["radius"],
        "shadow": preset["shadow"],
        "motion": preset["motion"],
        "breakpoints": BREAKPOINTS,
        "semantic": {
            "focusRing": "2px solid color-mix(in oklab, token(color.primary) 70%, white)",
            "borderSubtle": "color-mix(in oklab, token(color.border) 60%, transparent)",
            "textOnPrimary": "white",
        },
        "components": {
            "button": {
                "height": {"sm": 32, "md": 40, "lg": 48},
                "paddingX": {"sm": 12, "md": 16, "lg": 24},
                "radius": "token(radius.sm)",
                "states": ["default", "hover", "active", "focus-visible", "disabled"],
                "transition": "token(motion.fast) token(motion.easing)",
            },
            "input": {"height": 40, "radius": "token(radius.sm)", "states": ["default", "focus", "error", "disabled"]},
            "card": {"radius": "token(radius.md)", "shadow": "token(shadow.card)", "padding": "token(space.s5)"},
            "badge": {"height": 24, "radius": "token(radius.pill)", "paddingX": "token(space.s2)"},
        },
        "a11y": {
            "minContrastBody": 4.5,
            "minContrastLarge": 3.0,
            "minTargetSize": 44,
            "reducedMotion": "prefers-reduced-motion: 关闭位移/缩放，仅保留透明度变化",
        },
        "avoid": preset["avoid"],
    }


def light_shift_for_dark(hex_color: str) -> str:
    """暗色模式下的主色：提高明度、略降饱和，避免在深底上发闷。"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    s = 0 if mx == mn else (mx - mn) / (1 - abs(2 * l - 1))
    hh = 0.0
    if mx != mn:
        d = mx - mn
        if mx == r:
            hh = ((g - b) / d) % 6
        elif mx == g:
            hh = (b - r) / d + 2
        else:
            hh = (r - g) / d + 4
        hh *= 60
    l = min(0.78, max(0.62, l + 0.22))
    s = min(1.0, max(0.35, s * 0.92))
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((hh / 60) % 2 - 1))
    m = l - c / 2
    seg = int(hh // 60) % 6
    rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][seg]
    return "#" + "".join(f"{round((v + m) * 255):02X}" for v in rgb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="列出预设")
    ap.add_argument("--preset", default="neutral-pro")
    ap.add_argument("--primary", default=None, help="覆盖主色，如 #2F6B4F")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    data = load()
    presets = {p["id"]: p for p in data["presets"]}
    if args.list:
        for p in data["presets"]:
            print(f'{p["id"]:<18} {p["name"]:<14} {p["fit"]}')
        return 0
    if args.preset not in presets:
        print(f"未知预设 {args.preset!r}，可选：{', '.join(presets)}", file=sys.stderr)
        return 2

    tokens = build(presets[args.preset], args.primary)
    text = json.dumps(tokens, ensure_ascii=False, indent=2)
    if args.out:
        pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"written: {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

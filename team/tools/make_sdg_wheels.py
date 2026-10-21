"""Generate the SDG wheel in three languages and move the (?) next to the heading."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Circle, Wedge

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"

SDG = [
    (1,  "#E5243B"),
    (2,  "#DDA63A"),
    (3,  "#4C9F38"),
    (4,  "#C5192D"),
    (5,  "#FF3A21"),
    (6,  "#26BDE2"),
    (7,  "#FCC30B"),
    (8,  "#A21942"),
    (9,  "#FD6925"),
    (10, "#DD1367"),
    (11, "#FD9D24"),
    (12, "#BF8B2E"),
    (13, "#3F7E44"),
    (14, "#0A97D9"),
    (15, "#56C02B"),
    (16, "#00689D"),
    (17, "#19486A"),
]

TEXT = {
    "en": {
        "centre": ("SUSTAINABLE", "DEVELOPMENT", "GOALS"),
        "legend_title": "This pathway supports",
        "items": [
            (4, "Quality Education"),
            (5, "Gender Equality"),
            (8, "Decent Work & Economic Growth"),
            (9, "Industry, Innovation & Infrastructure"),
            (10, "Reduced Inequalities"),
        ],
        "font": "DejaVu Sans",
        "file": "sdg_wheel_en.png",
    },
    "zh": {
        "centre": ("可持续", "发展目标", "17 个"),
        "legend_title": "这条路径主要贡献",
        "items": [
            (4, "优质教育"),
            (5, "性别平等"),
            (8, "体面工作与经济增长"),
            (9, "产业、创新与基础设施"),
            (10, "减少不平等"),
        ],
        "font": None,      # resolved below from available CJK fonts
        "file": "sdg_wheel_zh.png",
    },
    "ms": {
        "centre": ("PEMBANGUNAN", "MAMPAN", "17 MATLAMAT"),
        "legend_title": "Laluan ini menyokong",
        "items": [
            (4, "Pendidikan Berkualiti"),
            (5, "Kesaksamaan Gender"),
            (8, "Pekerjaan Layak & Ekonomi"),
            (9, "Industri, Inovasi & Infrastruktur"),
            (10, "Kurang Ketidaksamaan"),
        ],
        "font": "DejaVu Sans",
        "file": "sdg_wheel_ms.png",
    },
}


def pick_cjk_font() -> str:
    from matplotlib import font_manager

    candidates = [
        "Microsoft YaHei", "Microsoft JhengHei", "SimHei", "SimSun",
        "Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC",
        "PingFang SC", "WenQuanYi Zen Hei", "Arial Unicode MS",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    return "DejaVu Sans"


def build(lang: str) -> None:
    cfg = TEXT[lang]
    font = cfg["font"] or pick_cjk_font()
    if lang == "zh":
        print("  chinese font:", font)

    fig, ax = plt.subplots(figsize=(9.6, 8.4), dpi=200)
    ax.set_xlim(-1.3, 1.95)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    R_OUT, R_IN = 1.0, 0.60
    for i, (num, colour) in enumerate(SDG):
        start = 90 - (i + 1) * (360 / 17)
        end = 90 - i * (360 / 17)
        ax.add_patch(
            Wedge((0, 0), R_OUT, start, end, width=R_OUT - R_IN,
                  facecolor=colour, edgecolor="white", linewidth=1.5)
        )
        mid = math.radians((start + end) / 2)
        r = (R_OUT + R_IN) / 2
        ax.text(r * math.cos(mid), r * math.sin(mid), str(num),
                ha="center", va="center", color="white",
                fontsize=16, fontweight="bold", family="DejaVu Sans")

    ax.add_patch(Circle((0, 0), R_IN, facecolor="white", edgecolor="#e6e6e6", linewidth=1))
    l1, l2, l3 = cfg["centre"]
    ax.text(0, 0.16, l1, ha="center", va="center", fontsize=13, fontweight="bold",
            color="#1a1a1a", family=font)
    ax.text(0, 0.0, l2, ha="center", va="center", fontsize=11.5, fontweight="bold",
            color="#1a1a1a", family=font)
    ax.text(0, -0.17, l3, ha="center", va="center", fontsize=9,
            color="#666666", family=font)

    # legend on the right
    lx = 1.10
    ax.text(lx, 0.92, cfg["legend_title"], fontsize=10, fontweight="bold",
            family=font, color="#333333")
    y = 0.72
    for num, label in cfg["items"]:
        colour = next(c for n, c in SDG if n == num)
        ax.add_patch(Circle((lx + 0.035, y), 0.032, facecolor=colour, edgecolor="none"))
        ax.text(lx + 0.10, y, f"{num}", fontsize=8.6, fontweight="bold",
                va="center", family="DejaVu Sans", color="#333333")
        ax.text(lx + 0.20, y, label, fontsize=8.2, va="center", family=font, color="#333333")
        y -= 0.145

    out = DOCS / cfg["file"]
    plt.tight_layout()
    plt.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out.name, out.stat().st_size, "bytes")


for lang in ("en", "zh", "ms"):
    build(lang)

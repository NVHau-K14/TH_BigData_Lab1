"""Render output của các cell có dòng đầu `# ANH: <mã> | <chú thích>` thành ảnh PNG.

Chạy trong container:
    python /home/jovyan/work/tools/render_outputs.py /home/jovyan/work/notebooks/00_chuan_bi_du_lieu.ipynb

Kết quả:
    report/images/<2 số đầu tên notebook>/<mã>.png
    report/images/<2 số đầu tên notebook>/danh_sach_anh.md
"""

import base64
import os
import re
import sys
from pathlib import Path

import nbformat
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent          # thư mục dự án
IMAGES_DIR = ROOT / "report" / "images"

ANH_RE = re.compile(r"^\s*#\s*ANH:\s*([^|]+?)\s*\|\s*(.+?)\s*$")
NOISE_RE = re.compile(r"WARN|Setting default log level|\[Stage\s*\d|^\s*To adjust logging level")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

FONT_SIZE = 16
MARGIN = 20
MAX_WIDTH = 1600
MAX_LINES = 60
LINE_SPACING = 6
BG = (255, 255, 255)
FG = (33, 33, 33)
BORDER = (210, 210, 210)
PAD = 12           # khoảng cách giữa khung viền và chữ


def vietnamese_chars():
    import unicodedata
    chars = set("đĐ")
    for ch in "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY":
        for tone in ["", "̀", "́", "̉", "̃", "̣"]:
            chars.add(unicodedata.normalize("NFC", ch + tone))
    return chars


def find_font():
    """Chọn font monospace đầu tiên có đủ chữ tiếng Việt.

    DejaVu Sans Mono (kèm matplotlib) thiếu các chữ có dấu chồng (ố, ể, ắ, ...),
    nên trong image hiện tại font được chọn thực tế là Liberation Mono.
    """
    from fontTools.ttLib import TTFont
    cands = []
    try:
        import matplotlib
        from matplotlib import font_manager
        cands.append(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSansMono.ttf"))
        for fam in ["DejaVu Sans Mono", "Liberation Mono"]:
            try:
                cands.append(font_manager.findfont(
                    font_manager.FontProperties(family=fam), fallback_to_default=False))
            except Exception:
                pass
    except ImportError:
        pass
    cands += ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"]
    need = vietnamese_chars()
    for p in cands:
        if not os.path.exists(p):
            continue
        try:
            cmap = TTFont(p).getBestCmap()
        except Exception:
            continue
        if all(ord(c) in cmap for c in need):
            return p
    raise SystemExit("Không tìm thấy font monospace có đủ chữ tiếng Việt")


def clean_text(text):
    text = ANSI_RE.sub("", text).replace("\r\n", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    lines = []
    for line in text.split("\n"):
        if "\r" in line:                      # thanh tiến độ ghi đè bằng \r: lấy phần cuối
            line = line.split("\r")[-1]
        if NOISE_RE.search(line):
            continue
        lines.append(line.rstrip())
    return lines


def collect_output(cell):
    """Trả về ('png', bytes) hoặc ('text', [dòng]) hoặc (None, None)."""
    lines = []
    for out in cell.get("outputs", []):
        otype = out.get("output_type")
        if otype in ("display_data", "execute_result"):
            data = out.get("data", {})
            if "image/png" in data:
                png = data["image/png"]
                if isinstance(png, list):
                    png = "".join(png)
                return "png", base64.b64decode(png)
            if "text/plain" in data:
                txt = data["text/plain"]
                lines += clean_text("".join(txt) if isinstance(txt, list) else txt)
        elif otype == "stream" and out.get("name") == "stdout":
            txt = out.get("text", "")
            lines += clean_text("".join(txt) if isinstance(txt, list) else txt)
        # stderr và error: bỏ qua
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return None, None
    return "text", lines


def render_text(lines, font, path):
    if len(lines) > MAX_LINES:
        rest = len(lines) - MAX_LINES
        lines = lines[:MAX_LINES] + [f"… (còn {rest} dòng)"]
    lines = [l.expandtabs(4) for l in lines]

    max_text_w = MAX_WIDTH - 2 * (MARGIN + PAD)
    ell_w = font.getlength("…")
    fitted = []
    for l in lines:
        if font.getlength(l) > max_text_w:
            while l and font.getlength(l) + ell_w > max_text_w:
                l = l[:-1]
            l += "…"
        fitted.append(l)

    asc, desc = font.getmetrics()
    line_h = asc + desc + LINE_SPACING
    text_w = max([font.getlength(l) for l in fitted] + [1])
    w = int(text_w) + 2 * (MARGIN + PAD)
    h = line_h * len(fitted) - LINE_SPACING + 2 * (MARGIN + PAD)

    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([MARGIN, MARGIN, w - MARGIN - 1, h - MARGIN - 1], outline=BORDER, width=1)
    y = MARGIN + PAD
    for l in fitted:
        draw.text((MARGIN + PAD, y), l, font=font, fill=FG)
        y += line_h
    img.save(path)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Cách dùng: python render_outputs.py <notebook.ipynb>")
    nb_path = Path(sys.argv[1])
    nb_num = nb_path.name[:2]
    out_dir = IMAGES_DIR / nb_num
    out_dir.mkdir(parents=True, exist_ok=True)

    nb = nbformat.read(str(nb_path), as_version=4)
    font_path = find_font()
    print(f"Font: {font_path}")
    font = ImageFont.truetype(font_path, FONT_SIZE)

    rows, warnings = [], 0
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        first = cell.source.split("\n", 1)[0]
        m = ANH_RE.match(first)
        if not m:
            continue
        code, caption = m.group(1).strip(), m.group(2).strip()
        fname = f"{code}.png"
        kind, content = collect_output(cell)
        if kind is None:
            print(f"CẢNH BÁO: cell {idx} ({code}) có '# ANH:' nhưng không có output -> không tạo ảnh")
            warnings += 1
            continue
        if kind == "png":
            (out_dir / fname).write_bytes(content)
        else:
            render_text(content, font, out_dir / fname)
        rows.append((code, fname, caption))
        print(f"Đã lưu {out_dir / fname}")

    md = [f"# Danh sách ảnh – notebook {nb_path.name}", "",
          "| Mã | File | Chú thích |", "|---|---|---|"]
    md += [f"| {c} | `{f}` | {cap} |" for c, f, cap in rows]
    (out_dir / "danh_sach_anh.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Tổng: {len(rows)} ảnh, {warnings} cảnh báo. Danh sách: {out_dir / 'danh_sach_anh.md'}")


if __name__ == "__main__":
    main()

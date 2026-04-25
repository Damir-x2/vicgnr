from __future__ import annotations

import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "static", "ArialRegular.ttf")
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Arial", FONT_PATH))
    LETTER_FONT = "Arial"

LTR_H_CM = 4.0
VIS_D_CM = 5.0

W, H = A4
MX = 1.0 * cm
MY = 1.0 * cm
CW = 6.2 * cm
CH = 6.8 * cm
GAP = 0.35 * cm

VIS_COL = {
    "black": colors.HexColor("#000000"),
    "red": colors.HexColor("#d02f20"),
    "yellow": colors.HexColor("#fcfe58"),
    "green": colors.HexColor("#5bad5c"),
    "blue": colors.HexColor("#63aeea"),
}


def _page_grid():
    use_w = W - 2 * MX
    use_h = H - 2 * MY
    cols = max(1, int((use_w + GAP) // (CW + GAP)))
    rows = max(1, int((use_h + GAP) // (CH + GAP)))
    return cols, rows, cols * rows


def _draw_ltr(c, x, y, ltr):
    size = LTR_H_CM * cm
    c.setFillColor(colors.black)
    c.setFont(LETTER_FONT, size)
    y0 = y + (CH - size) / 2 + 8
    c.drawCentredString(x + CW / 2, y0, ltr)


def _draw_vis(c, x, y, rings):
    cx = x + CW / 2
    cy = y + CH / 2
    r0 = (VIS_D_CM * cm) / 2
    step = r0 / 5

    for i, color_name in enumerate(reversed(rings)):
        r = r0 - i * step
        c.setFillColor(VIS_COL[color_name])
        c.circle(cx, cy, r, stroke=0, fill=1)

    c.setLineWidth(0.9)
    c.setStrokeColor(colors.black)
    for i in range(0, 6):
        r = r0 - i * step
        if r < 0:
            continue
        c.circle(cx, cy, r, stroke=1, fill=0)


def _draw_card(c, x, y, item):
    data = item.data

    c.setStrokeColor(colors.HexColor("#DADADA"))
    c.setLineWidth(1)
    c.rect(x, y, CW, CH, stroke=1, fill=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(x + 0.2 * cm, y + CH - 0.35 * cm, f"#{item.position:02d}")

    if item.item_type == "letter":
        _draw_ltr(c, x, y, data["letter"])
    else:
        _draw_vis(c, x, y, data["rings"])


def _draw_key(c, kit, items):
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, H - 2 * cm, f"Answer Key - {kit.title}")

    c.setFont("Helvetica", 10)
    y = H - 3 * cm
    for i in items:
        data = i.data
        if i.item_type == "letter":
            detail = data["letter"]
        else:
            initials = "-".join(color[:1].upper() for color in data["rings"])
            detail = f"{initials} sum={i.value_sum}"

        line = (
            f"#{i.position:02d} | {i.item_type:<6} | "
            f"{'REAL' if i.is_real else 'FALSE':<5} | {detail} | {i.status or '-'}"
        )
        c.drawString(2 * cm, y, line)
        y -= 0.55 * cm

        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = H - 2 * cm


def make_pdf(kit, items):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"{kit.title}.pdf")

    cols, _rows, per_page = _page_grid()
    for i, item in enumerate(items):
        if i > 0 and i % per_page == 0:
            c.showPage()

        slot = i % per_page
        row = slot // cols
        col = slot % cols

        x = MX + col * (CW + GAP)
        y = H - MY - CH - row * (CH + GAP)
        _draw_card(c, x, y, item)

    _draw_key(c, kit, items)

    c.save()
    buf.seek(0)
    return buf.getvalue()

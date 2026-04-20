from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

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
    "red": colors.HexColor("#d9534f"),
    "yellow": colors.HexColor("#f0ad4e"),
    "green": colors.HexColor("#5cb85c"),
    "blue": colors.HexColor("#0275d8"),
}


def _page_grid() -> tuple[int, int, int]:
    use_w = W - 2 * MX
    use_h = H - 2 * MY
    cols = max(1, int((use_w + GAP) // (CW + GAP)))
    rows = max(1, int((use_h + GAP) // (CH + GAP)))
    return cols, rows, cols * rows


def _draw_ltr(c: canvas.Canvas, x: float, y: float, ltr: str) -> None:
    size = LTR_H_CM * cm
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", size)
    y0 = y + (CH - size) / 2 + 8
    c.drawCentredString(x + CW / 2, y0, ltr)


def _draw_vis(c: canvas.Canvas, x: float, y: float, rings: list[str]) -> None:
    cx = x + CW / 2
    cy = y + CH / 2
    r0 = (VIS_D_CM * cm) / 2
    step = r0 / 5

    # Fill from outer ring to center.
    for i, color_name in enumerate(reversed(rings)):
        r = r0 - i * step
        c.setFillColor(VIS_COL[color_name])
        c.circle(cx, cy, r, stroke=0, fill=1)

    # Draw boundaries to keep rings visible even when adjacent colors are the same.
    c.setLineWidth(0.9)
    c.setStrokeColor(colors.black)
    for i in range(0, 6):
        r = r0 - i * step
        if r < 0:
            continue
        c.circle(cx, cy, r, stroke=1, fill=0)


def _draw_card(c: canvas.Canvas, x: float, y: float, item) -> None:
    data = item.data

    c.setStrokeColor(colors.HexColor("#808080"))
    c.setLineWidth(1)
    c.rect(x, y, CW, CH, stroke=1, fill=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawString(x + 0.2 * cm, y + CH - 0.35 * cm, f"#{item.position:02d}")

    if item.item_type == "letter":
        _draw_ltr(c, x, y, data["letter"])
    else:
        _draw_vis(c, x, y, data["rings"])


def _draw_key(c: canvas.Canvas, kit, items: list) -> None:
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, H - 2 * cm, f"Answer Key - {kit.title}")

    c.setFont("Helvetica", 10)
    y = H - 3 * cm
    for item in items:
        data = item.data
        if item.item_type == "letter":
            detail = data["letter"]
        else:
            initials = "-".join(color[:1].upper() for color in data["rings"])
            detail = f"{initials} sum={item.value_sum}"

        line = (
            f"#{item.position:02d} | {item.item_type:<6} | "
            f"{'REAL' if item.is_real else 'FALSE':<5} | {detail} | {item.status or '-'}"
        )
        c.drawString(2 * cm, y, line)
        y -= 0.55 * cm

        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = H - 2 * cm


def make_pdf(kit, items: list) -> bytes:
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

build_kit_pdf = make_pdf

import os

from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

PAGE_WIDTH = 7 * 72
PAGE_HEIGHT = 4 * 72
BLUE = HexColor("#1f4aa8")
MIN_FONT_SIZE = 6


def dotted_line(c, x1, x2, y):
    c.setDash(1, 2)
    c.line(x1, y, x2, y)
    c.setDash()


def resolve_logo_path():
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")
    for name in ("logo.jpg", "logo.jpeg", "logo.png"):
        path = os.path.join(asset_dir, name)
        if os.path.exists(path):
            return path
    return None


def fit_font_size(text, font_name, max_font_size, max_width):
    text = str(text or "")
    if not text:
        return max_font_size

    font_size = max_font_size
    while font_size > MIN_FONT_SIZE and stringWidth(text, font_name, font_size) > max_width:
        font_size -= 0.5
    return max(font_size, MIN_FONT_SIZE)


def draw_text_in_box(c, text, x1, x2, y, font_name="Helvetica", font_size=10, align="left"):
    text = str(text or "")
    if not text:
        return

    usable_width = max(x2 - x1 - 4, 10)
    fitted_size = fit_font_size(text, font_name, font_size, usable_width)
    c.setFont(font_name, fitted_size)

    if align == "center":
        c.drawCentredString((x1 + x2) / 2, y, text)
    elif align == "right":
        c.drawRightString(x2 - 2, y, text)
    else:
        c.drawString(x1 + 2, y, text)


def wrap_text(text, font_name, font_size, max_width, max_lines=2):
    text = str(text or "").strip()
    if not text:
        return []

    words = text.split()
    lines = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue

        lines.append(current)
        current = word
        if len(lines) == max_lines - 1:
            break

    remaining = words[len(" ".join(lines + [current]).split()):]
    if remaining:
        tail = " ".join([current] + remaining)
        while tail and stringWidth(f"{tail}...", font_name, font_size) > max_width:
            tail = tail.rsplit(" ", 1)[0]
        current = f"{tail}..." if tail else "..."

    lines.append(current)
    return lines[:max_lines]


def generate_receipt_pdf(file_path, data):
    c = canvas.Canvas(file_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    width = PAGE_WIDTH
    height = PAGE_HEIGHT

    logo_path = resolve_logo_path()

    # OUTER BORDER
    c.setStrokeColor(BLUE)
    c.setLineWidth(1)
    c.rect(5, 5, width - 10, height - 10)

    # LOGO
    if logo_path and os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            12,
            height - 48,
            width=40,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )

    # HEADER TITLE
    c.setFillColor(BLUE)
    header_left = 58
    header_right = width - 50
    # draw_text_in_box(c, "LEAD THE WAY", header_left, header_right, height - 24, "Helvetica-Bold", 24)
    # c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2 + 20, height - 24, "LEAD THE WAY")

    # SUBTITLE BAR
    c.setFillColor(BLUE)
    c.rect(header_left, height - 42, header_right - header_left, 10, fill=1, stroke=0)

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((header_left + header_right) / 2, height - 39, "English for a Better Future")

    # ADDRESS
    c.setFillColor(BLUE)
    c.setFont("Helvetica", 7)
    c.drawCentredString(
        width / 2,
        height - 50,
        "House # 24, Road # 12, Sector # 11, Uttara, Dhaka-1230, Bangladesh."
    )

    c.drawCentredString(
        width / 2,
        height - 60,
        "Tel: 028991232, Cell: 01788932619, 01941125442, E-mail: leadthewayuttara@gmail.com"
    )

    # MONEY RECEIPT BUTTON
    c.roundRect(192, height - 86, 120, 18, 9, fill=1)
    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(252, height - 80.5, "Money Receipt")

    c.setFillColor(BLUE)

    # TOP FIELDS
    y = height - 98

    # MR NO
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "MR No")
    dotted_line(c, 60, 155, y - 2)
    draw_text_in_box(c, data.get("mr_no", "101"), 60, 155, y + 1, "Helvetica-Bold", 11, "center")

    # DATE
    c.setFont("Helvetica-Bold", 9)
    c.drawString(390, y, "Date:")
    dotted_line(c, 425, 495, y - 2)
    draw_text_in_box(c, data["date"], 425, 495, y + 1, "Helvetica-Bold", 10, "center")

    y -= 18

    # STUDENT NAME
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "Student's Name:")
    dotted_line(c, 95, 360, y - 2)
    draw_text_in_box(c, data["student_name"], 95, 360, y + 1, "Helvetica", 10)

    # MONTH
    c.setFont("Helvetica-Bold", 9)
    c.drawString(380, y, "Month:")
    dotted_line(c, 420, 495, y - 2)
    draw_text_in_box(c, data["month"], 420, 495, y + 1, "Helvetica", 10, "center")

    y -= 18

    # CLASS
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y, "Class:")
    dotted_line(c, 50, 180, y - 2)
    draw_text_in_box(c, data["student_class"], 50, 180, y + 1, "Helvetica", 10, "center")

    # DAY
    c.setFont("Helvetica-Bold", 9)
    c.drawString(245, y, "Day:")
    dotted_line(c, 275, 380, y - 2)
    draw_text_in_box(c, data["day"], 275, 380, y + 1, "Helvetica", 10, "center")

    # TIME
    c.setFont("Helvetica-Bold", 9)
    c.drawString(400, y, "Time:")
    dotted_line(c, 435, 495, y - 2)
    draw_text_in_box(c, data["time"], 435, 495, y + 1, "Helvetica", 10, "center")

    # TABLE
    table_top = y - 12
    left = 20
    right = 500
    row_h = 18
    table_height = 90
    bottom = table_top - table_height

    c.rect(left, bottom, right - left, table_height)

    c.line(55, table_top, 55, bottom)
    c.line(380, table_top, 380, bottom)

    for i in range(1, 5):
        c.line(left, table_top - i * row_h, right, table_top - i * row_h)

    # TABLE HEADERS
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(38, table_top - 12, "NO.")
    c.drawCentredString(220, table_top - 12, "Particulars")
    c.drawCentredString(440, table_top - 12, "Amount (BDT)")

    c.setFont("Helvetica", 10)

    c.drawString(34, table_top - 30, "1.")
    draw_text_in_box(c, "Admission Fee", 60, 375, table_top - 30, "Helvetica", 10)

    c.drawString(34, table_top - 48, "2.")
    draw_text_in_box(c, "Monthly Tuition Fee", 60, 375, table_top - 48, "Helvetica", 10)

    c.drawString(34, table_top - 66, "3.")
    draw_text_in_box(c, "Miscellaneous", 60, 375, table_top - 66, "Helvetica", 10)

    if data["admission_fee"] > 0:
        draw_text_in_box(c, f"{data['admission_fee']}/=", 385, 470, table_top - 30, "Helvetica", 10, "right")

    if data["monthly_fee"] > 0:
        draw_text_in_box(c, f"{data['monthly_fee']}/=", 385, 470, table_top - 48, "Helvetica", 10, "right")

    if data["misc_fee"] > 0:
        draw_text_in_box(c, f"{data['misc_fee']}/=", 385, 470, table_top - 66, "Helvetica", 10, "right")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(335, table_top - 84, "Total =")
    draw_text_in_box(c, f"{data['total']}/=", 385, 470, table_top - 84, "Helvetica-Bold", 10, "right")

    # IN WORD
    y2 = bottom - 12
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20, y2, "In Word :")
    dotted_line(c, 68, 495, y2 - 2)

    word_lines = wrap_text(data["words"], "Helvetica", 8, 385, max_lines=2)
    c.setFont("Helvetica", 8)
    for index, line in enumerate(word_lines):
        c.drawString(72, y2 + 2 - (index * 8), line)

    # FOOTER
    c.setFont("Helvetica-Bold", 7)
    c.drawString(20, 20, "NB : Admission & tuition fee non-refundable & non-exchangeable")
    c.drawString(55, 10, "Please preserve your copy")

    # SIGNATURE
    c.setFont("Helvetica-Bold", 10)
    c.line(388, 22, 490, 22)
    c.drawString(390, 10, "For- Lead The Way")

    c.save()

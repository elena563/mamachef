from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

def generate_list_pdf(shop_list):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595.27, 841.89))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 780, f"{shop_list.name}")

    c.setFont("Helvetica", 12)
    date = datetime.now().strftime("%d/%m/%Y")
    c.drawString(50, 750, f"Export date: {date}")
    c.setDash(6, 3)
    c.line(50, 730, 500, 730)
    y = 700
    for item in shop_list.items.all():
        if y < 50:
            c.showPage()
            y = 780
        status = "[X]" if item.bought else "[  ]"
        if item.ingredient:
            item_name = item.ingredient.name
        else:
            item_name = item.custom_name
        c.drawString(50, y, f"{status} {item_name} - {item.quantity} {item.unit}")
        y -= 20

    c.save()
    buffer.seek(0)
    return buffer
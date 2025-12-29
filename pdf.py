from fpdf import FPDF
import os
from datetime import datetime

def generar_boleta(cliente, servicio, cantidad, subtotal, igv, total):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Lavandería Mora", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Cliente: {cliente}", ln=True)
    pdf.cell(0, 8, f"Servicio: {servicio}", ln=True)
    pdf.cell(0, 8, f"Cantidad: {cantidad}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 8, f"Subtotal: S/ {subtotal:.2f}", ln=True)
    pdf.cell(0, 8, f"IGV (18%): S/ {igv:.2f}", ln=True)
    pdf.cell(0, 8, f"Total: S/ {total:.2f}", ln=True)

    # Crear carpeta si no existe
    if not os.path.exists("boletas"):
        os.makedirs("boletas")

    nombre_archivo = f"boleta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    ruta = os.path.join("boletas", nombre_archivo)

    pdf.output(ruta)

    return ruta


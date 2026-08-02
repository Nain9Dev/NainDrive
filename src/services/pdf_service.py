"""
In-Memory PDF Document Generation Service.
Produces official accounting invoice layouts using FPDF2 without persisting temporary files to disk.
"""
from fpdf import FPDF
from src.domain.models import InvoiceCalculation


class PDFInvoiceGenerator(FPDF):
    """Custom PDF Layout Builder for Driving School Accounting Documents."""

    def __init__(self, invoice: InvoiceCalculation):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.invoice = invoice
        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()
        self._build_document_content()

    def header(self) -> None:
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(24, 43, 73)
        self.cell(0, 10, "AUTOESCUELA NAINDEV - GESTIÓN Y FACTURACIÓN", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Plataforma Tecnológica Modular | Registro Contable Oficial", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(24, 43, 73)
        self.set_line_width(0.8)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-18)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 5, f"Documento fiscal generado digitalmente - Referencia: {self.invoice.invoice_number}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Página {self.page_no()}", align="C", new_x="LMARGIN", new_y="NEXT")

    def _build_document_content(self) -> None:
        inv = self.invoice

        # Metadata section
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        self.cell(90, 6, f"N. Factura: {inv.invoice_number}", align="L", new_x="RIGHT", new_y="TOP")
        self.cell(90, 6, f"Fecha Emisión: {inv.invoice_date}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Client details box
        start_y = self.get_y()
        self.set_fill_color(242, 245, 249)
        self.rect(15, start_y, 180, 24, "F")
        self.set_xy(18, start_y + 3)
        self.cell(0, 5, f"ALUMNO / CLIENTE: {inv.student_name.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.set_x(18)
        self.cell(0, 5, f"DNI / NIF: {inv.student_dni}", new_x="LMARGIN", new_y="NEXT")
        self.set_x(18)
        self.cell(0, 5, f"TIPO PERMISO: {inv.target_license}", new_x="LMARGIN", new_y="NEXT")
        self.set_y(start_y + 28)

        # Itemized table header
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(24, 43, 73)
        self.set_text_color(255, 255, 255)
        self.cell(85, 8, "Concepto Formativo / Tasa", border=0, fill=True, align="L")
        self.cell(45, 8, "Volumen / Cantidad", border=0, fill=True, align="C")
        self.cell(50, 8, "Importe Bruto (EUR)", border=0, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

        # Table rows
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        
        # Row 1: Enrollment
        self.cell(85, 8, "Matrícula y Tramitación Oficial", border="B")
        self.cell(45, 8, f"Incluye {inv.included_classes} clases", border="B", align="C")
        self.cell(50, 8, f"{inv.enrollment_fee:.2f} EUR", border="B", align="R", new_x="LMARGIN", new_y="NEXT")

        # Row 2: Extra practical classes
        self.cell(85, 8, "Clases Prácticas Adicionales", border="B")
        self.cell(45, 8, f"{inv.extra_classes_count} extra ({inv.completed_classes} en total)", border="B", align="C")
        self.cell(50, 8, f"{inv.extra_classes_cost:.2f} EUR", border="B", align="R", new_x="LMARGIN", new_y="NEXT")

        # Row 3: Exams
        self.cell(85, 8, "Tasas Examen DGT / Tramitación", border="B")
        self.cell(45, 8, f"{inv.total_exams_count} convocatoria(s)", border="B", align="C")
        self.cell(50, 8, f"{inv.total_exams_cost:.2f} EUR", border="B", align="R", new_x="LMARGIN", new_y="NEXT")

        self.ln(8)

        # Totals Summary Area
        self.set_x(110)
        self.cell(35, 7, "SUBTOTAL BRUTO:", align="R")
        self.cell(50, 7, f"{inv.subtotal_amount:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")

        self.set_x(110)
        self.cell(35, 7, f"IVA LEGAL ({int(inv.vat_percentage * 100)}%):", align="R")
        self.cell(50, 7, f"{inv.vat_amount:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")

        self.set_x(110)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(24, 43, 73)
        self.cell(35, 8, "TOTAL FACTURADO:", align="R", border="T")
        self.cell(50, 8, f"{inv.total_with_vat:.2f} EUR", align="R", border="T", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(110)
        self.cell(35, 7, "ANTICIPOS PAGADOS:", align="R")
        self.cell(50, 7, f"- {inv.advances_paid:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")

        self.ln(2)
        self.set_x(100)
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(230, 238, 248)
        self.set_text_color(0, 51, 102)
        self.cell(45, 10, "SALDO A PAGAR:", align="R", fill=True)
        self.cell(50, 10, f"{inv.pending_balance:.2f} EUR", align="R", fill=True, new_x="LMARGIN", new_y="NEXT")


def generate_invoice_pdf_bytes(invoice: InvoiceCalculation) -> bytes:
    """Returns official PDF documentation as a safe byte stream ready for HTTP streaming/download."""
    generator = PDFInvoiceGenerator(invoice)
    return bytes(generator.output())

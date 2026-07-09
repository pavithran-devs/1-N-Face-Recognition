from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fpdf import FPDF


class DocumentationPDF(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, "1:N Face Recognition Platform - Technical Documentation", 0, 1, "L")
        self.set_draw_color(210, 210, 210)
        self.line(10, 16, 200, 16)
        self.ln(3)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 6, f"Page {self.page_no()}", 0, 0, "C")


def draw_cover(pdf: DocumentationPDF, title: str) -> None:
    pdf.add_page()
    pdf.set_fill_color(26, 54, 93)
    pdf.rect(0, 0, 210, 90, "F")

    pdf.set_xy(15, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.multi_cell(0, 12, title)

    pdf.set_xy(15, 105)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        7,
        "Comprehensive architecture and implementation documentation for the\n"
        "enrollment and identification services.",
    )

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(45, 7, "Generated:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def render_markdown_like(pdf: DocumentationPDF, text: str) -> None:
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        pdf.set_x(pdf.l_margin)
        if not line:
            pdf.ln(2)
            continue

        if line.startswith("# "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 17)
            pdf.set_text_color(26, 54, 93)
            pdf.multi_cell(0, 9, line[2:].strip())
            pdf.ln(1)
            continue

        if line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(43, 108, 176)
            pdf.multi_cell(0, 7, line[3:].strip())
            continue

        if line.startswith("### "):
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(43, 108, 176)
            pdf.multi_cell(0, 6, line[4:].strip())
            continue

        if line.startswith("- "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 6, f"- {line[2:].strip()}")
            continue

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        safe_line = line.replace("\t", "    ")
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, 6, safe_line)


def main() -> None:
    root = Path(__file__).resolve().parent
    source = root / "System_Technical_Documentation.md"
    output = root / "System_Technical_Documentation.pdf"

    if not source.exists():
        raise FileNotFoundError(f"Missing source file: {source}")

    pdf = DocumentationPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(10, 20, 10)

    draw_cover(pdf, "1:N Face Recognition Platform")
    pdf.add_page()
    render_markdown_like(pdf, source.read_text(encoding="utf-8"))
    pdf.output(str(output))

    print(f"Generated: {output}")


if __name__ == "__main__":
    main()


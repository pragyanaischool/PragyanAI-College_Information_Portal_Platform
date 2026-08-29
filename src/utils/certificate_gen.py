"""
src/utils/certificate_gen.py

Automated Verifiable E-Certificate Generator using fpdf2.
Creates styled, landscape-oriented participation and merit certificates
for students attending Free AI Masterclasses, IoT Bootcamps, and Webinars.
"""

from datetime import datetime
import io
import os
import uuid
from fpdf import FPDF


class CertificatePDF(FPDF):
    """Custom landscape PDF class for styled institutional micro-credentials."""

    def draw_ornamental_border(self):
        """Draws double-line borders and decorative header accents."""
        # Outer Border (Navy Blue)
        self.set_draw_color(15, 23, 42)
        self.set_line_width(1.5)
        self.rect(8, 8, 281, 194)

        # Inner Border (Gold Accent)
        self.set_draw_color(217, 119, 6)
        self.set_line_width(0.6)
        self.rect(12, 12, 273, 186)

        # Top Center Badge Graphic
        self.set_fill_color(30, 58, 138)
        self.rect(118, 8, 61, 6, "F")


class CertificateGenerator:
    """Generates official, downloadable PDF completion certificates."""

    @staticmethod
    def generate(
        student_name: str,
        event_title: str,
        institution_name: str = "Partner Institution",
        event_date: Optional[str] = None,
        speaker_name: str = "Sateesh Ambesange",
        speaker_title: str = "Founder & AI Architect, PragyanAI",
        certificate_id: Optional[str] = None,
    ) -> io.BytesIO:
        """Compiles a complete landscape certificate and returns it as an in-memory BytesIO buffer."""
        cert_id = certificate_id or f"PRG-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
        issue_date = event_date or datetime.now().strftime("%B %d, %Y")

        pdf = CertificatePDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=False)
        pdf.add_page()
        pdf.draw_ornamental_border()

        # 1. Organization Header
        pdf.set_y(22)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, "PRAGYANAI INSTITUTIONAL INTELLIGENCE & OUTREACH HUB", 0, 1, "C")

        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 5, "In Collaboration with Autonomous Engineering Centers of Excellence", 0, 1, "C")
        pdf.ln(6)

        # 2. Certificate Title
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(180, 83, 9)  # Deep Amber / Gold
        pdf.cell(0, 10, "CERTIFICATE OF PARTICIPATION", 0, 1, "C")
        pdf.ln(4)

        # 3. Presentation Line
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 6, "This is proudly presented to", 0, 1, "C")
        pdf.ln(4)

        # 4. Student Name
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(29, 78, 216)  # Royal Blue
        pdf.cell(0, 10, student_name.upper(), 0, 1, "C")

        # Decorative underline for candidate name
        pdf.set_draw_color(37, 99, 235)
        pdf.set_line_width(0.5)
        name_width = min(pdf.get_string_width(student_name.upper()) + 20, 180)
        start_x = (297 - name_width) / 2
        pdf.line(start_x, pdf.get_y() + 1, start_x + name_width, pdf.get_y() + 1)
        pdf.ln(6)

        # 5. Course & Institution Statement
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(51, 65, 85)
        text_body = (
            f"representing {institution_name}, for successfully attending and demonstrating "
            f"exceptional engagement in the specialized technical outreach masterclass:"
        )
        pdf.multi_cell(0, 5.5, text_body, 0, "C")
        pdf.ln(2)

        # Event Title
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(0, 6, f'"{event_title}"', 0, "C")
        pdf.ln(12)

        # 6. Signatures and Verification Block
        sig_y = 152
        pdf.set_y(sig_y)

        # Left Signature: Event Speaker / Lead Architect
        pdf.set_x(30)
        pdf.set_draw_color(148, 163, 184)
        pdf.set_line_width(0.3)
        pdf.line(30, sig_y + 12, 105, sig_y + 12)

        pdf.set_xy(30, sig_y + 14)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(75, 4, speaker_name, 0, 1, "C")
        pdf.set_x(30)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(75, 4, speaker_title, 0, 0, "C")

        # Center Badge: Verification ID & Date
        pdf.set_xy(110, sig_y + 4)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(77, 4, "VERIFIED DIGITAL CREDENTIAL", 0, 1, "C")
        pdf.set_x(110)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(77, 3.5, f"Certificate ID: {cert_id}", 0, 1, "C")
        pdf.set_x(110)
        pdf.cell(77, 3.5, f"Date of Issue: {issue_date}", 0, 0, "C")

        # Right Signature: Dean of Outreach / Institutional Advisory
        pdf.set_x(192)
        pdf.line(192, sig_y + 12, 267, sig_y + 12)

        pdf.set_xy(192, sig_y + 14)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(75, 4, "Dr. K. S. Venkatesh Murthy", 0, 1, "C")
        pdf.set_x(192)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(75, 4, "Dean of Outreach & Admissions", 0, 0, "C")

        # 7. Output PDF bytes
        pdf_bytes = io.BytesIO()
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)
        return pdf_bytes


def generate_event_certificate(
    student_name: str,
    event_title: str,
    institution_name: str = "Partner Institution",
    event_date: Optional[str] = None,
) -> io.BytesIO:
    """Convenience helper to construct and return a certificate buffer."""
    return CertificateGenerator.generate(
        student_name=student_name,
        event_title=event_title,
        institution_name=institution_name,
        event_date=event_date,
    )

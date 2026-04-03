import re

from fpdf import FPDF


_REPLACEMENTS = {
    "\u2013": "-",
    "\u2014": "--",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2022": "-",
    "\u2026": "...",
    "\u00a0": " ",
}


def _safe(text):
    """Encode text safely for built-in Latin-1 fonts."""
    if not text:
        return ""
    for old, new in _REPLACEMENTS.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class CVPDF(FPDF):
    """Professional CV PDF layout."""

    ACCENT = (26, 54, 93)
    TEXT = (40, 40, 40)
    LIGHT = (100, 100, 100)
    LH = 4.5  # line height

    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 12, 15)
        self._cw = self.w - 15 - 15  # content width (180mm)

    # -- font helpers --

    def _accent(self, size=10, bold=True):
        self.set_font("Helvetica", "B" if bold else "", size)
        self.set_text_color(*self.ACCENT)

    def _body(self, size=9.5, bold=False):
        self.set_font("Helvetica", "B" if bold else "", size)
        self.set_text_color(*self.TEXT)

    def _italic(self, size=9):
        self.set_font("Helvetica", "I", size)
        self.set_text_color(*self.LIGHT)

    # -- layout helpers --

    def section_header(self, title):
        self.ln(3)
        self._accent(10, bold=True)
        self.cell(0, 5.5, title.upper(), new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.4)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2)

    def bullet_list(self, items, font_size=9.5):
        """Render bullets with properly indented wrapped lines."""
        indent = 7  # text start from left margin
        for item in items:
            self._body(font_size)
            text_x = self.l_margin + indent
            w = self.w - text_x - self.r_margin

            # dash
            self.set_x(self.l_margin + 3)
            self.cell(4, self.LH, "-")

            # text — shift l_margin so multi_cell wraps to indent
            saved = self.l_margin
            self.l_margin = text_x
            self.multi_cell(w, self.LH, _safe(item), new_x="LMARGIN", new_y="NEXT")
            self.l_margin = saved


def generate_cv_pdf(data: dict) -> tuple[bytes, str]:
    """Generate a CV PDF from structured data.

    Returns (pdf_bytes, filename).
    """
    pdf = CVPDF()
    pdf.add_page()

    name = data.get("name", "CV")

    # === NAME ===
    pdf._accent(20, bold=True)
    pdf.cell(0, 10, _safe(name), align="C", new_x="LMARGIN", new_y="NEXT")

    # === CONTACT LINE ===
    contact = data.get("contact", {})
    parts = [
        contact.get(f)
        for f in ("email", "phone", "location", "linkedin", "website")
        if contact.get(f)
    ]
    if parts:
        pdf._italic(9)
        pdf.cell(
            0, 5, "  |  ".join(_safe(p) for p in parts),
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
    pdf.ln(1)

    # === SUMMARY ===
    if data.get("summary"):
        pdf.section_header("Professional Summary")
        pdf._body(9.5)
        pdf.multi_cell(0, pdf.LH, _safe(data["summary"]), new_x="LMARGIN", new_y="NEXT")

    # === EXPERIENCE ===
    experience = data.get("experience", [])
    if experience:
        pdf.section_header("Professional Experience")
        for i, job in enumerate(experience):
            if i > 0:
                pdf.ln(1.5)

            # Line 1: Title -- Company (bold, wraps if long)
            pdf._body(10, bold=True)
            title_line = job.get("title", "")
            if job.get("company"):
                title_line += f" -- {job['company']}"
            pdf.multi_cell(0, 5, _safe(title_line), new_x="LMARGIN", new_y="NEXT")

            # Line 2: Location | Dates (italic)
            meta = []
            if job.get("location"):
                meta.append(job["location"])
            if job.get("dates"):
                meta.append(job["dates"])
            if meta:
                pdf._italic(9)
                pdf.cell(
                    0, pdf.LH, _safe(" | ".join(meta)),
                    new_x="LMARGIN", new_y="NEXT",
                )

            pdf.ln(0.5)
            pdf.bullet_list(job.get("highlights", []))

    # === EDUCATION ===
    education = data.get("education", [])
    if education:
        pdf.section_header("Education")
        for i, edu in enumerate(education):
            if i > 0:
                pdf.ln(1)

            degree_line = edu.get("degree", "")
            if edu.get("institution"):
                degree_line += " -- " + edu["institution"]
            dates = edu.get("dates", "")

            if dates:
                # check if degree + date fit on one line
                pdf._body(9.5, bold=True)
                dw = pdf.get_string_width(_safe(degree_line))
                pdf._italic(8.5)
                tw = pdf.get_string_width(_safe(dates))

                if dw + tw + 10 < pdf._cw:
                    # one line: degree left, date right
                    pdf._body(9.5, bold=True)
                    pdf.cell(0, 5, _safe(degree_line), new_x="LMARGIN", new_y="NEXT")
                    pdf.set_y(pdf.get_y() - 5)
                    pdf._italic(8.5)
                    pdf.cell(0, 5, _safe(dates), align="R", new_x="LMARGIN", new_y="NEXT")
                else:
                    # two lines
                    pdf._body(9.5, bold=True)
                    pdf.multi_cell(0, 5, _safe(degree_line), new_x="LMARGIN", new_y="NEXT")
                    pdf._italic(8.5)
                    pdf.cell(0, pdf.LH, _safe(dates), new_x="LMARGIN", new_y="NEXT")
            else:
                pdf._body(9.5, bold=True)
                pdf.multi_cell(0, 5, _safe(degree_line), new_x="LMARGIN", new_y="NEXT")

            if edu.get("details"):
                pdf._body(9)
                pdf.multi_cell(0, pdf.LH, _safe(edu["details"]), new_x="LMARGIN", new_y="NEXT")

    # === SKILLS ===
    skills = data.get("skills", [])
    if skills:
        pdf.section_header("Technical Skills")
        pdf._body(9)
        pdf.multi_cell(0, pdf.LH, "  |  ".join(_safe(s) for s in skills), new_x="LMARGIN", new_y="NEXT")

    # === ADDITIONAL SECTIONS ===
    for section in data.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        if title and items:
            pdf.section_header(title)
            if len(items) == 1:
                # single item (e.g. Languages) — plain text
                pdf._body(9.5)
                pdf.multi_cell(0, pdf.LH, _safe(items[0]), new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.bullet_list(items, font_size=9)

    pdf_bytes = pdf.output()
    clean_name = re.sub(r"[^\w\s-]", "", name).strip()
    clean_name = re.sub(r"\s+", "_", clean_name)
    filename = f"{clean_name}_CV.pdf" if clean_name else "CV.pdf"

    return pdf_bytes, filename

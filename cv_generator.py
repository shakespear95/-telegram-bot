import os
import re

from fpdf import FPDF

PHOTO_PATH = os.path.join(os.path.dirname(__file__), "photo.jpeg")


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


def generate_cover_letter_pdf(data: dict) -> tuple[bytes, str]:
    """Generate a cover letter PDF from structured data.

    Returns (pdf_bytes, filename).
    """
    pdf = CVPDF()
    pdf.add_page()

    name = data.get("name", "")
    contact = data.get("contact", {})
    job_title = data.get("job_title", "")
    company_name = data.get("company_name", "")
    hiring_manager = data.get("hiring_manager", "Hiring Manager")
    date_str = data.get("date", "")
    paragraphs = data.get("paragraphs", [])

    # === SENDER NAME ===
    pdf._accent(16, bold=True)
    pdf.cell(0, 9, _safe(name), new_x="LMARGIN", new_y="NEXT")

    # === CONTACT LINE ===
    parts = [
        contact.get(f)
        for f in ("email", "phone", "location", "linkedin")
        if contact.get(f)
    ]
    if parts:
        pdf._italic(9)
        pdf.cell(0, 5, "  |  ".join(_safe(p) for p in parts), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_draw_color(*CVPDF.ACCENT)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(5)

    # === DATE ===
    if date_str:
        pdf._italic(9)
        pdf.cell(0, 5, _safe(date_str), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # === RECIPIENT ===
    pdf._body(9.5, bold=True)
    pdf.cell(0, 5, _safe(hiring_manager), new_x="LMARGIN", new_y="NEXT")
    if company_name:
        pdf._body(9.5)
        pdf.cell(0, 5, _safe(company_name), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # === SUBJECT ===
    if job_title:
        pdf._body(10, bold=True)
        subject = f"Re: Application for {job_title}"
        if company_name:
            subject += f" at {company_name}"
        pdf.cell(0, 5.5, _safe(subject), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # === SALUTATION ===
    pdf._body(9.5)
    salutation = f"Dear {hiring_manager},"
    pdf.cell(0, 5, _safe(salutation), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # === BODY PARAGRAPHS ===
    for para in paragraphs:
        if para:
            pdf._body(9.5)
            pdf.multi_cell(0, pdf.LH, _safe(para), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2.5)

    # === SIGN-OFF ===
    pdf.ln(1)
    pdf._body(9.5)
    pdf.cell(0, 5, "Yours sincerely,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf._body(9.5, bold=True)
    pdf.cell(0, 5, _safe(name), new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    clean_name = re.sub(r"[^\w\s-]", "", name).strip()
    clean_name = re.sub(r"\s+", "_", clean_name)
    filename = f"{clean_name}_Cover_Letter.pdf" if clean_name else "Cover_Letter.pdf"

    return pdf_bytes, filename


def generate_dach_cv_pdf(data: dict) -> tuple[bytes, str]:
    """Generate a DACH-format Lebenslauf PDF (Germany/Austria/Switzerland).

    Includes professional photo, personal data block (DOB, nationality),
    CEFR language levels, and signature line.

    Returns (pdf_bytes, filename).
    """
    pdf = CVPDF()
    pdf.add_page()

    name = data.get("name", "CV")
    contact = data.get("contact", {})
    personal = data.get("personal", {})  # dob, nationality, marital_status
    photo_path = PHOTO_PATH if os.path.exists(PHOTO_PATH) else None

    # === HEADER: name left, photo right ===
    PHOTO_W = 30
    PHOTO_H = 38
    name_col_w = pdf._cw - PHOTO_W - 5

    y_before_header = pdf.get_y()

    # Name + contact on the left
    pdf._accent(18, bold=True)
    pdf.cell(name_col_w, 10, _safe(name), new_x="RIGHT", new_y="TOP")
    if photo_path:
        pdf.image(photo_path, x=pdf.w - pdf.r_margin - PHOTO_W, y=y_before_header, w=PHOTO_W, h=PHOTO_H)
    pdf.ln(10)

    # Contact details below name
    contact_fields = [
        ("Adresse", contact.get("location")),
        ("Telefon", contact.get("phone")),
        ("E-Mail", contact.get("email")),
        ("LinkedIn", contact.get("linkedin")),
    ]
    for label, value in contact_fields:
        if value:
            pdf._body(9, bold=True)
            pdf.cell(28, pdf.LH, _safe(label + ":"), new_x="RIGHT", new_y="TOP")
            pdf._body(9)
            pdf.cell(name_col_w - 28, pdf.LH, _safe(value), new_x="LMARGIN", new_y="NEXT")

    # Personal data (DOB, nationality, marital status)
    personal_fields = [
        ("Geburtsdatum", personal.get("dob")),
        ("Nationalitat", personal.get("nationality")),
        ("Familienstand", personal.get("marital_status")),
    ]
    for label, value in personal_fields:
        if value:
            pdf._body(9, bold=True)
            pdf.cell(28, pdf.LH, _safe(label + ":"), new_x="RIGHT", new_y="TOP")
            pdf._body(9)
            pdf.cell(name_col_w - 28, pdf.LH, _safe(value), new_x="LMARGIN", new_y="NEXT")

    # Ensure we clear the photo space before continuing
    photo_bottom = y_before_header + PHOTO_H + 3
    if pdf.get_y() < photo_bottom:
        pdf.set_y(photo_bottom)

    # === SUMMARY / PROFIL ===
    if data.get("summary"):
        pdf.section_header("Profil")
        pdf._body(9.5)
        pdf.multi_cell(0, pdf.LH, _safe(data["summary"]), new_x="LMARGIN", new_y="NEXT")

    # === BERUFSERFAHRUNG (Experience) ===
    experience = data.get("experience", [])
    if experience:
        pdf.section_header("Berufserfahrung")
        for i, job in enumerate(experience):
            if i > 0:
                pdf.ln(1.5)

            # Dates on the left, title + company on the right
            dates = _safe(job.get("dates", ""))
            title_line = job.get("title", "")
            if job.get("company"):
                title_line += f" -- {job['company']}"

            DATE_COL = 32
            pdf._italic(9)
            pdf.cell(DATE_COL, 5, dates, new_x="RIGHT", new_y="TOP")
            pdf._body(10, bold=True)
            pdf.multi_cell(pdf._cw - DATE_COL, 5, _safe(title_line), new_x="LMARGIN", new_y="NEXT")

            if job.get("location"):
                pdf.set_x(pdf.l_margin + DATE_COL)
                pdf._italic(9)
                pdf.cell(0, pdf.LH, _safe(job["location"]), new_x="LMARGIN", new_y="NEXT")

            pdf.ln(0.5)
            pdf.bullet_list(job.get("highlights", []))

    # === AUSBILDUNG (Education) ===
    education = data.get("education", [])
    if education:
        pdf.section_header("Ausbildung")
        for i, edu in enumerate(education):
            if i > 0:
                pdf.ln(1)

            dates = _safe(edu.get("dates", ""))
            degree_line = edu.get("degree", "")
            if edu.get("institution"):
                degree_line += " -- " + edu["institution"]

            DATE_COL = 32
            pdf._italic(9)
            pdf.cell(DATE_COL, 5, dates, new_x="RIGHT", new_y="TOP")
            pdf._body(9.5, bold=True)
            pdf.multi_cell(pdf._cw - DATE_COL, 5, _safe(degree_line), new_x="LMARGIN", new_y="NEXT")

            if edu.get("details"):
                pdf.set_x(pdf.l_margin + DATE_COL)
                pdf._body(9)
                pdf.multi_cell(pdf._cw - DATE_COL, pdf.LH, _safe(edu["details"]), new_x="LMARGIN", new_y="NEXT")

    # === KENNTNISSE (Skills) ===
    skills = data.get("skills", [])
    if skills:
        pdf.section_header("Kenntnisse")
        pdf._body(9)
        pdf.multi_cell(0, pdf.LH, "  |  ".join(_safe(s) for s in skills), new_x="LMARGIN", new_y="NEXT")

    # === SPRACHEN (Languages with CEFR) ===
    languages = data.get("languages", [])
    if languages:
        pdf.section_header("Sprachen")
        for lang in languages:
            pdf._body(9, bold=True)
            pdf.cell(40, pdf.LH, _safe(lang.get("language", "")), new_x="RIGHT", new_y="TOP")
            pdf._body(9)
            pdf.cell(0, pdf.LH, _safe(lang.get("level", "")), new_x="LMARGIN", new_y="NEXT")

    # === ADDITIONAL SECTIONS ===
    for section in data.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        if title and items:
            pdf.section_header(title)
            if len(items) == 1:
                pdf._body(9.5)
                pdf.multi_cell(0, pdf.LH, _safe(items[0]), new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.bullet_list(items, font_size=9)

    # === SIGNATURE LINE ===
    pdf.ln(8)
    pdf._italic(9)
    location = contact.get("location", "St. Gallen")
    city = location.split(",")[0].strip() if location else "St. Gallen"
    pdf.cell(0, 5, _safe(f"{city}, 13. Juni 2026"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf._body(9.5, bold=True)
    pdf.cell(0, 5, _safe(name), new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    clean_name = re.sub(r"[^\w\s-]", "", name).strip()
    clean_name = re.sub(r"\s+", "_", clean_name)
    filename = f"{clean_name}_Lebenslauf.pdf" if clean_name else "Lebenslauf.pdf"

    return pdf_bytes, filename

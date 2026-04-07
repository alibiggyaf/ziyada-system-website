from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import requests
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from bs4 import BeautifulSoup
from fpdf import FPDF


BASE_LOCAL = "http://localhost:5173"
BASE_PROD = "https://www.ziyada-system.com"
OUT_DIR = Path("outputs/geo-audit")
REPORT_MD = OUT_DIR / "GEO-AUDIT-REPORT-AR.md"
REPORT_PDF = OUT_DIR / "GEO-AUDIT-REPORT-AR.pdf"


def ar_text(text: str) -> str:
    return get_display(reshape(text))


def soften_long_tokens(text: str, limit: int = 55) -> str:
    parts = text.split()
    fixed: List[str] = []
    for part in parts:
        if len(part) <= limit:
            fixed.append(part)
            continue
        chunks = [part[i : i + limit] for i in range(0, len(part), limit)]
        fixed.append(" ".join(chunks))
    return " ".join(fixed)


def safe_pdf_line(pdf: FPDF, text: str, line_h: float = 6.0) -> None:
    pdf.set_x(pdf.l_margin)
    try:
        pdf.multi_cell(0, line_h, ar_text(text), align="R")
    except Exception:
        # Fallback: aggressively normalize punctuation/links and split into short chunks.
        normalized = re.sub(r"https?://\S+", "link", text)
        normalized = re.sub(r"[`|\\]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if not normalized:
            pdf.ln(2)
            return
        chunk_size = 45
        for i in range(0, len(normalized), chunk_size):
            chunk = normalized[i : i + chunk_size]
            try:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, line_h, ar_text(chunk), align="R")
            except Exception:
                # Last resort: emit ASCII-safe content.
                ascii_chunk = re.sub(r"[^\x20-\x7E\u0600-\u06FF]", " ", chunk)
                ascii_chunk = re.sub(r"\s+", " ", ascii_chunk).strip() or "-"
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, line_h, ascii_chunk, align="R")


def fetch(url: str, timeout: int = 15) -> Tuple[int, str]:
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code, resp.text
    except Exception:
        return 0, ""


def parse_sitemap(xml_text: str) -> List[str]:
    if not xml_text.strip():
        return []
    soup = BeautifulSoup(xml_text, "xml")
    urls: List[str] = []
    for loc in soup.find_all("loc"):
        href = (loc.text or "").strip()
        if href:
            urls.append(href)
    return urls


def to_local(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return f"{BASE_LOCAL}{path}"


@dataclass
class PageData:
    url: str
    status: int
    title: str
    meta_description: str
    canonical: str
    h1_count: int
    h2_count: int
    word_count: int
    has_faq_signal: bool
    schema_types: List[str]
    has_open_graph: bool
    has_twitter_card: bool
    has_author_signal: bool
    internal_links: int
    external_links: int


def analyze_page(local_url: str) -> PageData:
    status, html = fetch(local_url)
    soup = BeautifulSoup(html or "", "lxml")

    def sel_text(selector: str, attr: str | None = None) -> str:
        el = soup.select_one(selector)
        if not el:
            return ""
        if attr:
            return (el.get(attr) or "").strip()
        return el.get_text(" ", strip=True)

    title = sel_text("title")
    meta_description = sel_text("meta[name='description']", "content")
    canonical = sel_text("link[rel='canonical']", "href")

    text = soup.get_text(" ", strip=True)
    words = re.findall(r"[\w\u0600-\u06FF]+", text)

    jsonld_blocks = [
        (s.get_text(" ", strip=True) or "")
        for s in soup.select("script[type='application/ld+json']")
    ]
    schema_types: List[str] = []
    for block in jsonld_blocks:
        block = block.strip()
        if not block:
            continue
        try:
            payload = json.loads(block)
            items = payload if isinstance(payload, list) else [payload]
            for item in items:
                t = item.get("@type") if isinstance(item, dict) else None
                if isinstance(t, list):
                    schema_types.extend([str(v) for v in t])
                elif isinstance(t, str):
                    schema_types.append(t)
        except Exception:
            continue

    internal = 0
    external = 0
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        if href.startswith("/"):
            internal += 1
        elif "ziyada-system.com" in href or "localhost:5173" in href:
            internal += 1
        elif href.startswith("http"):
            external += 1

    text_lower = text.lower()
    faq_signal = ("faq" in text_lower) or ("الأسئلة الشائعة" in text)
    author_signal = any(k in text for k in ["الكاتب", "بقلم", "المحرر", "فريق", "عن الشركة"])

    return PageData(
        url=local_url,
        status=status,
        title=title,
        meta_description=meta_description,
        canonical=canonical,
        h1_count=len(soup.select("h1")),
        h2_count=len(soup.select("h2")),
        word_count=len(words),
        has_faq_signal=faq_signal,
        schema_types=sorted(set(schema_types)),
        has_open_graph=bool(soup.select_one("meta[property='og:title']")),
        has_twitter_card=bool(soup.select_one("meta[name='twitter:card']")),
        has_author_signal=author_signal,
        internal_links=internal,
        external_links=external,
    )


def clamp(v: float) -> int:
    return int(max(0, min(100, round(v))))


def compute_scores(pages: List[PageData], robots_ok: bool, llms_exists: bool) -> Dict[str, int]:
    ok_pages = [p for p in pages if 200 <= p.status < 400]
    ok_ratio = (len(ok_pages) / len(pages)) if pages else 0
    avg_words = (sum(p.word_count for p in ok_pages) / len(ok_pages)) if ok_pages else 0
    schema_pages = sum(1 for p in ok_pages if p.schema_types)
    twitter_pages = sum(1 for p in ok_pages if p.has_twitter_card)
    og_pages = sum(1 for p in ok_pages if p.has_open_graph)
    faq_pages = sum(1 for p in ok_pages if p.has_faq_signal)
    author_pages = sum(1 for p in ok_pages if p.has_author_signal)
    ext_links = sum(p.external_links for p in ok_pages)

    citability = clamp(35 + (20 if avg_words >= 250 else avg_words / 12) + (15 if faq_pages > 0 else 0) + (15 if og_pages > 0 else 0) + (15 * ok_ratio))
    brand = clamp(30 + min(30, ext_links * 4) + (20 if any("about" in p.url.lower() for p in ok_pages) else 0) + (20 if any("contact" in p.url.lower() for p in ok_pages) else 0))
    eeat = clamp(35 + (20 if any("about" in p.url.lower() for p in ok_pages) else 0) + (15 if any("privacy" in p.url.lower() for p in ok_pages) else 0) + (15 if any("terms" in p.url.lower() for p in ok_pages) else 0) + min(15, author_pages * 5))
    technical = clamp(30 + (30 * ok_ratio) + (20 if robots_ok else 0) + (20 if llms_exists else 0))
    schema = clamp(20 + (40 * (schema_pages / len(ok_pages) if ok_pages else 0)) + min(20, len(set(t for p in ok_pages for t in p.schema_types)) * 8) + (20 if any("Organization" in p.schema_types for p in ok_pages) else 0))
    platform = clamp(25 + (15 if any("blog" in p.url.lower() for p in ok_pages) else 0) + (15 if faq_pages > 0 else 0) + (20 if twitter_pages > 0 else 0) + (25 if ext_links >= 3 else ext_links * 5))

    return {
        "AI Citability": citability,
        "Brand Authority": brand,
        "Content E-E-A-T": eeat,
        "Technical GEO": technical,
        "Schema & Structured Data": schema,
        "Platform Optimization": platform,
    }


def weighted_total(scores: Dict[str, int]) -> float:
    return (
        scores["AI Citability"] * 0.25
        + scores["Brand Authority"] * 0.20
        + scores["Content E-E-A-T"] * 0.20
        + scores["Technical GEO"] * 0.15
        + scores["Schema & Structured Data"] * 0.10
        + scores["Platform Optimization"] * 0.10
    )


def band(score: float) -> str:
    if score >= 90:
        return "ممتاز"
    if score >= 75:
        return "جيد"
    if score >= 60:
        return "مقبول"
    if score >= 40:
        return "ضعيف"
    return "حرج"


def make_markdown(
    pages: List[PageData],
    scores: Dict[str, int],
    overall: float,
    robots_text: str,
    llms_exists: bool,
) -> str:
    today = date.today().isoformat()
    pages_ok = [p for p in pages if 200 <= p.status < 400]
    top_schema = sorted(set(t for p in pages_ok for t in p.schema_types))

    critical: List[str] = []
    high: List[str] = []
    medium: List[str] = []
    low: List[str] = []

    if not llms_exists:
        high.append("غياب ملف llms.txt (يرجع 404) مما يقلل قابلية التوجيه لمحركات الذكاء الاصطناعي.")
    if any(p.status >= 500 for p in pages):
        critical.append("وجود صفحات بخطأ 5xx ضمن العينة المفحوصة.")
    if not any(p.has_twitter_card for p in pages_ok):
        medium.append("لا توجد وسوم Twitter Card على الصفحات الرئيسية.")
    if len(top_schema) <= 1:
        high.append("البيانات المنظمة محدودة (غالبا Organization فقط) وتحتاج توسيع إلى WebSite/Service/FAQPage.")
    if "Disallow: /youtube-trends" in robots_text:
        low.append("تحقق من أن مسارات المنع في robots.txt لا تحجب صفحات تسويقية مهمة بالخطأ.")

    if not critical:
        critical.append("لم يتم رصد مشكلة حرجة على مستوى HTTP في العينة الحالية، مع بقاء رصد أخطاء runtime في الواجهة أولوية تقنية.")

    rows = "\n".join(
        [
            f"| AI Citability | {scores['AI Citability']}/100 | 25% | {scores['AI Citability']*0.25:.1f} |",
            f"| Brand Authority | {scores['Brand Authority']}/100 | 20% | {scores['Brand Authority']*0.20:.1f} |",
            f"| Content E-E-A-T | {scores['Content E-E-A-T']}/100 | 20% | {scores['Content E-E-A-T']*0.20:.1f} |",
            f"| Technical GEO | {scores['Technical GEO']}/100 | 15% | {scores['Technical GEO']*0.15:.1f} |",
            f"| Schema & Structured Data | {scores['Schema & Structured Data']}/100 | 10% | {scores['Schema & Structured Data']*0.10:.1f} |",
            f"| Platform Optimization | {scores['Platform Optimization']}/100 | 10% | {scores['Platform Optimization']*0.10:.1f} |",
        ]
    )

    page_table = "\n".join(
        f"| {p.url} | {p.status} | {p.h1_count} | {p.h2_count} | {p.word_count} | {', '.join(p.schema_types) if p.schema_types else '-'} |"
        for p in pages
    )

    return f"""# تقرير تدقيق GEO الشامل: Ziyada Systems

**تاريخ التدقيق:** {today}  
**الرابط المفحوص:** {BASE_LOCAL}/Home  
**نوع النشاط:** وكالة/خدمات نمو رقمي (Agency/Services)  
**عدد الصفحات المفحوصة:** {len(pages)}

---

## الملخص التنفيذي

**النتيجة الكلية GEO: {overall:.1f}/100 ({band(overall)})**

يُظهر الموقع أساسًا قويًا في وضوح الرسالة التجارية والمحتوى العربي الموجّه للتحويل، مع بنية تنقّل وخريطة موقع جيدة.
الفرص الأعلى تأثيرًا تتركز في توسيع البيانات المنظمة، إضافة llms.txt، وتحسين جاهزية المنصات (خاصة Twitter Cards والإشارات المرجعية متعددة المنصات).

### تفصيل الدرجات

| الفئة | الدرجة | الوزن | الدرجة الموزونة |
|---|---:|---:|---:|
{rows}
| **الإجمالي** |  |  | **{overall:.1f}/100** |

---

## القضايا الحرجة (إصلاح فوري)

""" + "\n".join(f"- {x}" for x in critical) + f"""

## القضايا عالية الأولوية (خلال أسبوع)

""" + "\n".join(f"- {x}" for x in high) + f"""

## القضايا متوسطة الأولوية (خلال شهر)

""" + "\n".join(f"- {x}" for x in medium) + f"""

## القضايا منخفضة الأولوية

""" + "\n".join(f"- {x}" for x in low) + f"""

---

## تحليل الصفحات المفحوصة

| الصفحة | HTTP | H1 | H2 | Word Count | Schema Types |
|---|---:|---:|---:|---:|---|
{page_table}

---

## التعمق حسب الفئات

### 1) AI Citability ({scores['AI Citability']}/100)
- نقاط قوة: عناوين واضحة، رسائل قيمة مباشرة، CTA واضح.
- فرص: إضافة مقاطع Q&A أكثر صراحة في الصفحات الخدمية، وتضمين أدلة/أرقام موثقة لكل خدمة.

### 2) Brand Authority ({scores['Brand Authority']}/100)
- نقاط قوة: تموضع علامة واضح وهوية متسقة.
- فرص: زيادة الإشارات الخارجية (LinkedIn/YouTube/Medium/Reddit) وربطها داخل الموقع.

### 3) Content E-E-A-T ({scores['Content E-E-A-T']}/100)
- نقاط قوة: خطاب خبراتي واضح، صفحات قانونية وروابط ثقة أساسية.
- فرص: تعزيز صفحات الفريق/الخبراء بسير عملية وشهادات/دراسات حالة.

### 4) Technical GEO ({scores['Technical GEO']}/100)
- نقاط قوة: robots.txt و sitemap.xml متاحان.
- فرص: إضافة llms.txt، ومراجعة أي أخطاء runtime/API قد تؤثر على استقرار العرض.

### 5) Schema & Structured Data ({scores['Schema & Structured Data']}/100)
- نقاط قوة: وجود Organization schema.
- فرص: إضافة WebSite + Service + FAQPage + BreadcrumbList حسب الصفحة.

### 6) Platform Optimization ({scores['Platform Optimization']}/100)
- نقاط قوة: محتوى خدمات واضح وسهل الالتقاط.
- فرص: تحسين meta/social graph لكل صفحة خدمة وإضافة أصول محتوى قابلة للاقتباس في المنصات.

---

## Quick Wins (هذا الأسبوع)

1. إنشاء ملف llms.txt في الجذر مع روابط الصفحات الرئيسية والسياسات.
2. إضافة Twitter Card tags لكل الصفحات الأساسية.
3. تحويل `og:image` إلى رابط مطلق production.
4. إدراج JSON-LD من نوع Service لكل صفحة خدمة.
5. إضافة FAQ schema حيث توجد أسئلة متكررة.

## خطة 30 يوم

1. الأسبوع 1: إصلاح metadata والـ schema الأساسية + llms.txt.
2. الأسبوع 2: تحديث صفحات الخدمات بمقاطع قابلة للاقتباس (Problems/Solutions/Outcomes).
3. الأسبوع 3: بناء صفحات خبراء/دراسات حالة مع إشارات ثقة موثقة.
4. الأسبوع 4: قياس تأثير التحسينات ومقارنة النتيجة قبل/بعد.

---

## ملاحظة منهجية

تم الالتزام بوزن التقييم المعتمد في مهارة GEO Audit:
AI Citability 25%، Brand Authority 20%، E-E-A-T 20%، Technical 15%، Schema 10%، Platform 10%.
"""


class GeoPDF(FPDF):
    def header(self) -> None:
        self.set_fill_color(15, 23, 42)  # #0f172a
        self.rect(0, 0, 210, 24, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("AR", size=12)
        self.set_xy(10, 8)
        self.cell(190, 8, ar_text("تقرير GEO الشامل - Ziyada Systems"), align="R")
        self.ln(14)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_text_color(120, 120, 120)
        self.set_font("AR", size=9)
        self.cell(0, 6, ar_text(f"صفحة {self.page_no()}"), align="C")


def pick_arabic_font() -> str:
    candidates = [
        "/System/Library/Fonts/Supplemental/Geeza Pro.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise FileNotFoundError("No Arabic-capable font found on this macOS machine.")


def markdown_to_pdf(md: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(md, encoding="utf-8")

    font_path = pick_arabic_font()
    pdf = GeoPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("AR", fname=font_path)
    pdf.add_page()

    accent = (59, 130, 246)  # #3b82f6

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line:
            pdf.ln(3)
            continue

        if line.startswith("# "):
            pdf.set_text_color(*accent)
            pdf.set_font("AR", size=15)
            safe_pdf_line(pdf, line[2:], line_h=8)
            pdf.set_text_color(20, 20, 20)
            continue

        if line.startswith("## "):
            pdf.set_text_color(15, 23, 42)
            pdf.set_font("AR", size=13)
            safe_pdf_line(pdf, line[3:], line_h=7)
            pdf.set_text_color(20, 20, 20)
            continue

        if line.startswith("### "):
            pdf.set_font("AR", size=12)
            pdf.set_text_color(30, 58, 138)
            safe_pdf_line(pdf, line[4:], line_h=6.5)
            pdf.set_text_color(20, 20, 20)
            continue

        if line.startswith("|"):
            # Render markdown tables as plain right-aligned lines for simplicity.
            cleaned = re.sub(r"\|", " | ", line)
            cleaned = re.sub(r"https?://\S+", "[link]", cleaned)
            cleaned = soften_long_tokens(cleaned, limit=40)
            pdf.set_font("AR", size=9)
            safe_pdf_line(pdf, cleaned, line_h=5)
            continue

        if line.startswith("- "):
            pdf.set_font("AR", size=11)
            safe_pdf_line(pdf, "• " + line[2:], line_h=6)
            continue

        if re.match(r"^\d+\.\s", line):
            pdf.set_font("AR", size=11)
            safe_pdf_line(pdf, line, line_h=6)
            continue

        rendered = soften_long_tokens(re.sub(r"https?://\S+", "[link]", line), limit=55)
        pdf.set_font("AR", size=11)
        safe_pdf_line(pdf, rendered, line_h=6)

    pdf.output(str(REPORT_PDF))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    robots_status, robots_text = fetch(f"{BASE_LOCAL}/robots.txt")
    llms_status, _llms_text = fetch(f"{BASE_LOCAL}/llms.txt")
    sitemap_status, sitemap_xml = fetch(f"{BASE_LOCAL}/sitemap.xml")

    sitemap_urls = parse_sitemap(sitemap_xml) if sitemap_status == 200 else []
    if not sitemap_urls:
        sitemap_urls = [f"{BASE_PROD}/Home", f"{BASE_PROD}/Services", f"{BASE_PROD}/About", f"{BASE_PROD}/Contact", f"{BASE_PROD}/Blog"]

    selected_prod = []
    # Keep homepage + key business pages first.
    priority_patterns = ["/Home", "/Services", "/About", "/Contact", "/Blog", "/FAQ", "/Privacy", "/Terms"]
    for pat in priority_patterns:
        for u in sitemap_urls:
            if u not in selected_prod and pat in u:
                selected_prod.append(u)
    for u in sitemap_urls:
        if u not in selected_prod:
            selected_prod.append(u)
    selected_prod = selected_prod[:15]

    pages = [analyze_page(to_local(u)) for u in selected_prod]

    scores = compute_scores(
        pages=pages,
        robots_ok=(robots_status == 200 and "Allow: /" in robots_text),
        llms_exists=(llms_status == 200),
    )
    overall = weighted_total(scores)
    md = make_markdown(
        pages=pages,
        scores=scores,
        overall=overall,
        robots_text=robots_text,
        llms_exists=(llms_status == 200),
    )
    markdown_to_pdf(md)

    print(f"Markdown report: {REPORT_MD}")
    print(f"PDF report: {REPORT_PDF}")
    print(f"Overall GEO score: {overall:.1f}/100")


if __name__ == "__main__":
    main()

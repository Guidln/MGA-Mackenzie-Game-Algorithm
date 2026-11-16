"""Gera os documentos do projeto (DOCX e PDF) no layout do relatório da Etapa 3:
A4, Times New Roman 12, justificado, espaçamento 1,5, margens ABNT (3/2/3/2 cm), número de página no alto à direita,
legendas em negrito acima e 'Fonte:' abaixo. Requer pandoc, python-docx e LibreOffice (soffice).
Uso: python docs/build_docs.py"""
import copy, os, re, subprocess, sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entrega"); os.makedirs(OUT, exist_ok=True)
TMP = "/tmp/mga_build"; os.makedirs(TMP, exist_ok=True)
FONT = "Times New Roman"
AUTORES = ["Bruna Graciano", "Guilherme Marques Gomes dos Santos", "Guilherme Barros Toledo Batista", "Lincoln Cavalcanti Bertoldo Alves"]
FONTE_FIG = {**{n: "Fonte: elaboração própria (2026)." for n in range(20, 25)}, 11: "Fonte: elaboração própria (2026).", 19: "Fonte: elaboração própria, aba Consultas_Top5 da planilha MGA_Resultados_Etapa3.xlsx (execução de 29/10/2026)."}
FONTE_PADRAO = "Fonte: elaboração própria, saída do script mga_etapa3.py (execução de 29/10/2026)."


def set_font(style, size=12, bold=None, italic=None):
    style.font.name = FONT; style.font.size = Pt(size); style.font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None: style.font.bold = bold
    if italic is not None: style.font.italic = italic
    rpr = style.element.get_or_add_rPr()
    for c in rpr.findall(qn("w:color")):
        for a in ("w:themeColor", "w:themeShade", "w:themeTint"):
            if c.get(qn(a)) is not None: del c.attrib[qn(a)]
        c.set(qn("w:val"), "000000")
    rf = rpr.find(qn("w:rFonts"))
    if rf is None: rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), FONT)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]


def para_fmt(style, align=None, first=None, before=0, after=0, line=1.5, left=None):
    pf = style.paragraph_format
    if align is not None: pf.alignment = align
    if first is not None: pf.first_line_indent = first
    if left is not None: pf.left_indent = left
    pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = line


def make_reference():
    ref = os.path.join(TMP, "ref.docx")
    open(ref, "wb").write(subprocess.check_output(["pandoc", "--print-default-data-file", "reference.docx"]))
    d = Document(ref); st = d.styles
    def S(n):
        for x in st:
            if x.name.lower() == n.lower(): return x
        return None
    for n in ("Normal", "Body Text", "First Paragraph"):
        s = S(n)
        if s: set_font(s); para_fmt(s, WD_ALIGN_PARAGRAPH.JUSTIFY, Cm(1.25), 0, 0, 1.5)
    for n in ("Compact", "Block Text"):
        s = S(n)
        if s: set_font(s); para_fmt(s, WD_ALIGN_PARAGRAPH.JUSTIFY, Cm(0), 0, 0, 1.5)
    for n in ("Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        s = S(n)
        if s:
            set_font(s, 12, bold=True, italic=False); para_fmt(s, WD_ALIGN_PARAGRAPH.LEFT, Cm(0), 18, 0, 1.5)
            s.paragraph_format.keep_with_next = True
    for n in ("Verbatim Char", "Hyperlink"):
        s = S(n)
        if s: set_font(s)
    s = S("Image Caption")
    if s: set_font(s, 10, bold=True); para_fmt(s, WD_ALIGN_PARAGRAPH.CENTER, Cm(0), 0, 0, 1.0)
    d.save(ref); return ref


def add_field(par, instr):
    for t, txt in (("begin", None), (None, instr), ("end", None)):
        r = par.add_run(); r.font.name = FONT; r.font.size = Pt(12)
        if t:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), t); r._r.append(f)
        else:
            i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve"); i.text = txt; r._r.append(i)


def prepare_md(path, numerar):
    s = open(path, encoding="utf-8").read()
    m = re.search(r"^# (.+)$", s, re.M); titulo = m.group(1).strip() if m else ""
    if "## 8 RESULTADOS" in s: s = s[s.index("## 8 RESULTADOS"):]
    elif m: s = s[m.end():]
    s = re.sub(r"^---\s*$", "", s, flags=re.M)
    s = re.sub(r"^\*\*Link do vídeo no YouTube:\*\*", "**Link do vídeo no YouTube:**", s, flags=re.M)
    if numerar:
        n1 = n2 = 0; out = []
        for ln in s.split("\n"):
            if ln.startswith("## "): n1 += 1; n2 = 0; ln = f"## {n1} {ln[3:].upper()}"
            elif ln.startswith("### "): n2 += 1; ln = f"### {n1}.{n2} {ln[4:]}"
            out.append(ln)
        s = "\n".join(out)
    def img(mm):
        nome = mm.group(2); w = "11cm" if "fluxograma" in nome else ("13cm" if "sensib" in nome else "15cm")
        return f"![{mm.group(1)}]({nome}){{width={w}}}"
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, s)
    return titulo, s


def cover(doc, subtitulo):
    body = doc.element.body; first = body[0]
    def P(text, bold=False, size=12, before=0, after=0, align=WD_ALIGN_PARAGRAPH.CENTER, brk=False):
        p = doc.add_paragraph(); pf = p.paragraph_format
        pf.alignment = align; pf.first_line_indent = Cm(0); pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = 1.5
        r = p.add_run(text); r.bold = bold; r.font.size = Pt(size); r.font.name = FONT
        if brk: r.add_break(WD_BREAK.PAGE)
        first.addprevious(p._p); return p
    P("UNIVERSIDADE PRESBITERIANA MACKENZIE", True)
    for k, a in enumerate(AUTORES): P(a, before=90 if k == 0 else 0)
    P("MGA – MACKENZIE GAME ALGORITHM", True, 14, before=112)
    P("Sistema de recomendação de jogos digitais baseado em conteúdo")
    P(subtitulo)
    P("São Paulo", before=150); P("2026", brk=True)


def tabelas(doc):
    W = 16.0
    for t in doc.tables:
        rows = t.rows; ncol = len(t.columns)
        if ncol == 0: continue
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        pr = t._tbl.tblPr
        for tag in ("w:tblBorders", "w:tblLayout", "w:tblW"):
            for e in pr.findall(qn(tag)): pr.remove(e)
        b = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "808080"); b.append(e)
        pr.append(b)
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); pr.append(lay)
        tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(W * 567))); tw.set(qn("w:type"), "dxa"); pr.append(tw)
        lens = [0] * ncol
        for r in rows:
            for j, c in enumerate(r.cells[:ncol]): lens[j] += len(c.text)
        w = [min(max(l / max(len(rows), 1), 8), 70) ** 0.8 for l in lens]; tot = sum(w)
        wd = [int(W * 567 * x / tot) for x in w]
        grid = t._tbl.tblGrid
        for j, gc in enumerate(grid.findall(qn("w:gridCol"))): gc.set(qn("w:w"), str(wd[j]))
        size = 8.5 if ncol >= 5 else 9.5
        for i, r in enumerate(rows):
            for j, c in enumerate(r.cells[:ncol]):
                c.width = Cm(W * wd[j] / (W * 567))
                tcpr = c._tc.get_or_add_tcPr()
                if i == 0:
                    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), "E6E6E6"); tcpr.append(sh)
                for p in c.paragraphs:
                    pf = p.paragraph_format; pf.first_line_indent = Cm(0); pf.line_spacing = 1.0; pf.space_before = Pt(2); pf.space_after = Pt(2)
                    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.size = Pt(size); run.font.name = FONT
                        if i == 0: run.bold = True
        if rows:
            trpr = rows[0]._tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); trpr.append(h)


def legendas(doc):
    pat = re.compile(r"^(Tabela|Quadro|Figura) \d+ – ")
    for p in doc.paragraphs:
        txt = p.text.strip()
        if pat.match(txt) and len(txt) < 400 and not p._p.xpath(".//w:drawing"):
            pf = p.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.CENTER; pf.first_line_indent = Cm(0)
            pf.line_spacing = 1.0; pf.space_before = Pt(12); pf.space_after = Pt(6); pf.keep_with_next = True
            for r in p.runs: r.bold = True; r.font.size = Pt(10)
        elif txt.startswith("Fonte:"):
            pf = p.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.CENTER; pf.first_line_indent = Cm(0)
            pf.line_spacing = 1.0; pf.space_before = Pt(6); pf.space_after = Pt(12)
            for r in p.runs: r.font.size = Pt(10); r.bold = False
    paras = list(doc.paragraphs)
    for i, p in enumerate(paras[:-1]):
        nxt = paras[i + 1]
        if p._p.xpath(".//w:drawing") and re.match(r"^Figura \d+", nxt.text.strip()):
            n = int(re.match(r"^Figura (\d+)", nxt.text.strip()).group(1))
            full = nxt.text.strip(); mm = re.match(r"^(.*?)\.\s+(.+)$", full)
            titulo, resto = (mm.group(1), mm.group(2)) if mm else (full.rstrip("."), "")
            nxt.clear(); r = nxt.add_run(titulo); r.bold = True; r.font.size = Pt(10); r.font.name = FONT
            nxt.paragraph_format.keep_with_next = True
            pf = p.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.CENTER; pf.first_line_indent = Cm(0); pf.line_spacing = 1.0
            pf.space_before = Pt(0); pf.space_after = Pt(0); pf.keep_with_next = True
            p._p.addprevious(nxt._p)
            f = doc.add_paragraph(FONTE_FIG.get(n, FONTE_PADRAO))
            fp = f.paragraph_format; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER; fp.first_line_indent = Cm(0); fp.line_spacing = 1.0
            fp.space_before = Pt(6); fp.space_after = Pt(12)
            for r in f.runs: r.font.size = Pt(10); r.font.name = FONT
            p._p.addnext(f._p)
            if resto:
                b = doc.add_paragraph(resto, style="Body Text"); f._p.addnext(b._p)


def pagina(doc, com_capa, inicio):
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin, s.right_margin, s.top_margin, s.bottom_margin = Cm(3), Cm(2), Cm(3), Cm(2)
    s.header_distance = Cm(1.25); s.footer_distance = Cm(1.25)
    s.different_first_page_header_footer = com_capa
    hp = s.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; hp.text = ""; add_field(hp, "PAGE")
    if inicio:
        pg = OxmlElement("w:pgNumType"); pg.set(qn("w:start"), str(inicio)); s._sectPr.append(pg)


def construir(md, nome, subtitulo, capa=True, inicio=None, numerar=True, saida=None, outdir=None, anexo=None, sem_numero_1a=False):
    outdir = outdir or OUT
    titulo, s = prepare_md(os.path.join(HERE, md), numerar)
    src = os.path.join(TMP, nome + ".md"); open(src, "w", encoding="utf-8").write(s)
    dst = os.path.join(TMP, nome + ".docx")
    subprocess.check_call(["pandoc", src, "-f", "markdown-implicit_figures", "-o", dst, "--reference-doc", REF,
                           "--shift-heading-level-by=-1", f"--resource-path={HERE}"])
    d = Document(dst); pagina(d, capa or sem_numero_1a, inicio); tabelas(d); legendas(d)
    if anexo:
        t = d.add_paragraph(); pf = t.paragraph_format; pf.alignment = WD_ALIGN_PARAGRAPH.CENTER; pf.first_line_indent = Cm(0); pf.space_after = Pt(6); pf.line_spacing = 1.5
        r = t.add_run(anexo); r.bold = True; r.font.size = Pt(12); r.font.name = FONT
        d.element.body[0].addprevious(t._p)
    if capa: cover(d, subtitulo)
    final = os.path.join(outdir, (saida or nome) + ".docx"); d.save(final)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, final], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=200)
    print("ok", saida or nome)
    return final[:-5] + ".pdf"


REF = make_reference()
if __name__ == "__main__":
    construir("relatorio_final.md", "MGA_Relatorio_Etapa4", "Projeto Aplicado III – Etapa 4 (Resultados, Conclusão e Trabalhos Futuros)", numerar=False)
    construir("relatorio_final.md", "MGA_Relatorio_Secoes_8_9", "", capa=False, inicio=28, numerar=False)
    construir("Canvas_Projeto_MGA.md", "Canvas_Projeto_MGA", "Projeto Aplicado III – Documentação do projeto (Canvas)")
    construir("metodologia.md", "Metodologia", "Projeto Aplicado III – Documento de metodologia")
    construir("plano_testes.md", "Plano_de_Testes", "Projeto Aplicado III – Plano e registro de testes")

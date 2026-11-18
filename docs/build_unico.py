"""Monta o PDF único da entrega: índice + relatório (Etapa 3 + seções 8 e 9) + anexos A a F, com paginação contínua.
Uso: python docs/build_unico.py  (depois de editar os .md; roda também build_docs.py e make_diagramas.py)."""
import os, subprocess, runpy
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
subprocess.check_call(["python3", os.path.join(HERE, "make_diagramas.py")], stdout=subprocess.DEVNULL)
runpy.run_path(os.path.join(HERE, "build_docs.py"), run_name="__main__")
import importlib.util
spec = importlib.util.spec_from_file_location("bd", os.path.join(HERE, "build_docs.py")); bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
TMP = bd.TMP; ANX = os.path.join(TMP, "anexos"); os.makedirs(ANX, exist_ok=True)
ETAPA3 = os.path.join(ROOT, "artifacts", "reports", "MGA_Projeto_Aplicado_III_Etapa_3.pdf")
S89 = os.path.join(bd.OUT, "MGA_Relatorio_Secoes_8_9.pdf")
n = lambda p: len(PdfReader(p).pages)
p_et3 = n(ETAPA3); p_89 = n(S89); ini = p_et3 + 1
lista = [("A", "CANVAS DO PROJETO", "Canvas_Projeto_MGA.md", "A_Canvas"), ("B", "DOCUMENTO DE METODOLOGIA", "metodologia.md", "B_Metodologia"),
         ("C", "DOCUMENTO DE ARQUITETURA E DIAGRAMAS", "_arquitetura_doc.md", "C_Arquitetura"), ("D", "PLANO E REGISTRO DE TESTES", "plano_testes.md", "D_Testes")]
start = ini + p_89; faixas = {}; pdfs = []
for letra, titulo, md, nome in lista:
    pdf = bd.construir(md, nome, "", capa=False, inicio=start, anexo=f"ANEXO {letra} – {titulo}", outdir=ANX)
    c = n(pdf); faixas[letra] = (start, start + c - 1, titulo); pdfs.append((letra, titulo, pdf)); start += c
U = "https://github.com/Guidln/MGA-Mackenzie-Game-Algorithm"
# link do repositório na capa (sobreposição na página 1 do PDF da Etapa 3, com área clicável)
import io
from reportlab.pdfgen import canvas
from pypdf.annotations import Link
buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(595.304, 841.89)); H = 841.89
c.setFont("Times-Bold", 11); c.drawCentredString(297.65, H - 520, "Repositório do projeto:")
c.setFont("Times-Roman", 11); c.drawCentredString(297.65, H - 536, U); c.save(); buf.seek(0)
capa = PdfReader(ETAPA3); pg0 = capa.pages[0]; pg0.merge_page(PdfReader(buf).pages[0])
w = PdfWriter(); w.add_page(pg0)
for pg in capa.pages[1:]: w.add_page(pg)
w.add_annotation(page_number=0, annotation=Link(rect=(150, H - 542, 445, H - 528), url=U))
w.add_outline_item("Relatório – Etapas 1 a 3 (seções 1 a 7)", 0)
def add(path, marca):
    pos = len(w.pages)
    for pg in PdfReader(path).pages: w.add_page(pg)
    w.add_outline_item(marca, pos)
add(S89, "Relatório – Etapa 4 (seções 8 e 9)")
for l, t, pdf in pdfs: add(pdf, f"Anexo {l} – {t.capitalize()}")
w.add_metadata({"/Title": "MGA – Mackenzie Game Algorithm – Projeto Aplicado III, Etapa 4"})
out = os.path.join(bd.OUT, "MGA_Documento_Unico_Etapa4.pdf"); w.write(out); print("OK", out, len(w.pages), "páginas")

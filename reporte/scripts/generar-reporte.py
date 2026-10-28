#!/usr/bin/env python3
from pathlib import Path
import json, re, html, math, subprocess, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from entrega import construir_paginas, construir_coleccion

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
RESULTS=json.loads((ROOT/'datos/resultados.json').read_text())
assert len(RESULTS)==51, f'Se necesitan 51 casos, hay {len(RESULTS)}'
assert all(r['estado']==r['esperado'] and r['pruebas']['failed']==0 for r in RESULTS)
for r in RESULTS: assert (ROOT/r['archivo']).exists()
for family,path in [('Arial','Arial.TTF'),('Arial-Bold','Arialbd.TTF'),('Arial-Italic','Ariali.TTF'),('CourierNew','cour.ttf')]:
    pdfmetrics.registerFont(TTFont(family,'/usr/share/fonts/TTF/'+path))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
STYLES={
'toc':ParagraphStyle('TOC',fontName='Arial',fontSize=10,leading=12,spaceAfter=9),
'p':ParagraphStyle('Body',fontName='Arial',fontSize=12,leading=18,alignment=TA_JUSTIFY,spaceAfter=9),
'h1':ParagraphStyle('Title',fontName='Arial-Bold',fontSize=14,leading=18,spaceAfter=12),
'h2':ParagraphStyle('Sub',fontName='Arial-Bold',fontSize=12,leading=17,spaceBefore=7,spaceAfter=5),
'caption':ParagraphStyle('Caption',fontName='Arial-Italic',fontSize=9,leading=12,alignment=TA_CENTER,spaceAfter=8),
'code':ParagraphStyle('Code',fontName='CourierNew',fontSize=9,leading=13,spaceAfter=2),
'cell':ParagraphStyle('Cell',fontName='Arial',fontSize=10,leading=13),
'compactcell':ParagraphStyle('CompactCell',fontName='Arial',fontSize=9,leading=11),
'center':ParagraphStyle('Center',fontName='Arial',fontSize=16,leading=23,alignment=TA_CENTER),
}
PAGES=construir_paginas(RESULTS)
passed=sum(r['pruebas']['passed'] for r in RESULTS)
TOC_RANGES=[(i,min(i+21,len(PAGES))) for i in range(0,len(PAGES),21)]
(ROOT/'datos/contenido.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2))

# PDF: tamaño carta, Arial, cuerpo justificado, logotipos y foliación del ejemplo.
PDF=OUT/'REPORTE DE PRACTICA - EJERCICIO CRUD.pdf'
c=canvas.Canvas(str(PDF),pagesize=(612,792),pageCompression=1)
c.setTitle('Reporte de práctica: Ejercicio CRUD — Biblioteca Lumbre')
c.setAuthor('José Antonio Pareja Pérez')
layout=[]
def header(folio=None):
    c.drawImage(str(ROOT/'recursos/tescha.jpg'),24,733,167,44.4,mask='auto')
    c.drawImage(str(ROOT/'recursos/sistemas.png'),444,732,139,47.5,mask='auto')
    if folio is not None:
        c.setFont('Arial',11);c.drawCentredString(306,24,str(folio))
def para(text,style,y,width=468,x=72):
    p=Paragraph(text,STYLES[style]);_,h=p.wrap(width,700)
    p.drawOn(c,x,y-h)
    return y-h-STYLES[style].spaceAfter
def textp(text,style,y):return para(escape(text).replace('\n','<br/>'),style,y)
def table_pdf(data,y,summary=False):
    heads,rows=data
    colwidths=[28,48,296,43,53] if summary else ([170,298] if len(heads)==2 else None)
    cells=[[Paragraph(escape(str(v)),STYLES['compactcell' if summary else 'cell']) for v in row] for row in [heads]+rows]
    t=Table(cells,colWidths=colwidths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Arial-Bold'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#888888')),('INNERGRID',(0,0),(-1,-1),.3,colors.HexColor('#bbbbbb')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),2 if summary else 5),('BOTTOMPADDING',(0,0),(-1,-1),2 if summary else 5)]))
    _,h=t.wrap(468,700);t.drawOn(c,72,y-h);return y-h-10

header()
y=684
for line in ['DESARROLLO DE APLICACIONES PARA LA CIENCIA','DE DATOS.']:
    c.setFont('Arial-Bold',18);c.drawCentredString(306,y,line);y-=24
for y,label,value in [(558,'Alumno:','José Antonio Pareja Pérez'),(495,'Carrera:','Ingeniería en Sistemas Computacionales'),(432,'Fecha de entrega:','Viernes 23 de octubre de 2026'),(369,'Reporte:','Ejercicio CRUD — Biblioteca Lumbre')]:
    para(f'<b>{label}</b> <i>{escape(value)}</i>','center',y,540,36)
c.drawImage(str(ROOT/'recursos/portada-ciencia.png'),166,35,280,278.5,mask='auto')
c.showPage()
# Dos páginas de índice, como en el ejemplo.
for start,end in TOC_RANGES:
    header();y=textp('ÍNDICE' if start==0 else 'ÍNDICE (CONTINUACIÓN)','h1',716)
    y-=10
    for i in range(start,end):
        title=PAGES[i]['title']
        y_before=y
        y=para(escape(title),'toc',y,435,72)
        c.setFont('Arial',10)
        c.drawRightString(540,y_before-11,str(i+1))
        y=min(y,y_before-27)
    c.showPage()
for folio,page in enumerate(PAGES,1):
    header(folio);y=textp(page['title'],'h1',716)
    blocks=page['blocks']
    for index,(kind,value) in enumerate(blocks):
        if kind=='h2':y-=5;y=textp(value,'h2',y)
        elif kind in ['p','result']:y=textp(value,'p',y)
        elif kind=='code':
            for line in value.splitlines():y=textp(line,'code',y)
        elif kind in ['list','steps']:
            for number,text in enumerate(value,1):
                prefix=f'{number}. ' if kind=='steps' else '• '
                y=textp(prefix+text,'p',y)
        elif kind in ['table','summarytable']:y=table_pdf(value,y,summary=kind=='summarytable')
        elif kind=='capture':
            image=ImageReader(str(ROOT/value));iw,ih=image.getSize()
            remaining=sum(Paragraph(escape(v),STYLES['caption' if k=='caption' else 'p']).wrap(468,700)[1]+STYLES['caption' if k=='caption' else 'p'].spaceAfter for k,v in blocks[index+1:] if k in ['caption','result'])
            maxh=min(390,y-remaining-48)
            w=min(468,maxh*iw/ih);h=w*ih/iw
            assert w>=340,(folio,'imagen pequeña',w)
            c.drawImage(image,72+(468-w)/2,y-h,width=w,height=h,mask='auto');y-=h+7
        elif kind=='caption':y=textp(value,'caption',y)
    assert y>=42,(folio,'desbordamiento',y)
    layout.append({'folio':folio,'title':page['title'],'bottom_y':round(y,2)})
    c.showPage()
c.save()
(ROOT/'datos/maquetacion.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))

# DOCX editable, con el mismo contenido, encabezados y saltos de página.
doc=Document()
section=doc.sections[0]
section.page_width=Inches(8.5);section.page_height=Inches(11)
section.top_margin=section.bottom_margin=section.left_margin=section.right_margin=Inches(1)
section.header_distance=Pt(12);section.footer_distance=Pt(14)
normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(12)
normal.paragraph_format.line_spacing=1.5;normal.paragraph_format.space_after=Pt(9)
for name,size in [('Heading 1',14),('Heading 2',12)]:
    st=doc.styles[name];st.font.name='Arial';st.font.size=Pt(size);st.font.bold=True;st.font.color.rgb=__import__('docx').shared.RGBColor(0,0,0)
    st.paragraph_format.space_before=Pt(5);st.paragraph_format.space_after=Pt(8);st.paragraph_format.line_spacing=1.0
hp=section.header.paragraphs[0];hp.paragraph_format.left_indent=Pt(-48);hp.paragraph_format.right_indent=Pt(-48);hp.paragraph_format.line_spacing=1
hp.paragraph_format.tab_stops.add_tab_stop(Pt(516),WD_TAB_ALIGNMENT.RIGHT)
hp.add_run().add_picture(str(ROOT/'recursos/tescha.jpg'),width=Pt(167))
hp.add_run('\t');hp.add_run().add_picture(str(ROOT/'recursos/sistemas.png'),width=Pt(139))
def dp(text,kind='p'):
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    if kind=='h1':p.style='Heading 1'
    if kind=='h2':p.style='Heading 2'
    r=p.add_run(text)
    if kind=='caption':
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER;r.italic=True;r.font.size=Pt(9);p.paragraph_format.line_spacing=1
    if kind=='code':r.font.name='Courier New';r.font.size=Pt(9);p.paragraph_format.line_spacing=1
    return p
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(35);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('DESARROLLO DE APLICACIONES PARA LA CIENCIA\nDE DATOS.');r.bold=True;r.font.size=Pt(18)
p.paragraph_format.line_spacing=1.2;p.paragraph_format.space_after=Pt(65)
for label,value in [('Alumno:','José Antonio Pareja Pérez'),('Carrera:','Ingeniería en Sistemas Computacionales'),('Fecha de entrega:','Viernes 23 de octubre de 2026'),('Reporte:','Ejercicio CRUD — Biblioteca Lumbre')]:
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(27);p.paragraph_format.line_spacing=1
    r=p.add_run(label+' ');r.bold=True;r.font.size=Pt(16)
    r=p.add_run(value);r.italic=True;r.font.size=Pt(16)
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0)
p.add_run().add_picture(str(ROOT/'recursos/portada-ciencia.png'),width=Pt(260))
for start,end in TOC_RANGES:
    doc.add_page_break();dp('ÍNDICE' if start==0 else 'ÍNDICE (CONTINUACIÓN)','h1')
    for i in range(start,end):
        p=doc.add_paragraph();p.paragraph_format.tab_stops.add_tab_stop(Pt(468),WD_TAB_ALIGNMENT.RIGHT,__import__('docx').enum.text.WD_TAB_LEADER.DOTS)
        p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(12)
        r=p.add_run(PAGES[i]['title']+'\t'+str(i+1));r.font.size=Pt(10.6)
section=doc.add_section(WD_SECTION_START.NEW_PAGE)
section.footer.is_linked_to_previous=False
pg=OxmlElement('w:pgNumType');pg.set(qn('w:start'),'1');section._sectPr.append(pg)
fp=section.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');fp._p.append(field)
for i,page in enumerate(PAGES):
    if i:doc.add_page_break()
    dp(page['title'],'h1')
    for kind,value in page['blocks']:
        if kind in ['p','h2','caption','code','result']:dp(value,'p' if kind=='result' else kind)
        elif kind in ['list','steps']:
            for n,text in enumerate(value,1):dp((f'{n}. ' if kind=='steps' else '• ')+text)
        elif kind=='capture':
            p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(5);p.paragraph_format.line_spacing=1
            # El editable reserva espacio adicional por las diferencias de maquetación de Word.
            p.add_run().add_picture(str(ROOT/value),width=Pt(380))
        elif kind in ['table','summarytable']:
            heads,rows=value;t=doc.add_table(rows=1,cols=len(heads));t.style='Table Grid'
            for cell,text in zip(t.rows[0].cells,heads):cell.text=text
            for row in rows:
                for cell,text in zip(t.add_row().cells,row):cell.text=str(text)
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1
                        for r in p.runs:r.font.size=Pt(9 if len(heads)>2 else 10)
doc.core_properties.title='Reporte de práctica: Ejercicio CRUD — Biblioteca Lumbre'
doc.core_properties.author='José Antonio Pareja Pérez'
doc.save(OUT/'REPORTE DE PRACTICA - EJERCICIO CRUD.docx')

# La colección conserva las aserciones realmente ejecutadas y ejemplos saneados.
(ROOT/'Lumbre-CRUD.postman_collection.json').write_text(json.dumps(construir_coleccion(RESULTS),ensure_ascii=False,indent=2))
checksums=['%s  %s'%(hashlib.sha256(path.read_bytes()).hexdigest(),str(path.relative_to(ROOT))) for path in sorted((ROOT/'evidencias').glob('*.png'))]
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n')
print(json.dumps({'pdf':str(PDF),'paginas':len(PAGES)+1+len(TOC_RANGES),'capturas':len(RESULTS),'aserciones':passed,'min_bottom_y':min(x['bottom_y'] for x in layout)},ensure_ascii=False))

import os, sys, json
from xml.sax.saxutils import escape as _xml_escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, KeepTogether, NextPageTemplate)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
WIDTH, HEIGHT = A4
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = None
for p in [os.path.join(SCRIPT_DIR, "volk_logo.png"), "/home/claude/volk_logo.png"]:
    if os.path.exists(p):
        LOGO_PATH = os.path.abspath(p); break
NAVY=HexColor("#0A1020"); NAVY_2=HexColor("#0F1A30"); BLUE=HexColor("#3B82F6")
TEAL=HexColor("#38BDF8"); WHITE=HexColor("#FFFFFF"); WHITE_DIM=HexColor("#CBD5E1")
SLATE=HexColor("#94A3B8"); TEXT_DARK=HexColor("#1E293B"); TEXT_MID=HexColor("#475569")
LINE_SOFT=HexColor("#E2E8F0"); CARD_BG=HexColor("#F8FAFC"); PILL_TEAL=HexColor("#EAF6FE")
RED=HexColor("#EF4444"); AMBER=HexColor("#F59E0B"); GREEN=HexColor("#10B981")
BAR_PEND=HexColor("#CBD5E1")
CHIP_MAP={"COMPLETADA":GREEN,"PENDIENTE":AMBER,"ATRASADA":RED}
# Paleta por formato (para barras apiladas y encabezados de tabla)
FMT_COLS=[HexColor("#EF4444"),HexColor("#A78BFA"),HexColor("#F59E0B"),HexColor("#94A3B8"),HexColor("#60A5FA"),HexColor("#F472B6"),HexColor("#10B981")]
MARGIN_X=42; HERO_H=196; MINI_H=60; FOOTER_H=30; CW=WIDTH-2*MARGIN_X-24
S={}
S['card_title']=ParagraphStyle('ct',fontName='Helvetica-Bold',fontSize=13,textColor=NAVY,leading=16)
S['body']=ParagraphStyle('b',fontName='Helvetica',fontSize=11.5,textColor=TEXT_MID,leading=16.5,alignment=TA_JUSTIFY)
S['task']=ParagraphStyle('tk',fontName='Helvetica-Bold',fontSize=10.5,textColor=NAVY,leading=13.5)
S['sub']=ParagraphStyle('su',fontName='Helvetica',fontSize=9,textColor=SLATE,leading=12)
S['note']=ParagraphStyle('nt',fontName='Helvetica-Oblique',fontSize=11,textColor=TEXT_MID,leading=15.5,alignment=TA_JUSTIFY)
S['person']=ParagraphStyle('pe',fontName='Helvetica-Bold',fontSize=12,textColor=NAVY,leading=15)
S['th']=ParagraphStyle('th',fontName='Helvetica-Bold',fontSize=8,textColor=WHITE,leading=10,alignment=1)
S['td']=ParagraphStyle('td',fontName='Helvetica',fontSize=8.5,textColor=TEXT_DARK,leading=11,alignment=1)
S['td_cli']=ParagraphStyle('tdc',fontName='Helvetica-Bold',fontSize=8.5,textColor=NAVY,leading=11,alignment=0)
D={}
def esc(t): return _xml_escape(str(t if t is not None else ""))
def _logo(c,x,y,w,color=WHITE):
    V=[(0.98,0.010,0.033,0.966,0.989),(0.94,0.030,0.103,0.897,0.969),(0.90,0.050,0.172,0.827,0.949),(0.86,0.069,0.241,0.759,0.929),(0.82,0.089,0.268,0.732,0.909),(0.70,0.149,0.325,0.675,0.849),(0.58,0.209,0.384,0.617,0.788),(0.50,0.248,0.423,0.578,0.748),(0.42,0.288,0.461,0.555,0.708),(0.38,0.308,0.480,0.574,0.688),(0.30,0.348,0.519,0.612,0.648)]
    TIP=(0.02,0.487,0.506)
    def px(n): return x+n*w
    def py(n): return y+n*w
    c.saveState(); c.setFillColor(color)
    lo=[(r[1],r[0]) for r in V]+[(TIP[1],TIP[0])]; li=[(r[2],r[0]) for r in V]+[(TIP[2],TIP[0])]
    p=c.beginPath(); p.moveTo(px(lo[0][0]),py(lo[0][1]))
    for a,b in lo[1:]: p.lineTo(px(a),py(b))
    for a,b in reversed(li): p.lineTo(px(a),py(b))
    p.close(); c.drawPath(p,fill=1,stroke=0)
    rr=[r for r in V if r[0]>=0.30]; ro=[(r[3],r[0]) for r in rr]; ri=[(r[4],r[0]) for r in rr]
    q=c.beginPath(); q.moveTo(px(ro[0][0]),py(ro[0][1]))
    for a,b in ro[1:]: q.lineTo(px(a),py(b))
    for a,b in reversed(ri): q.lineTo(px(a),py(b))
    q.close(); c.drawPath(q,fill=1,stroke=0); c.restoreState()
def _fit_font(c,text,font,max_size,min_size,max_w):
    size=max_size
    while size>min_size and c.stringWidth(text,font,size)>max_w: size-=0.5
    return size
def _footer(c,doc):
    c.setStrokeColor(LINE_SOFT); c.setLineWidth(0.6)
    c.line(MARGIN_X,FOOTER_H+8,WIDTH-MARGIN_X,FOOTER_H+8)
    c.setFont('Helvetica',8); c.setFillColor(TEXT_MID)
    c.drawString(MARGIN_X,FOOTER_H-4,"volkmediacr.com   -   @volkmediacr   -   info@volkmediacr.com")
    c.setFont('Helvetica-Oblique',7.5); c.setFillColor(SLATE)
    c.drawRightString(WIDTH-MARGIN_X,FOOTER_H-4,"Reporte mensual - Volk Media - %02d"%doc.page)
def draw_hero(c,doc):
    c.setFillColor(NAVY); c.rect(0,HEIGHT-HERO_H,WIDTH,HERO_H,fill=True,stroke=False)
    c.setStrokeColor(NAVY_2); c.setLineWidth(0.6)
    for i in range(0,8):
        x=WIDTH*0.55+i*26; c.line(x,HEIGHT-HERO_H,x+HERO_H,HEIGHT)
    c.setFillColor(TEAL); c.rect(0,HEIGHT-HERO_H,5,HERO_H,fill=True,stroke=False)
    _logo(c,MARGIN_X,HEIGHT-52,26); tx=MARGIN_X+36
    c.setFont('Helvetica-Bold',12); c.setFillColor(WHITE); c.drawString(tx,HEIGHT-44,"VOLK ")
    vw=c.stringWidth("VOLK ",'Helvetica-Bold',12)
    c.setFont('Helvetica',12); c.setFillColor(TEAL); c.drawString(tx+vw,HEIGHT-44,"MEDIA")
    c.setFont('Helvetica-Bold',9); c.setFillColor(TEAL)
    c.drawString(MARGIN_X,HEIGHT-86,"R E P O R T E   M E N S U A L   D E   O P E R A C I O N E S")
    titulo=D.get("titulo","Cierre Mensual de Operaciones")
    fs=_fit_font(c,titulo,'Helvetica-Bold',22,13,WIDTH-2*MARGIN_X)
    c.setFont('Helvetica-Bold',fs); c.setFillColor(WHITE); c.drawString(MARGIN_X,HEIGHT-110,titulo)
    c.setFont('Helvetica',10); c.setFillColor(WHITE_DIM)
    c.drawString(MARGIN_X,HEIGHT-127,"Responsable:  "+str(D.get('responsable','Raul Lopez')))
    k=D.get("kpi",{})
    stats=[("MES",D.get("semana_label","")),("COMPLETADAS",str(k.get("completadas",0))),
           ("PENDIENTES",str(k.get("pendientes",0))),("CUMPLIMIENTO","%s%%"%k.get('cumplimiento',0))]
    sy=HEIGHT-171; col_w=(WIDTH-2*MARGIN_X)/4
    for i,(lab,val) in enumerate(stats):
        x=MARGIN_X+i*col_w
        if i>0:
            c.setStrokeColor(NAVY_2); c.setLineWidth(0.8); c.line(x-8,sy-4,x-8,sy+23)
        c.setFont('Helvetica-Bold',7.5); c.setFillColor(TEAL); c.drawString(x,sy+14,lab)
        vfs=_fit_font(c,str(val),'Helvetica-Bold',12,8,col_w-12)
        c.setFont('Helvetica-Bold',vfs); c.setFillColor(WHITE); c.drawString(x,sy-3,str(val))
    _footer(c,doc)
def draw_mini(c,doc):
    c.setFillColor(NAVY); c.rect(0,HEIGHT-MINI_H,WIDTH,MINI_H,fill=True,stroke=False)
    c.setFillColor(TEAL); c.rect(0,HEIGHT-MINI_H,5,MINI_H,fill=True,stroke=False)
    _logo(c,MARGIN_X,HEIGHT-42,22); tx=MARGIN_X+32
    c.setFont('Helvetica-Bold',11); c.setFillColor(WHITE); c.drawString(tx,HEIGHT-33,"VOLK ")
    vw=c.stringWidth("VOLK ",'Helvetica-Bold',11)
    c.setFont('Helvetica',11); c.setFillColor(TEAL); c.drawString(tx+vw,HEIGHT-33,"MEDIA")
    c.setFont('Helvetica',8.5); c.setFillColor(WHITE_DIM); c.drawString(tx,HEIGHT-46,"Reporte Mensual de Operaciones")
    c.setFont('Helvetica-Bold',12); c.setFillColor(WHITE_DIM)
    c.drawRightString(WIDTH-MARGIN_X,HEIGHT-38,"%02d"%doc.page)
    _footer(c,doc)
def card(title,accent,inner_flowables):
    rows=[]
    if title:
        tr=Table([[Paragraph(esc(title),S['card_title'])]],colWidths=[CW])
        tr.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        rows.append(tr)
    inner=rows+inner_flowables
    inner_tbl=Table([[f] for f in inner],colWidths=[CW])
    inner_tbl.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    outer=Table([['',inner_tbl]],colWidths=[4,WIDTH-2*MARGIN_X-4])
    outer.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),accent),('BACKGROUND',(1,0),(1,-1),CARD_BG),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(1,0),(1,-1),14),('RIGHTPADDING',(1,0),(1,-1),14),('TOPPADDING',(1,0),(1,-1),12),('BOTTOMPADDING',(1,0),(1,-1),12),('LEFTPADDING',(0,0),(0,-1),0),('RIGHTPADDING',(0,0),(0,-1),0),('BOX',(0,0),(-1,-1),0.6,LINE_SOFT)]))
    return outer
def status_chip(text):
    color=CHIP_MAP.get(text,SLATE)
    t=Table([[Paragraph('<font color="#FFFFFF"><b>%s</b></font>'%esc(text),ParagraphStyle('p',fontName='Helvetica-Bold',fontSize=7.5,alignment=1,leading=9.5))]],colWidths=[74],rowHeights=[16])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),color),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1),('ROUNDEDCORNERS',[3,3,3,3])]))
    return t
def task_rows(items):
    rows=[]
    for row in items:
        tarea,cliente,estado,fecha,chip=(list(row)+["","","","","PENDIENTE"])[:5]
        meta=" - ".join([x for x in [cliente,estado] if x])
        body=Table([[Paragraph(esc(tarea),S['task'])],[Paragraph(esc(meta),S['sub'])]],colWidths=[CW-62-78])
        body.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
        fech=Paragraph(esc(fecha),ParagraphStyle('fe',fontName='Helvetica',fontSize=9,textColor=TEXT_MID,leading=12,alignment=2))
        r=Table([[body,fech,status_chip(chip)]],colWidths=[CW-62-78,58,78])
        r.setStyle(TableStyle([('VALIGN',(0,0),(-1,0),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('ALIGN',(2,0),(2,0),'RIGHT'),('LINEBELOW',(0,0),(-1,-1),0.5,LINE_SOFT)]))
        rows.append([r])
    wrap=Table(rows,colWidths=[CW])
    wrap.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    return wrap
def _legend(d,x,y,w):
    items=[("Completadas",TEAL),("Pendientes",BAR_PEND)]; cx=x
    for lab,col in items:
        d.add(Rect(cx,y,9,9,fillColor=col,strokeColor=None))
        d.add(String(cx+13,y+1.5,lab,fontName='Helvetica',fontSize=8,fillColor=TEXT_MID))
        cx+=16+len(lab)*4.6+14
def chart_barras(labels,done,pend,titulo_eje=""):
    n=len(labels); row_h,gap=20,7; top_pad,bot_pad=6,24
    h=top_pad+n*row_h+(n-1)*gap+bot_pad; w=CW; lab_w=118; bar_x=lab_w+6
    bar_max=w-bar_x-46; total_max=max([d+p for d,p in zip(done,pend)]+[1])
    d=Drawing(w,h)
    for f in (0.25,0.5,0.75,1.0):
        gx=bar_x+bar_max*f; d.add(Line(gx,bot_pad-4,gx,h-top_pad,strokeColor=LINE_SOFT,strokeWidth=0.5))
    y=h-top_pad-row_h
    for i in range(n):
        lab=labels[i]
        if len(lab)>20: lab=lab[:19]+"..."
        d.add(String(lab_w,y+row_h/2-3,lab,fontName='Helvetica-Bold',fontSize=8.5,fillColor=TEXT_DARK,textAnchor='end'))
        dv,pv=done[i],pend[i]; wd=bar_max*(dv/total_max); wp=bar_max*(pv/total_max)
        bh=13; by=y+(row_h-bh)/2
        if wd>0: d.add(Rect(bar_x,by,wd,bh,fillColor=TEAL,strokeColor=None))
        if wp>0: d.add(Rect(bar_x+wd,by,wp,bh,fillColor=BAR_PEND,strokeColor=None))
        tot=dv+pv; pct=int(round(dv*100/tot)) if tot else 0
        d.add(String(bar_x+wd+wp+7,by+3.5,"%d/%d  -  %d%%"%(dv,tot,pct),fontName='Helvetica-Bold',fontSize=8,fillColor=TEXT_MID))
        y-=(row_h+gap)
    d.add(Line(bar_x,bot_pad-4,bar_x+bar_max,bot_pad-4,strokeColor=LINE_SOFT,strokeWidth=0.8))
    _legend(d,bar_x,4,w); return d
# ===== NUEVO: barras apiladas por formato =====
def _legend_fmt(d,x,y,w,labels,cols):
    cx=x; cy=y
    for i,lab in enumerate(labels):
        seg=14+len(lab)*4.7+12
        if cx+seg>x+w:
            cx=x; cy-=14
        d.add(Rect(cx,cy,9,9,fillColor=cols[i%len(cols)],strokeColor=None))
        d.add(String(cx+12,cy+1.5,lab,fontName='Helvetica',fontSize=7.5,fillColor=TEXT_MID))
        cx+=seg
    return cy
def chart_formatos(clientes, matriz, fmt_labels):
    # matriz: lista por cliente de lista de conteos alineada con fmt_labels
    n=len(clientes); row_h,gap=20,8; top_pad=6
    # espacio para leyenda multilinea
    leg_lines=1+ (sum(14+len(l)*4.7+12 for l in fmt_labels)//max(int(CW-130),1))
    bot_pad=24+int(leg_lines)*14
    h=top_pad+n*row_h+(n-1)*gap+bot_pad; w=CW; lab_w=118; bar_x=lab_w+6
    bar_max=w-bar_x-52
    totales=[sum(r) for r in matriz]
    total_max=max(totales+[1])
    d=Drawing(w,h)
    for f in (0.25,0.5,0.75,1.0):
        gx=bar_x+bar_max*f; d.add(Line(gx,bot_pad-4,gx,h-top_pad,strokeColor=LINE_SOFT,strokeWidth=0.5))
    y=h-top_pad-row_h
    for i in range(n):
        lab=clientes[i]
        if len(lab)>20: lab=lab[:19]+"..."
        d.add(String(lab_w,y+row_h/2-3,lab,fontName='Helvetica-Bold',fontSize=8.5,fillColor=TEXT_DARK,textAnchor='end'))
        bh=13; by=y+(row_h-bh)/2; cx=bar_x
        for j,val in enumerate(matriz[i]):
            if val>0:
                wseg=bar_max*(val/total_max)
                d.add(Rect(cx,by,wseg,bh,fillColor=FMT_COLS[j%len(FMT_COLS)],strokeColor=None))
                cx+=wseg
        d.add(String(cx+7,by+3.5,"%d"%totales[i],fontName='Helvetica-Bold',fontSize=8,fillColor=TEXT_MID))
        y-=(row_h+gap)
    d.add(Line(bar_x,bot_pad-4,bar_x+bar_max,bot_pad-4,strokeColor=LINE_SOFT,strokeWidth=0.8))
    _legend_fmt(d,bar_x,bot_pad-18,bar_max,fmt_labels,FMT_COLS)
    return d
def tabla_formatos(headers, filas):
    # headers: [Cliente, Reels, Diseno, ...Total]; filas: [[cliente,n,n,...,total],...]
    data=[[Paragraph(esc(h),S['th']) for h in headers]]
    for f in filas:
        row=[Paragraph(esc(f[0]),S['td_cli'])]
        for v in f[1:]:
            row.append(Paragraph(esc(v),S['td']))
        data.append(row)
    ncol=len(headers)
    first_w=CW-(ncol-1)*int((CW-92)/ (ncol-1)) if ncol>1 else CW
    rest=(CW-92)/(ncol-1) if ncol>1 else CW
    col_widths=[92]+[rest]*(ncol-1)
    t=Table(data,colWidths=col_widths)
    st=[('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
        ('LINEBELOW',(0,0),(-1,-1),0.4,LINE_SOFT),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,HexColor('#F1F5F9')])]
    # color de encabezados de formato
    for j in range(1,ncol-1):
        st.append(('TEXTCOLOR',(j,0),(j,0),WHITE))
    t.setStyle(TableStyle(st))
    return t
def build(data,out_path):
    global D; D=data
    doc=BaseDocTemplate(out_path,pagesize=A4,leftMargin=MARGIN_X,rightMargin=MARGIN_X,topMargin=HERO_H+14,bottomMargin=FOOTER_H+16,title="Reporte Mensual de Operaciones - Volk Media",author="Volk Media")
    frame_first=Frame(MARGIN_X,FOOTER_H+16,WIDTH-2*MARGIN_X,HEIGHT-(HERO_H+14)-(FOOTER_H+16),id='first',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    frame_later=Frame(MARGIN_X,FOOTER_H+16,WIDTH-2*MARGIN_X,HEIGHT-(MINI_H+16)-(FOOTER_H+16),id='later',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='first',frames=[frame_first],onPage=draw_hero),PageTemplate(id='later',frames=[frame_later],onPage=draw_mini)])
    sp=lambda h:Spacer(1,h); story=[NextPageTemplate('later')]
    if data.get("periodo_bar"):
        p=Paragraph('<font color="#0EA5E9"><b>PERIODO&nbsp;&nbsp;</b></font><font color="#475569">%s</font>'%esc(data["periodo_bar"]),ParagraphStyle('att',fontName='Helvetica',fontSize=10,leading=14))
        t=Table([[p]],colWidths=[WIDTH-2*MARGIN_X])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PILL_TEAL),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBEFORE',(0,0),(0,-1),3,TEAL)]))
        story+=[t,sp(12)]
    if data.get("resumen"):
        story+=[card("Resumen del mes",BLUE,[Paragraph(esc(data["resumen"]),S['body'])]),sp(10)]
    pr=data.get("por_responsable",[])
    if pr:
        ch=chart_barras([x["nombre"] for x in pr],[x["done"] for x in pr],[max(x["total"]-x["done"],0) for x in pr])
        story+=[KeepTogether([card("Cumplimiento por responsable",TEAL,[ch])]),sp(10)]
    pc=data.get("por_cliente",[])
    if pc:
        ch2=chart_barras([x["nombre"] for x in pc],[x["done"] for x in pc],[x["pend"] for x in pc])
        story+=[KeepTogether([card("Entregas por cliente",BLUE,[ch2])]),sp(10)]
    # ===== NUEVO: piezas por cliente y formato =====
    pf=data.get("por_formato",[])
    fh=data.get("formato_headers",[])
    if pf and fh:
        fmt_labels=fh[1:-1]  # sin "Cliente" ni "Total"
        clientes=[r[0] for r in pf]
        matriz=[[int(x) for x in r[1:-1]] for r in pf]
        chf=chart_formatos(clientes,matriz,fmt_labels)
        tf=tabla_formatos(fh,[[str(x) for x in r] for r in pf])
        story+=[KeepTogether([card("Piezas producidas por cliente y formato",TEAL,[chf,sp(10),tf])]),sp(10)]
    for per in pr:
        head=Paragraph('%s <font size="9" color="#94A3B8">- %d/%d completadas - %d%%</font>'%(esc(per["nombre"]),per["done"],per["total"],per["pct"]),S['person'])
        inner=[head,sp(6)]
        if per.get("tareas"): inner.append(task_rows(per["tareas"]))
        else: inner.append(Paragraph("Sin tareas con fecha de este mes.",S['sub']))
        story+=[KeepTogether([card(None,TEAL if per["pct"]>=70 else AMBER,inner)]),sp(10)]
    if data.get("arrastre"):
        story+=[KeepTogether([card("Arrastre de meses anteriores (%d) - no cuenta en el cumplimiento"%len(data["arrastre"]),AMBER,[task_rows(data["arrastre"])])]),sp(10)]
    if data.get("notas"):
        story+=[card("Notas",SLATE,[Paragraph(esc(data["notas"]),S['note'])])]
    doc.build(story); return out_path
def main():
    args=sys.argv[1:]
    if args:
        with open(args[0],"r",encoding="utf-8") as f: data=json.load(f)
        out=args[1] if len(args)>1 else data.get("output_filename","Reporte.pdf")
    else:
        data={"titulo":"Prueba","kpi":{}}; out="Reporte.pdf"
    print("OK:",build(data,out))
if __name__=="__main__": main()

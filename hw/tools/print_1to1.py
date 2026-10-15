"""1:1 paper print of the board (Letter portrait): pads + silkscreen, pads + reference designators, bottom side.
Needs PyMuPDF. The layer PDFs come from kicad-cli (see the commands in hw/tools/print_1to1.sh).
usage: python3 print_1to1.py top.pdf assy.pdf bottom.pdf out.pdf
"""
import sys,datetime,subprocess
import pymupdf as fitz
MM=72/25.4
top,assy,bot,out=sys.argv[1:5]
NAME=sys.argv[5] if len(sys.argv)>5 else 'ADS7057 test board'
NOTE=sys.argv[6] if len(sys.argv)>6 else 'Board outline 64.0 x 32.0 mm. The right-angle PMOD header J3 sticks out 5.9 mm past the right edge and is not drawn.'
rev=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip()
PAGES=[(top,'Top side: pads and silkscreen','Place the real parts on the pads to check every footprint before you order.'),
       (assy,'Top side: pads and reference designators','Use it to find a part. The names are the same as in the schematic and the BOM.'),
       (bot,'Bottom side, seen from below (mirrored)','Only the through-hole pins and the ground pour are on this side (on the head board: the face the piezo sits on).')]
doc=fitz.open()
for src,title,sub in PAGES:
    p=doc.new_page(width=612,height=792)
    p.insert_text((36,50),'AUSELIA  /  '+NAME+'  /  1:1 print',fontsize=9,fontname='helv',color=(.36,.48,.39))
    p.insert_text((36,80),title,fontsize=18,fontname='hebo',color=(.08,.15,.11))
    p.insert_text((36,100),sub,fontsize=10,fontname='helv',color=(.1,.1,.1))
    p.insert_text((36,122),'Print at 100 % (actual size). Do not use "fit to page". The bar below must measure 100 mm.',fontsize=10,fontname='hebo',color=(.7,.2,.1))
    # 100 mm scale bar with 10 mm ticks
    y=160; x0=36
    p.draw_line((x0,y),(x0+100*MM,y),width=1.0)
    for k in range(11):
        h=8 if k%5==0 else 5
        p.draw_line((x0+k*10*MM,y),(x0+k*10*MM,y-h),width=0.7)
    p.insert_text((x0,y+14),'0',fontsize=8,fontname='helv'); p.insert_text((x0+50*MM-6,y+14),'50 mm',fontsize=8,fontname='helv'); p.insert_text((x0+100*MM-10,y+14),'100 mm',fontsize=8,fontname='helv')
    # board at exactly its real size, centered, with crop marks
    s=fitz.open(src); w=s[0].rect.width; h=s[0].rect.height
    cx=306; cy=330
    r=fitz.Rect(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
    p.show_pdf_page(r,s,0)
    for (x,yy,dx,dy) in ((r.x0,r.y0,-1,-1),(r.x1,r.y0,1,-1),(r.x0,r.y1,-1,1),(r.x1,r.y1,1,1)):
        p.draw_line((x+dx*4,yy),(x+dx*14,yy),width=0.5); p.draw_line((x,yy+dy*4),(x,yy+dy*14),width=0.5)
    p.insert_text((36,cy+h/2+40),NOTE,fontsize=8.5,fontname='helv')
    p.insert_text((36,740),f'{NAME}  /  commit {rev}  /  {datetime.date.today().isoformat()}',fontsize=8,fontname='helv',color=(.36,.36,.36))
doc.save(out); print('saved',out,len(doc),'pages')

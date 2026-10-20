"""Project rules (JLCPCB 4-layer), inner plane zones, Specctra DSN.  usage: kicad-python bp_prep.py BP_Module|FMC_Adapter"""
import sys,os,json,re,shutil
HERE=os.path.dirname(os.path.abspath(__file__))
import pcbnew
name=sys.argv[1]
RULES={'BP_Module':dict(clr=0.15,track=0.2,via=0.6,drill=0.3,planes=[('In1_Cu','GND'),('In2_Cu','+3V3')],power=['+5V','+5V_IN'],pw=0.6),
       'FMC_Adapter':dict(clr=0.127,track=0.15,via=0.45,drill=0.2,planes=[('In1_Cu','GND')],power=['+3V3_FMC','VADJ'],pw=0.4)}[name]
pro=os.path.join(HERE,name+'.kicad_pro')
if not os.path.exists(pro): shutil.copy(os.path.join(HERE,'..','ADC_Test.kicad_pro'),pro)
j=json.load(open(pro)); ds=j['board']['design_settings']
ds['rules'].update({"min_clearance":RULES['clr'],"min_copper_edge_clearance":0.3,"min_hole_clearance":0.25,"min_hole_to_hole":0.25,"min_text_height":0.8,"min_text_thickness":0.12,
  "min_through_hole_diameter":0.2,"min_track_width":0.1,"min_via_annular_width":0.1,"min_via_diameter":0.4,"min_silk_clearance":0.0})
ns=j['net_settings']; d=[c for c in ns['classes'] if c['name']=='Default'][0]
d.update({"clearance":RULES['clr'],"track_width":RULES['track'],"via_diameter":RULES['via'],"via_drill":RULES['drill']})
pw=dict(d); pw.update({"name":"Power","track_width":RULES['pw'],"priority":0})
ns['classes']=[d,pw]; ns['netclass_patterns']=[{"netclass":"Power","pattern":x} for x in RULES['power']]
j['meta']['filename']=name+'.kicad_pro'; json.dump(j,open(pro,'w'),indent=2)
PCB=os.path.join(HERE,name+'.kicad_pcb'); b=pcbnew.LoadBoard(PCB); mm=pcbnew.FromMM
bb=b.GetBoardEdgesBoundingBox(); x0,y0,x1,y1=[pcbnew.ToMM(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())]
if not os.environ.get('NOPLANE'):
    for ly,net in RULES['planes']:
        z=pcbnew.ZONE(b); z.SetLayer(getattr(pcbnew,ly)); z.SetNet(b.FindNet(net))
        ch=pcbnew.SHAPE_LINE_CHAIN()
        for (x,y) in [(x0+0.3,y0+0.3),(x1-0.3,y0+0.3),(x1-0.3,y1-0.3),(x0+0.3,y1-0.3)]: ch.Append(mm(x),mm(y))
        ch.SetClosed(True); z.Outline().AddOutline(ch); z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3)); b.Add(z)
    sys.path.insert(0,HERE)
    from bp_stubs import add_stub_vias
    n,fails=add_stub_vias(b,sorted({net for _,net in RULES['planes']}),via=RULES['via'],drill=RULES['drill'],width=RULES['track'])
    print('plane stubs added',n,'failed',fails)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
pcbnew.ExportSpecctraDSN(b,os.path.join(HERE,name+'.dsn'))
s=open(os.path.join(HERE,name+'.dsn')).read()
print('layers:',re.findall(r'\(layer (\S+)\s',s)[:6],'planes:',len(re.findall(r'\(plane ',s)))
for ly in [p[0].replace('_','.') for p in RULES['planes']]:      # inner planes are power layers: the router must not put signals on them
    s=s.replace('(layer %s\n      (type signal)'%ly,'(layer %s\n      (type power)'%ly)
open(os.path.join(HERE,name+'.dsn'),'w').write(s)

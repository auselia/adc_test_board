"""Design rules (JLCPCB 2-layer friendly) written into ADC_Test.kicad_pro."""
import json,os
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
p=os.path.join(HW,'ADC_Test.kicad_pro'); j=json.load(open(p))
ds=j['board']['design_settings']
ds['rules'].update({"min_clearance":0.15,"min_copper_edge_clearance":0.3,"min_hole_clearance":0.25,"min_hole_to_hole":0.25,"min_text_height":0.8,"min_text_thickness":0.12,
  "min_through_hole_diameter":0.25,"min_track_width":0.15,"min_via_annular_width":0.13,"min_via_diameter":0.5,"min_silk_clearance":0.0})
ds.setdefault('defaults',{}).update({"silk_text_size_h":0.8,"silk_text_size_v":0.8,"silk_text_thickness":0.12})
ns=j['net_settings']; d=[c for c in ns['classes'] if c['name']=='Default'][0]
d.update({"clearance":0.15,"track_width":0.2,"via_diameter":0.6,"via_drill":0.3})
pw=dict(d); pw.update({"name":"Power","track_width":0.35,"priority":0})
ns['classes']=[d,pw]
ns['netclass_patterns']=[{"netclass":"Power","pattern":x} for x in ['+5V','VMID5','+9VP','+9V_IN']]
j['meta']['filename']='ADC_Test.kicad_pro'
json.dump(j,open(p,'w'),indent=2); print('pro rules set')

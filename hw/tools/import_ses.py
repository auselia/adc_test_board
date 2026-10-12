import pcbnew,os,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
b=pcbnew.LoadBoard(os.path.join(HW,'ADC_Test.kicad_pcb'))
print('import',pcbnew.ImportSpecctraSES(b,os.path.join(HW,sys.argv[1])))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(os.path.join(HW,'ADC_Test.kicad_pcb'))
tr=list(b.GetTracks()); v=[t for t in tr if t.Type()==pcbnew.PCB_VIA_T]
print('tracks',len(tr)-len(v),'vias',len(v))

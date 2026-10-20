import pcbnew,os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); name=sys.argv[1]
b=pcbnew.LoadBoard(os.path.join(HERE,name+'.kicad_pcb'))
print('import',pcbnew.ImportSpecctraSES(b,os.path.join(HERE,name+'.ses')))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(os.path.join(HERE,name+'.kicad_pcb'))
tr=list(b.GetTracks()); v=[t for t in tr if t.Type()==pcbnew.PCB_VIA_T]
print('tracks',len(tr)-len(v),'vias',len(v))

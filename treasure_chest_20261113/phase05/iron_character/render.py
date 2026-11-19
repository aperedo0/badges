from pathlib import Path
F=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_fidelity')
D=Path(__file__).resolve().parent
s=(F/"render_candidate.py").read_text().replace("D=Path(__file__).resolve().parent;OLD", "D=Path("+repr(str(D))+");OLD",1).replace("(D/'environment.py').read_text()", "(Path("+repr(str(D))+ ")/'environment.py').read_text()").replace("apply_environment(sc,D,ENV)","apply_environment(sc,Path("+repr(str(F))+"),ENV)")
s=s.replace("code=code.replace(needle,setup+needle,1);exec", "code=code.replace(\'sc.cycles.samples=64 if final else 24\',\'sc.cycles.samples=128 if final else 24\');code=code.replace(needle,setup+needle,1);exec")
exec(compile(s,"reused_iron_render_infrastructure","exec"))

from pathlib import Path
D=Path(__file__).resolve().parent;S=D.parent/'surface_definition'
code=(S/'render.py').read_text().replace("D=Path(__file__).resolve().parent;",'D=Path('+repr(str(S))+');',1).replace('softwarm','copperlight').replace("'Key':(1,.82,.58)","'Key':(1,.77,.46)")
exec(compile(code,'isolated_copper_key_test','exec'))

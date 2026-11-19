from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'render_aov.py').read_text().replace('from aov_iron import setup_iron_aovs','from aov_edge_cut import setup_iron_aovs');exec(compile(s,'reused_edge_aov_adapter','exec'))

from pathlib import Path
W=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement')
KEY='P_physical_fractures'
exec(compile((W/'apply_candidate_live.py').read_text(),'apply_candidate_live','exec'))
exec(compile((W/'render_candidate.py').read_text(),'render_candidate','exec'))

exec(compile((W/'validate_and_render_p.py').read_text(),'validate_and_render_p','exec'))

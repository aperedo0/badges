from pathlib import Path
W=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement')
KEY='O_timber_balanced'
exec(compile((W/'apply_candidate_live.py').read_text(),'apply_candidate_live','exec'))
exec(compile((W/'render_candidate.py').read_text(),'render_candidate','exec'))

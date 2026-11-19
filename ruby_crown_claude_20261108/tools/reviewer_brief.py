"""Fill the fixed reviewer prompt for one build: reviewer_brief.py CANDIDATE_DIR > brief.txt"""
import sys
from pathlib import Path
ROOT = Path('/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108')
cand = Path(sys.argv[1]).resolve()
text = (ROOT / 'tools/reviewer_prompt.md').read_text()
text = text.replace('{MOCKUP}', str(ROOT / 'reference/crown.png'))
text = text.replace('{SAME_HEIGHT}', str(cand / 'same_height.png'))
text = text.replace('{POSES}', str(cand / 'compare_all.png'))
text = text.replace('{INTENDED}', 'Every arch reaches the top middle of the crown and meets the others under the fleur de lis (in the mockup the outermost arches curl outward instead). The stones that are blue in the mockup are ruby red in the build.')
print(text)

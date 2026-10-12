import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
tier,number=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3]
w=Path(MANIFEST[tier]['work']);out=w/'candidates'/number
st=Usd.Stage.Open(str(next((out/'usd').glob('*.usd*'))))
package=out/(tier+'_badge_mobile.usdz')
if package.exists():package.unlink()
report=json.loads((out/'build.json').read_text());changes=report['changes']
if (out/'sharpness.json').exists():changes.append(json.loads((out/'sharpness.json').read_text()))
finish(tier,w,out,st,changes)

"""setconst.py name=value ... : sets the `constant <type> name = value;` lines of BadgeGemSurface.metal (float3 values as a,b,c)."""
import re, sys
p = '/Users/antonioperedo/Desktop/screen_time/ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal'
s = open(p).read()
for arg in sys.argv[1:]:
    name, value = arg.split('=')
    m = re.search(r'^(constant (?:float3|float|int) %s = )(.*?);' % re.escape(name), s, re.M)
    assert m, name
    new = f'float3({value})' if ',' in value else value
    s = s[:m.start(2)] + new + s[m.end(2):]
open(p, 'w').write(s)
print('set', ' '.join(sys.argv[1:]))

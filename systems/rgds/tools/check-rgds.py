#!/usr/bin/env python3
"""Validate RG DS theme assets, screen bounds, launchers and touch behavior."""
from pathlib import Path
import re, subprocess, tempfile, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
THEME=ROOT/'multi-pop-rgds'
for p in THEME.rglob('*.xml'):
    tree=ET.parse(p)
    for n in tree.iter():
        if n.tag in ('path','fontPath','default') and n.text and n.text.startswith('${themePath}/'):
            assert (THEME/n.text.removeprefix('${themePath}/')).is_file(), (p,n.text)
        if n.tag=='include' and n.text and '${' not in n.text:
            assert (p.parent/n.text).is_file(), (p,n.text)
for p in (THEME/'layouts').glob('*.xml'):
    for view in ET.parse(p).getroot().findall('view'):
        for n in view:
            pos=n.find('pos'); size=n.find('size')
            if size is None: size=n.find('maxSize')
            if pos is None or size is None or n.get('name')=='canvas': continue
            x,y=map(float,pos.text.split()); w,h=map(float,size.text.split())
            if x==1 and y==1: continue
            ox,oy=map(float,n.findtext('origin','0 0').split())
            assert y-h*oy >= -1e-6 and y+h*(1-oy) <= 1+1e-6, (p,n.get('name'),'vertical bounds')
            left=x-w*ox; right=left+w
            assert (left>=1/3-1e-6 and right<=2/3+1e-6) or (left>=2/3-1e-6 and right<=1+1e-6), (p,n.get('name'),left,right)
for p in (THEME/'scripts').glob('*.sh'):
    subprocess.run(['bash','-n',str(p)],check=True)
patch=(THEME/'frontend/rgds-game-paging.patch').read_text()
marker='--- /dev/null\n+++ b/es-core/src/components/ThorTouchGesture.h\n'
with tempfile.TemporaryDirectory() as tmp:
    work=Path(tmp)
    subprocess.run(['patch','-p1','--batch'],input=marker+patch.split(marker)[1],text=True,cwd=work,check=True,stdout=subprocess.DEVNULL)
    (work/'test.cpp').write_text('''#include "es-core/src/components/ThorTouchGesture.h"
#include <cassert>
int main() {
  assert(ThorTouchGesture::libraryBackHit(660,20));
  assert(ThorTouchGesture::libraryBackHit(1310,20));
  assert(!ThorTouchGesture::libraryBackHit(1400,20));
  ThorTouchGesture g;
  g.begin(1500,200,100); assert(g.move(1505,202)==0); assert(g.tap(200));
  g.begin(1500,200,100); assert(g.move(1400,200)==2); assert(!g.tap(200));
  g.begin(1500,200,100); assert(g.move(1500,250)==0); assert(!g.tap(200));
  g.begin(1500,200,100); g.move(1279,200); assert(!g.tap(200));
  g.begin(800,200,100,640,1280); assert(g.move(750,200)==1);
  ThorTouchTargets t; t.add(1,1300,100,100,150); assert(t.hit(1350,120)==1); assert(t.hit(1500,120)==-1);
}''')
    subprocess.run(['c++','-std=c++11',str(work/'test.cpp'),'-o',str(work/'test')],check=True)
    subprocess.run([str(work/'test')],check=True)
assert 'seat seat1 attach "1046:911:Goodix_Capacitive_TouchScreen"' in (THEME/'scripts/enable_multi_pop_rgds.sh').read_text()
assert 'X Game info' in ET.parse(THEME/'layouts/games.xml').findtext(".//text[@name='browse-hints']/text")
# Selection must remain visible on pale system palettes at the native panel size.
def luminance(value):
    rgb = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))
for palette in (THEME / 'palettes').glob('*.xml'):
    variables = ET.parse(palette).find('variables')
    if variables is None or variables.find('accent') is None:
        continue
    paper = luminance(variables.findtext('paper', 'F7F8FCFF'))
    outline = luminance(variables.findtext('selectionAccent'))
    assert (paper + .05) / (outline + .05) >= 3, palette
print('PASS: XML, assets, panel bounds, shell syntax, RG DS gesture behavior')

subprocess.run([__import__('sys').executable, str(ROOT/'tools/check-logo-assets.py'), str(THEME)], check=True)

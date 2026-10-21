#!/usr/bin/env python3
"""Compile the actual jump-menu placement block and enforce upper-panel bounds."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
patch=(root/'multi-pop-rgds/frontend/rgds-popup-placement.patch').read_text()
part=patch.split('--- a/es-app/src/views/SystemView.cpp\n',1)[1].split('new file mode',1)[0]
block='\n'.join(line[1:] for line in part.splitlines() if line.startswith('+') and not line.startswith('+++'))
# Animate calls are outside the placement block; use its actual declarations and clamp.
block=block.split('gs->getMenu().animateTo',1)[0]
block='\n'.join(line for line in block.splitlines() if 'Vector2f' not in line)
source='''#include <algorithm>
#include <cassert>
namespace Renderer { int getScreenWidth(){return 1920;} int getScreenHeight(){return 480;} }
namespace Math { float min(float a,float b){return std::min(a,b);} }
void check(float w) {
'''+block+'''
assert(w <= 600);
assert(menuX >= 640);
assert(menuX + w <= 1280);
assert(startX + w == 640);
}
int main(){ for(float w : {320.f,480.f,640.f,960.f,1800.f}) check(w); }
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'test.cpp').write_text(source)
 subprocess.run(['c++','-std=c++11',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: actual jump-menu placement stays within the upper640px panel')

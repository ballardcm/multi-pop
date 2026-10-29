"""Refresh logo routing without replacing RG DS palette colors or selection contrast."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
THEME=Path(__file__).resolve().parents[1]/'multi-pop-rgds'
catalog=json.loads((THEME/'assets/logos/catalog.json').read_text())
platforms=json.loads((THEME/'platforms.json').read_text())
for key,info in platforms.items():
    path=THEME/'palettes'/(key+'.xml');tree=ET.parse(path);variables=tree.find('variables')
    for prefix,kind,lookup in [('platform','platforms',key),('manufacturer','manufacturers',info['manufacturer'])]:
        entry=catalog[kind].get(lookup)
        values={prefix+'Logo':'${themePath}/assets/logos/'+entry['file'] if entry else '${themePath}/assets/ui/white.svg',prefix+'LogoVisible':str(bool(entry)).lower(),prefix+'TextVisible':str(not entry).lower()}
        for name,value in values.items():
            element=variables.find(name)
            if element is None:element=ET.SubElement(variables,name)
            element.text=value
    ET.indent(tree,space='  ');tree.write(path,encoding='utf-8',xml_declaration=True)
print('Updated logo routing in',len(platforms),'RG DS palettes.')

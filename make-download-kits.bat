@echo off
cd /d "%~dp0"
echo Laddar ner CC0-byggstenar (Quaternius) till media\library\kits
if not exist media\library\kits mkdir media\library\kits
cd media\library\kits
curl -L --fail --retry 3 -o medieval_village_megakit.zip https://opengameart.org/sites/default/files/medieval_village_megakitstandard.zip
curl -L --fail --retry 3 -o fantasy_props_megakit.zip https://opengameart.org/sites/default/files/fantasy_props_megakitstandard.zip
if not exist medieval-village mkdir medieval-village
tar -xf medieval_village_megakit.zip -C medieval-village
if not exist fantasy-props mkdir fantasy-props
tar -xf fantasy_props_megakit.zip -C fantasy-props
dir /s /b *.gltf *.glb | find /c "."
echo klar

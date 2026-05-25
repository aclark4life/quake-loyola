# Quake Map Build Instructions

## Generate the map

```bash
python generate_map.py
```

## Compile with ericw-tools

```bash
TOOLS=~/Downloads/ericw-tools-v0.18.1-Darwin/bin
MAP=/Users/alex.clark/Developer/quake-loyola/loyola.map

$TOOLS/qbsp "$MAP"
$TOOLS/vis "${MAP%.map}.bsp"
$TOOLS/light "${MAP%.map}.bsp"
```

## Deploy to Quake

```bash
mkdir -p /Applications/id1/maps
cp /Users/alex.clark/Developer/quake-loyola/loyola.bsp /Applications/id1/maps/
```

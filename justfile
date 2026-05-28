# justfile for Loyola bridge Quake 1 map

# Paths to tools and directories
tools_bin := "~/Downloads/ericw-tools-v0.18.1-Darwin/bin"
quake_dir := "/Applications/id1"
maps_dir  := quake_dir + "/maps"
map_name  := "loyola"

# Default task: generate, compile, and deploy
all: generate compile deploy

# Generate the .map file from the Python script
generate:
    python3 generate_map.py

# Compile the map (geometry, visibility, and lighting)
compile:
    {{tools_bin}}/qbsp {{map_name}}.map
    {{tools_bin}}/vis {{map_name}}.bsp
    {{tools_bin}}/light {{map_name}}.bsp

# Deploy the compiled map and lighting data to the Quake directory
deploy:
    mkdir -p {{maps_dir}}
    cp {{map_name}}.bsp {{maps_dir}}/
    cp {{map_name}}.lit {{maps_dir}}/

# Clean up temporary build files
clean:
    rm -f {{map_name}}.bsp {{map_name}}.lit {{map_name}}.prt {{map_name}}.pts {{map_name}}.log

# justfile for Loyola bridge Quake 1 map

# Paths to tools and directories
ericw_version := "v0.18.1"
ericw_dir     := justfile_directory() + "/.tools/ericw-tools-" + ericw_version + "-Darwin"
tools_bin     := ericw_dir + "/bin"
quake_dir := "/Applications/id1"
maps_dir  := quake_dir + "/maps"
map_name  := "loyola"

# Show available recipes
default:
    @just all

# Default task: setup, generate, compile, and deploy
all: setup generate compile-fast deploy

# Download and install ericw-tools into .tools/
install-tools:
    #!/usr/bin/env bash
    set -euo pipefail
    archive="ericw-tools-{{ericw_version}}-Darwin.zip"
    url="https://github.com/ericwa/ericw-tools/releases/download/{{ericw_version}}/$archive"
    dest="{{justfile_directory()}}/.tools"
    if [ -d "{{ericw_dir}}" ]; then
        echo "ericw-tools {{ericw_version}} already installed at {{ericw_dir}}"
    else
        mkdir -p "$dest"
        echo "Downloading $archive..."
        curl -L -o "$dest/$archive" "$url"
        unzip -q "$dest/$archive" -d "$dest"
        rm "$dest/$archive"
        echo "Installed ericw-tools {{ericw_version}} to {{ericw_dir}}"
    fi

# Download WADs if they don't exist
setup:
    @if [ ! -f quake101.wad ]; then \
        echo "quake101.wad not found, downloading from Quaketastic..."; \
        curl -L -o quake101.wad http://www.quaketastic.com/files/texture_wads/quake101.wad; \
    fi
    @if [ ! -f ad.wad ]; then \
        echo "ad.wad not found, downloading from Quaketastic..."; \
        curl -L -o ad.wad http://www.quaketastic.com/files/texture_wads/ad.wad; \
    fi

# Generate the .map file from the Python script
generate:
    python3 generate_map.py

# Compile the map (geometry, visibility, and lighting)
compile: install-tools
    {{tools_bin}}/qbsp {{map_name}}.map
    {{tools_bin}}/vis {{map_name}}.bsp
    {{tools_bin}}/light {{map_name}}.bsp

# Fast compile: skips Full Vis pass, uses 2x2 extra sampling for lighting
compile-fast: install-tools
    {{tools_bin}}/qbsp {{map_name}}.map
    {{tools_bin}}/vis -fast {{map_name}}.bsp
    {{tools_bin}}/light {{map_name}}.bsp

# Deploy the compiled map and lighting data to the Quake directory
deploy:
    mkdir -p {{maps_dir}}
    cp {{map_name}}.bsp {{maps_dir}}/
    cp {{map_name}}.lit {{maps_dir}}/

# Clean up temporary build files
clean:
    rm -f {{map_name}}.bsp {{map_name}}.lit {{map_name}}.prt {{map_name}}.pts {{map_name}}.log

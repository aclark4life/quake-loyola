# justfile for Loyola bridge Quake 1 map

# Paths to tools and directories
ericw_version := "v0.18.1"
ericw_os      := if os() == "macos" { "Darwin" } else { "Linux" }
ericw_dir     := justfile_directory() + "/.tools/ericw-tools-" + ericw_version + "-" + ericw_os
tools_bin     := ericw_dir + "/bin"
gmqcc_bin  := justfile_directory() + "/.tools/gmqcc/gmqcc"
progs_src  := justfile_directory() + "/qc/progs.src"
quake_dir  := "/Applications/id1"
maps_dir   := quake_dir + "/maps"
map_name  := "loyola"

# Show available recipes
default:
    @just all

# Alias for run
alias r := run

# Default task: setup, generate, compile, and deploy
all: setup generate compile-fast deploy

# Download and install ericw-tools into .tools/
install-tools:
    #!/usr/bin/env bash
    set -euo pipefail
    archive="ericw-tools-{{ericw_version}}-{{ericw_os}}.zip"
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

# Create the local .venv and install test and docs dependencies
venv:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -d .venv ]; then python3 -m venv .venv; fi
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -e . --group dev --group docs

# Run the Python unit + regression test suite with pytest
test: venv
    .venv/bin/pytest

# Compile the map (geometry, visibility, and lighting)
compile: install-tools venv
    #!/usr/bin/env bash
    set -euo pipefail
    light_extra=$(.venv/bin/python3 -c "from quake_loyola import config; print(config.get_build('light_extra'))")
    {{tools_bin}}/qbsp -bsp2 {{map_name}}.map
    {{tools_bin}}/vis {{map_name}}.bsp
    light_args=()
    if [ "$light_extra" = "True" ]; then light_args+=(-extra); fi
    {{tools_bin}}/light "${light_args[@]}" {{map_name}}.bsp

# Fast compile: skips Full Vis pass, honors ql.toml's [build] light_extra setting
compile-fast: install-tools venv
    #!/usr/bin/env bash
    set -euo pipefail
    light_extra=$(.venv/bin/python3 -c "from quake_loyola import config; print(config.get_build('light_extra'))")
    {{tools_bin}}/qbsp -bsp2 {{map_name}}.map
    {{tools_bin}}/vis -fast {{map_name}}.bsp
    light_args=()
    if [ "$light_extra" = "True" ]; then light_args+=(-extra); fi
    {{tools_bin}}/light "${light_args[@]}" {{map_name}}.bsp

# Deploy the compiled map and lighting data to the Quake directory
deploy:
    mkdir -p {{maps_dir}}
    cp {{map_name}}.bsp {{maps_dir}}/
    cp {{map_name}}.lit {{maps_dir}}/

# Build the Sphinx HTML documentation into docs/_build/html/
docs: venv
    .venv/bin/sphinx-build -b html docs docs/_build/html
    @echo "Docs written to docs/_build/html/index.html"

# Serve the reveal.js project presentation at http://localhost:8000/presentation/
present:
    @echo "Serving presentation at http://localhost:8000/presentation/ (Ctrl-C to stop)"
    python3 -m http.server 8000

# Update the golden hash/counts in tests/test_regression.py from the current map output
update-golden: venv
    .venv/bin/python scripts/update_golden.py

# Compile QuakeC source in qc/ into progs.dat using gmqcc
# NOTE: this recipe requires .tools/gmqcc/gmqcc, which is *not* installed by
# `just install-tools` — build it from source manually first. QC integration
# is an on-hold experiment; see docs/quakec.rst for the full toolchain setup.
compile-qc:
    cd qc && {{gmqcc_bin}} -std=fteqcc -Wall -o ../progs.dat \
        defs.qc subs.qc combat.qc items.qc weapons.qc world.qc \
        client.qc player.qc doors.qc buttons.qc triggers.qc plats.qc misc.qc \
        server.qc

# Deploy progs.dat to the Quake id1 directory (overrides stock game logic)
deploy-qc:
    python3 scripts/make_pak3.py progs.dat {{quake_dir}}/pak2.pak

# Clean up temporary build files and test artifacts
clean:
    rm -f {{map_name}}.bsp {{map_name}}.lit {{map_name}}.vis
    rm -f progs.dat
    rm -f test.bsp
    rm -f test_*.json
    rm -f *.log *.prt *.pts
    find . -name "__pycache__" -type d -exec rm -rf {} +

# Run Quake
run:
    /Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir /Applications +map loyola -game ad

# Alias for r-nosound
alias r-ns := r-nosound

# Run Quake with sound disabled
r-nosound:
    /Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir /Applications +map loyola -game ad -nosound

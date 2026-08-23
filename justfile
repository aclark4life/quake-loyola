# justfile for Loyola bridge Quake 1 map

# Paths to tools and directories
# ericw-tools 2.0.0-alpha11 or newer is required: qbsp v0.18.1 drops and
# orphans faces on Pier 6's rotated stonework, which shows up in game as
# see-through holes and invisible walls.
ericw_version := "2.0.0-alpha11"
ericw_os      := if os() == "macos" { "Darwin" } else { "Linux" }
ericw_dir     := justfile_directory() + "/.tools/ericw-tools-" + ericw_version + "-" + ericw_os
tools_bin     := ericw_dir
gmqcc_bin  := justfile_directory() + "/.tools/gmqcc/gmqcc"
progs_src  := justfile_directory() + "/qc/progs.src"
# Match `quake_loyola.skyboxes.quake_dir()`, which the `ql build --deploy` path
# uses: both honour $QUAKE_DIR so `just deploy` and `ql build` can never target
# different directories on the same machine.
quake_dir  := env_var_or_default("QUAKE_DIR", "/Applications/id1")
quake_base := parent_directory(quake_dir)
maps_dir   := quake_dir + "/maps"
map_name  := "loyola"

# The QuakeC experiment gets its own gamedir rather than overriding id1's stock
# game logic. A custom progs.dat anywhere in id1 replaces stock Quake for EVERY
# map, not just this one -- an orphaned pak of an old, half-finished build once
# sat in id1 and killed `map loyola` with "Host_Error: Illegible server message
# 39" the moment the player spawned. That was invisible from `just run`, which
# passes `-game ad` and so loaded AD's progs instead, and only showed up when
# launching vkQuake from the macOS launcher with no arguments. Confined to its
# own gamedir, the experiment is opt-in via `just run-qc` and can't contaminate
# a plain launch. Maps still deploy to id1/maps; the engine falls back to id1
# for anything the gamedir lacks, so `-game loyola` still finds loyola.bsp.
qc_game    := "loyola"
qc_dir     := quake_base / qc_game

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
        # The 2.x archives have no top-level directory, so extract into one.
        unzip -q "$dest/$archive" -d "{{ericw_dir}}"
        rm "$dest/$archive"
        # macOS quarantines downloaded binaries; Gatekeeper would block them.
        if [ "{{ericw_os}}" = "Darwin" ]; then
            xattr -dr com.apple.quarantine "{{ericw_dir}}" 2>/dev/null || true
        fi
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

# Compile the map (geometry, visibility, and lighting) with a full Vis pass.
# Delegates to `ql build`, so there is a single implementation of the
# qbsp -> vis -> light pipeline; the recipe name pins the Vis pass via --vis,
# overriding ql.toml's [build] vis_mode for this run only. [build] light_extra
# is honored unless overridden.
compile: install-tools venv
    .venv/bin/ql build --vis full --no-gen --no-deploy

# Fast compile: skips the Full Vis pass. As with `compile`, the recipe name
# pins the Vis pass via --vis; everything else comes from ql.toml's [build].
compile-fast: install-tools venv
    .venv/bin/ql build --vis fast --no-gen --no-deploy

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

# Deploy progs.dat into its own gamedir (never id1 — see the qc_dir comment)
deploy-qc:
    mkdir -p {{qc_dir}}
    python3 scripts/make_pak3.py progs.dat {{qc_dir}}/pak0.pak
    @echo "Deployed to {{qc_dir}}/pak0.pak — run it with \`just run-qc\`."

# Remove the deployed QuakeC gamedir pak, reverting to stock game logic
undeploy-qc:
    rm -f {{qc_dir}}/pak0.pak
    @echo "Removed {{qc_dir}}/pak0.pak — \`just run-qc\` now falls back to stock progs."

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
    /Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir {{quake_base}} +map loyola -game ad

# Alias for r-nosound
alias r-ns := r-nosound

# Run Quake with sound disabled
r-nosound:
    /Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir {{quake_base}} +map loyola -game ad -nosound

# Run the map against the experimental QuakeC gamedir instead of Arcane Dimensions
run-qc:
    /Applications/vkQuake.app/Contents/MacOS/vkQuake -basedir {{quake_base}} +map loyola -game {{qc_game}}

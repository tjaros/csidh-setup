{
  description = "Dev shell for ChipWhisperer + csidhtools (pure venv, no global leakage)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python311
            python311Packages.virtualenv  # ensures `python -m venv` works
            llvmPackages_9.clang-unwrapped
            gcc-arm-embedded-9
            cmake
            sage
            gcc
            ripgrep
            texliveFull
            libusb1
            hidapi
          ];

          # For ctypes/dlls at runtime if needed
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.hidapi
            pkgs.libusb1
            pkgs.stdenv.cc.cc.lib
          ];

          shellHook = ''
            set -euo pipefail

            # absolute isolation from user/site packages
            export PYTHONNOUSERSITE=1
            unset PYTHONPATH

            VENV_DIR="$PWD/.venv"
            if [ ! -d "$VENV_DIR" ]; then
              python -m venv "$VENV_DIR"
            fi
            # shellcheck disable=SC1090
            source "$VENV_DIR/bin/activate"

            python -m pip install --upgrade pip wheel setuptools

            # --- Patch + install ChipWhisperer (editable or regular) ---
            if [ -d ./chipwhisperer ] && [ -f ./patches/chipwhisperer.patch ]; then
              echo "[chipwhisperer] applying patch if clean..."
              ( cd chipwhisperer
                # reset only the working tree of the local clone; adapt if you have local changes you want to keep
                git reset --hard
                if git apply --check ../patches/chipwhisperer.patch >/dev/null 2>&1; then
                  git apply ../patches/chipwhisperer.patch
                else
                  echo "[chipwhisperer] patch already applied or not applicable"
                fi
              )
              # install chipwhisperer (choose one):
              python -m pip install -r chipwhisperer/jupyter/requirements.txt
              python -m pip install ./chipwhisperer
            else
              echo "[chipwhisperer] repo or patch not found; skipping"
            fi

            # --- Install your package (editable) ---
            if [ -d ./csidh-tools ]; then
              python -m pip install -e ./csidh-tools
            fi

            echo
            echo "Python: $(python -V)"
            echo "Which python: $(command -v python)"
            echo "Pip site-packages: $(python -c 'import sys, site; print(site.getsitepackages())')"
            echo "Venv ready. You're isolated from system/user packages."
          '';
        };
      });
}


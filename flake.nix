{
  description = "Development shell for my Chipwhisperer shenanigans";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      libPath = with pkgs;
        lib.makeLibraryPath [
          hidapi
          libusb1
          stdenv.cc.cc.lib
        ];
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python311.withPackages (ps:
        with ps; [
          virtualenv
          pip
          notebook
        ]);
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python
          llvmPackages_9.clang-unwrapped
          gcc-arm-embedded-9
          cmake
          sage
	  gcc
          ripgrep
          texliveFull
	  helix
        ];

        shellHook = ''
          # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
          # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
          export PIP_PREFIX=$(pwd)/_build/pip_packages
          export PYTHONPATH="$PIP_PREFIX/${python.sitePackages}:$PYTHONPATH"
          export PATH="${python}/bin:$PIP_PREFIX/bin:$PATH"
          unset SOURCE_DATE_EPOCH

          # Patch the chipwhisperer module
          # Apply the chipwhisperer patch if not already applied
          if [ -d ./chipwhisperer ] && [ -f ./patches/chipwhisperer.patch ]; then
            cd chipwhisperer
            if git apply --check ../patches/chipwhisperer.patch > /dev/null 2>&1; then
              echo "Applying chipwhisperer patch..."
              git apply ../patches/chipwhisperer.patch
            else
              echo "Chipwhisperer patch already applied or cannot be applied cleanly."
            fi
            cd ..
          else
            echo "Chipwhisperer directory or patch file not found!"
          fi

         # Install our version of Chipwhisperer
	 cd chipwhisperer
         pip install -r jupyter/requirements.txt
         pip install .
	 cd ..

	 # Install our utility scripts
	 cd csidh-tools
	 pip install .
        '';

        LD_LIBRARY_PATH = libPath;
      };
    });
}

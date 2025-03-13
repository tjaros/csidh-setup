{
  description = "Python development shell 3.10";
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
          # load external libraries that you need in your rust project here
          hidapi
          libusb1
          stdenv.cc.cc
        ];
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python311.withPackages (ps:
        with ps; [
          virtualenv
          pip
        ]);
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python
          llvmPackages_9.clang-unwrapped
          gcc-arm-embedded-9
          cmake
          sage
          packer
        ];

        shellHook = ''
          # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
          # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
          export PIP_PREFIX=$(pwd)/_build/pip_packages
          export PYTHONPATH="$PIP_PREFIX/${python.sitePackages}:$PYTHONPATH"
          export PATH="${python}/bin:$PIP_PREFIX/bin:$PATH"
          unset SOURCE_DATE_EPOCH
        '';

        LD_LIBRARY_PATH = libPath;
      };
    });
}

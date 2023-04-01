# SPDX-FileCopyrightText: 2021 Serokell <https://serokell.io/>
#
# SPDX-License-Identifier: CC0-1.0

{
  description = "My Python application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    returns-nix.url = "github:jesseDMoore1994/returns-nix";
  };

  outputs = { self, nixpkgs, flake-utils, returns-nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        customOverrides = self: super: {
          # Overrides go here
        };

        myOverrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: {
          iniconfig = super.iniconfig.overridePythonAttrs
          (
            old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ super.hatchling super.hatch-vcs ];
            }
          );
          returns = super.returns.overridePythonAttrs
          (
            old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ super.poetry ];
            }
          );
        });

        app = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          overrides = myOverrides;
        };

        env = pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          overrides = myOverrides;
        };

        packageName = "random-anime";
      in {
        packages.${packageName} = app;

        defaultPackage = self.packages.${system}.${packageName};

        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.poetry
            returns-nix.packages.${system}.returns
            pkgs.lightspark
            env
          ];
          inputsFrom = builtins.attrValues self.packages.${system};
        };
      });
}

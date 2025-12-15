# CSIDH Setup

This repository contains a development environment for CSIDH implementation with ChipWhisperer support using Nix.

## Prerequisites

### Install Nix

Install Nix via the recommended multi-user installation:

```bash
sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --daemon
```

For more installation options, see the [official Nix installation guide](https://nixos.org/download/#nix-install-linux).

## Setup

### Clone the repository

```bash
git clone -j8 https://github.com/tjaros/csidh-setup.git --recurse-submodules
```

```bash
cd csidh-setup
```

### Install ChipWhisperer udev rules

```bash
sudo cp chipwhisperer/hardware/50-newae.rules /etc/udev/rules.d/50-newae.rules
```

```bash
sudo udevadm control --reload-rules
```

```bash
sudo groupadd -fr chipwhisperer
```

```bash
sudo usermod -aG chipwhisperer $USER
```

```bash
sudo usermod -aG plugdev $USER
```

**Reboot your system** for the udev rules to take effect.

For more details on ChipWhisperer installation, see the [official ChipWhisperer Linux installation guide](https://chipwhisperer.readthedocs.io/en/latest/linux-install.html).

### Set up CSIDH implementation

Choose which CSIDH implementation you want to use by switching to the appropriate branch in the `csidh-target` submodule:

```bash
cd csidh-target
```

```bash
git switch dummy
```

or

```bash
git switch dummy-free
```

```bash
cd ..
```

### IMPORTANT: Create HAL symlink

If it does not exist, create a symlink to the ChipWhisperer HAL directory:

```bash
ln -s ./chipwhisperer/hardware/victims/firmware/hal csidh-target/src/hal
```

### Enter the development environment

```bash
nix develop
```

This command will:
- Install all necessary compilers (ARM GCC, AVR GCC, Clang)
- Set up Python 3.11 with a virtual environment
- Install ChipWhisperer and apply necessary patches
- Install csidh-tools in editable mode
- Configure all dependencies (cmake, sage, libusb, etc.)

## Directory Structure

```
csidh-setup/
├── notebooks/              # Contains Jupyter notebooks used for analysis
│   └── data/               $ Contains collected data in JSON format 
├── chipwhisperer/          # ChipWhisperer submodule
├── csidh-target/           # CSIDH implementation sources (from csidhfi)
│   └── src/
│       └── hal/            # Symlink to chipwhisperer/hardware/victims/firmware/hal/
├── csidh-tools/            # CSIDH tools package
├── patches/                # Patches for ChipWhisperer
│   └── chipwhisperer.patch
├── flake.nix               # Nix development environment configuration
└── README.md               # This file
```

## Working with Jupyter Notebooks

To launch Jupyter Lab for interactive notebooks:

```bash
jupyter-lab
```

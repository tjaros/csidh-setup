# Setup

This repository contains a guide to setting up the FI setup on CW and CW-Husky.

Python version: `3.10<=`.
Chipwhisperer version: `5.7.0`

## Downloading this repository

First we clone this repository and initialize the submodules.

```bash
git clone -j8 https://github.com/tjaros/csidh-setup.git --recurse-submodules
```

## Installing Chipwhisperer

This part was taken from [Chipwhisperer Quick installation instructions](https://chipwhisperer.readthedocs.io/en/latest/linux-install.html). Assuming you have Debian/Ubuntu based distribution with `apt-get` and `apt`.

```bash
sudo apt update && sudo apt upgrade

# python prereqs
sudo apt-get install build-essential gdb lcov pkg-config \
    libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
    lzma lzma-dev tk-dev uuid-dev zlib1g-dev curl

sudo apt install libusb-dev make git avr-libc gcc-avr \
    gcc-arm-none-eabi libusb-1.0-0-dev usbutils

# Virtual environment setup
# install pyenv - skip if already done
    curl https://pyenv.run | bash
    echo 'export PATH="~/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="~/.pyenv/shims:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv install 3.10.13
pyenv virtualenv 3.10.13 cw
pyenv activate cw

cd chipwhisperer
sudo cp hardware/50-newae.rules /etc/udev/rules.d/50-newae.rules
sudo udevadm control --reload-rules
sudo groupadd -f chipwhisperer
sudo usermod -aG chipwhisperer $USER
sudo usermod -aG plugdev $USER

# Alternatively you can try
# pip install chipwhisperer
python -m pip install -e .
```

Docker image might be set up alternatively, though thats future work for now.

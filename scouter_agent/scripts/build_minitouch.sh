#!/bin/bash

# ===========================================
#  Script: build_minitouch.sh
#  Purpose: Automate the build process for minitouch on WSL/Linux
#  Author: JM (with GPT assistant)
# ===========================================

set -e  # Exit on first error

# -------- CONFIGURATION --------
NDK_VERSION="r25c"
NDK_ZIP="android-ndk-${NDK_VERSION}-linux.zip"
NDK_URL="https://dl.google.com/android/repository/${NDK_ZIP}"
NDK_DIR="$HOME/android-ndk"

MINITOUCH_REPO="https://github.com/openstf/minitouch.git"
MINITOUCH_DIR="$HOME/minitouch"

# -------- FUNCTIONS --------

install_dependencies() {
    echo "🔧 Installing required packages..."
    sudo apt update
    sudo apt install -y wget unzip git make
}

download_ndk() {
    if [ ! -d "$NDK_DIR" ]; then
        echo "⬇️  Downloading Android NDK..."
        wget $NDK_URL
        unzip $NDK_ZIP
        mv android-ndk-$NDK_VERSION $NDK_DIR
        rm $NDK_ZIP
    else
        echo "✅ NDK already exists at $NDK_DIR"
    fi
}

clone_minitouch() {
    if [ ! -d "$MINITOUCH_DIR" ]; then
        echo "📥 Cloning minitouch repository..."
        git clone $MINITOUCH_REPO $MINITOUCH_DIR
    else
        echo "✅ minitouch repository already cloned."
    fi
}

init_submodules() {
    echo "🔄 Initializing git submodules..."
    cd $MINITOUCH_DIR
    git submodule update --init --recursive
}

build_minitouch() {
    echo "⚙️  Building minitouch..."
    export NDK=$NDK_DIR
    export PATH=$NDK:$PATH
    cd $MINITOUCH_DIR
    make
}

copy_binaries() {
    echo "📦 Copying built binaries to scouter_agent/infrastructure/minitouch_binaries..."
    mkdir -p ~/scouter_agent/infrastructure/minitouch_binaries
    cp -r $MINITOUCH_DIR/out/* ~/scouter_agent/infrastructure/minitouch_binaries/
    echo "✅ Binaries copied."
}

# -------- EXECUTION --------

echo "🚀 Starting minitouch build process..."
install_dependencies
download_ndk
clone_minitouch
init_submodules
build_minitouch
copy_binaries
echo "🏁 Build process completed successfully!"

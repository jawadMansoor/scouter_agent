# 📘 Documentation: Building minitouch for Scouter Agent
## Overview
This guide explains how to build minitouch from source for automating multi-touch gestures in your Scouter Agent project.

---

## 🛠 Prerequisites
Windows 10/11 with WSL (Ubuntu) installed.

~2GB free space for Android NDK.

ADB installed on Windows (for device communication).

---

## 🚀 Build Steps
1. Clone Your Scouter Repo

```bash
git clone https://github.com/yourusername/scouter_agent.git
cd scouter_agent
```
2. Run the Automated Build Script

```bash
bash scripts/build_minitouch.sh
```
3. The script will:

Install required Linux packages.

Download & setup Android NDK.

Clone minitouch and initialize submodules.

Build binaries for multiple architectures.

Copy binaries to:

```bash
scouter_agent/infrastructure/minitouch_binaries/
```

---

## 🎯 Usage in Scouter Agent
At runtime, your agent can push the correct binary:

```bash
adb -s $DEVICE_ID push infrastructure/minitouch_binaries/x86/minitouch /data/local/tmp/
adb -s $DEVICE_ID shell chmod 755 /data/local/tmp/minitouch
```
Then forward the port and connect for gesture control.

---

## 💡 Notes
This script is idempotent — safe to run multiple times.

To update minitouch source, simply cd ~/minitouch && git pull && git submodule update --init --recursive.

You can adjust NDK_VERSION if needed.
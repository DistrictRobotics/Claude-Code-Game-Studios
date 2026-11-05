#!/usr/bin/env bash
# Provision a RunPod instance for DC GoGo Fest UE5 development.
# Run once on a fresh pod:  bash provision-runpod.sh
set -euo pipefail

WORKSPACE=/workspace
UE_VERSION=5.6

echo "==> Verifying persistent volume at ${WORKSPACE}"
if ! mountpoint -q "${WORKSPACE}" 2>/dev/null && [ ! -d "${WORKSPACE}" ]; then
  echo "ERROR: ${WORKSPACE} not present. Pod was created without a volume." >&2
  echo "Work stored outside ${WORKSPACE} is LOST when the pod stops." >&2
  exit 1
fi
df -h "${WORKSPACE}"

echo "==> Installing system dependencies"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  build-essential clang lld cmake ninja-build \
  git git-lfs curl wget unzip \
  python3 python3-pip python3-venv \
  mono-complete dos2unix xdg-user-dirs \
  libvulkan1 vulkan-tools mesa-vulkan-drivers \
  libsdl2-dev libx11-dev libxcursor-dev libxrandr-dev libxinerama-dev libxi-dev \
  ffmpeg

git lfs install --skip-repo

echo "==> Installing Node.js 20 (required by ue-mcp)"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y -qq nodejs
node --version

echo "==> Creating workspace layout"
mkdir -p "${WORKSPACE}"/{engine,projects,assets,tools,cache}

# Keep Unreal's derived data cache on the persistent volume so it survives
# a pod stop. Rebuilding a cold DDC costs hours.
export XDG_CACHE_HOME="${WORKSPACE}/cache"
if ! grep -q 'XDG_CACHE_HOME=/workspace/cache' /root/.bashrc; then
  {
    echo 'export XDG_CACHE_HOME=/workspace/cache'
    echo 'export UE_ROOT=/workspace/engine/UnrealEngine'
    echo 'export PATH="$PATH:/workspace/tools/bin"'
  } >> /root/.bashrc
fi

echo "==> Checking GPU"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || \
  echo "WARNING: nvidia-smi unavailable; GPU rendering will not work."

cat <<'EOF'

========================================================
Base provisioning complete.

Next step is the engine, which is the slow part (~1-2 hrs):

  cd /workspace/engine
  git clone --depth 1 -b 5.6 \
    https://github.com/EpicGames/UnrealEngine.git
  cd UnrealEngine
  ./Setup.sh && ./GenerateProjectFiles.sh && make

Cloning EpicGames/UnrealEngine requires your GitHub account to
be linked to Epic (you already have that access). Use a GitHub
personal access token as the password when git prompts.

Everything lives under /workspace, so it survives a pod stop.
========================================================
EOF

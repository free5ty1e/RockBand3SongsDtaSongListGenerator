FROM --platform=linux/amd64 ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

# ── System packages ───────────────────────────────────────────────────────────
# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    jq \
    python3 \
    python3-pip \
    unzip \
    wget \
    sudo \
    cifs-utils \
    git \
    p7zip-full \
    libgl1 \
    libglu1-mesa \
    libx11-6 \
    libfontconfig1 \
    libfreetype6 \
    xvfb \
    alsa-utils \
    libpulse0 \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js 22 (NodeSource) ───────────────────────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && node --version \
    && npm --version

# ── Onyx CLI (mtolly/onyx — Linux x86_64 binary) ─────────────────────────────
# The Onyx project ships pre-built Linux binaries as GitHub release assets.
# We fetch the latest release via the GitHub API and download the linux binary.
#
# If the download URL changes between releases, update ONYX_TAG below to pin
# a specific version (e.g. "20251011"). Set to "latest" to always pull newest.
ARG ONYX_TAG=20251011

RUN set -ex; \
    ONYX_URL="https://github.com/mtolly/onyx/releases/download/${ONYX_TAG}/onyx-${ONYX_TAG}-linux-x64.AppImage"; \
    echo "Downloading Onyx ${ONYX_TAG} from ${ONYX_URL}"; \
    curl -fsSL "${ONYX_URL}" -o /tmp/onyx.AppImage \
    && mkdir -p /tmp/onyx-extracted \
    && 7z x /tmp/onyx.AppImage -o/tmp/onyx-extracted usr/bin/onyx usr/lib \
    && cp /tmp/onyx-extracted/usr/bin/onyx /usr/local/bin/ \
    && if [ -d /tmp/onyx-extracted/usr/lib ]; then cp -rn /tmp/onyx-extracted/usr/lib/* /usr/local/lib/; fi \
    && chmod +x /usr/local/bin/onyx \
    && ldconfig \
    && rm -rf /tmp/onyx.AppImage /tmp/onyx-extracted

# ── Smoke test ───────────────────────────────────────────────────────────────
# Prints version to confirm Onyx is on PATH. If this fails during `docker build`
# it means the binary URL or asset name changed — update ONYX_TAG / URL above.
RUN onyx 2>&1 | grep "Onyx Music Game Toolkit" || echo "⚠️  Onyx version check failed — binary may need URL update (see Dockerfile comments)"

# Install native x64 opencode CLI (v1.3.13)
RUN curl -fsSL -o /tmp/opencode.tar.gz https://github.com/anomalyco/opencode/releases/download/v1.3.13/opencode-linux-x64.tar.gz \
    && tar -xzf /tmp/opencode.tar.gz -C /usr/local/bin \
    && chmod +x /usr/local/bin/opencode \
    && rm /tmp/opencode.tar.gz

# ── Non-root user (vscode convention) ────────────────────────────────────────
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# Fix for Ubuntu 24.04: rename/modify the existing 'ubuntu' user if UID 1000 is taken
RUN if getent passwd $USER_UID > /dev/null; then \
    userdel -r ubuntu || true; \
    fi \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /workspace

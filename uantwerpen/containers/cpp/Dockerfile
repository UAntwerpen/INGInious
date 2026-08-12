# DOCKER-VERSION 1.1.0

ARG VERSION=main
ARG REGISTRY=ghcr.io
FROM ${REGISTRY}/inginious/env-base:${VERSION} AS env-cpp

LABEL org.inginious.grading.name="cpp"
LABEL org.inginious.grading.agent_version=4
LABEL org.opencontainers.image.source=https://github.com/UAntwerpen/INGInious

# Install Development Tools
RUN dnf -y install dnf-utils

# Enable CodeReady Builder repository
RUN dnf -y install dnf-plugins-core && \
    dnf config-manager --set-enabled crb || true

# Install GCC 13+ (supports C++20)
RUN dnf -y install gcc gcc-c++ make

# Verify GCC version
RUN gcc --version && g++ --version

# Upgrade pip and install packages for Python
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir \
        msgpack pyzmq jinja2 PyYAML timeout-decorator pydevd-pycharm

# -------------------------
# Verification
# -------------------------

RUN gcc --version && g++ --version && python3 --version


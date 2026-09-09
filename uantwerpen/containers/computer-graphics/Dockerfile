# DOCKER-VERSION 1.1.0

ARG VERSION=main
ARG REGISTRY=ghcr.io
FROM ${REGISTRY}/inginious/env-base:${VERSION} AS env-computer-graphics

LABEL org.inginious.grading.name="computer-graphics"
LABEL org.inginious.grading.agent_version=4
LABEL org.opencontainers.image.source=https://github.com/UAntwerpen/INGInious

# Install Development Tools
RUN dnf -y install dnf-utils

# Enable CodeReady Builder repository
RUN dnf -y install dnf-plugins-core && \
    dnf config-manager --set-enabled crb || true

# Install GCC (13+ ships natively in Rocky Linux 10)
RUN dnf -y install gcc gcc-c++ make

# Verify GCC version
RUN gcc --version && g++ --version

# -------------------------
# Install Python 3.10
# -------------------------

ARG PYTHON_VERSION=3.10.14

RUN dnf -y install \
        gcc make wget tar xz \
        openssl-devel bzip2-devel libffi-devel zlib-devel \
        readline-devel sqlite-devel ncurses-devel tk-devel xz-devel \
    && cd /tmp \
    && wget -q https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar -xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --with-ensurepip=install \
    && make -j$(nproc) \
    && make altinstall \
    && dnf clean all \
    && rm -rf /tmp/Python*

# inginious_container_api is installed by env-base into the SYSTEM python.
# Copy it (pure-Python) into the 3.10 site-packages, locating it via the
# system interpreter so we do not depend on the exact path. Runs before the
# python3 symlink swap below, so /usr/bin/python3 is still the system python.
RUN set -eux; \
    sys_sp="$(/usr/bin/python3 -c 'import os, inginious_container_api as m; print(os.path.dirname(os.path.dirname(m.__file__)))')"; \
    cp -r "$sys_sp"/inginious_container_api* /usr/local/lib/python3.10/site-packages/

# Python 3.10 runtime deps for the INGInious container scripts + course libs.
# Keep in sync with base-containers/base/pyproject.toml [project.dependencies].
RUN /usr/local/bin/python3.10 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /usr/local/bin/python3.10 -m pip install --no-cache-dir \
        msgpack pyzmq jinja2 PyYAML timeout-decorator ipython pydevd-pycharm \
        numpy scikit-image

# Make Python 3.10 the default python3 (course grading scripts call `python3`).
# The console scripts in /usr/local/bin (INGInious, feedback, ...) have a
# `#!/usr/bin/python3` shebang and will now run under 3.10.
RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python3

# -------------------------
# Verification
# -------------------------

RUN set -eux; \
    gcc --version; g++ --version; python3 --version; \
    test "$(readlink -f "$(command -v python3)")" = /usr/local/bin/python3.10; \
    python3 -c 'import inginious_container_api, msgpack, zmq, jinja2, yaml, IPython'
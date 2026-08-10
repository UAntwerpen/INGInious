# DOCKER-VERSION 1.1.0

ARG VERSION=main
ARG REGISTRY=ghcr.io
FROM ${REGISTRY}/inginious/env-base:${VERSION}

LABEL org.inginious.grading.name="computer-graphics"
LABEL org.opencontainers.image.source=https://github.com/UAntwerpen/INGInious

# Install Development Tools
RUN dnf -y install dnf-utils

# Enable CodeReady Builder repository
RUN dnf -y install dnf-plugins-core && \
    dnf config-manager --set-enabled crb || true

# Install GCC 13 toolset
RUN dnf -y install gcc-toolset-13

# Make GCC 13 default
RUN echo "source /opt/rh/gcc-toolset-13/enable" >> /etc/profile.d/gcc13.sh
ENV PATH=/opt/rh/gcc-toolset-13/root/usr/bin:$PATH

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
    && make altinstall

# Make Python 3.10 the default python3
RUN ln -sf /usr/local/bin/python3.10 /bin/python3

# Upgrade pip and install packages for Python 3.10
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir numpy scikit-image jinja2 msgpack pyzmq pyyaml

# Copy inginious_container_api from system python to Python 3.10
RUN cp -r /usr/lib/python*/site-packages/inginious_container_api* \
          /usr/local/lib/python3.10/site-packages/ || true

# Cleanup
RUN rm -rf /tmp/Python* && dnf clean all

# -------------------------
# Verification
# -------------------------

RUN gcc --version && g++ --version && python3 --version
# Use Ubuntu as base image
FROM ubuntu:22.04

# Install build dependencies and debugging tools
RUN set -x && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --fix-missing && \
    apt-get install -y \
    build-essential \
    git \
    cmake \
    libssl-dev \
    ca-certificates \
    net-tools \
    iproute2 \
    iputils-ping \
    libc6-dev \
    file \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Clone bacnet-stack repository with retry mechanism
WORKDIR /opt
RUN git config --global http.sslVerify false && \
    for i in 1 2 3 4 5; do \
        echo "Attempt $i: Cloning bacnet-stack..." && \
        git clone https://github.com/bacnet-stack/bacnet-stack.git && break || \
        sleep 5; \
    done

# Build bacnet-stack library
WORKDIR /opt/bacnet-stack
RUN cmake -B build \
    -DBACNET_STACK_BUILD_APPS=OFF \
    -DBACNET_STACK_BUILD_WITH_STATIC=OFF \
    -DBACNET_STACK_BUILD_SHARED=ON \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_VERBOSE_MAKEFILE=ON \
    && cmake --build build --verbose \
    && cmake --install build --verbose

# Print library information for debugging
RUN echo "Installed libraries:" && \
    ls -l /usr/lib/x86_64-linux-gnu/lib* && \
    echo "Installed headers:" && \
    ls -l /usr/include/bacnet*

# Copy our application files
WORKDIR /app
COPY main.c .
COPY config.ini .

# Build our application with verbose output and error checking
RUN set -x && \
    echo "Building bacnet-emulator..." && \
    gcc -v -g -o bacnet-emulator main.c \
    -I/usr/include \
    -L/usr/lib/x86_64-linux-gnu \
    -lbacnet-stack \
    -lpthread \
    && echo "Build completed successfully" && \
    ls -l bacnet-emulator && \
    file bacnet-emulator && \
    ldd bacnet-emulator && \
    chmod +x bacnet-emulator

# Create a more robust start script
RUN echo '#!/bin/bash' > start.sh && \
    echo 'set -x' >> start.sh && \
    echo 'echo "Current directory: $(pwd)"' >> start.sh && \
    echo 'echo "Directory contents:"' >> start.sh && \
    echo 'ls -la' >> start.sh && \
    echo 'echo "Executable information:"' >> start.sh && \
    echo 'file ./bacnet-emulator' >> start.sh && \
    echo 'echo "Library dependencies:"' >> start.sh && \
    echo 'ldd ./bacnet-emulator' >> start.sh && \
    echo 'echo "Starting BACnet emulator..."' >> start.sh && \
    echo './bacnet-emulator config.ini' >> start.sh && \
    chmod +x start.sh

# Expose BACnet port
EXPOSE 47808/udp

# Run the emulator
CMD ["./start.sh"]
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar paquetes base
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    iproute2 \
    iputils-ping \
    iperf3 \
    python2 \
    python2-dev \
    python-is-python2 \
    mininet \
    && apt-get clean

# Instalar pip para Python 2 manualmente
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py && \
    python2 get-pip.py && \
    rm get-pip.py

# Clonar POX y cambiar a la rama adecuada
RUN git clone http://github.com/noxrepo/pox /pox && \
    cd /pox && \
    git fetch --all && \
    git checkout -b fangtooth origin/fangtooth


# Copiar archivos-
COPY firewall.py /pox/ext/firewall.py
COPY config.json /pox/ext/config.json
COPY topology.py /pox/ext/topology.py

# Comando por defecto
CMD ["/bin/bash"]

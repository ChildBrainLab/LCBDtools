FROM ghcr.io/washu-it-ris/novnc:ubuntu22.04

RUN apt-get update && \
  apt-get install -y bison

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository universe && apt-get update
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get install -y tcsh xfonts-base gsl-bin netpbm    \
                        libjpeg62 xvfb xterm vim curl     \
                        gedit evince eog                  \
                        libglu1-mesa-dev libglw1-mesa     \
                        libxm4 build-essential            \
                        libcurl4-openssl-dev libxml2-dev  \
                        libssl-dev git python3-pip        \
                        python-is-python3 cmake           \
                        nautilus firefox xfonts-100dpi
                        

# Setup python libraries
RUN pip install scipy numpy mdp scikit-learn matplotlib

# Define environment paths
ENV HOME="/root"
ENV PATH="${PATH}:/root/abin"

# Install AFNI binaries
RUN ln -s /usr/lib/x86_64-linux-gnu/libgsl.so.23 /usr/lib/x86_64-linux-gnu/libgsl.so.19
RUN cd && curl -O https://afni.nimh.nih.gov/pub/dist/bin/misc/@update.afni.binaries && \
          tcsh @update.afni.binaries -package linux_ubuntu_16_64 -do_extras

#ENV HOME="/root"
#ENV PATH="${PATH}:${HOME}/abin"
RUN cp $HOME/abin/AFNI.afnirc $HOME/.afnirc && suma -update_env
RUN apsearch -update_all_afni_help

RUN afni_system_check.py -check_all

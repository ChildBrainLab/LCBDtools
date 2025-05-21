#Start from ris noVNC base
FROM ghcr.io/washu-it-ris/novnc:ubuntu20.04

ENV PASSWORD=password
RUN export PASSWORD

ENV STORAGE_ALLOCATION=perlmansusan
RUN export STORAGE_ALLOCATION

ENV CONDA_ENVS_DIRS=/storage1/fs1/perlmansusan/Active/moochie/resources/conda/envs/
RUN export CONDA_ENVS_DIRS

ENV CONDA_PKGS_DIRS=/storage1/fs1/perlmansusan/Active/moochie/resources/conda/pkgs/
RUN export CONDA_PKGS_DIRS

# Install FSL and freesurfer tool dependencies
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev cmake git \
    python3 python3-pip r-base libssl-dev \
    python3-matplotlib python3-numpy  \
    python3-flask python3-flask-cors  \
    python3-pil gsl-bin netpbm  \
    libjpeg62 xvfb xterm vim curl     \
    gedit evince eog libglu1-mesa-dev \
    libglw1-mesa libxm4 build-essential \
    libcurl4-openssl-dev libxml2-dev  \
    libgfortran-8-dev libgomp1        \
    firefox xfonts-100dpi             \
    r-base-dev cmake                  \
    libgdal-dev libopenblas-dev       \
    libnode-dev libudunits2-dev       \
    libgfortran4 tcsh libclang-dev    \
    libpq5 libgtk-3-dev psychopy flatpak \
    gettext language-pack-en x11-apps csh \
    bc xorg xorg-dev libncurses5 \
    && apt-get clean

# Install conda for the FreeSurfer installation
#ENV PATH="/root/miniconda3/bin:${PATH}"
#ARG PATH="/root/miniconda3/bin:${PATH}"
#RUN apt-get update

#RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir /root/conda \
#    && bash Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm -f Miniconda3-latest-Linux-x86_64.sh 
#RUN conda --version

# Install FSL
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py \
    && su -c "python3 fslinstaller.py -d /usr/local/fsl/" \
    && rm fslinstaller.py

ENV FSLDIR=/usr/local/fsl
RUN export FSLDIR

ENV FSLOUTPUTTYPE=NIFTI_GZ
RUN export FSLOUTPUTTYPE

RUN apt-get --fix-broken -y install

# Install freesurferß
RUN wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.3.2/freesurfer_ubuntu20-7.3.2_amd64.deb \
    && dpkg -i freesurfer_ubuntu20-7.3.2_amd64.deb \
    && rm freesurfer_ubuntu20-7.3.2_amd64.deb

ENV FREESURFER_HOME=/usr/local/freesurfer/7.3.2
RUN export FREESURFER_HOME

RUN apt-get --fix-broken -y install

# Install typical python dependencies
RUN pip install pandas matplotlib scipy numpy \
 torch tensorflow tqdm boto3 nltk
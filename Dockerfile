FROM tensorflow/tensorflow:1.12.0-gpu-py3
# 위의 베이스 이미지는 원하는 TensorFlow 버전으로 변경

RUN apt-get update

# ==================================================================
# opencv 설치
# ------------------------------------------------------------------
RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
    PIP_INSTALL="pip --no-cache-dir install --upgrade" && \
    GIT_CLONE="git clone --depth 10" && \
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        libatlas-base-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        build-essential \
        git \
        ca-certificates \
        cmake \
        wget \
        git \
        vim \
        pkg-config \
        rsync \
        unzip

# ==================================================================
# install ffmpeg (영상 처리를 위한 ffmpeg 설치)
# ==================================================================
RUN add-apt-repository ppa:jonathonf/ffmpeg-4 && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg

# ==================================================================
# 공통 python libraries
# &&로 연결된 python library들은 한 명령어로 인식되기에, 추가/제거 시 캐싱이 안됨
# ==================================================================
RUN PIP_INSTALL="pip --no-cache-dir install --upgrade" && \
    $PIP_INSTALL \
        setuptools \
        && \
    $PIP_INSTALL \
        scipy \
        pandas \
        scikit-learn \
        matplotlib \
        Cython \
        h5py \
        ipykernel \
        path.py \
        pyyaml \
        six \
        Pillow \
        scikit-image \
        tqdm \
        imageio

# ==================================================================
# Project dependent libraries
# 특정 프로젝트에서만 사용하는 라이브러리는 여기에 추가하는 것이 좋다.
# Dockerfile은 이미지를 빌드할 때, RUN, ARG, COPY 등의 도커 명령어 단위로 캐싱됨
# 위의 공통 라이브러리 설치 단계에 추가하면, 명령어 전체를 다시 수행하므로 빌드가 느려짐
# 여기다 추가하면 이미 빌드된 이미지가 있을 경우에 캐싱된 이미지에서 부터 빌드하므로 빠름
# 현재 텐서보드의 1.13이 TF 1.13 이상에서만 동작해 버전 지정해 놓은 상태
# ==================================================================
RUN PIP_INSTALL="pip --no-cache-dir install --upgrade" && \
    $PIP_INSTALL \
        tensorboard==1.12.2 \
        tensorflow-hub \
        moviepy \
        pytube \ 
        youtube-dl
# 스크립트를 실행하며 생성되는 파일의 권한과 소유주 설정을 위해, 현재 로그인된 사용자의 uid와 gid를 넘겨줌
# 이런 설정을 하지 않으면, root의 파일로 생성되어 보고 옮기고 지우는데 불필요한 sudo 권한이 필요해짐

ARG uid
ARG gid

# 도커 컨테이너 안에서 해당 uid와 gid를 가진 script_runner라는 사용자와 그룹을 만든다.
# 도커 컨테이너 안에서 동작하는 것이므로 실제 사용자와는 관계가 없음
RUN groupadd -g $gid script_runner && \
    useradd -u $uid -g $gid script_runner

# 컨테이너 안에서 명령을 수행하는 사용자를 script_runner로 변경
USER script_runner

# /shells 라는 디렉토리 생성 후 그 디렉토리로 이동한다
WORKDIR /shells

# 현재 디렉토리에 있는 모든 sh 파일(e.g. start_docker.sh, start_experiment.sh)을 /shells 아래에 복사한다
COPY *.sh /shells/

USER root

# 모든 .sh 파일에 실행 가능 권한을 주고 /shells의 소유주 및 그룹을 변경한다
RUN chmod +x *.sh && \
    chown $uid:$gid -R /shells

USER script_runner

# 엔트리포인트(도커 컨테이너 실행 시 수행되는 명령어, 기본적으로
# `docker run #SOME_CONTAINER #CMD` 할 때, ENTRYPOINT + CMD로 실행된다고 생각하면 됨)
ENTRYPOINT [ "bash", "-c"]

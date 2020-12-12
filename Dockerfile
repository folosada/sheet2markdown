FROM public.ecr.aws/lambda/python:3.8

# Install OpenCV

# First: get all the dependencies:
#
RUN yum -y update
RUN yum -y install git libgtk2.0-dev pkg-config libavcodec-dev \
libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev \
libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev unzip
RUN yum -y remove cmake
RUN yum -y install wget

# Just get a simple editor for convienience (you could just cancel this line)
RUN yum -y install vim

RUN cd \
    && wget https://cmake.org/files/v3.6/cmake-3.6.2.tar.gz \
    && tar -zxvf cmake-3.6.2.tar.gz
    && cd cmake-3.6.2
    && ./bootstrap --prefix=/usr/local
    && make
    && make install
    && cmake --version

# Second: get and build OpenCV 3.2
#
RUN cd \
    && wget https://github.com/opencv/opencv/archive/4.5.0.zip \
    && unzip 4.5.0.zip \
    && cd opencv-4.5.0 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j8 \
    && make install \
    && cd \
    && rm 4.5.0.zip


# Third: install and build opencv_contrib
#
RUN cd \
    && wget https://github.com/opencv/opencv_contrib/archive/4.5.0.zip \
    && unzip 4.5.0.zip \
    && cd opencv-4.5.0/build \
    && cmake -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.5.0/modules/ .. \
    && make -j8 \
    && make install \
    && cd ../.. \
    && rm 4.5.0.zip

COPY app.py requirements.txt ./

RUN python3.8 -m pip install -r requirements.txt -t .

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]

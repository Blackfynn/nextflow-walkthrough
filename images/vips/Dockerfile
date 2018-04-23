FROM python:3.6-jessie

ARG VIPS_VERSION=8.6.3
ARG VIPS_URL=https://github.com/jcupitt/libvips/releases/download

RUN apt-get update && apt-get install -y libgsf-1-dev openjpeg-tools

RUN wget -O- ${VIPS_URL}/v${VIPS_VERSION}/vips-${VIPS_VERSION}.tar.gz | tar xzC /tmp
RUN cd /tmp/vips-${VIPS_VERSION} \
        && ./configure --prefix=/usr --disable-static --disable-debug \
        && make V=0 \
        && make install

RUN pip install awscli

FROM amazon/aws-lambda-python:3.9

ENV TZ=Europe/Bucharest

# Install Chrome dependencies
RUN yum install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm unzip \
    nano tzdata

# Set to local timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# COPY app/* ./
COPY app ./

# Run Chrome Installer
RUN chmod +x chrome-installer.sh
RUN ./chrome-installer.sh
RUN rm chrome-installer.sh

RUN pip install -r requirements.txt --no-deps --no-cache-dir

ENTRYPOINT ["/bin/bash"]
# CMD ["main.lambda_handler"]

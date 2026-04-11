# OpenAuto

I have not yet managed to build this.

# Building for armhf On Intel Laptop


This uses qemu-arm-static and chroot

download from https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/


```
wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip
unzip 2021-05-07-raspios-buster-armhf-lite.zip

sudo apt install qemu-user-static


truncate -s +10G 2021-05-07-raspios-buster-armhf-lite.img

## Attach the loop device with partitions
sudo losetup --find --partscan --show 2021-05-07-raspios-buster-armhf-lite.img

sudo parted /dev/loop27

## print 
## resizepart 2 100%
## quit


sudo e2fsck -f /dev/loop27p2
sudo resize2fs /dev/loop27p2

sudo mount /dev/loop27p2 ./rootfs/


df -h rootfs

sudo cp /usr/bin/qemu-arm-static ./rootfs/usr/bin/


sudo mount -t proc /proc rootfs/proc
sudo mount --rbind /sys rootfs/sys
sudo mount --rbind /dev rootfs/dev
sudo mount --bind /etc/resolv.conf rootfs/etc/resolv.conf


sudo chroot rootfs /bin/bash
```







```
## Attach the loop device with partitions
sudo losetup --find --partscan --show 2021-05-07-raspios-buster-armhf-lite.img
sudo mount /dev/loop27p2 ./rootfs/

sudo mount -t proc /proc rootfs/proc
sudo mount --rbind /sys rootfs/sys
sudo mount --rbind /dev rootfs/dev
sudo mount --bind /etc/resolv.conf rootfs/etc/resolv.conf

sudo chroot rootfs /bin/bash
```


```
root@LXP-J-ROGERS2:/# uname -m
armv7l
```

Try and update and fails as expected

```
root@LXP-J-ROGERS2:/# apt update
Ign:1 http://raspbian.raspberrypi.org/raspbian buster InRelease
Get:2 http://archive.raspberrypi.org/debian buster InRelease [54.2 kB]
Err:3 http://raspbian.raspberrypi.org/raspbian buster Release                                
  404  Not Found [IP: 93.93.128.193 80]
Get:4 http://archive.raspberrypi.org/debian buster/main armhf Packages [400 kB]              
Reading package lists... Done     
E: The repository 'http://raspbian.raspberrypi.org/raspbian buster Release' no longer has a Release file.
N: Updating from such a repository can't be done securely, and is therefore disabled by default.
N: See apt-secure(8) manpage for repository creation and user configuration details.
N: Repository 'http://archive.raspberrypi.org/debian buster InRelease' changed its 'Suite' value from 'testing' to ''

```


```
nano /etc/apt/sources.list
```
change to
```
deb http://legacy.raspbian.org/raspbian buster main contrib non-free rpi 
```

## Updates

```
apt install -y \
  build-essential \
  cmake \
  git \
  libboost-all-dev \
  libusb-1.0-0-dev \
  libprotobuf-dev \
  protobuf-compiler \
  libasound2-dev \
  libgl1-mesa-dev \
  libglew-dev \
  libegl1-mesa-dev \
  mesa-common-dev
```
  
  
## protobuf

```
cd /usr/src
curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v21.12/protobuf-all-21.12.tar.gz
tar xf protobuf-all-21.12.tar.gz
cd protobuf-21.12

#./configure \
#  --prefix=/usr/local \
#  --disable-shared \
#  --enable-static

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -Dprotobuf_BUILD_SHARED_LIBS=ON \
  -Dprotobuf_BUILD_TESTS=O





make -j4
make install
ldconfig

```  
  
  
  
  
## abseil
  
  
  ```
  cd /usr/src
git clone https://github.com/abseil/abseil-cpp.git
cd abseil-cpp
git checkout 20210324.2
```

```
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
export CMAKE_C_COMPILER=/usr/bin/gcc
export CMAKE_CXX_COMPILER=/usr/bin/g++

mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DABSL_ENABLE_INSTALL=ON \
  -DCMAKE_CXX_COMPILER_WORKS=ON \
  -DCMAKE_C_COMPILER_WORKS=ON \
  -DABSL_USE_SYSTEM_INCLUDES=ON
  
  
make install
```

  
  
  
## AA  
  
```
git clone https://github.com/opencardev/aasdk.git
cd https://github.com/opencardev/aasdk.git
./build.sh



cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_PREFIX_PATH="/usr/local;/usr" \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -Dabsl_DIR=/usr/local/lib/cmake/absl \
  -DProtobuf_PROTOC_EXECUTABLE=/usr/local/bin/protoc \
  -DProtobuf_INCLUDE_DIR=/usr/local/include \
  -DProtobuf_LIBRARY=/usr/local/lib/libprotobuf.a \
  -DBoost_SYSTEM_LIBRARY=/usr/lib/arm-linux-gnueabihf/libboost_system.so \
  -DBoost_LOG_LIBRARY=/usr/lib/arm-linux-gnueabihf/libboost_log.so \
  -DBoost_LOG_SETUP_LIBRARY=/usr/lib/arm-linux-gnueabihf/libboost_log_setup.so \
  -DLIBUSB_1_INCLUDE_DIR=/usr/include/libusb-1.0 \
  -DLIBUSB_1_LIBRARY=/usr/lib/arm-linux-gnueabihf/libusb-1.0.so \
-DOPENSSL_ROOT_DIR=/usr \
-DOPENSSL_INCLUDE_DIR=/usr/include \
-DOPENSSL_SSL_LIBRARY=/usr/lib/arm-linux-gnueabihf/libssl.so \
-DOPENSSL_CRYPTO_LIBRARY=/usr/lib/arm-linux-gnueabihf/libcrypto.so
```
  
  
  
  
  
  
  
trying https://github.com/opencardev/openauto


```
git clone https://github.com/abseil/abseil-cpp.git
cd abseil-cpp
git checkout 20210324.2
mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON
make -j$(nproc)
make install

```


```
root@LXP-J-ROGERS2:/home/pi# git clone https://github.com/opencardev/openauto.git
Cloning into 'openauto'...
remote: Enumerating objects: 5323, done.
remote: Counting objects: 100% (1858/1858), done.
remote: Compressing objects: 100% (263/263), done.
remote: Total 5323 (delta 1701), reused 1595 (delta 1595), pack-reused 3465 (from 1)
Receiving objects: 100% (5323/5323), 4.12 MiB | 14.71 MiB/s, done.
Resolving deltas: 100% (3043/3043), done.


```  
  
  
  
  
  
## Shutdown
  

```
exit
sudo umount ./rootfs
sudo losetup -d /dev/loop28
```
  
  

# OpenAuto with rootfs

I have not yet managed to build this - The Pain i real !!!

# Building for armhf on an Intel Laptop

This uses qemu-arm-static and chroot

Download from https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/

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

Try apt update; it fails as expected.

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

Change it to

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
    libasound2-dev \
    libgl1-mesa-dev \
    libglew-dev \
    libegl1-mesa-dev \
    mesa-common-dev \
    zlib1g-dev \
    pkg-config \
    libc6-dev \
    libssl-dev

```

## Step 2 protobuf

Build the specific protobuf version that is apparently required.

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
  -Dprotobuf_BUILD_SHARED_LIBS=OFF \
  -Dprotobuf_BUILD_TESTS=OFF

make -j4
make install
ldconfig
```

## Step 3 abseil

```
cd /usr/src
git clone https://github.com/abseil/abseil-cpp.git
cd abseil-cpp
git checkout 20210324.2
mkdir build && cd build

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DABSL_ENABLE_INSTALL=ON \
  -DABSL_PROPAGATE_CXX_STD=ON \
  -DCMAKE_CXX_STANDARD=14

## It may fail once; run cmake again.

make install
ldconfig

```

## Step 4 AASDK

Note: my `main` branch from https://github.com/xjasonrogersx/aasdk.git is based on main at https://github.com/opencardev. It is old, and a `newdev` branch exists.

In this armhf buster chroot, this only configured after two changes:

1. Explicitly set all Boost component library paths in the CMake command.
2. Patch `/usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake` because CMake 3.16 can call `list(REMOVE_ITEM ...)` with an empty list in this environment.

Root cause note:

- This was primarily a CMake/chroot environment issue (CMake 3.16 module behavior), not an AASDK logic issue.
- AASDK `CMakeLists.txt` changes could reduce Boost friction, but they do not fully solve the compiler-id/module error in this environment.
- A cleaner long-term fix is using a newer CMake version in the chroot if possible.

```
git clone https://github.com/xjasonrogersx/aasdk.git
cd aasdk
mkdir build; cd build

# Backup and patch the CMake 3.16 module in the chroot.
cp /usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake \
  /usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake.bak

perl -0777 -i -pe 's/list\(REMOVE_ITEM lang_files \$\{nonlang_files\}\)/if(nonlang_files)\n  list(REMOVE_ITEM lang_files \$\{nonlang_files\})\nendif()/g' \
  /usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake

rm -rf CMakeCache.txt CMakeFiles

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DCMAKE_PREFIX_PATH="/usr/local;/usr" \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DProtobuf_PROTOC_EXECUTABLE=/usr/local/bin/protoc \
  -DProtobuf_INCLUDE_DIR=/usr/local/include \
  -DProtobuf_LIBRARY=/usr/local/lib/libprotobuf.a \
  -DLIBUSB_1_INCLUDE_DIR=/usr/include/libusb-1.0 \
  -DLIBUSB_1_LIBRARY=/usr/lib/arm-linux-gnueabihf/libusb-1.0.so \
  -DOPENSSL_ROOT_DIR=/usr \
  -DOPENSSL_INCLUDE_DIR=/usr/include \
  -DOPENSSL_SSL_LIBRARY=/usr/lib/arm-linux-gnueabihf/libssl.so \
  -DOPENSSL_CRYPTO_LIBRARY=/usr/lib/arm-linux-gnueabihf/libcrypto.so \
  -DBoost_NO_BOOST_CMAKE=ON \
  -DBOOST_ROOT=/usr \
  -DBOOST_INCLUDEDIR=/usr/include \
  -DBOOST_LIBRARYDIR=/usr/lib/arm-linux-gnueabihf \
  -DBoost_SYSTEM_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_system.so \
  -DBoost_LOG_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_log.so \
  -DBoost_LOG_SETUP_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_log_setup.so \
  -DBoost_DATE_TIME_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_date_time.so \
  -DBoost_FILESYSTEM_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_filesystem.so \
  -DBoost_THREAD_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_thread.so \
  -DBoost_REGEX_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_regex.so \
  -DBoost_CHRONO_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_chrono.so \
  -DBoost_ATOMIC_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_atomic.so \
  -DBoost_UNIT_TEST_FRAMEWORK_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_unit_test_framework.so

make -j4
make install
ldconfig

# Optional: restore stock module after build
# cp /usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake.bak \
#   /usr/share/cmake-3.16/Modules/CMakeCompilerIdDetection.cmake
```

## OpenAuto

I need to find a version that builds with my branch of AASDK.

trying https://github.com/opencardev/openauto

```

apt install -y \
  qtbase5-dev \
  qtchooser \
  qt5-qmake \
  qtbase5-dev-tools \
  qtmultimedia5-dev \
  qtconnectivity5-dev

apt install -y libtag1-dev
apt install -y librtaudio-dev


git clone https://github.com/opencardev/openauto.git


cd openauto
mkdir build;cd build


  cd ~/openauto/build
rm -rf CMakeCache.txt CMakeFiles
cd build
rm -rf CMakeCache.txt CMakeFiles

cmake .. \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_C_COMPILER=/usr/bin/gcc \
	-DCMAKE_CXX_COMPILER=/usr/bin/g++ \
	-DCMAKE_PREFIX_PATH="/usr/lib/arm-linux-gnueabihf/cmake;/usr/local;/usr" \
	-DQt5_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5 \
	-DQt5Core_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Core \
	-DQt5Gui_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Gui \
	-DQt5DBus_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5DBus \
	-DQt5Network_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Network \
	-DQt5Multimedia_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Multimedia \
	-DQt5MultimediaWidgets_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5MultimediaWidgets \
	-DQt5Bluetooth_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Bluetooth \
	-DOPENSSL_ROOT_DIR=/usr \
	-DProtobuf_PROTOC_EXECUTABLE=/usr/local/bin/protoc \
	-DProtobuf_INCLUDE_DIR=/usr/local/include \
	-DProtobuf_LIBRARY=/usr/local/lib/libprotobuf.a \
	-DAASDK_INCLUDE_DIR=/root/aasdk/include/aasdk \
	-DAASDK_INCLUDE_DIRS=/root/aasdk/include/aasdk \
	-DAASDK_LIB_DIR=/root/aasdk/lib/libaasdk.a \
	-DAASDK_LIB_DIRS=/root/aasdk/lib/libaasdk.a \
	-DAAP_PROTOBUF_INCLUDE_DIR=/root/aasdk/include \
	-DAAP_PROTOBUF_INCLUDE_DIRS=/root/aasdk/include \
	-DAAP_PROTOBUF_LIB_DIR=/root/aasdk/lib/libaap_protobuf.a \
	-DAAP_PROTOBUF_LIB_DIRS=/root/aasdk/lib/libaap_protobuf.a \
	-DLIBUSB_1_INCLUDE_DIR=/usr/include/libusb-1.0 \
	-DLIBUSB_1_LIBRARY=/usr/lib/arm-linux-gnueabihf/libusb-1.0.so \
	-DBoost_NO_BOOST_CMAKE=ON \
	-DBOOST_ROOT=/usr \
	-DBOOST_INCLUDEDIR=/usr/include \
	-DBOOST_LIBRARYDIR=/usr/lib/arm-linux-gnueabihf \
	-DBoost_SYSTEM_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_system.so \
	-DBoost_LOG_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_log.so \
	-DBoost_LOG_SETUP_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_log_setup.so \
	-DBoost_DATE_TIME_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_date_time.so \
	-DBoost_FILESYSTEM_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_filesystem.so \
	-DBoost_THREAD_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_thread.so \
	-DBoost_REGEX_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_regex.so \
	-DBoost_CHRONO_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_chrono.so \
	-DBoost_ATOMIC_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_atomic.so \
	-DBoost_UNIT_TEST_FRAMEWORK_LIBRARY_RELEASE=/usr/lib/arm-linux-gnueabihf/libboost_unit_test_framework.so \
	-DOPENSSL_ROOT_DIR=/usr \
	-DOPENSSL_INCLUDE_DIR=/usr/include \
	-DOPENSSL_SSL_LIBRARY=/usr/lib/arm-linux-gnueabihf/libssl.so \
	-DOPENSSL_CRYPTO_LIBRARY=/usr/lib/arm-linux-gnueabihf/libcrypto.so  \
	-DRTAUDIO_INCLUDE_DIRS=/usr/include/rtaudio \
	-DRTAUDIO_LIBRARIES=/usr/lib/arm-linux-gnueabihf/librtaudio.so \
	-DQt5Widgets_DIR=/usr/lib/arm-linux-gnueabihf/cmake/Qt5Widgets \
	-DBLKID_INCLUDE_DIRS=/usr/include/blkid \
	-DBLKID_LIBRARIES=/usr/lib/arm-linux-gnueabihf/libblkid.so \
	-DGPS_INCLUDE_DIRS=/usr/include \
	-DGPS_LIBRARIES=/usr/lib/arm-linux-gnueabihf/libgps.so \
	-DTAGLIB_INCLUDE_DIRS=/usr/include/taglib \
	-DTAGLIB_LIBRARIES=/usr/lib/arm-linux-gnueabihf/libtag.so \
	-DCMAKE_C_COMPILER_FORCED=ON \
	-DCMAKE_CXX_COMPILER_FORCED=ON \
	-DCMAKE_C_COMPILER_ID=GNU \
	-DCMAKE_CXX_COMPILER_ID=GNU \
	-DCMAKE_C_COMPILER_VERSION=8.3.0 \
	-DCMAKE_CXX_COMPILER_VERSION=8.3.0 \
	-DCMAKE_C_STANDARD_COMPUTED_DEFAULT=11 \
	-DCMAKE_C_EXTENSIONS_COMPUTED_DEFAULT=ON \
	-DCMAKE_CXX_STANDARD_COMPUTED_DEFAULT=14 \
	-DCMAKE_CXX_EXTENSIONS_COMPUTED_DEFAULT=ON \
	-DCMAKE_CXX_KNOWN_FEATURES="cxx_std_98;cxx_std_11;cxx_std_14;cxx_std_17;cxx_alias_templates;cxx_alignas;cxx_alignof;cxx_attributes;cxx_auto_type;cxx_constexpr;cxx_decltype;cxx_defaulted_functions;cxx_defaulted_move_initializers;cxx_delegating_constructors;cxx_deleted_functions;cxx_enum_forward_declarations;cxx_explicit_conversions;cxx_final;cxx_func_identifier;cxx_generalized_initializers;cxx_inheriting_constructors;cxx_lambdas;cxx_local_type_template_args;cxx_long_long_type;cxx_noexcept;cxx_nonstatic_member_init;cxx_nullptr;cxx_override;cxx_range_for;cxx_raw_string_literals;cxx_reference_qualified_functions;cxx_right_angle_brackets;cxx_rvalue_references;cxx_sizeof_member;cxx_static_assert;cxx_strong_enums;cxx_thread_local;cxx_trailing_return_types;cxx_unicode_literals;cxx_uniform_initialization;cxx_unrestricted_unions;cxx_user_literals;cxx_variadic_macros;cxx_variadic_templates" \
	-DCMAKE_CXX_COMPILE_FEATURES="cxx_std_98;cxx_std_11;cxx_std_14;cxx_std_17;cxx_alias_templates;cxx_alignas;cxx_alignof;cxx_attributes;cxx_auto_type;cxx_constexpr;cxx_decltype;cxx_defaulted_functions;cxx_defaulted_move_initializers;cxx_delegating_constructors;cxx_deleted_functions;cxx_enum_forward_declarations;cxx_explicit_conversions;cxx_final;cxx_func_identifier;cxx_generalized_initializers;cxx_inheriting_constructors;cxx_lambdas;cxx_local_type_template_args;cxx_long_long_type;cxx_noexcept;cxx_nonstatic_member_init;cxx_nullptr;cxx_override;cxx_range_for;cxx_raw_string_literals;cxx_reference_qualified_functions;cxx_right_angle_brackets;cxx_rvalue_references;cxx_sizeof_member;cxx_static_assert;cxx_strong_enums;cxx_thread_local;cxx_trailing_return_types;cxx_unicode_literals;cxx_uniform_initialization;cxx_unrestricted_unions;cxx_user_literals;cxx_variadic_macros;cxx_variadic_templates" \
	-DCMAKE_CXX_STANDARD=17

```

## Shutdown

```
exit
sudo umount ./rootfs
sudo losetup -d /dev/loop28
```

#

Setting up the image

```
truncate -s +10G 2025-11-24-raspios-bookworm-armhf-lite.img

## Attach the loop device with partitions
sudo losetup --find --partscan --show 2025-11-24-raspios-bookworm-armhf-lite.img

sudo sudo parted /dev/loop35 resizepart 2 100%

## My laptop is Ubuntu22 and the following does not work
## sudo e2fsck -f /dev/loop35p2
## sudo resize2fs /dev/loop25p2

## Gemi recomended the following which did work
sudo docker run --rm --privileged -v /dev:/dev ubuntu:24.04 \
bash -c "apt update && apt install -y e2fsprogs && e2fsck -f -y /dev/loop35p2 && resize2fs /dev/loop35p2"

```

```
export LOOPID=`sudo losetup --find --partscan --show 2025-11-24-raspios-bookworm-armhf-lite.img`
echo "Loop device: $LOOPID"

export PARTITION1=${LOOPID}p1
export PARTITION2=${LOOPID}p2

echo "Mounting partitions..."
sudo mount $PARTITION2 ./rootfs/

sudo mount -t proc /proc rootfs/proc
sudo mount --rbind /sys rootfs/sys
sudo mount --rbind /dev rootfs/dev
sudo mount --bind /etc/resolv.conf rootfs/etc/resolv.conf

sudo chroot rootfs /bin/bash
```

```
apt update
apt install -y git
apt install -y cmake libprotobuf-dev protobuf-compiler libboost-all-dev libabsl-dev
apt install -y libprotobuf-dev protobuf-compiler libusb-1.0-0-dev libssl-dev

git clone https://github.com/opencardev/openauto.git

cd openauto

./build.sh release --package --with-aasdk

```

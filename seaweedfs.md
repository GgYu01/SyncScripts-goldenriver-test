mkdir seaweed
cd seaweed
wget https://github.com/seaweedfs/seaweedfs/releases/download/3.73/linux_amd64_full.tar.gz
tar -xf linux_amd64_full.tar.gz
mkdir -p volume
mkdir -p master
mkdir -p idx
mkdir -p filer
mkdir -p $HOME/.seaweedfs/
touch master.conf
touch volume.conf
touch filer.conf

/mnt/sso/seaweed/weed master -options=/mnt/sso/seaweed/master.conf
/mnt/sso/seaweed/weed volume -options=/mnt/sso/seaweed/volume.conf
/mnt/sso/seaweed/weed filer -options=/mnt/sso/seaweed/filer.conf
/mnt/sso/seaweed/weed mount -options=/mnt/sso/seaweed/mount.conf

sudo weed mount -filer=<filer_server>:9332 -dir=/mnt/seaweedfs

sudo chown 1000:1000 /mnt
mkdir -p /mnt/seaweedfs
./weed mount -filer=112.30.116.152:9332 -dir=/mnt/seaweedfs
sudo sed -i 's/^#user_allow_other/user_allow_other/' /etc/fuse.conf
./weed mount -options=mount.conf
-o sync

sudo chown 1000:1000 /etc/systemd/system/
touch /etc/systemd/system/seaweedfs-volume.service
touch /etc/systemd/system/seaweedfs-master.service
touch /etc/systemd/system/seaweedfs-filer.service
touch /etc/systemd/system/seaweedfs-mount.service

sudo systemctl daemon-reload
sudo systemctl start seaweedfs-master
sudo systemctl start seaweedfs-volume
sudo systemctl start seaweedfs-filer
sudo systemctl enable seaweedfs-master
sudo systemctl enable seaweedfs-volume
sudo systemctl enable seaweedfs-filer

sudo systemctl restart seaweedfs-master
sudo systemctl restart seaweedfs-volume

sudo systemctl start seaweedfs-mount
sudo systemctl enable seaweedfs-mount

curl http://112.30.116.152:9332/cluster/status
curl http://112.30.116.152:9333/cluster/status
curl http://112.30.116.152:9333/dir/status
curl http://112.30.116.152:9332/stats/counter
curl http://112.30.116.152:9332/volumes
curl http://112.30.116.152:9332/dir/status

nc -vz 100.64.0.5 5005
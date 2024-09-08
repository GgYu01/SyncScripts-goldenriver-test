sudo apt install apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release -y 

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
 "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
 bookworm stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl status docker
sudo systemctl start docker
sudo systemctl enable docker
sudo docker version
sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod 777 /usr/local/bin/docker-compose
docker-compose version
pip install docker-compose
docker-compose --version

sudo usermod -aG docker $USER
sudo chmod 666 /var/run/docker.sock
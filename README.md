Steps for instance setup:
```shell
sudo apt update
sudo apt install -y python3-pip mongodb-org transmission-cli
pip install -r requirements.txt

# mongo set up
sudo mkdir -p /data/db
sudo chown -R `id -un` /data/db
# might need to get updated version? https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
# if error: https://askubuntu.com/questions/842592/apt-get-fails-on-16-04-or-18-04-installing-mongodb

use transmission-cli to download wikipedia dump

我需要建立一个最新的ubutnu docker请你设立1个新用户gitea加入sudo组plugdev，gitea的密码是666666。使用SSH登录docker，把/home/gaoyx/.ssh这个路径及其所有子路径和文件映射到gitea的home目录下，把22端口映射到10126.通过docker composev2管理这个docker，请把本路径下的user_home目录并映射到docker中的gitea用户的home目录，如果我想让所有用户在使用sudo的时候都不用输入密码验证。
我希望我使用docker时终端有正常的颜色输出。可以和本机终端颜色配置一样丰富而不是白色。

sudo apt-get update
sudo apt-get install -y build-essential libreadline-dev zlib1g-dev flex bison
sudo apt-get update
sudo apt-get install -y libicu-dev pkg-config
sudo apt-get update
sudo apt-get install -y build-essential libreadline-dev zlib1g-dev flex bison libxml2-dev libxslt1-dev libssl-dev libpam0g-dev libldap2-dev python3-dev tcl-dev gettext libzstd-dev liblz4-dev
sudo apt-get update
sudo apt-get install -y build-essential libreadline-dev zlib1g-dev flex bison libicu-dev pkg-config libxml2-dev libxslt1-dev libssl-dev libpam0g-dev libldap2-dev python3-dev tcl-dev gettext libzstd-dev liblz4-dev gawk libkrb5-dev libavahi-compat-libdnssd-dev libselinux1-dev libsystemd-dev libxml2-utils xsltproc fop dbtoepub uuid-dev libevent-dev




mkdir -p /home/gitea/postgresql/data
/home/gitea/postgresql/bin/initdb -D /home/gitea/postgresql/data
/home/gitea/postgresql/bin/pg_ctl -D /home/gitea/postgresql/data -l logfile start
/home/gitea/postgresql/bin/createdb test
/home/gitea/postgresql/bin/psql test

wget -O gitea https://dl.gitea.com/gitea/1.22.1/gitea-1.22.1-linux-amd64

export GITEA_WORK_DIR=/home/nebula/gitea
nohup /home/nebula/bin/gitea web -c /home/nebula/app/app.ini &

/home/nebula/bin/gitea admin user list --config /home/nebula/app/app.ini

/home/nebula/bin/gitea admin user create --username gaoyx --password gaoyx --email gaoyx@goldenrivertek.com --admin --config /home/nebula/app/app.ini

/home/nebula/bin/gitea admin user change-password --username admin --password admin --config /home/nebula/app/app.ini

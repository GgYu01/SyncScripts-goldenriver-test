wget https://ftp.postgresql.org/pub/source/v16.4/postgresql-16.4.tar.gz
tar -zxf postgresql-16.4.tar.gz 
mkdir build_temp
cd build_temp/
sudo apt-get install gcc make zlib1g-dev libreadline-dev libicu-dev pkg-config -y

$HOME/postgresql-16.4/configure --cache-file=$HOME/postgresql-16.4/build_temp/CACHEFILE --prefix=$HOME/pgsql/ --with-pgport=5432

make world -j2
make check -j2 
make install-world -j2

mkdir $HOME/pgsql/data
# .bashrc or .profile
export PGDATA=$HOME/pgsql/data
export LD_LIBRARY_PATH=$HOME/pgsql/lib:$LD_LIBRARY_PATH
export MANPATH=/usr/local/pgsql/share/man:$MANPATH
export PATH=$HOME/pgsql/bin:$PATH

initdb -D $PGDATA

# $PGDATA/postgresql.conf 
listen_addresses = '*'  # 如果需要远程访问
port = 5432

# $PGDATA/pg_hba.conf
# 允许本地连接
local   all   all                   trust
# 允许本地网络连接
host    all   all   127.0.0.1/32    trust
host    all   all   ::1/128         trust
host    all             all             0.0.0.0/0               trust

pg_ctl -D $PGDATA -l logfile start
psql -d postgres
SELECT datname FROM pg_database;

psql -U postgres -c "CREATE DATABASE k3s;"
psql -U postgres -c "CREATE DATABASE gitea;"

curl -sfL https://get.k3s.io | sh -s - server \
  --datastore-endpoint='postgres://postgres@<postgres-container-ip>:5432/k3s'
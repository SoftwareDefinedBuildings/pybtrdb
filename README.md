# PyBTrDB

This is just a very basic API for now. We hope to flesh it out soon. The basic
dependencies are covered by pip, so you can use:

apt-get install python-pip
pip install btrdb

# UUIDResolver

If you want to use the UUID resolver, you will additionally need to install sqlalchemy
with the correct drivers for your database. For MySQL this means you need
```
apt-get install libmysqlclient-dev
apt-get install python-dev
apt-get install python-mysqldb
apt-get install python-sqlalchemy

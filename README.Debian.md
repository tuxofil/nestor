# Debian notes

## Install as system service

```
apt-get update
apt-get install git python3-pip
adduser --system --disabled-password --home /var/log/nestor nestor
su -l -s /bin/sh -c 'pip3 install slackclient' nestor

git clone https://github.com/tuxofil/nestor
cd nestor
cp nestor.conf /etc/nestor.conf
chmod 0400 /etc/nestor.conf
chown nestor: /etc/nestor.conf
cp nestor.py /usr/local/bin/nestor
cp nestor.service /lib/systemd/system/
systemctl daemon-reload
```

Then set valid OAuth token to `/etc/nestor.conf`.

And finally:

```
systemctl enable nestor
systemctl start nestor
```

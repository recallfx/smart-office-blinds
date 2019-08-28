Hackdays Project: Smart office blinds
=====================================

Requirements
------------

This runs on Raspberry Pi 3 with 4 servo motors attached.


Setup
-----

Install `pigpiod` and optionally `forward`.

```
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
sudo pip install -r requirements.txt
```

Setup required services:

Copy `*.service` files from local `etc` to  `/etc/systemd/system/`

```
sudo systemctl enable forward
sudo systemctl enable pigpiod
sudo systemctl enable smart-blinds
```

Server
------

```
sudo ./bin/server
```

Console
-------

```
python3 -m smart_blinds open -u john.doe
```

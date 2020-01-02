# 🧠🏢 Blinds v2.0

![](https://github.com/recallfx/smart-office-blinds/blob/master/assets/header.jpg?raw=true)

Smart office blinds controlled mechanically pressing the button on the remote using servo motors (one per two buttons - up/down) 

## Prerequisites

Tested on raspbian buster.

## Setup

```bash
yarn
cd functions
npm install
cd ..
yarn firebase login
```

Go to firebase Settings -> Service accounts and generate new private key. Save received json file as `server/smart_blinds/service_account_key.json`.

Also setup `server/smart_blinds/config.py`.

### Serve locally

```bash
yarn firebase serve
```

### Deploy

```bash
yarn firebase deploy
```

## Raspberry Pi server

### Setup

```bash
sudo apt install build-essential libssl-dev libffi-dev python3-dev
sudo pip3 install -r server/requirements.txt
sudo cp server/etc/systemd/system/* /etc/systemd/system/
```

### Systemd

```bash
sudo systemctl enable pigpiod
sudo systemctl enable smart-blinds
sudo systemctl restart smart-blinds
```

View logs:

```bash
journalctl -f smart-blinds
```

## Server

```
cd server
sudo ./bin/server
```

### Console

```
cd server
python3 -m smart_blinds --action open -c channel_name
python3 -m smart_blinds -s
```

### Note

On Mac Os you might need to use this to work:

```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```


## 3D print

It was tested with PLA, 25% infill and 2 perimeters.

[Assembly STL file](https://github.com/recallfx/smart-office-blinds/blob/master/assets/rack.stl?raw=true)
[Print 3MF file](https://github.com/recallfx/smart-office-blinds/blob/master/assets/rack_print.3mf?raw=true)

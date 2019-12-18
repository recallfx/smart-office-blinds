# 🧠🏢 Blinds v2.0

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
```

View logs:

```bash
journalctl -f scanteen-scanner
```

## Server

```
cd server
sudo ./bin/server
```

### Console

```
cd server
python3 -m smart_blinds open -c channel_name
python3 -m smart_blinds -s
```

### Note

On Mac Os you might need to use this to work:

```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

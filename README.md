# Smart Office Blinds v2.0

Blinds controlled mechanically pressing the button on the remote using servo motors (one per two buttons - up/down) 

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
sudo apt install python3-opencv
sudo pip3 install -r server/requirements.txt
sudo cp server/etc/systemd/system/* etc/systemd/system/
```

### Systemd

```bash
sudo systemctl start scanteen-scanner
sudo systemctl restart scanteen-scanner
```

View logs:

```bash
journalctl -f scanteen-scanner
```

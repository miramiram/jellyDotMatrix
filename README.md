# JellyDotPixel

A script for showing the currently playing JellyFin music's album art on your iDotPixel display.

## Setup

### Requirements

Start by installing:

- [Python](https://www.python.org/downloads/)

- [Git](https://git-scm.com/downloads)

### Linux

Run the following in your terminal:

```shell
git clone https://github.com/miramiram/jellyDotMatrix.git
cd jellyDotMatrix
python -m venv venv
source ./venv/bin/activate
python -m pip install -r ./requirements.txt
python ./display_now_playing.py
# At this point the script will create a config file you need to fill in:
nano ./secrets/config.toml
# After filling in the config:
python ./display_now_playing.py
```

### Windows

Run the following in PowerShell:

```powershell
git clone https://github.com/miramiram/jellyDotMatrix.git
cd jellyDotMatrix
python -m venv venv
source .\venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
python .\display_now_playing.py
# At this point the script will create a config file you need to fill in:
notepad .\secrets\config.toml
# After filling in the config:
python .\display_now_playing.py
```

### Notes

#### Jellyfin

The account you use to log in should either be the same you'll be playing music from, or have the account permissions to manage other users.

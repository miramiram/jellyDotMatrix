# JellyDotMatrix

**A script for showing the currently playing JellyFin music's album art on your iDotPixel display.**

Uses the JellyFin API to get your last playing music, and derkalle4's [iDotMatrix library](https://github.com/derkalle4/python3-idotmatrix-library/tree/main) for iDotMatrix communication (check out his [iDotMatrix client](https://github.com/derkalle4/python3-idotmatrix-client/tree/main) while you're at it).

## Setup

### Requirements

Start by installing:

- [Python](https://www.python.org/downloads/)

- [Git](https://git-scm.com/downloads)

### Linux

Run the following in your terminal:

```shell
git clone --recurse-submodules https://github.com/miramiram/jellyDotMatrix.git
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

Run the following in PowerShell _(Note that Windows needs the additional "bleak-winrt" pip package)_:

```powershell
git clone --recurse-submodules https://github.com/miramiram/jellyDotMatrix.git
cd jellyDotMatrix
python -m venv venv
source .\venv\Scripts\Activate.ps1
python -m pip install -r .\requirements.txt
python -m pip install bleak-winrt
python .\display_now_playing.py
# At this point the script will create a config file you need to fill in:
notepad .\secrets\config.toml
# After filling in the config:
python .\display_now_playing.py
```

### Notes

#### Jellyfin

- The account you use to log in should either be the same you'll be playing music from, or have the account permissions to manage other users.
- If you don't want your password in thr config, you can remove it after the script has created the "./secrets/logon_response.json" file, which contains your access token.
  - If you need to change your password, delete this file to re-generate the access token the next time you run the script.

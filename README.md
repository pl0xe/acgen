# acgen.py

tool to help autogenerate assetto corsa servers.

- Downloads the AssettoServer server files from github.

- Download your server pack you created with content manager
using ssh/scp.

- unpack into ./servers/ directory and configure some settings
with sane defaults.

# usage
```bash
acgen myserver -u user --server 192.168.0.2
cd ./server/myserver/
./AssettoServer
```

```
usage: acgen.py [-h] -s SERVER [-l LOCATION] [-u USERNAME] [-p PASSWORD] [-g GITHUB_RELEASE] [--time-of-day TIME_OF_DAY] serverName

downloads assettoserver (release) from githubcreates a directory for it based off the nameand then SSHs into my computer to download theserver pack. Based off the command linearguments will edit
the config files

positional arguments:
  serverName            directory name to save server files too. can not be a full path, just a name.

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        ssh server to download the assetto server pack created from content manager ex: 192.168.0.2
  -l LOCATION, --location LOCATION
                        location on the system where the file is stored at. Watch out for windows paths if you are not using powershell as default shell ex linux: ~/Desktop/server.tar.gz ex
                        windows: Desktop\server.tar.gz
  -u USERNAME, --username USERNAME
                        ssh username
  -p PASSWORD, --password PASSWORD
                        ssh password, wrap password in single qoutes 'password!' to avoid any weird bash string interpolations
  -g GITHUB_RELEASE, --github-release GITHUB_RELEASE
                        direct download link for the assetto service tar.gz file
  --time-of-day TIME_OF_DAY
                        set time of day HH:MM
```

# installing

```bash
# in root project directory directory
git clone git@github.com:pl0xe/acgen.git
cd acgen
pip -m build 
pip install ./dist/acgen-0.0.1.tar.gz
```

```bash
# can be used as a python module instead of installing
python3 ./acgen/ serverName \
    -u username \
    -p password \
    --server 192.168.0.2
```

import sys
import logging
import argparse
import requests
import tarfile
from paramiko import SSHClient
from scp import SCPClient

# setup command line parameters 
parser = argparse.ArgumentParser(prog='acgen.py',
                                    description='downloads assettoserver (release) from github'
                                        'creates a directory for it based off the name'
                                        'and then SSHs into my computer to download the'
                                        'server pack. Based off the command line'
                                        'arguments will edit the config files')

parser.add_argument('serverName', 
                    type=str, 
                    help='directory name to save server files too.'
                    'can not be a full path, just a name.')

parser.add_argument('-s',
                    '--server', 
                    type=str,
                    required=True,
                    help='ssh server to download the assetto server pack created from content manager ex: 192.168.0.2') 

parser.add_argument('-l',
                    '--location',
                    help='location on the system where the file is stored at. Watch out for windows paths if you are not using powershell as default shell\n'
                    'ex linux: ~/Desktop/server.tar.gz\n'
                    'ex windows: Desktop\\server.tar.gz',
                    default='./Desktop/server.tar.gz')

parser.add_argument('-u',
                    '--username',
                    default='user',
                    help='ssh username')

parser.add_argument('-p',
                    '--password',
                    default=None,
                    help='ssh password, wrap password in single qoutes \'password!\' to avoid any weird bash string interpolations')

# default v0.0.54 for download
parser.add_argument('-g', 
                    '--github-release', 
                    type=str, 
                    default='https://github.com/compujuckel/AssettoServer/releases/download/v0.0.54/assetto-server-linux-x64.tar.gz',
                    help='direct download link for the assetto service tar.gz file')

parser.add_argument('--time-of-day',
                    type=str,
                    default=None,
                    help='set time of day HH:MM')

args = parser.parse_args()

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='acgen.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# print logging msgs to stdout
logger.addHandler(logging.StreamHandler(sys.stdout))

def downloadAssettoServer(tarFileName: str, serverDirectory: str) -> None:
    # download the latest release for assetto server
    logger.info('downloading %s' % args.github_release)
    logger.info('saving as %s' % tarFileName)

    with requests.get(args.github_release, stream=True) as r:
        r.raise_for_status()
        with open(tarFileName, 'wb') as f:
            try:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                logger.info('assetto server download complete')
            except:
                logger.exception('dowloading assetto server')
                sys.exit(3)

    try:
        with tarfile.open(tarFileName, 'r:gz') as t:
            logger.info('extracting %s' % tarFileName)
            t.extractall(serverDirectory)
            logger.info('extracting complete')                
    except:
        logger.exception('could not extract server files')
        sys.exit(4)

def downloadServerPack(tarFileName: str, serverDirectory: str) -> None:
    try:
        logger.info('setting up ssh client')
        ssh = SSHClient()
        ssh.load_system_host_keys()
        # mad af cant login to my machine with keys only, need password
        if args.password == None:
            args.password = input(f'{args.username} password : ')
        ssh.connect(hostname=args.server, username=args.username, password=args.password)
        
        # scp section
        logger.info('scp serverpack file')
        scp = SCPClient(ssh.get_transport())
        scp.get(args.location, tarFileName)
        scp.close()
    except:
        logger.exception('failed to scp server pack')
        sys.exit(5)

    # extract server pack ( downloaded from you/client )
    try:
        with tarfile.open(tarFileName, 'r:gz') as t:
            logger.info('extracting %s' % tarFileName)
            t.extractall(serverDirectory)
            logger.info('extracting serverpack complete')
    except:
        logger.exception('could not extract server pack files')
        sys.exit(6)
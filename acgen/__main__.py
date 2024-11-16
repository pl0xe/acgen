'''downloads assettoserver (release) from github
    creates a directory for it based off the name
    and then SSHs into my computer to download the
    server pack. Based off the command line
    arguments will edit the config files'''

import os
import sys
import argparse
import requests
import logging
import tarfile
import subprocess


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

parser.add_argument

parser.add_argument('-s',
                    '--server', 
                    type=str,
                    required=True,
                    help='ex: user@192.168.0.2:~/Desktop/server.tar.gz') 

parser.add_argument('-l',
                    '--location',
                    help='location on the system where the file is stored at.\n'
                    'if file is on users desktop ex: Desktop/server.tar.gz',
                    default='Desktop/server.tar.gz')

parser.add_argument('-u',
                    '--username',
                    default='user',
                    help='ssh username')

parser.add_argument('-p',
                    '--password',
                    default=None,
                    help='ssh password')

# default v0.0.54 for download
parser.add_argument('-g', 
                    '--github-release', 
                    type=str, 
                    default='https://github.com/compujuckel/AssettoServer/releases/download/v0.0.54/assetto-server-linux-x64.tar.gz',
                    help='direct download link for the assetto service tar.gz file')

args = parser.parse_args()

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='acgen.log',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# print logging msgs to stdout
logger.addHandler(logging.StreamHandler(sys.stdout))

def downloadServerPack():
    '''uses SSH to scp a file specified from command line
    to download from your client computer to the server.
    obviously setup your ssh keys or specify them.'''
    
    client = paramiko.SSHClient()
    client.load_system_host_keys()        
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
def main():

    ''' main entry for script '''
    serverDest = f'{args.serverName}/server.tar.gz'

    # create directrory for server
    if os.path.exists(args.serverName):
        logging.error('server name / directory already exists.')
        sys.exit(1)
    else:
        try:
            logger.info('creating directory %s' % args.serverName)
            os.mkdir(args.serverName)
            logger.info('created directory')
        except Exception as e:
            logging.exception(e)
            sys.exit(2)

    # download the latest release for assetto server
    logger.info('downloading %s' % args.github_release)
    logger.info('saving as %s' % serverDest)

    with requests.get(args.github_release, stream=True) as r:
        r.raise_for_status()
        with open(serverDest, 'wb') as f:
            try:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                logger.info('assetto server download complete')
            except:
                logger.exception('dowloading assetto server')
                sys.exit(3)

    try:
        with tarfile.open(serverDest, 'r:gz') as t:
            logger.info('extracting %s' % serverDest)
            t.extractall(args.serverName)
            logger.info('extracting complete')
    except:
        logging.exception('could not extract server files')
        sys.exit(4)
    
    # scp the server.tar.gz file created from content manager
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
        scp.get(args.location, serverDest)
        scp.close()
    except:
        logger.exception('failed to scp server pack')
        sys.exit(5)

    # extract server pack ( downloaded from you/client )
    try:
        with tarfile.open(serverDest, 'r:gz') as t:
            logger.info('extracting %s' % serverDest)
            t.extractall(args.serverName)
            logger.info('extracting serverpack complete')
    except:
        logging.exception('could not extract server pack files')
        sys.exit(6)

    # SO DISGUSTING, HAVE TO DO TO LAUNCH SERVER TO GENERATE
    # CONFIGS
    os.chdir(args.serverName)
    resp = subprocess.check_output('./AssettoServer')
    os.chdir('..')

    # https://assettoserver.org/docs/common-configuration-errors/#missing-car-checksums
    # disable car checksums

    # TERRIBLE need a copy of a default extra_cfg.yml to exist first
    extra_cfg_path = 'extra_cfg.yml'
    os.mkdir('cfg')
    if not os.path.exists(extra_cfg_path):
        logger.error('could not find extra_cfg.yml')
        sys.exit(9)
    
    data = None
    with open(extra_cfg_path, 'r') as f:
        data = f.read()

    data.replace('MissingCarChecksums: false', 'MissingCarChecksums: true')
    logger.info('set MissingCarChecksums to true')
    
    with open(f'{args.serverName}/cfg/extra_cfg.yml', 'w') as f:
        logger.info('applying setting to config file')
        f.write(data)

main()

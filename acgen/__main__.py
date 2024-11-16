'''downloads assettoserver (release) from github
    creates a directory for it based off the name
    and then SSHs into my computer to download the
    server pack. Based off the command line
    arguments will edit the config files'''

import os
import sys
import subprocess

import acutil

def createServerDirectory() -> str:

    '''create the directory the server will be in
    returns the full path to the directory'''

    fullpath = os.path.abspath(f'servers/{acutil.args.serverName}')

    # check if servers directory if not make it
    if not os.path.exists(f'servers'):
        try:
            os.mkdir('servers')
        except Exception as e:
            acutil.logger.exception(e)
            sys.exit(10)
        
    # check if full path already exists
    if os.path.exists(fullpath):
        acutil.logger.error('server directory name %s already exists.' % fullpath)
        sys.exit(1)
    else:
        try:
            # 
            acutil.logger.info('creating directory %s' % fullpath)
            os.mkdir(fullpath)
            acutil.logger.info('created directory')
        except Exception as e:
            acutil.logger.exception(e)
            sys.exit(2)

    return fullpath

def main():

    ''' main entry for script '''

    serverDirectory = createServerDirectory()
    assettoServerTarFilePath = os.path.abspath(os.path.join(serverDirectory, 'assettoserver.tar.gz'))
    serverPackTarFilePath = os.path.abspath(os.path.join(serverDirectory, 'serverpack.tar.gz'))
    serverExecPath = os.path.abspath(os.path.join(serverDirectory, 'AssettoServer'))

    acutil.logger.debug('paths :')
    acutil.logger.debug('serverDirectory %s' % serverDirectory)
    acutil.logger.debug('assettoServerTarFilePath %s' % assettoServerTarFilePath)
    acutil.logger.debug('serverPackTarFilePath %s' % serverPackTarFilePath)
    acutil.logger.debug('serverExecPath %s' % serverExecPath)

    # download the github release of assettoserver
    acutil.downloadAssettoServer(assettoServerTarFilePath, serverDirectory)
    
    # scp the server.tar.gz file created from content manager
    acutil.downloadServerPack(serverPackTarFilePath, serverDirectory)

    # start the server to generate default configs
    process = subprocess.Popen(serverExecPath,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=serverDirectory,
            text=True)

    # check server output to see if it started then close it
    for line in iter(process.stdout.readline, ''):
        print(line.strip()) # assetto server startup output
        if 'Starting server' in line:
            process.terminate()
            break

    # https://assettoserver.org/docs/common-configuration-errors/#missing-car-checksums
    # disable car checksums
    extraCfgPath = os.path.abspath(os.path.join(serverDirectory, 'cfg/extra_cfg.yml'))
    data = None
    with open(extraCfgPath, 'r') as f:
        data = f.read()

    data = data.replace('MissingCarChecksums: false', 'MissingCarChecksums: true')
    acutil.logger.info('set MissingCarChecksums to true')
    
    with open(extraCfgPath, 'w') as f:
        acutil.logger.info('applying setting to config file')
        f.write(data)

    acutil.logger.info('success creating %s' % serverDirectory)

main()

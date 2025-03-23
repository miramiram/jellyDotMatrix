import json
import os
import sys
import subprocess
import time
import traceback
import tomllib
import asyncio
import logging

from utils import img_processing
from utils import jellyfin_helper as jh
from submodules.patched_python3_idotmatrix_library import idotmatrix as idm


class ErrorInterceptor(logging.Handler):
    def __init__(seld, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            raise RuntimeError(f"An error was logged: {record.getMessage()}")

intercept = ['submodules.patched_python3_idotmatrix_library.idotmatrix', 'idotmatrix']
for mod in intercept:
    logging.getLogger(mod).addHandler(ErrorInterceptor())

pwd = os.path.dirname(os.path.abspath(__file__))
def main():
    config, logon_resp_file = setup()
    asyncio.run(
            mainloop(config, logon_resp_file)
            )


def setup():
    secrets = f"{pwd}/secrets"
    os.makedirs(secrets, exist_ok=True)
    logon_resp_file=f'{secrets}/logon_response.json'
    config_file = f"{secrets}/config.toml"
    config = None

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write('jellyfin_url = "http://"\n'
                    'username     = ""\n'
                    'password     = ""  #Used if the logon_response.json file doesn\'t exist.\n'
                    'iDotPixel_address    = "auto"\n'
                    'iDotPixel_pixel_size = 16\n'
                    'checking_interval    = 10'
                    )
        raise SystemExit(f"Please enter your details into the new config file, and run again: {config_file} \n(You can remove your password after the logon response file has been generated, next time you run.)")


    with open(config_file, 'rb') as f:
        config = tomllib.load(f)

    if not os.path.exists(logon_resp_file):
        for req in ['jellyfin_url', 'username', 'password', 'iDotPixel_address']:
            if not req in config:
                raise Exception(f"TOML file is missing key: {req}")
        jh.make_token(jellyfinurl=config['jellyfin_url'], 
                      username=config['username'], 
                      password=config['password'], 
                      client_nickname="jellyDotPixel",
                      device_nickname=f"device_{config['username']}",   
                      response_filename=logon_resp_file)
    return config, logon_resp_file  



async def mainloop(config, logon_resp_file):
    logon_resp=jh.get_logon_response(logon_resp_file)

    outdir  = f"{pwd}/output"
    os.makedirs(outdir,  exist_ok=True)

    domain     = config["jellyfin_url"]
    pixel_size = int(config["iDotPixel_pixel_size"])
    interval   = int(config['checking_interval'])

    if not domain.endswith('/'):
        domain = f"{domain}/"

    firstloop     = True
    prev_media_id = None
    conn = idm.ConnectionManager()


    async def connect() -> str:
        if str(config['iDotPixel_address']).lower() == "auto":
            await conn.connectBySearch()
        else:
            await conn.connectByAddress(config['iDotPixel_address'])
        return conn.address

    while True:
        try:
            if firstloop: 
                address = await connect()
                firstloop = False
            else:
                await asyncio.sleep(interval)

            rsp=jh.send_get(domain, f'Sessions?ActiveWithinSeconds={interval+1}', logon_resp=logon_resp)
            jh.save(f'{outdir}/out_lastmedia.json', rsp)

            rspj = rsp.json()
            if type(rspj) != list or len(rspj)==0: 
                continue

            if 'MediaSourceId' not in rspj[0]['PlayState']:
                continue

            media_id = rspj[0]['PlayState']['MediaSourceId']
            if media_id==prev_media_id:
                continue

            prev_media_id = media_id
            rsp=jh.send_get(domain, f'Items/{media_id}/Images/Primary', logon_resp=logon_resp)

            if not rsp or (type(rsp)==list and len(rsp)==0): 
                continue

            imgpath = f'{outdir}/nowplaying.png'
            with open(imgpath, 'wb') as f:
                f.write(rsp.content)

            imgpath = img_processing.resize_and_process(imgpath, pixel_size)


            image = idm.Gif()
            image.conn = conn
            #await image.setMode(mode=1)
            await image.uploadUnprocessed(
                file_path=imgpath,
            )

            # todo:
            # - check if image is the same as previous, e.g. when they're in the same album (only store prev image)
            # - get album id to get its img for the songs that dont have them embedded
            #   by searching for 'album' on https://jmshrv.com/posts/jellyfin-api/


        except RuntimeError as e:
            def is_idotmatrix_connection_error(exception):
                matches = ["'not found",  
                           "device address is not set.", 
                           "no target devices found."]
                for text in matches:
                    if text in str(e): return True
            if is_idotmatrix_connection_error(e):
                print("Failed to connect to device: ", e)
                print("Reconnecting...")
                try:
                    address = await connect()
                except RuntimeError as e:
                    if is_idotmatrix_connection_error(e):
                        print("Failed to connect to device: ", e)
                        print("Check that the display is turned on, is nearby, and that bluetooth works properly on the device you're running this on. If you're using a specific iDotMatrix address, try using \"auto\" instead.")
                        sys.exit()
                    else:
                        raise
                else:
                    continue


            traceback.print_exc()
        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    main()


import json
import os
import subprocess
import time
import traceback
import tomllib
import asyncio

from utils import img_processing
from utils import jellyfin_helper as jh
from submodules.patched_python3_idotmatrix_library import idotmatrix as idm


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

    domain        = config["jellyfin_url"]
    address       = config["iDotPixel_address"]
    pixel_size    = int(config["iDotPixel_pixel_size"])

    if not domain.endswith('/'):
        domain = f"{domain}/"

    firstloop     = True
    prev_media_id = None
    conn = idm.ConnectionManager()


    if str(address).lower() == "auto":
        devices = await conn.scan()
        if devices:
            address = devices[0]
        else:
            self.logging.error("no target devices found.")
            raise SystemExit("Couldn't find your iDotMatrix display, check your devices bluetooth.")

    await conn.connectByAddress(address)

    interval=int(config['checking_interval'])
    while True:
        if firstloop: 
            firstloop = False
        else:
            await asyncio.sleep(interval)

        try:
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


        except Exception as e:
            traceback.print_exc()

if __name__ == '__main__':
    main()


import requests
import hashlib
import sys
import json
import hashlib


def make_device_id(username):
	id_hash = hashlib.new('sha256')
	id_hash.update(username.encode())
	return f"user{id_hash.hexdigest()}"

def get_logon_response(logon_response_file)->dict:
	with open(logon_response_file, 'r') as f:
		return json.load(f)
def save(filename, response_object):
	with open(filename, 'w') as f:
		f.write(json.dumps(response_object.json(), indent=4))


def make_auth_header(logon_response:dict)->dict:
	seshinf = logon_response['SessionInfo']
	client_nickname = seshinf['Client']
	device_nickname = seshinf['DeviceName']
	device_id       = seshinf['DeviceId']
	auth_token      = logon_response['AccessToken']
	return {
		'Authorization':f'MediaBrowser Token="{auth_token}", Client="{client_nickname}", Device="{device_nickname}", DeviceId="{device_id}"',
	}




def send_get(domain, path, logon_resp:dict):
	return requests.get(
		url=f'{domain}{path}',
		headers={
			"content-type": "application/json",
			**make_auth_header(logon_resp)
			}
		)

def send_post(domain, path, logon_resp:dict, body:dict):
	return requests.post(
		url=f'{domain}{path}',
		headers={
			"content-type": "application/json",
			**make_auth_header(logon_resp)
		},
		json=body,
	)



def make_token(jellyfinurl, username, password, client_nickname, device_nickname, response_filename=None, chosen_version='1.0'):

	url=jellyfinurl
	pth="/Users/AuthenticateByName"
	hdrs = {
		"content-type": "application/json",
		'Authorization':f'MediaBrowser Client="{client_nickname}", Device="{device_nickname}", DeviceId="{make_device_id(username)}", Version="{chosen_version}"',
	}
	body = {
		"Username":username,
		"Pw":password
	}
	rsp = requests.post(
			url=f'{url}{pth}',
			headers=hdrs,
			json=body,
			)

	rspjson = rsp.json()
	if response_filename:
		with open(response_filename, 'w') as f:
			f.write(json.dumps(rspjson, indent=4))
	if not rsp.status_code == 200:
		raise Exception(f"Received status code {rsp.status_code}: {rspjson}")
	return rspjson['AccessToken']


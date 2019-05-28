#!/usr/bin/env python3
##############################################################################
# SCRIPT NUTANIX TOOLS FOR IMAGE REPLICATION PC-PETOPE  					 #
# PYTHON 3  																 #
# Testing on AOS , 5.8.x, 5.9.x, 5.10.x								         #				       
# David Lira, dlira96@gmail.com										         #
##############################################################################

import getpass
import paramiko, time
import json
import requests
import urllib3
import time
import datetime
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version_soft = 'Nutanix tools for image replication PC-PETOPE v1.1'
print('------------------------------------------------------------') 
print(version_soft)
print('------------------------------------------------------------')
print('-------------------------"LOGIN"----------------------------')
##SECURE LOGIN PRISM CENTRAL
pc_ip = input("Prism-Central-IP: ")
pc_url = ('https://' + pc_ip +':9440')
pc_username = input("Username PC: ")
pc_password = getpass.getpass()
pc_ssh_username = input("SSH Username: ") ##Admin or Nutanix user
pc_ssh_password = getpass.getpass()

##NO SECURE LOGIN PRISM CENTRAL
#pc_ip = 'someip'
#pc_url = ('https://' + pc_ip +':9440')
#pc_username = 'admin'
#pc_password = 'somepass'
#pc_ssh_username = 'admin' ##Admin or Nutanix user
#pc_ssh_password = 'somepass' 

##VARIABLE
poolingimageapi = 500
TIMEOUT = 15

print('\n##########################################')
print ('Prism Central URL', pc_url)
print('##########################################')
print()
try:
	session = requests.Session()
	session.auth = (pc_username,pc_password)
	session.verify = False
	session.headers.update({'Content-Type': 'application/json; charset = utf-8'})
	session.headers.update({'Accept': 'application/json'})
	###PRISM CENTRAL
	pcimage='{"kind": "image","offset": 0}'
	pcclusterpe ='{"kind": "cluster"}'
	pc_image = session.post(pc_url + '/api/nutanix/v3/images/list',pcimage)
	pc_clusterpe = session.post(pc_url + '/api/nutanix/v3/clusters/list',pcclusterpe)
	pc_clusterpe_raw = pc_clusterpe.json()
	#print(pc_clusterpe_raw)

except Exception as e:
	print('Login Failed to API, Bad Password , Bad IP/FQDN Prism Central or networks problems. Run again the script')
	print(f"Error: {e}")
	time.sleep(2)
	sys.exit()	

if pc_clusterpe.status_code == requests.codes.ok:
	pc_numberofpe = str(pc_clusterpe_raw['metadata']['total_matches'])
	print('Number of Prism Element on Prism Central:' ,int(pc_numberofpe)-1)
	index = 0
	pe_list = []
	pe_index = []
	for x in pc_clusterpe_raw['entities']:
		pc_namepe = x['status']['name']
		if not pc_namepe == 'Unnamed':
			index = index + 1
			pc_networkpe = x['status']['resources']['network']['external_ip']
			pe_uuid = x['metadata']['uuid']
			print('------------------------------------------------------------')
			print(index,")",'Prism Element: ',pc_namepe, '| IP External: ', pc_networkpe)
			pe_list.append([index,[pc_networkpe,pe_uuid,pc_namepe]])
			pe_index.append(index)

###SOURCE PE AND IMAGE
exit = 0
while not exit == 1:
	print('------------------------------------------------------------')
	select = input("Select source Prism Element : ")
	if select in str(pe_index):
		pe_name= pe_list[int(select)-int(1)][1][2]
		pe_ip = pe_list[int(select)-int(1)][1][0]
		pe_uuid = pe_list[int(select)-int(1)][1][1]
		print('Selected PE Name:', pe_name)
		#print('Selected PE UUID:', pe_uuid)		
		try:
			pe_image = requests.get('https://'+str(pe_ip)+':9440'+'/PrismGateway/services/rest/v2.0/images/?include_vm_disk_sizes=true', auth=(pc_username, pc_password), verify=False, timeout=TIMEOUT)	
			out_json = pe_image.json()
			image = out_json['entities']
		except Exception as e:
			print('Login Failed to API, Bad Password , Bad IP/FQDN Prism Central or networks problems. Run again the script')
			print(f"Error: {e}")
			time.sleep(2)
			sys.exit()	
		print('------------------------------------------------------------')
		print('---------------ONLY ACTIVE IMAGES ARE LISTED----------------')
		print('------------------------------------------------------------')	
		index1=0
		image_list = []
		image_list_index = []
		for image_not_size in image:
			if 'ACTIVE' == image_not_size['image_state']:
				if not 'vm_disk_size' in image_not_size.keys():
					index1=index1 + 1
					nameimage = image_not_size['name']
					if 'image_type' in image_not_size.keys():
						image_type = image_not_size['image_type']
					else:
						image_type = '-'
					image_state = image_not_size['image_state']
					image_uuid = image_not_size['uuid']
					image_list.append([index1,[image_uuid,nameimage]])
					image_list_index.append(index1)
					print(index1,")",'IMAGE: ', nameimage,'| TYPE: ',image_type,'| STATE: ', image_state,'| SIZE: ','-' )
		for image_size in image:
			if 'ACTIVE' == image_size['image_state']:
				if 'vm_disk_size' in image_size.keys():
					index1=index1 + 1
					nameimage1 = image_size['name']
					image_size1 = image_size['vm_disk_size']
					if 'image_type' in image_size.keys():
						image_type1 = image_size['image_type']
					else:
						image_type1 = '-'
					image_state1 = image_size['image_state']
					image_uuid1 = image_size['uuid']
					image_list.append([index1,[image_uuid1,nameimage1]])
					image_list_index.append(index1)
					print(index1,")",'IMAGE: ', nameimage1,'| TYPE: ',image_type1,'| STATE: ', image_state1,'| SIZE: ', (image_size1/1024/1024/1024),'GB' )
	
		loop = 0
		while not loop == 1:
			print('------------------------------------------------------------')
			select1 = str(input("Select image : "))
			if select1 in str(image_list_index):
				select1 = int(select1) - 1
				pc_image_uuid = image_list[int(select1)][1][0]
				pc_image_name = image_list[int(select1)][1][1]
				loop = loop + 1 ##EXIT WHILE
			else:
				print('Select a correct value')
		exit = exit + 1
	else:
		print('Select a correct value')

###DESTINY PE
index = 0
exit = 0
print('------------SELECT A DIFFERENT ONE TO THE SOURCE------------')
for x in pc_clusterpe_raw['entities']:
		pc_namepe = x['status']['name']
		if not pc_namepe == 'Unnamed':
			index = index + 1
			pc_networkpe = x['status']['resources']['network']['external_ip']
			pe_uuid = x['metadata']['uuid']
			print(index,")",'Prism Element: ',pc_namepe, '| IP External: ', pc_networkpe)
print('------------------------------------------------------------')
print('SOURCE:',pe_name)
print('------------------------------------------------------------')
select_destiny = input("Select destiny Prism Element : ")				
print('------------------------------------------------------------')		
while not exit == 1:
	if select_destiny in str(pe_index):
		pe_name_destiny= pe_list[int(select_destiny)-int(1)][1][2]
		pe_ip_destiny = pe_list[int(select_destiny)-int(1)][1][0]
		pe_uuid_destiny = pe_list[int(select_destiny)-int(1)][1][1]
		exit = 1 ##EXIT WHILE
		print('Selected PE Name:', pe_name_destiny)
	else:
		print('Select a correct value in range')


###CHECK IF IMAGE EXIST ON PRISM CENTRAL
pc_total_image = session.post(pc_url + '/api/nutanix/v3/images/list','{"kind": "image","offset": 0,"length": 1}')
pc_total_image_raw = pc_total_image.json()
pctotalimage = pc_total_image_raw['metadata']['total_matches']

if pctotalimage < 500:
	imageinfo='{"kind": "image","offset": 0,"length": 500}'
	pc_check_list = session.post(pc_url + '/api/nutanix/v3/images/list',imageinfo)
	pc_check_list_raw = pc_check_list.json()
	pc_check_list_uuid = []
	for x in pc_check_list_raw['entities']:
		pc_check_image = x['metadata']['uuid']
		pc_check_list_uuid.append(pc_check_image)
	if pc_image_uuid in pc_check_list_uuid:
		print('------------------------------------------------------------')
		print('No metadata is needed replicate to Prism Central')
	else: ###REPLICATE METADATA
		print('------------------------------------------------------------')	
		print('Replicate metadata to Prism Central, Please Wait...')
		pemigrate ='{"image_reference_list": [{"kind": "image","name": "'+pc_image_name+'","uuid": "'+pc_image_uuid+'"}],"cluster_reference": {"kind": "cluster","name": "'+pe_name+'","uuid": "'+pe_uuid+'"}}'
		pe_migrate = session.post(pc_url + '/api/nutanix/v3/images/migrate',pemigrate)
		pe_migrate_raw = pe_migrate.json()
		time.sleep(15)

else:
	offset_s = 0
	length_s = poolingimageapi
	while(offset_s <= pc_vm_total_vminpc):
		vminfo='{"kind": "image","offset": '+str(offset_s)+',"length": '+str(length_s)+'}'
		length_s = length_s + poolingimageapi
		offset_s = offset_s + poolingimageapi
		pc_check_list = session.post(pc_url + '/api/nutanix/v3/images/list',imageinfo)
		pc_check_list_raw = pc_check_list.json()
		pc_check_list_uuid = []
		for x in pc_check_list_raw['entities']:
			pc_check_image = x['metadata']['uuid']
			pc_check_list_uuid.append(pc_check_image)
		if pc_image_uuid in pc_check_list_uuid:
			print('------------------------------------------------------------')
			print('No metadata is needed replicate to Prism Central')
		else: ###REPLICATE METADATA
			print('------------------------------------------------------------')	
			print('Replicate metadata to Prism Central, Please Wait...')
			pemigrate ='{"image_reference_list": [{"kind": "image","name": "'+pc_image_name+'","uuid": "'+pc_image_uuid+'"}],"cluster_reference": {"kind": "cluster","name": "'+pe_name+'","uuid": "'+pe_uuid+'"}}'
			pe_migrate = session.post(pc_url + '/api/nutanix/v3/images/migrate',pemigrate)
			pe_migrate_raw = pe_migrate.json()
			time.sleep(15)
	
'''
if pc_image_uuid in pc_check_list_uuid:
	print('------------------------------------------------------------')
	print('No metadata is needed replicate to Prism Central')
else:
	###REPLICATE METADATA
	print('------------------------------------------------------------')	
	print('Replicate metadata to Prism Central, Please Wait...')
	pemigrate ='{"image_reference_list": [{"kind": "image","name": "'+pc_image_name+'","uuid": "'+pc_image_uuid+'"}],"cluster_reference": {"kind": "cluster","name": "'+pe_name+'","uuid": "'+pe_uuid+'"}}'
	pe_migrate = session.post(pc_url + '/api/nutanix/v3/images/migrate',pemigrate)
	pe_migrate_raw = pe_migrate.json()
	time.sleep(15)
	#print(pe_migrate_raw) ##TAKE TASK UUID
'''

## SSH BELOW ##
class ShellHandler:
	def __init__(self, host, user, psw):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.ssh.connect(host, username=user, password=psw, port=22)
		channel = self.ssh.invoke_shell()
		self.stdin = channel.makefile('wb')
		self.stdout = channel.makefile('r')

	def __del__(self):
		self.ssh.close()

	def execute(self, cmd):
		global shout
		"""
		:param cmd: the command to be executed on the remote computer
		:examples:  execute('ls')
				    execute('finger')
				    execute('cd folder_name')
		"""
		cmd = cmd.strip('\n')
		self.stdin.write(cmd + '\n')
		finish = 'end of stdOUT buffer. finished with exit status'
		echo_cmd = 'echo {} $?'.format(finish)
		self.stdin.write(echo_cmd + '\n')
		shin = self.stdin
		self.stdin.flush()

		shout = []
		sherr = []
		exit_status = 0
		for line in self.stdout:
			if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
				# up for now filled with shell junk from stdin
				shout = []
			elif str(line).startswith(finish):
				# our finish command ends with the exit status
				exit_status = int(str(line).rsplit(maxsplit=1)[1])
				if exit_status:
				    # stderr is combined with stdout.
				    # thus, swap sherr with shout in a case of failure.
					sherr = shout
					shout = []
				break
			else:
				# get rid of 'coloring and formatting' special characters
				shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
					replace('\b', '').replace('\r', ''))

		# first and last lines of shout/sherr contain a prompt
		if shout and echo_cmd in shout[-1]:
			shout.pop()
		if shout and cmd in shout[0]:
			shout.pop(0)
		if sherr and echo_cmd in sherr[-1]:
			sherr.pop()
		if sherr and cmd in sherr[0]:
			sherr.pop(0)
		return shout

###RUN COMMAND CREATE TASK	
RUN_1 = ShellHandler(pc_ip,'admin',pc_ssh_password)
#print("checkout_catalog --destination_cluster_uuid_list="+pe_uuid_destiny+" --wait_for_checkout=False "+pc_image_uuid)
RUN_1.execute("checkout_catalog --destination_cluster_uuid_list="+pe_uuid_destiny+" --wait_for_checkout=False "+pc_image_uuid)

###GET TASK UUID
stringToMatch = "Checkout task created :"
matchedLine = ''
for line in shout:
	if stringToMatch in line:
		matchedLine = line
		TASK_UUID = str(matchedLine.replace("Checkout task created : ",''))
		TASK_CLEAN = ' '.join(TASK_UUID.split())
		print('------------------------------------------------------------')
		print('TASK CREATED WITH UUID :', TASK_CLEAN)
		print('------------------------------------------------------------')
		time.sleep(4)
		break

###CHECK TASK STATUS
loop = 0
while not loop == 1:
	taskdata = session.get(pc_url + '/api/nutanix/v3/tasks/'+TASK_CLEAN)
	taskdata_raw = taskdata.json()
	taskstatus = taskdata_raw['status']
	taskpercentage = taskdata_raw['percentage_complete']
	if taskstatus == 'RUNNING':
		print('Copy Status',taskpercentage,'%', end='\r')
		time.sleep(3)
	if taskstatus == 'FAILED':
		print('Failed copy image , check prism central log')
		loop = loop + 1
	if taskstatus == 'SUCCEEDED':
		print('Finish upload image',taskpercentage,'%')
		loop = loop + 1


				


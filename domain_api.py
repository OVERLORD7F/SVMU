# functions for working with domain-api
import requests
import secrets #for generating unique names

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel

power_state = ["Unknown" , "Off" , "Suspend" , "On"] #3 - on; 2 - suspend; 1 - off; 0 - unknown


def get_domain_info(base_url , api_key , domain_uuid):
    url= f"http://{base_url}/api/domains/{domain_uuid}"
    response = requests.get(url , headers={'Authorization' : api_key})
    
    if response.status_code == 200: #200 - OK
        domain_data = response.json()
        return domain_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")



def get_domain_all_content(base_url, api_key, domain_uuid):
    url= f"http://{base_url}/api/domains/{domain_uuid}/all-content"
    response = requests.get(url , headers={'Authorization' : api_key})
    if response.status_code == 200: #200 - OK    
        domain_all_data = response.json()
        return domain_all_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")


def get_disk_uuids(base_url , api_key , domain_all_content):
    #domain_all_content (type - dictionary)
    #returns VMs vdisk uuids (type - list)   
    try:
        # check for "vdisks" field in recieved json response
        if 'vdisks' not in domain_all_content:
            raise KeyError("No 'vdisks' field in recieved data")
        # Get list of all vdisks
        disks = domain_all_content['vdisks']
        # Extracting UUID for each disk
        vdisk_uuid = [disk['id'] for disk in disks]
        vdisk_size = []
        return vdisk_uuid
    except KeyError as e:
        print(f"ERROR: {e}")
        return []
    except TypeError:
        print("ERROR: unexpected data format")
        return []


def delete_disk(base_url , api_key , vdisk_uuid):      
        url = f"http://{base_url}/api/vdisks/{vdisk_uuid}/remove/"
        headers={
        "Authorization" : api_key,
        "Content-Type" : "application/json",
        }
        payload= {
        "force": False,
        "guaranteed": False,
        "clean_type": "zero",
        "clean_count": 1
        }
        response = requests.post(url , headers=headers, json=payload)
        if response.status_code == 200:
            print(f"vDisk {vdisk_uuid} successfully deleted")
            return True
        else:
            print(f"ERROR deleting disk {vdisk_uuid} :\n {response.status_code} - {response.text}")
            return False


def get_disk_info(domain_all_content):
    # check for "vdisks" field in recieved json response
    if 'vdisks' not in domain_all_content:
        print("No 'vdisks' field in recieved data")
        return
    
    # get vdisk list
    disks = domain_all_content['vdisks']
    
    # check for disks
    if not disks:
        print("No 'disks' field in recieved data. \nProbably VM does not have any attached disks?")
        return
    # Print info for each disk
    for disk in disks:
        # check for requiered fileds
        if 'id' in disk and 'verbose_name' in disk and 'size' in disk:
            print(f"Name: {disk['verbose_name']}")
            print(f"UUID: {disk['id']}")
            print(f"Size: {disk['size']} GB")
            print("-" * 51)
        else:
            print("ERROR: failed to retrieve vdisk data.")


def vm_info(base_url , api_key , vm_uuids): 
    domain_info = get_domain_info(base_url , api_key , vm_uuids)
    domain_all_content = get_domain_all_content(base_url , api_key , vm_uuids)
    if domain_info:
        print("\n" , "=" * 14 , "Virtual Machine Info" , "=" * 15)
        print(f"\t VM: {domain_info['verbose_name']}")
        print(f"\t Power State: {power_state[domain_info['user_power_state']]}") #translating status code to "pretty name"
        print(f"\t vDisks: {domain_info['vdisks_count']}")
        print("-" * 19 , "vDisks Info" , "-" * 19)
        get_disk_info(domain_all_content)


def vm_info_short(base_url , api_key): #output data pool info 
    url= f"http://{base_url}//api/domains/"
    response = requests.get(url , headers={'Authorization' : api_key})
    if response.status_code == 200:
        vm_info_short = response.json()
        results_vm_info_short = vm_info_short['results']
        print(f"\nShort VM overview | Total: {vm_info_short['count']}")
        print("=" * 43)         
        for x in results_vm_info_short:
            print(f"  VM: {x['verbose_name']}")
            print(f"UUID: {x['id']}")
            print("-" * 43) 
        
    else:
        print(f"Failed to retrieve data {response.status_code}")  

def create_and_attach_disk(base_url , api_key , vm_id, data_pool_uuid, vdisk_size, preallocation):
    domain_name=get_domain_info(base_url , api_key , vm_id)
    disk_name=domain_name["verbose_name"]+"_"+secrets.token_hex(5) #generates unique hex id. this method can generate ~million unique ids
    url = f"http://{base_url}/api/domains/{vm_id}/create-attach-vdisk/"
    headers={
    "Authorization" : api_key,
    "Content-Type" : "application/json",
    }
    payload= {
    "verbose_name": disk_name,
    "preallocation": preallocation,
    "size": vdisk_size,
    "datapool": data_pool_uuid,
    "target_bus": "virtio",
    }    
    response = requests.post(url , headers=headers, json=payload)
    if response.status_code == 200:
        print(f"vDisk {disk_name} - {vdisk_size}GB has been created and attached to VM - {vm_id}")
        return True
    else:
        print(f"ERROR creating vDisk :\n {response.status_code} - {response.text}")
        return False  

#checks for power on.     
def vm_check_power(base_url , api_key , vm_uuids):
    domain_info = get_domain_info(base_url , api_key , vm_uuids)

    if domain_info:
        #3 - on; 2 - suspend; 1 - off; 0 - unknown
        if domain_info['user_power_state'] == 3 or domain_info['user_power_state'] == 2 : #if ON or SUSPEND
            raise Exception(f"VM - {vm_uuids} IS POWERED ON! \n Turn it off and relaunch Utility.")
        if domain_info['user_power_state'] == 0:  
            raise Exception(f"VM - {vm_uuids} is UNAVAILABLE! \n Have fun figuring that out D:")
        if domain_info['user_power_state'] == 1:
            print(f"VM - {vm_uuids} Power check passed!")
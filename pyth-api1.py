import requests
import json
import copy
import sys

base_url = "http://10.2.1.52/api"
power_state = ["Unknown" , "Off" , "Suspend" , "On"] #3 - on; 2 - suspend; 1 - off; 0 - unknown

#importing API-KEY from file
with open("Y:\\py\\integration_key_pod5.txt", "r") as f: # using  '\' (instead of '\\') throws syntax warning
    api_key = "jwt " + f.read() #actual format for api_key. That was realy obvious DACOM >:C


#importing VM-UUIDs from file
with open("Y:\\py\\VM-UUIDs.txt", "r") as f:
    vm_uuids =  f.read() 

#get domain info "http://10.2.1.52/api/domains/uuid   OR  /domains/{id}/all-content/"
def get_domain_info(domain_uuid):
    url= f"{base_url}/domains/{domain_uuid}"
    response = requests.get(url , headers={'Authorization' : api_key})
    
    if response.status_code == 200: #200 - OK
        domain_data = response.json()
        return domain_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")
    
    

def get_domain_all_content(domain_uuid):
    url= f"{base_url}/domains/{domain_uuid}/all-content"
    response = requests.get(url , headers={'Authorization' : api_key})
    if response.status_code == 200: #200 - OK    
        domain_all_data = response.json()
        return domain_all_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")


def get_disk_uuids(domain_all_content):
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



def get_disk_info(domain_all_content):
    # check for "vdisks" field in recieved json response
    if 'vdisks' not in domain_all_content:
        print("No 'vdisks' field in recieved data")
        return
    
    # get vdisk list
    disks = domain_all_content['vdisks']
    
    # check for disks
    if not disks:
        print("No 'disks' field in recieved data. Probably VM does not have any attached disks?")
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


def delete_disk(vdisk_uuid):
        
        url = f"{base_url}/vdisks/{vdisk_uuid}/remove/"
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

def create_disk(data_pool_uuid, vdisk_size):
    url = f"{base_url}/vdisks/"
    headers={
    "Authorization" : api_key,
    "Content-Type" : "application/json",
    }
    payload= {
    "verbose_name": "Auto-created-vdisk", #UNIC NAME !!!!!!!!!!
    "preallocation": False,
    "size": vdisk_size,
    "datapool": data_pool_uuid
    }    
    response = requests.post(url , headers=headers, json=payload)
    if response.status_code == 200:
        print(f"vDisk {vdisk_size} has been created")
        return True

    else:
        print(f"ERROR creating vDisk :\n {response.status_code} - {response.text}")
        return False        

def attach_disk(vdisk_uuid, vm_id):
    url = f"{base_url}/domains/{vm_id}/attach_disk/"
    #todo

#so-called INT MAIN

domain_uuid = vm_uuids 
domain_info = get_domain_info(domain_uuid)
domain_all_content = get_domain_all_content(domain_uuid)
#vdisk_ids = domain_all_content["vdisks"]

#print(domain_info)
if domain_info:
    print("=" * 14 , "Virtual Machine Info" , "=" * 15)
    print(f"\t VM: {domain_info["verbose_name"]}")
    print(f"\t Power State: {power_state[domain_info["user_power_state"]]}") #translating status code to "pretty name"
    print(f"\t vDisks: {domain_info["vdisks_count"]}")
    print("-" * 19 , "vDisks Info" , "-" * 19)
    get_disk_info(domain_all_content)
    #print(domain_all_content)
    
read_input=input("Enter disk edit mode Y / N: ")
menu_choice=str(read_input)
if menu_choice == "Y" or menu_choice == "y":
    print("\033[H\033[2J", end="") # clears cmd screen, but saves scrollback buffer
    print("Select option: \n 1) Delete vDisk by UUID \n 2) Delete ALL vDisks on selected Virtual Machine \n 3) Create Disk")
    read_input=input(">> ")
    menu_choice=int(read_input)
    if menu_choice == 1:
        read_input=input("Input vDisk uuid to delete: ")
        vdisk_uuid=str(read_input)
        delete_disk(vdisk_uuid)      
    if menu_choice == 2:
        disk_uuids = get_disk_uuids(domain_all_content)
        for x in disk_uuids:
            delete_disk(x)
        print("All attached vDisks has been deleted")
    if menu_choice == 3:
        create_disk("67497424-e54b-46f1-b023-4d6d65eac104", 15)    
    

print("Exiting Utility..")
sys.exit()




#attach disk(disk , domain_uuid)
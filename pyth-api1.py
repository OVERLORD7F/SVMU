import requests
import json
import copy
import sys
import secrets #for generating unique names

power_state = ["Unknown" , "Off" , "Suspend" , "On"] #3 - on; 2 - suspend; 1 - off; 0 - unknown
config_relative_path = "C:\\Users\\n.danilov\\config.txt" # absolute path to cluster config file  
VM_UUID_relative_path = "C:\\scripts\\VM-UUIDs.txt"  # absolute path to cluster config file  

# edit config or use old 
read_input=input("Create new config file? (Y / N): ") 
menu_choice=str(read_input)
if menu_choice == "Y" or menu_choice == "y":
    base_url = input("Type ip address: ")
    api_key = input("Type integration key: ")
    lines = [base_url, api_key]
    with open(config_relative_path, "w+") as file:
        for  line in lines:
            file.write(line + '\n')

#importing API-KEY and ip address from config file
with open(config_relative_path, "r") as f: # using  '\' (instead of '\\') throws syntax warning
    all_lines = f.readlines()  
    base_url = all_lines[0].strip('\n')
    api_key = "jwt " + all_lines[1].strip('\n') #actual format for api_key. That was realy obvious DACOM >:C


#importing ONLY 1st entry in VM-UUIDs file
with open(VM_UUID_relative_path, "r") as f:
    vm_uuids =  f.readline().strip('\n')

    
#importing data_pool_uuid from file
#selected data pool will be used for new disks and alike
with open("C:\\scripts\\data-pool.txt", "r") as f:
    data_pool_uuid =  f.readline()     

#get domain info "http://10.2.1.52/api/domains/uuid   OR  /domains/{id}/all-content/"
def get_domain_info(domain_uuid):
    url= f"http://{base_url}/api/domains/{domain_uuid}"
    response = requests.get(url , headers={'Authorization' : api_key})
    
    if response.status_code == 200: #200 - OK
        domain_data = response.json()
        return domain_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")
        
        
def get_domain_all_content(domain_uuid):
    url= f"http://{base_url}/api/domains/{domain_uuid}/all-content"
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

def create_and_attach_disk(vm_id, data_pool_uuid, vdisk_size, preallocation):
    domain_name=get_domain_info(domain_uuid)
    disk_name=domain_name["verbose_name"]+"_"+secrets.token_hex(5) #generates unique hex id. this method can generate ~million unique ids
    url = f"http://{base_url}/api/domains/{vm_id}/create-attach-vdisk/"
    headers={
    "Authorization" : api_key,
    "Content-Type" : "application/json",
    }
    payload= {
    "verbose_name": disk_name, #UNIQUE NAME !!!!!!!!!!
    "preallocation": preallocation,
    "size": vdisk_size,
    "datapool": data_pool_uuid,
    "target_bus": "virtio",
    }    
    response = requests.post(url , headers=headers, json=payload)
    if response.status_code == 200:
        print(f"\nvDisk {disk_name} - {vdisk_size}GB has been created")
        return True
    else:
        print(f"ERROR creating vDisk :\n {response.status_code} - {response.text}")
        return False        


#so-called INT MAIN

domain_uuid = vm_uuids
print(domain_uuid)
print((domain_uuid))
domain_info = get_domain_info(domain_uuid)
domain_all_content = get_domain_all_content(domain_uuid)


#print(domain_info)
if domain_info:
    print("=" * 14 , "Virtual Machine Info" , "=" * 15)
    print(f"\t VM: {domain_info['verbose_name']}")
    print(f"\t Power State: {power_state[domain_info['user_power_state']]}") #translating status code to "pretty name"
    print(f"\t vDisks: {domain_info['vdisks_count']}")
    print("-" * 19 , "vDisks Info" , "-" * 19)
    get_disk_info(domain_all_content)

    
read_input=input("Enter disk edit mode Y / N: ")
menu_choice=str(read_input)
if menu_choice == "Y" or menu_choice == "y":
    print("\033[H\033[2J", end="") # clears cmd screen, but saves scrollback buffer
    print("Select option: \n 1) Delete vDisk by UUID \n 2) Delete ALL vDisks on selected Virtual Machine \n 3) Create Disk \n 4) Prepare VMs for Courses™")
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
        print("All attached vDisks has been deleted!")
    if menu_choice == 3:
        read_input=input("Enter disk size (GB): ")
        menu_choice=str(read_input)
        create_and_attach_disk(vm_uuids , data_pool_uuid, menu_choice, "falloc")
    if menu_choice == 4:
       print("#" * 5 , "Preparing VMs for Courses" , "#" * 5) 
       with open(VM_UUID_relative_path, "r") as f:
            for x in f: # only for removing disks
               
                domain_uuid = x.strip('\n')
                domain_info = get_domain_info(domain_uuid)
                domain_all_content = get_domain_all_content(domain_uuid)

                if domain_info:
                    print("=" * 14 , "Virtual Machine Info" , "=" * 15)
                    print(f"\t VM: {domain_info['verbose_name']}")
                    print(f"\t Power State: {power_state[domain_info['user_power_state']]}") #translating status code to "pretty name"
                    print(f"\t vDisks: {domain_info['vdisks_count']}")
                    print("-" * 19 , "vDisks Info" , "-" * 19)
                    get_disk_info(domain_all_content)
                    disk_uuids = get_disk_uuids(domain_all_content)
                    for y in disk_uuids:
                        delete_disk(y)
                    print("All attached vDisks has been deleted!")
       with open(VM_UUID_relative_path, "r") as f:
            for z in f: # only for creating disks
                domain_uuid = z.strip('\n')
                domain_info = get_domain_info(domain_uuid)
                domain_all_content = get_domain_all_content(domain_uuid)
                
                if domain_info:
                    create_and_attach_disk(domain_uuid , data_pool_uuid, 10, "falloc")
                    create_and_attach_disk(domain_uuid , data_pool_uuid, 20, "falloc")
                    create_and_attach_disk(domain_uuid , data_pool_uuid, 20, "falloc")
    
            





print("Exiting Utility..")
sys.exit()


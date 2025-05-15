import sys
import os

from config_data_import import *

from cluster_api import *
from domain_api import * 

power_state = ["Unknown" , "Off" , "Suspend" , "On"] #3 - on; 2 - suspend; 1 - off; 0 - unknown

#config.txt in the same directory with main.py
base_dir = os.getcwd() # Use the current directory as fallback
config_relative_path = os.path.join(base_dir, 'config.txt')

#config_relative_path = "Y:\\py\\SpaceVM_VM_Utility\\config.txt" 

def config_edit():
    read_input=input("Create new config file? (Y / N): ") 
    menu_choice=str(read_input)
    if menu_choice == "Y" or menu_choice == "y":
        base_url = input("Type SpaceVM Controller IP: ")
        api_key = input("Type your API Key: ")
        data_pool_uuid = input("Type Data pool uuid you wish to use: ")
        lines = [base_url, api_key, data_pool_uuid]
        with open(config_relative_path, "w+") as file:
            for line in lines:
                file.write(line + '\n')
               
        print("Type VM-UUID (input ENTER to stop)")
        with open(config_relative_path, "a") as file: #appends new content at the end without modifying the existing data
            vm_input="test"
            while (vm_input != ""):
                vm_input = input(">> ")
                file.write(vm_input + '\n') 
            print("UUIDs has been written in config")
            print("\nConfiguration completed!")
if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: #check if file exists and not empty
    pass #do nothing
else:
    print("Config file was not found or empty.. ")
    config_edit()

#importing API-KEY / IP / DATA POOL UUID from config
threelines = import_threelines(config_relative_path)
print(f"3 lines: {threelines}")
base_url=threelines[0]
api_key=threelines[1]
data_pool_uuid=threelines[2]


'''
with open(config_relative_path, "r") as f:
    all_lines = f.readlines()  
    base_url = all_lines[0].strip('\n')
    api_key = "jwt " + all_lines[1].strip('\n') #actual format for api_key. That was realy obvious DACOM >:C
    data_pool_uuid = all_lines[2].strip('\n')
'''

#importing VM-UUIDs
vm_uuids = import_vm_uuid(config_relative_path)
print(f"vm uuids: {vm_uuids}")

#so-called INT MAIN
menu_choice=0
while(menu_choice != ""):    #main menu loop
    read_input=input("\nUitility Main Menu: \n1) Manage utility config \n2) Enter disk edit mode \n3) Show breif cluster overview \n4) Show VM info \n>>> ")
    menu_choice=str(read_input)

    if menu_choice == "1":
        print("\033[H\033[2J", end="") # clears cmd screen, but saves scrollback buffer
        print("1) Show current configuration \n2) Change configuraion")
        read_input=input(">> ")
        menu_choice=int(read_input)
        if menu_choice == 1:
            print("Current configuration:\n")
            with open(config_relative_path, "r") as f:
                print(f.read())
        if menu_choice == 2:
            config_edit()
    if menu_choice == "2":
        print("\033[H\033[2J", end="")
        print("Select option: \n 1) Delete vDisk by UUID \n 2) Delete ALL vDisks on selected Virtual Machine \n 3) Create Disk \n 4) Prepare VMs for Courses™")
        read_input=input(">> ")
        menu_choice=int(read_input)
        if menu_choice == 1:
            read_input=input("Input vDisk uuid to delete: ")
            vdisk_uuid=str(read_input)
            delete_disk(base_url , api_key , vdisk_uuid)      
        if menu_choice == 2:
            print(vm_uuids)
            select_uuids=int(input("Select VM to delete disks from. \n Type VM uuid index number (from list above) to select: ")) - 1
            domain_all_content = get_domain_all_content(base_url , api_key , vm_uuids[select_uuids])
            disk_uuids = get_disk_uuids(base_url , api_key , domain_all_content)
            for x in disk_uuids:
                delete_disk(base_url , api_key , x)
            print("All attached vDisks has been deleted!")
        if menu_choice == 3:
            vdisk_size=str(input("Enter disk size (GB): "))
            print(vm_uuids)
            select_uuids=int(input("Select VM to attach new disk. \n Type VM uuid index number (from list above) to select: ")) - 1
            create_and_attach_disk(vm_uuids[select_uuids] , data_pool_uuid, vdisk_size, "falloc")
        if menu_choice == 4:
            print("#" * 5 , "Preparing VMs for Courses" , "#" * 5) 
            for x in vm_uuids: # only for removing disks
                domain_uuid = x.strip('\n')
                domain_info = get_domain_info(base_url , api_key , domain_uuid)
                domain_all_content = get_domain_all_content(base_url , api_key , domain_uuid)
                if domain_info:
                    print("=" * 14 , "Virtual Machine Info" , "=" * 15)
                    print(f"\t VM: {domain_info['verbose_name']}")
                    print(f"\t Power State: {power_state[domain_info['user_power_state']]}") #translating status code to "pretty name"
                    print(f"\t vDisks: {domain_info['vdisks_count']}")
                    print("-" * 19 , "vDisks Info" , "-" * 19)
                    get_disk_info(domain_all_content)
                    disk_uuids = get_disk_uuids(base_url , api_key , domain_all_content)
                    for y in disk_uuids:
                        delete_disk(base_url , api_key , y)
                    print("All attached vDisks has been deleted!")
            for z in vm_uuids: # only for creating disks
                domain_uuid = z.strip('\n')
                domain_info = get_domain_info(base_url , api_key , domain_uuid)
                domain_all_content = get_domain_all_content(base_url , api_key , domain_uuid)
                if domain_info:
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 10, "falloc")
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 20, "falloc")
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 20, "falloc")
    
    if menu_choice == "3":
        cluster_info(base_url , api_key)
    
    if menu_choice == "4":
        print("\033[H\033[2J", end="")
        for x in vm_uuids:
            vm_info(base_url , api_key , x)


print("Exiting Utility..")
sys.exit()






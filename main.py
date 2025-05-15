import os
from config_data_import import *
from cluster_api import *
from domain_api import * 
from data_pools_api import *

#config.txt in the same directory with main.py
config_relative_path = os.path.join(os.getcwd() , 'config.txt')
print(config_relative_path)
#check if config exists and not empty            
if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: 
    pass #do nothing
else:
    print("Config file was not found or empty.. ")
    config_edit(config_relative_path)

#importing API-KEY / IP / DATA POOL UUID / VM-UUIDs from config
#base_url=threelines[0]  api_key=threelines[1]   data_pool_uuid=threelines[2]
base_url, api_key, data_pool_uuid = import_threelines(config_relative_path)
vm_uuids = import_vm_uuid(config_relative_path)

menu_choice=0 
while(menu_choice != ""):    #main menu loop
    print("\nUitility Main Menu:")
    print("1) Manage utility config")
    print("2) Enter disk edit mode")
    print("3) Show breif cluster overview")
    print("4) Show VM info")
    print("5) Show data pools")
    print("6) Show VMs Name / UUID")
    menu_choice=str(input("\n>>> "))

    if menu_choice == "1":
        print("\033[H\033[2J", end="") # clears cmd screen, but saves scrollback buffer
        print("1) Show current configuration \n2) Change configuraion")
        sub_choice=str(input("\n>>> "))

        if sub_choice == "1":
            print("Current configuration:\n")
            with open(config_relative_path, "r") as f:
                print(f.read())
        if sub_choice == "2":
            config_edit(config_relative_path)

    if menu_choice == "2":
        print("\033[H\033[2J", end="")
        print("Select option: \n 1) Delete vDisk by UUID \n 2) Delete ALL vDisks on selected Virtual Machine \n 3) Create Disk \n 4) Prepare VMs for Courses™")
        sub_choice=str(input("\n>>> "))
        if sub_choice == "1":
            read_input=input("Input vDisk uuid to delete: ")
            vdisk_uuid=str(read_input)
            delete_disk(base_url , api_key , vdisk_uuid)
        if sub_choice == "2":
            print(vm_uuids)
            select_uuids=int(input("Select VM to delete disks from. \n Type VM uuid index number (from list above) to select: ")) - 1
            domain_all_content = get_domain_all_content(base_url , api_key , vm_uuids[select_uuids])
            disk_uuids = get_disk_uuids(base_url , api_key , domain_all_content)
            for x in disk_uuids:
                delete_disk(base_url , api_key , x)
            print("All attached vDisks has been deleted!")
        if sub_choice == "3":
            vdisk_size=str(input("Enter disk size (GB): "))
            print(vm_uuids)
            select_uuids=int(input("Select VM to attach new disk. \n Type VM uuid index number (from list above) to select: ")) - 1
            create_and_attach_disk(vm_uuids[select_uuids] , data_pool_uuid, vdisk_size, "falloc")
            
        if sub_choice == "4":
            print("#" * 5 , "Preparing VMs for Courses" , "#" * 5) 
            for x in vm_uuids: # only for removing disks
                domain_uuid = x.strip('\n')
                domain_info = get_domain_info(base_url , api_key , domain_uuid)
                domain_all_content = get_domain_all_content(base_url , api_key , domain_uuid)
                vm_info(base_url , api_key , domain_uuid)
                if domain_info:
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
    if menu_choice == "5":
        data_pools(base_url , api_key)
    if menu_choice == "6":
        vm_info_short(base_url , api_key)
print("Exiting Utility..")
import os
from config_data_import import *
from cluster_api import *
from domain_api import * 
from data_pools_api import *
from disk_edit_mode import *

config_relative_path = os.path.join(os.getcwd() , 'config.txt')  #config.txt in the same directory with main.py      
if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: #check if config exists and not empty   
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
    print("\n***    Uitility Main Menu:     ***\n")
    print("1) Manage utility config")
    print("2) Enter disk edit mode")
    print("3) Show breif cluster overview")
    print("4) Show VM info")
    print("5) Show data pools")
    print("6) Show VMs Name / UUID")
    print("\nENTER - exit Utility ")
    menu_choice=str(input("\n>>> "))
    if menu_choice == "1":
        config_menu(config_relative_path)
    if menu_choice == "2":
        disk_edit_mode(base_url , api_key , data_pool_uuid , vm_uuids)
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
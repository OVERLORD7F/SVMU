import os
from config_data_import import *
from cluster_api import *
from domain_api import * 
from data_pools_api import *
from disk_edit_mode import *
from rich import print
from rich.panel import Panel
from rich.console import Console , Align

config_relative_path = os.path.join(os.getcwd() , 'config.txt')  #config.txt in the same directory with main.py      
if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: #check if config exists and not empty   
    pass #do nothing
else:
    console.print("[yellow bold italic]Config file was not found or empty.. ")
    config_edit(config_relative_path)

#importing API-KEY / IP / DATA POOL UUID / VM-UUIDs from config
#base_url=threelines[0]  api_key=threelines[1]   data_pool_uuid=threelines[2]
base_url, api_key, data_pool_uuid = import_threelines(config_relative_path)
vm_uuids = import_vm_uuid(config_relative_path)

menu_choice=0
menu_options="[gold bold][1] [grey53 italic]Manage utility config\n[/grey53 italic] \
\n[gold bold][2] [grey53 italic]Enter disk edit mode[/grey53 italic]\n \
\n[gold bold][3] [grey53 italic]Show breif cluster overview[/grey53 italic]\n \
\n[gold bold][4] [grey53 italic]Show VM info \n    (for selected VMs in config)[/grey53 italic]\n \
\n[gold bold][5] [grey53 italic]Show data pools[/grey53 italic]\n \
\n[gold bold][6] [grey53 italic]Show VMs Name / UUID[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - exit Utility"
menu_options=Align.center(menu_options, vertical="middle")
menu_subtitle = "[blue bold][link=https://github.com/OVERLORD7F/SpaceVM_VM_Utility]:wrench: Project_GitHub[/link] [yellow]| [magenta bold][link=https://spacevm.ru/docs/]:books: SpaceVM_Docs[/link] [yellow]| [red bold][link=https://comptek.ru]:briefcase: Comptek[/link]"
console = Console()
os.system('cls' if os.name=='nt' else 'clear') 
while(menu_choice != ""):    #main menu loop
    console.print(Panel(menu_options, 
title="[bold magenta]SpaceVM Utility - Main Menu" , subtitle = menu_subtitle, subtitle_align="right" , style="yellow" , width=150 , padding = 2))
    menu_choice=str(input("\n>>> "))
    if menu_choice == "1":
        config_menu(config_relative_path)
    if menu_choice == "2":
        disk_edit_mode(base_url , api_key , data_pool_uuid , vm_uuids)
    if menu_choice == "3":
        cluster_info(base_url , api_key)
    if menu_choice == "4":
        os.system('cls' if os.name=='nt' else 'clear') 
        for x in vm_uuids:
            vm_info(base_url , api_key , x)
        Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    if menu_choice == "5":
        data_pools(base_url , api_key)
    if menu_choice == "6":
        vm_info_short(base_url , api_key)
    if menu_choice == "7":
        test(base_url, api_key)
    os.system('cls' if os.name=='nt' else 'clear')  #clears screen before looping back to main menu     
console.print("[red bold]Exiting Utility ")

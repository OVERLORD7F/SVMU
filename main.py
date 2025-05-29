import os
from config_data_import import *
from cluster_api import *
from domain_api import * 
from data_pools_api import *
from disk_edit_mode import *
from rich.panel import Panel
from rich.console import Console , Align

config_relative_path = os.path.join(os.getcwd() , 'SpaceVM_Utility.conf')  #config in the same directory with main.py

print("Reading config from:", os.path.abspath(config_relative_path))
if not os.path.exists(config_relative_path):
    print(f"Config file not found: {config_relative_path}")

menu_choice=0
console = Console()
os.system('cls' if os.name=='nt' else 'clear') 
while(menu_choice != ""):    #main menu loop
    check_config(config_relative_path)
    base_url, api_key, data_pool_uuid, data_pool_name, vm_uuids, vm_names, disk1_size, disk2_size, disk3_size = config_import(config_relative_path) #importing API-KEY / IP / DATA POOL UUID / VM-UUIDs from config
    menu_options=f"[gold bold][1] [grey53 italic]Manage utility config\n[/grey53 italic] \
\n[gold bold][2] [grey53 italic]Enter disk edit mode[/grey53 italic]\n \
\n[gold bold][3] [grey53 italic]Show breif cluster overview[/grey53 italic]\n \
\n[gold bold][4] [grey53 italic]Show VM info \n    (for selected VMs in config)[/grey53 italic]\n \
\n[gold bold][5] [grey53 italic]Show data pools[/grey53 italic]\n \
\n[gold bold][6] [grey53 italic]Show VMs Name / UUID[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - exit Utility[/]\n\n \
[underline bold grey53]Currently imported config:[/]\n \
[bold grey53]Connected to Controller: [bright_yellow]{base_url}[/]\n Selected Data Pool: [bright_yellow]{data_pool_name}[/]\n Selected VMs:\n [bright_yellow]{vm_names}"
    menu_options=Align.center(menu_options, vertical="middle")
    menu_subtitle = "[blue bold][link=https://github.com/OVERLORD7F/SpaceVM_VM_Utility]:wrench: Project_GitHub[/link] [yellow]| [magenta bold][link=https://spacevm.ru/docs/]:books: SpaceVM_Docs[/link] [yellow]| [red bold][link=https://comptek.ru]:briefcase: Comptek[/link]"
    console.print(Panel(menu_options, title="[bold magenta]SpaceVM Utility - Main Menu" , subtitle = menu_subtitle, subtitle_align="right" , style="yellow" , width=150 , padding = 2))
    menu_choice=str(input("\n>>> "))
    if menu_choice == "1":
        config_menu(base_url, api_key, config_relative_path)
    if menu_choice == "2":
        disk_edit_mode(base_url , api_key , data_pool_uuid , vm_uuids, disk1_size, disk2_size, disk3_size)
    if menu_choice == "3":
        cluster_info(base_url , api_key)
    if menu_choice == "4":
        os.system('cls' if os.name=='nt' else 'clear') 
        for x in vm_uuids:
            vm_info(base_url , api_key , x)
        Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    if menu_choice == "5":
        show_data_pools(base_url , api_key)
    if menu_choice == "6":
        vm_info_short(base_url , api_key)
    if menu_choice == "7":
        check_api_key(base_url, api_key)
    os.system('cls' if os.name=='nt' else 'clear')  #clears screen before looping back to main menu     
console.print("[red bold]Exiting Utility ")
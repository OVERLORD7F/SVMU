import os
from splash_screen import *
from config_data_import import *
from cluster_api import *
from domain_api import * 
from data_pools_api import *
from disk_edit_mode import *
from rich.panel import Panel
from rich.console import Console , Align
SVMU_ver="v0.4.4" # pls dont forget to change before uploading release (lol)

console = Console() # Initialize console and clear screen
os.system('cls' if os.name=='nt' else 'clear')
config_relative_path = get_default_config_path() # Get config path + necessery checks
skip_startup_splash = get_skip_startup_splash(config_relative_path) #check profile for skip startup. Profile is not imported at this point (!)
show_startup_logo(skip_startup_splash, SVMU_ver) #shows / skips startup splash (ASCII art)

menu_choice=0
while(menu_choice != ""):    #main menu loop
    profile_name = os.path.basename(os.path.splitext(config_relative_path)[0]) #converting full path to pretty file name
    skip_startup_splash, base_url, api_key, data_pool_uuid, data_pool_name, vm_uuids, vm_names, disk1_size, disk2_size, disk3_size, disk_interface, preallocation, iso_uuid, iso_name = config_import(config_relative_path) #importing API-KEY / IP / DATA POOL UUID / VM-UUIDs from config
    vm_pretty_names = ', '.join(vm_names)
    menu_options=f"[gold1 bold][1] [grey53 italic]Utiliy Configuration / Profiles\n[/grey53 italic] \
\n[gold1 bold][2] [grey53 italic]Enter disk edit mode[/grey53 italic]\n \
\n[gold1 bold][3] [grey53 italic]Show breif cluster overview[/grey53 italic]\n \
\n[gold1 bold][4] [grey53 italic]Enter VM menu[/grey53 italic]\n \
\n[gold1 bold][5] [grey53 italic]Show data pools[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - exit Utility[/]\n\n \
[underline bold grey53]Current profile:[/] [bold green]{profile_name}[/]\n \
[bold grey53]Connected to Controller: [bright_yellow]{base_url}[/]\n Selected Data Pool: [bright_yellow]{data_pool_name}[/]\n Selected VMs:\n [bright_yellow]{vm_pretty_names}[/]\n Auto-mount ISO: [bright_cyan]{iso_name}[/]"
    menu_options=Align.center(menu_options, vertical="middle")
    menu_subtitle = "[blue bold][link=https://github.com/OVERLORD7F/SVMU]:wrench: Project_GitHub[/link] [yellow]| [magenta bold][link=https://spacevm.ru/docs/]:books: SpaceVM_Docs[/link] [yellow]| [red bold][link=https://comptek.ru]:briefcase: Comptek[/link]"
    console.print(Panel(menu_options, title=f"[bold magenta]SpaceVM Utility {SVMU_ver} - Main Menu" , subtitle = menu_subtitle, subtitle_align="right" , style="yellow" , width=150 , padding = 2))
    menu_choice = console.input("[bold yellow]\n>>> [/]")
    
    if menu_choice == "1":
        new_profile, needs_reload = config_menu(base_url, api_key, config_relative_path)
        # If a new profile path was returned, switch to it
        if new_profile:
            config_relative_path = new_profile
            os.system('cls' if os.name=='nt' else 'clear')
            continue
        # If menu indicated that config changes require a reload, go back to main menu
        if needs_reload:
            os.system('cls' if os.name=='nt' else 'clear')
            continue
    if menu_choice == "2":
        disk_edit_mode(base_url , api_key , data_pool_uuid , vm_uuids, disk1_size, disk2_size, disk3_size, disk_interface, preallocation, iso_uuid)
        os.system('cls' if os.name=='nt' else 'clear')
    if menu_choice == "3":
        cluster_info(base_url , api_key)
        os.system('cls' if os.name=='nt' else 'clear')
    if menu_choice == "4":
        vm_menu(base_url , api_key, vm_uuids, config_relative_path)
        os.system('cls' if os.name=='nt' else 'clear')
    if menu_choice == "5":
        show_data_pools(base_url , api_key)
        os.system('cls' if os.name=='nt' else 'clear')     
console.print("[red bold]Exiting Utility ")

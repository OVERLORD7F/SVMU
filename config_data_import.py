import os
import subprocess
import configparser
from cluster_api import *
from domain_api import *
from data_pools_api import *
from rich import print
from rich.panel import Panel
from rich.console import Console , Align
from rich.prompt import Prompt
console = Console()

def config_menu(base_url, api_key, config_relative_path):
        cls()
        config_menu_options="[gold bold][0] [grey53 italic]Show example configuration\n[/]\
\n[gold bold][1] [grey53 italic]Show current configuration\n[/] \
\n[gold bold][2] [grey53 italic]Setup new config file[/]\n \
\n[gold bold][3] [grey53 italic]Change selected data pool[/]\n\
\n[gold bold][4] [grey53 italic]Change selected VMs[/]\n\
\n[gold bold][5] [grey53 italic]Change ISO UUID (auto-mount)[/]\n\
\n[gold bold][6] [grey53 italic]Skip start-up splash[/]\n\
\n\n[green_yellow bold]ENTER - return to Main Menu[/]"
        config_menu_options=Align.center(config_menu_options, vertical="middle")
        console = Console()
        console.print(Panel(config_menu_options, title="[gold bold]SpaceVM Utility - Utility Configuration" , border_style="magenta" , width=150 , padding = 2))
        sub_choice=str(input("\n>>> "))
        if sub_choice == "0":
            config_show_example()
        if sub_choice == "1":
            config_show(config_relative_path)
            config_menu(base_url, api_key, config_relative_path)
        if sub_choice == "2":
            config_edit(config_relative_path)
        if sub_choice == "3":
            change_data_pool(base_url, api_key, config_relative_path)
        if sub_choice == "4":
            change_vm_uuids(config_relative_path)
        if sub_choice == "5":
            change_iso_uuid(config_relative_path)
        if sub_choice == "6":
            change_startup_option(config_relative_path)

def config_show_example():
    conf_example= """
[General]
skip_startup_splash = no
#Master Controller IP of your cluster
#Has to be accessible for a machine, which will be executing this Utility
controller_ip = 10.20.30.44

#Integration API Key. how to get your key: 
# ( https://spacevm.ru/docs/latest/base/operator_guide/security/users/#_14 ) 
# do not specify JWT tag with your key! 
api_key = 


[Data_Pool]
#Data pool which will be used for utility operations
#(Targeted storage for new vDisks)
data_pool_uuid = 

[VM_List]
#Selected VMs which will be used for utility operations
#How to find UUID:
#List all available VMs in Utility Main Menu (Option 6)
#Use https://spacevm.ru/docs/latest/cli/space/vm/info/ or copy UUID from web panel

uuid_1 = 
uuid_2 = 

[VM_Options]
#Select interface which will be used in virtual disk creation.
#Available options: virtio / ide / scsi / sata
disk_interface = virtio

#Select allocation type for virtual disks
#Available options: none / falloc / full / metadata
preallocation = falloc

#Specify uuid of iso you wish to automatically mount to Virtual Machines during operations (Courses)
#This step is skipped if "none" provided
iso_uuid = none


[Courses-Space-VM]
#Set vDisk size for "Prepare VMs for Courses™" option
disk1 = 10
disk2 = 20
disk3 = 20
"""
    cls()
    console.rule(title = "Example config file", align="center", style="yellow")
    console.print(conf_example)
    console.rule(style="yellow")
    Prompt.ask("[green_yellow bold]ENTER - return to Utility Configuration.. :right_arrow_curving_down:")

def config_show(config_relative_path):

    cls()
    console.rule(title = "Current configuration" , align="center" , style="yellow")
    with open(config_relative_path, "r") as f:
        print(f.read())
    console.rule(style="yellow")
    Prompt.ask("[green_yellow bold]ENTER - return to Utility Configuration.. :right_arrow_curving_down:")

def config_import(config_relative_path):
    config = configparser.ConfigParser()
    config.read(config_relative_path)

    skip_startup_splash = config.get('General', 'skip_startup_splash')
    base_url = config.get('General', 'controller_ip')
    api_key = "jwt " + config.get('General', 'api_key') #That was realy obvious DACOM >:C
    data_pool_uuid = config.get('Data_Pool', 'data_pool_uuid')


    vm_list = []
    if 'VM_List' in config:
        for key, value in config['VM_List'].items():
            vm_list.append(value)
    
    #importing VM_Options
    if config.has_section('VM_Options'):
        iso_uuid = config.get('VM_Options' , 'iso_uuid')
        disk_interface = config.get('VM_Options' , 'disk_interface')    
        preallocation = config.get('VM_Options' , 'preallocation')
        iso_name=get_iso_name(base_url, api_key, iso_uuid)
    else:
        console.print("[bold yellow]Applying default values to Virtual Machine Options")
        iso_uuid = "none"
        disk_interface = "virtio" 
        preallocation = "falloc"
        iso_name= "none"
        config = configparser.ConfigParser() #writing default values to config
        config["VM_Options"] = {
            "disk_interface": "virtio",
            "preallocation": "falloc",
            "iso_uuid": "none",
        }        
        with open(config_relative_path, "a") as configfile: # appending to existing config file
            config.write(configfile) 

    #importing disk sizes for SpaceVM courses 
    if config.has_section('Courses-Space-VM'):
        disk1_size = config.get('Courses-Space-VM', 'disk1')
        disk2_size = config.get('Courses-Space-VM', 'disk2') 
        disk3_size = config.get('Courses-Space-VM', 'disk3')
    else:
        console.print("[bold yellow]Applying default values to Disk sizes for Courses")
        disk1_size, disk2_size, disk3_size = 10, 20, 20 #applying default values for courses
        config = configparser.ConfigParser() #writing default values to config
        config["Courses-Space-VM"] = {
            "disk1": 10,
            "disk2": 20,
            "disk3": 20,
        }
        with open(config_relative_path, "a") as configfile: # appending to existing config file
            config.write(configfile)        

    #get pretty name for selected data pool
    data_pool_name = get_data_pool_name(base_url , api_key , data_pool_uuid)
    #get pretty name for selected VMs
    vm_names=[]
    for x in vm_list:
        vm_names.append(get_vm_name(base_url, api_key, x))
    
    return skip_startup_splash, base_url, api_key, data_pool_uuid, data_pool_name, vm_list, vm_names, disk1_size, disk2_size, disk3_size, disk_interface, preallocation, iso_uuid, iso_name

def change_startup_option(config_relative_path):
    cls()
    #console.print("[yellow bold]Skip start-up splash ?")
    new_value = Prompt.ask("[yellow bold]Skip start-up splash ?[/]", choices=["Y", "N"], default="N", case_sensitive=False)
    if new_value == "Y" or new_value == "y":
        startup_option = "yes"
    if new_value == "N" or new_value == "n":
        startup_option = "no"
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('General'):
        config.set('General', 'skip_startup_splash', startup_option)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
        console.print(f"[green bold]Option set to: {new_value}")
    else:
        console.print("[red bold]No section 'General' in config file")

def change_data_pool(base_url, api_key, config_relative_path): #change selected data pool in config
    cls()
    show_data_pools(base_url, api_key)
    new_data_pool_uuid = input("Type NEW Data Pool UUID: ")
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('Data_Pool'):
        config.set('Data_Pool', 'data_pool_uuid', new_data_pool_uuid)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
    else:
        print("No 'Data_Pool' section in config file..")
    config_show(config_relative_path)

def change_iso_uuid(config_relative_path):
    cls()
    new_iso_uuid = input("Type ISO UUID: ")
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    if config.has_section('VM_Options'):
        config.set('VM_Options', 'iso_uuid', new_iso_uuid)
        with open(config_relative_path, 'w') as config_file:
            config.write(config_file)
    else:
        print("No 'VM_Options' section in config file..")
    config_show(config_relative_path)

def change_vm_uuids(config_relative_path): #change selected VM uuids in config
    config = configparser.ConfigParser()
    config.read(config_relative_path)
    # Remove old VM_List section if it exists, then add a fresh one
    if config.has_section('VM_List'):
        config.remove_section('VM_List')
    config.add_section('VM_List')
    cls()
    console.print("[yellow bold]Type new VM UUIDs one by one (input ENTER to stop):")
    x = 0
    while True:
        vm_input = input(">> ")
        if not vm_input:
            break
        x += 1
        config.set('VM_List', f'uuid_{x}', vm_input)

    with open(config_relative_path, 'w') as configfile:
        config.write(configfile)

    console.print("[green bold]VM UUIDs have been updated in config :pencil:")
    Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
    config_show(config_relative_path)


def config_edit(config_relative_path):
    read_input = Prompt.ask("[bold yellow]Create new config file?[/]", choices=["Y", "N"], default="N", case_sensitive=False)
    menu_choice = str(read_input)
    if menu_choice == "Y" or menu_choice == "y":
        base_url = input("Type SpaceVM Controller IP: ")
        while check_ping(base_url) != True:
            base_url = console.input("[bold red]No response.\nCheck and type SpaceVM Controller IP again: [/]")

        api_key = input("Type your API Key: ")
        while check_api_key(base_url, "jwt " + api_key) != 200:
            api_key = console.input("[bold red]Check and type SpaceVM Controller API Key again: [/]")
        show_data_pools(base_url, "jwt " + api_key)
        data_pool_uuid = input("Type Data Pool UUID you wish to use: ")

        config = configparser.ConfigParser()
        config["General"] = {
            "controller_ip": base_url,
            "api_key": api_key,
            "skip_startup_splash": "no",
        }
        config["Data_Pool"] = {"data_pool_uuid": data_pool_uuid}

        #disk_interface=input("Specify preffered disk interface (virtio / ide / scsi / sata): ")
        #preallocation=input("Specify allocation type for virtual disks (none / falloc / full / metadata): ")
        #iso_uuid=input("Specify ISO uuid you wish to auto-mount during operations(none - skip this step): ")
        #config["VM_Options"] = {
        #    "disk_interface": disk_interface,
        #    "preallocation": preallocation,
        #    "iso_uuid": iso_uuid
        #}

        with open(config_relative_path, "w") as configfile: #writing everything from above to config file
            config.write(configfile)

        print("Type VM UUIDs one by one (input ENTER to stop)")
        with open(config_relative_path, "a") as file:
            file.write("[VM_List]\n") #manually writing section for VMs
            vm_input = []
            x = 0
            while vm_input != "":
                vm_input = input(">> ")
                if vm_input:
                    x += 1
                    file.write(f"uuid_{x} = {vm_input}\n")

        console.print("[green bold]VM UUIDs have been written in config :pencil:")
        console.print("[green bold]Configuration completed ! :white_check_mark:")
        Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
        cls()

def check_config(config_relative_path):
    if os.path.exists(config_relative_path) and os.path.getsize(config_relative_path) > 0: #check if config exists and not empty   
        pass #do nothing
    else:
        console.print("[yellow bold]Config file was not found or empty.. ")
        config_edit(config_relative_path)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def check_ping(base_url):
    DNULL = open(os.devnull, 'w')
    if os.name == 'nt':
        status = subprocess.call(["ping","-n","1",base_url],stdout = DNULL)
    else:
        status = subprocess.call(["ping","-c","1",base_url],stdout = DNULL)
        
    if status == 0:
        return True
    else:
        return False
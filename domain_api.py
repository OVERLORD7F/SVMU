# functions for working with domain-api
import requests
import secrets #for generating unique names
import os
import configparser
from config_data_import import *
from rich.console import Console , Align
from rich.columns import Columns
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console() #necessary for pretty menus & output
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
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Deleting vDisk...", total=None)
        response = requests.post(url , headers=headers, json=payload)
        progress.remove_task(task)
    if response.status_code == 200:
        console.print(f"[grey53 italic]{vdisk_uuid}[/] :wastebasket:")
        return True
    else:
        print(f"ERROR deleting disk {vdisk_uuid} :\n {response.status_code} - {response.text}")
        return False


def get_disk_info(domain_all_content):
    console = Console()
    # check for "vdisks" field in recieved json response
    if 'vdisks' not in domain_all_content:
        print("No 'vdisks' field in recieved data")
        return
    # get vdisk list
    disks = domain_all_content['vdisks']
    # check for disks
    if not disks:
        console.print("[bold yellow]No 'disks' field in recieved data. \nProbably VM does not have any attached disks?")
        return
    
    disk_info_renderables = []
    # Print info for each disk
    for disk in disks:
        # check for required fields
        if 'id' in disk and 'verbose_name' in disk and 'size' in disk:
            output_string = (
                f"[bold]Name:[/] {disk['verbose_name']}\n"
                f"[bold]UUID:[/] [italic]{disk['id']}[/italic]\n"
                f"[bold]Size:[/] {disk['size']} GB")
            disk_info_renderables.append(Panel(output_string, expand=False, border_style="magenta"))
        else:
            print("ERROR: failed to retrieve vdisk data.")

    console.print(Columns(disk_info_renderables))

def get_cdrom_uuid(domain_all_content):
    if 'cdroms' in domain_all_content:
        cdrom_ids = [item['id'] for item in domain_all_content['cdroms']]
        #print("CD-ROM UUIDs:")
        for cdrom_id in cdrom_ids:
            #print(cdrom_id)
            return (cdrom_id)
    else:
        console.print("[bold yellow]No 'cdroms' field in recieved data. \nProbably VM does not have any CD-ROMs?")

def get_iso_name(base_url, api_key, iso_uuid): 
    url = f"http://{base_url}//api/iso/{iso_uuid}/"
    response = requests.get(url, headers={'Authorization': api_key})
    if response.status_code == 200:
        iso_name = response.json()
        return (f"{iso_name['filename']}")


def get_vm_name(base_url, api_key, vm_uuids):
    console = Console()
    url = f"http://{base_url}//api/domains/{vm_uuids}/"
    response = requests.get(url, headers={'Authorization': api_key})
    if response.status_code == 200:
        vm_name = response.json()
        return (f"{vm_name['verbose_name']}")


def vm_info(base_url, api_key, vm_uuids):
    domain_info = get_domain_info(base_url, api_key, vm_uuids)
    domain_all_content = get_domain_all_content(base_url, api_key, vm_uuids)
    if domain_info:
        console = Console()
        vm_info_lines = f"[bold]Power State:[/] [bold red]{power_state[domain_info['user_power_state']]}[/bold red] \n[bold]vDisks:[/] {domain_info['vdisks_count']}"
        vm_info_renderable = Panel(vm_info_lines, title=f"[bold magenta]{domain_info['verbose_name']}" , expand=False , border_style="yellow")
        vm_info_renderable=Align.center(vm_info_renderable, vertical="middle")
        print("\n")
        console.rule(style="yellow")
        console.print(vm_info_renderable)
        console.rule(title = "[bold yellow]vDisks Info" , style="grey53" , align="center")
        get_disk_info(domain_all_content)
        #console.rule(title = "[bold yellow]CD-ROM UUIDs" , style="grey53" , align="center")
        #print(get_cdrom_uuid(domain_all_content))
        console.rule(style="yellow")

def vm_info_short(base_url, api_key):
    url = f"http://{base_url}/api/domains/"
    response = requests.get(url, headers={'Authorization': api_key})
    if response.status_code == 200:
        vm_info_short = response.json()
        results_vm_info_short = vm_info_short['results']
        tag = vm_info_short['results'][0]['tags'][0]
        print(tag)
        #print(results_vm_info_short)
        os.system('cls' if os.name=='nt' else 'clear')
        console.print(Align.center(Panel(f"[bold magenta]Short VM overview | Total: {vm_info_short['count']}", expand=True , border_style="yellow") , vertical="middle"))
        console.rule(style="grey53")
        output_renderables = []
        for x in results_vm_info_short:
            output_string = f"VM: [bold]{x['verbose_name']}" + f"\nUUID: [italic]{x['id']}"
            output_renderable = Panel(output_string, expand=False, border_style="magenta")
            output_renderables.append(output_renderable) #adds current renderable
        console.print(Columns(output_renderables)) #print renderables by columns
    else:
        print(f"Failed to retrieve data {response.status_code}")
    console.rule(style="grey53")    
    Prompt.ask("[green_yellow bold]ENTER - return to Main Menu.... :right_arrow_curving_down:")
    os.system('cls' if os.name=='nt' else 'clear')  


def create_and_attach_disk(base_url , api_key , vm_id, data_pool_uuid, vdisk_size, disk_interface, preallocation):
    domain_name=get_domain_info(base_url , api_key , vm_id)
    disk_name=domain_name["verbose_name"] + "_" + secrets.token_hex(5) #generates unique hex id. this method can generate ~million unique ids
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
        "target_bus": disk_interface, #"virtio"
    }
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Creating and attaching vDisk...", total=None)
        response = requests.post(url , headers=headers, json=payload)
        progress.remove_task(task)
    if response.status_code == 200:
        console.print(f"[grey53 italic]{disk_name} ({vdisk_size}GB)[/] :white_check_mark:")
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
            pass

def select_vm_by_tags(base_url, api_key, config_relative_path):
    url = f"http://{base_url}/api/domains/"
    response = requests.get(url, headers={'Authorization': api_key})
    if response.status_code == 200:
        verbose_name_input = input("Specify tag: ")
        output_renderables = []
        vm_info_short = response.json()
        y= vm_info_short 
        vm_id_list = []
        for y in vm_info_short['results']:
            for x in y['tags']:
                if x['verbose_name'] == verbose_name_input:
                    vm_id_list.append(y['id'])
                    output_string = f"VM: [bold]{y['verbose_name']} [bold yellow]#{x['verbose_name']}[/]" + f"\nUUID: [italic]{y['id']}"
                    output_renderable = Panel(output_string, expand=False, border_style="magenta")
                    output_renderables.append(output_renderable) #adds current renderable
        console.print(Columns(output_renderables)) #print renderables by columns
    else:
        print(f"Failed to retrieve data {response.status_code}")
    console.rule(style="grey53")

    if vm_id_list: # promt to write found VM UUIDs to config
        write_to_config = Confirm.ask("[bold yellow]Write these VM UUIDs to config file?")
        if write_to_config:
            config = configparser.ConfigParser()
            config.read(config_relative_path)
            # Remove old VM_List section if it exists, then add a fresh one
            if config.has_section('VM_List'):
                config.remove_section('VM_List')
            config.add_section('VM_List')
            for idx, vm_id in enumerate(vm_id_list, 1):
                config.set('VM_List', f'uuid_{idx}', vm_id)
            with open(config_relative_path, 'w') as configfile:
                config.write(configfile)
            console.print(f"[green bold]VM UUIDs have been written in config :pencil:")  

    Prompt.ask("[green_yellow bold]ENTER - return to Main Menu.... :right_arrow_curving_down:")
    os.system('cls' if os.name=='nt' else 'clear')
    return(vm_id_list)


def attach_iso(base_url, api_key, vm_id, iso_uuid):
    url = f"http://{base_url}/api/domains/{vm_id}/attach-iso/"
    domain_all_content = get_domain_all_content(base_url, api_key, vm_id)
    cdrom_uuid=get_cdrom_uuid(domain_all_content)
    headers={
        "Authorization" : api_key,
        "Content-Type" : "application/json",
    }
    payload= {
        "iso": iso_uuid,
        "cdrom": cdrom_uuid
    } 

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Attaching selected ISO to VM...", total=None)
        response = requests.post(url , headers=headers, json=payload)
        progress.remove_task(task)
    if response.status_code == 200:
        iso_name = get_iso_name(base_url, api_key, iso_uuid)
        console.print(f"[grey53 italic]ISO {iso_name} attached[/] :white_check_mark:")
        return True
    else:
        console.print(f"[bold yellow]ERROR {response.status_code} attaching ISO \nProbably VM does not have any CD-ROMs?")
        return False




























def vm_menu(base_url, api_key, vm_uuids, config_relative_path):
        os.system('cls' if os.name=='nt' else 'clear') 
        config_menu_options="[gold bold][1] [grey53 italic]Show VM info \n    (for selected VMs in config)[/grey53 italic]\n \
\n[gold bold][2] [grey53 italic]Show VMs Name / UUID[/grey53 italic]\n \
\n[gold bold][3] [grey53 italic]Select VMs by tag / UUID[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - return to Main Menu[/]"
        config_menu_options=Align.center(config_menu_options, vertical="middle")
        console = Console()
        console.print(Panel(config_menu_options, title="[gold bold]Show VM info" , border_style="magenta" , width=150 , padding = 2))
        sub_choice=str(input("\n>>> "))
        if sub_choice == "1":
            os.system('cls' if os.name=='nt' else 'clear') 
            for x in vm_uuids:
                vm_info(base_url , api_key , x)
            Prompt.ask("[green_yellow bold]Press ENTER to proceed.. :right_arrow_curving_down:")
        if sub_choice == "2":
            os.system('cls' if os.name=='nt' else 'clear') 
            vm_info_short(base_url , api_key)
        if sub_choice == "3":
            os.system('cls' if os.name=='nt' else 'clear') 
            select_vm_by_tags(base_url , api_key, config_relative_path)
import os
import requests
from domain_api import *
from rich.prompt import Prompt
from rich.console import Console , Align

def disk_edit_mode(base_url , api_key , data_pool_uuid , vm_uuids): 
        os.system('cls' if os.name=='nt' else 'clear')
        diks_edit_menu_options="[gold bold][1] [grey53 italic]Delete vDisk by UUID\n[/grey53 italic] \
\n[gold bold][2] [grey53 italic]Delete ALL vDisks on selected Virtual Machine[/grey53 italic]\n \
\n[gold bold][3] [grey53 italic]Create Disk[/grey53 italic]\n \
\n[gold bold][4] [grey53 italic]Prepare VMs for Courses™[/grey53 italic]\n \
\n\n[green_yellow bold]ENTER - return to Main Menu"
        diks_edit_menu_options = Align.center(diks_edit_menu_options, vertical="middle")
        console = Console()
        console.print(Panel(diks_edit_menu_options, title="[bold red]Disk Edit Mode" , border_style="magenta" , width=150 , padding = 2))
        sub_choice=str(input("\n>>> "))
        if sub_choice == "1":
            read_input=input("Input vDisk uuid to delete: ")
            vdisk_uuid=str(read_input)
            delete_disk(base_url , api_key , vdisk_uuid)
        
        if sub_choice == "2":
            print(vm_uuids)
            select_uuids=int(input("Select VM to delete disks from. \n Type VM uuid index number (from list above) to select: ")) - 1
            vm_check_power(base_url , api_key , vm_uuids[select_uuids]) #power on check
            domain_all_content = get_domain_all_content(base_url , api_key , vm_uuids[select_uuids])
            disk_uuids = get_disk_uuids(base_url , api_key , domain_all_content)
            for x in disk_uuids:
                delete_disk(base_url , api_key , x)
            console.print("[bold red]All attached vDisks has been deleted!")
        
        if sub_choice == "3":
            vdisk_size=str(input("Enter disk size (GB): "))
            print(vm_uuids)
            select_uuids=int(input("Select VM to attach new disk. \n Type VM uuid index number (from list above) to select: ")) - 1
            print(f"{vm_uuids[select_uuids]} - {data_pool_uuid} - {vdisk_size} ")
            create_and_attach_disk(base_url , api_key , vm_uuids[select_uuids] , data_pool_uuid , vdisk_size , "falloc")
            
        if sub_choice == "4":
            os.system('cls' if os.name=='nt' else 'clear')
            console.rule(title="[bold magenta]Preparing VMs for Courses" , align="center" , style="grey53" , characters = "=")
            for y in vm_uuids: #power-on check
                domain_uuid = y.strip('\n')
                vm_check_power(base_url , api_key , domain_uuid)
            for x in vm_uuids: # only for removing disks
                domain_uuid = x.strip('\n')
                domain_info = get_domain_info(base_url , api_key , domain_uuid)
                domain_all_content = get_domain_all_content(base_url , api_key , domain_uuid)
                vm_info(base_url , api_key , domain_uuid)
                if domain_info:
                    disk_uuids = get_disk_uuids(base_url , api_key , domain_all_content)
                    for y in disk_uuids:
                        delete_disk(base_url , api_key , y)
                    console.print("[bold red]All attached vDisks has been deleted!")
            for z in vm_uuids: # only for creating disks
                domain_uuid = z.strip('\n')
                console.print(f"\n[bold underline yellow]Creating and attaching disk to VM {domain_uuid}")
                domain_info = get_domain_info(base_url , api_key , domain_uuid)
                domain_all_content = get_domain_all_content(base_url , api_key , domain_uuid)
                if domain_info:
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 10, "falloc")
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 20, "falloc")
                    create_and_attach_disk(base_url , api_key , domain_uuid , data_pool_uuid, 20, "falloc")
            console.print("[bold green]\nDone. Happy virtualization :thumbs_up::thumbs_up:")
            Prompt.ask("[green_yellow bold]ENTER - return to Main Menu.. :right_arrow_curving_down:")
        os.system('cls' if os.name=='nt' else 'clear')
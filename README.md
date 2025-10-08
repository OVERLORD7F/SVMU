# SpaceVM Utility (SVMU)
Utility for managing Virtual Machines in SpaceVM.

Written in python, uses [SpaceVM API](https://spacevm.ru/docs/6.5/api/) to collect and manage existing Virtual Machines in your SpaceVM cluster.

<p align="center">
<img src=assets/images/svmu-main-menu.png>
</p>

>[!NOTE]
>_This utility is focused on managing virtual disks_<br>
>_Works with SpaceVM 6.5.5 / 6.5.6 / 6.5.7_ <br>
> [:file_folder:_Repo Mirror Available Here_:clipboard:](https://gt.7fproject.com/OVERLORD/SVMU)

# Requirements
- Fully setup SpaceVM cluster with VMs
- Your SpaceVM cluster should be reachable by Utility (e.g. in LAN)
- Obtain your [API Key](https://spacevm.ru/docs/latest/base/operator_guide/security/users/#_14)
>[!WARNING]
> Utility tested only on Windows 10
>
> [New Microsoft Terminal](https://github.com/microsoft/terminal) is highly recommended for Windows 10 (correct colors, menus, etc)

# Utility usage
+ Clone repository, run `main.py` using python.<br>
_(This will require manual installation of all dependencies)_
+ Use precompiled .exe from [Releases Tab](https://github.com/OVERLORD7F/SpaceVM_VM_Utility/releases)
<img src=assets/images/disk_edit_mode.png>
<img src=assets/images/prepare_courses_1.png>
<img src=assets/images/prepare_courses_2.png>

## Config / Profiles
Directory _./profiles_ contains all configured profiles with necessary data for utility. 

This directory will be placed in the same directory as Utility itself.
>[!TIP]
>_You can create profiles and change specific options within the Utility._

<img src=assets/images/profiles_1.png>

<ins>**Profile example for reference:**</ins>
```
[General]
#Master Controller IP of your cluster
#Has to be accessible for a machine, which will be executing this Utility
controller_ip = 10.20.30.44

#Integration API Key
(how to get your key - https://spacevm.ru/docs/latest/base/operator_guide/security/users/#_14 )
# do not specify JWT tag with your key!
api_key = 

#skip start up splash screen (ASCII art)
skip_startup_splash = no

#loads this profile on utility startup by default
#only one profile could be loaded by default
load_by_default = false

[Data_Pool]
#Data pool which will be used for utility operations
#(Targeted storage for new vDisks)
data_pool_uuid = 

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
#Set vDisk size for "Prepare VMs for Courses" option
disk1 = 
disk2 = 
disk3 = 

[VM_List]
#Selected VMs which will be used for utility operations
#How to find UUID:
#List all available VMs in Utility Main Menu (Option 6)
#Use https://spacevm.ru/docs/latest/cli/space/vm/info/ or copy UUID from web panel
uuid_1 = 
uuid_2 =
```

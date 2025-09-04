# SpaceVM Utility (SVMU)
Utility to manage Virtual Machines in SpaceVM.

Written in python, uses [SpaceVM API](https://spacevm.ru/docs/6.5/api/) to collect and manage existing Virtual Machines in your SpaceVM cluster.

>[!NOTE]
>_This utility is focused on managing virtual disks_<br>
>_Works with SpaceVM 6.5.5 / 6.5.6 / 6.5.7_

# Requirements
- Fully setup SpaceVM cluster with VMs
- SpaceVM Utility and SpaceVM cluster should be in LAN
- Obtain your [API Key](https://spacevm.ru/docs/latest/base/operator_guide/security/users/#_14)
>[!WARNING]
> Utility is only tested on Windows 10
- For Windows 10 - [New Microsoft Terminal](https://github.com/microsoft/terminal) is highly recommended (correct colors, menus, etc)

# Utility usage
Clone repository or use compiled .exe from [Releases Tab](https://github.com/OVERLORD7F/SpaceVM_VM_Utility/releases)

Fill in the config file as stated below.

## Config File (SpaceVM_Utility.conf)
_SpaceVM_Utility.conf_ contains all necessary data for utility and has to be placed in the same directory as Utility itself.

You can create config and change specific options within the Utility.
```
[General]
#Master Controller IP of your cluster
#Has to be accessible for a machine, which will be executing this Utility
controller_ip = 10.20.30.44

#Integration API Key
(how to get your key - https://spacevm.ru/docs/latest/base/operator_guide/security/users/#_14 )
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

[Courses-Space-VM]
#Set vDisk size for "Prepare VMs for Courses" option
disk1 = 
disk2 = 
disk3 = 
```

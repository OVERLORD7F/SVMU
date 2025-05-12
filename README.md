# SpaceVM_VM_Utility
Utility to manage Virtual Machines in SpaceVM.

Written in python, uses [SpaceVM API](https://spacevm.ru/docs/6.5/api/) to collect and manage existing Virtual Machines in your SpaceVM cluster.

_For now, this utility is focused on managing virtual disks_

_Works with SpaceVM 6.5.5+_

# Config File
Config file contains all necessary data for utility and has to be placed in the same directory as Utility itself.

You can populate config within Utility Main Menu.

For manual input see format below:
```
Controller IP Address
API Integration Key
Data Pool UUID
VM UUID #1
VM UUID #2
VM UUID #3 
...
```

# SpaceVM_VM_Utility
Utility to manage Virtual Machines in SpaceVM.

Written in python, uses [SpaceVM API](https://spacevm.ru/docs/6.5/api/) to collect and manage existing Virtual Machines in your SpaceVM cluster.

_For now, this utility is focused on managing virtual disks_

_Works with SpaceVM 6.5.5+_

# Utility usage
Clone repository or use compiled .exe

Config file is essential for the utility.

## Config File
Config file contains all necessary data for utility and has to be placed in the same directory as Utility itself.

<ins>The following parameters are required:</ins>
```
1. Controller IP Address (Master)
2. API Integration Key
3. Data Pool UUID (which will be used for operations)
4. Virtual Machine UUID (List of selected VMs for operations)
5. Virtual Machine UUID
6. ...
```

You can populate config within Utility Main Menu.

For manual input see format below:
```
1.2.3.4
eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1...
67497424-e54b-46f1-b023-4d6d65eac104
304fd7be-06a6-4f4e-9bb9-41bf532ec4fb
f840320f-cecc-4a31-a799-fd84e7baf089
```

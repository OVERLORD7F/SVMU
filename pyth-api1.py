import requests
import json
import copy

base_url="http://10.2.1.52/api"
power_state= ["Unknown" , "Off" , "Suspend" , "On"] #3 - on; 2 - suspend; 1 - off; 0 - unknown

#importing API-KEY from file
with open("Y:\\py\\integration_key_pod5.txt", "r") as f: # using  '\' (instead of '\\') throws syntax warning
    api_key = "jwt " + f.read() #actual format for api_key. That was realy obvious DACOM >:C


#importing VM-UUIDs from file
with open("Y:\\py\\VM-UUIDs.txt", "r") as f:
    vm_uuids =  f.read() 

#get domain info "http://10.2.1.52/api/domains/uuid   OR  /domains/{id}/all-content/"
def get_domain_info(domain_uuid):
    url= f"{base_url}/domains/{domain_uuid}"
    response = requests.get(url , headers={'Authorization' : api_key})
    
    if response.status_code == 200: #200 - OK
        domain_data = response.json()
        return domain_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")
    
    

def get_domain_all_content(domain_uuid):
    url= f"{base_url}/domains/{domain_uuid}/all-content"
    response = requests.get(url , headers={'Authorization' : api_key})
    if response.status_code == 200: #200 - OK    
        domain_all_data = response.json()
        return domain_all_data #returns as dictionary!
    else:
        print(f"Failed to retrieve data {response.status_code}")

    """
def get_disk_uuids(domain_all_content):
    #domain_all_content (type - dictionary)
    #returns VMs vdisk uuids (type - list)   
    try:
        # Проверяем наличие необходимого ключа
        if 'vdisks' not in domain_all_content:
            raise KeyError("Отсутствует ключ 'vdisks' в данных")
        # Получаем список всех дисков
        disks = domain_all_content['vdisks']
        # Извлекаем UUID каждого диска
        vdisk_uuid = [disk['id'] for disk in disks]
        vdisk_size = []
        return vdisk_uuid
    except KeyError as e:
        print(f"Ошибка: {e}")
        return []
    except TypeError:
        print("Ошибка: данные не соответствуют ожидаемому формату")
        return []
    """


def get_disk_info(domain_all_content):
    # Проверяем наличие информации о дисках в полученном словаре
    if 'vdisks' not in domain_all_content:
        print("Информация о дисках не найдена")
        return
    
    # Получаем список дисков
    disks = domain_all_content['vdisks']
    
    # Проверяем наличие дисков
    if not disks:
        print("Дисков не обнаружено")
        return
    
    # Выводим информацию о каждом диске
    for disk in disks:
        # Проверяем наличие всех необходимых полей
        if 'id' in disk and 'verbose_name' in disk and 'size' in disk:
            print(f"Name: {disk['verbose_name']}")
            print(f"UUID: {disk['id']}")
            print(f"Size: {disk['size']} GB")
            print("-" * 51)
        else:
            print("ERROR: failed to retrieve vdisk data.")


#pfsense 2cf0ecd3-5219-43b1-a471-1851a4f569e0
#vPOD9-2 6b5b9a20-0e5c-4524-ac71-e6dd3c818228
domain_uuid = vm_uuids 
domain_info = get_domain_info(domain_uuid)
domain_all_content = get_domain_all_content(domain_uuid)
#vdisk_ids = domain_all_content["vdisks"]

#print(domain_info)
if domain_info:
    print("=" * 14 , "Virtual Machine Info" , "=" * 15)
    print(f"\t VM: {domain_info["verbose_name"]}")
    print(f"\t Power State: {power_state[domain_info["user_power_state"]]}") #translating status code to "pretty name"
    print(f"\t vDisks: {domain_info["vdisks_count"]}")
    print("-" * 19 , "vDisks Info" , "-" * 19)
    
    #get only vdisk UUIDs
    #disk_uuids = get_disk_uuids(domain_all_content)
    #print(disk_uuids)
    
    get_disk_info(domain_all_content)

    
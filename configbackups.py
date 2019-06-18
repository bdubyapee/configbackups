# Test Script 2 for Junos Automation
# Pull configs and save from all Routers using multiple Threads concurrently
# 11-15 Seconds Timed for 29 routers!

# BWP : 3/6/18 : Initial Creation
# BWP : 4/3/18 : Added YAML support for configuration information
# BWP : 11/15/18 : Updated for f-string support

import time
startup = time.time()
from lxml import etree
import sys
import threading
import yaml


from jnpr.junos import Device



def grab_config(each_router):
    try:
        with Device(host=each_router, user=device_username, passwd=device_password, port=device_port) as dev:
            bytesconfig = dev.rpc.get_config(options={"database" : "committed", "format" : "text"})
            with open(f"{dev.facts['hostname']}.txt", "a+") as outputfile:
                textconfig = etree.tostring(bytesconfig).decode()
                try:
                    textconfig = textconfig.replace('<configuration-text>\n', '')
                    textconfig = textconfig.replace('</configuration-text>', '')
                except Exception as err:
                    print(f"Did not find configuration text header or footer. Verify backup successful.\n  Error:{err}")
                outputfile.write(f"{textconfig}\n")
            
    except Exception as err:
        print(f"Error connecting to {dev.facts['hostname']}.  Error:{err}")
        


if __name__ == "__main__":
    try:
        with open("routers_configbackups.yml", "r") as configfile:
            config = yaml.load(configfile, Loader=yaml.SafeLoader)
    except Exception as err:
        print(f"Error opening or processing routers_configbackups.yml : {err}")
        sys.exit()

    device_username = config['credentials']['username']
    device_password = config['credentials']['password']
    device_port = config['credentials']['port']

    devices_address_list = config['routeriplist']
    

    threads = [threading.Thread(target=grab_config, args=(each_router,)) for each_router in devices_address_list]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
            
    print(f"Complete configuration backup in {(time.time() - startup):,.3f} seconds.")
    
    sys.exit()

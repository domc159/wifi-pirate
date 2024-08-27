# main.py
import subprocess
import functions

# Prikaz prve strani
subprocess.run('./first_page.sh', shell=True)
choice = ''

options = {
    "1": functions.get_wifi_networks,
    "2": lambda: functions.mdk4_deauth_attack_dualband(wlan1="wlan2mon", wlan2="wlan1"),
    "3": lambda: functions.mdk4_beacon_flood_random(wlan="wlan1"),
    "4": lambda: functions.mdk4_beacon_flood_multiply(wlan="wlan1"),
    "5": functions.wifi_phishing,
    "a": functions.prepare_interfaces,
    "b": functions.install_dependencies,
    "e": functions.program_stop,

}

while choice != 'e':
    while choice == '':
        choice = input("Choice: ")


    if choice in options:
        function = options[choice]
        result = function()  # Tukaj se funkcija izvede
    if result is not None:  # Če funkcija vrača vrednost, jo prikaži
            print(result)

    if choice != 'e':
        subprocess.run('./menu_page.sh', shell=True)
    
    if choice == '5':
        command= f'sudo systemctl start NetworkManager'
        subprocess.run(command, shell=True)
        print('Network restored')

    if choice == 'e':
        print('exiting ...')
        break
    else: 
        choice = ''
        continue
    choice = ''

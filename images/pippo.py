import subprocess

def get_version():
    try:
        # Sostituisci 'diff' con il comando reale per la versione di kdiff
        version = subprocess.check_output(['kdiff', '-v'], text=True).strip()
    except Exception:
        version = "version unknown"
    return version


BANNER_LOGO_TEMPLATE = '''

  _  _____ ___ ___ ___ 
 | |/ /   \_ _| __| __|
 | ' <| |) | || _|| _| 
 |_|\_\___/___|_| |_|  
                       
'''

if __name__ == "__main__":
    version = get_version()
    print(BANNER_LOGO_TEMPLATE.format(version=version))

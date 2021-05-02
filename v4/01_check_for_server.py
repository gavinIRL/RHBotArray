
from subprocess import check_output
from subprocess import run
import socket
output = run("arp -a", capture_output=True).stdout.decode()
# print(output)

list_ips = []
with open("servers.txt", "r") as f:
    lines = f.readlines()
    for ip in lines:
        if ip.strip() in output:
            list_ips.append(ip.strip())

print(list_ips)


output2 = run("ipconfig", capture_output=True).stdout.decode()
_, post = output2.split("IPv4 Address. . . . . . . . . . . : 192")
final, _ = post.split("Subnet Mask")
current_lan_ip = "192" + final
print(current_lan_ip)


from subprocess import check_output
from subprocess import run
import socket


def grab_online_servers():
    output = run("arp -a", capture_output=True).stdout.decode()
    list_ips = []
    with open("servers.txt", "r") as f:
        lines = f.readlines()
        for ip in lines:
            if ip.strip() in output:
                list_ips.append(ip.strip())
    return list_ips


print(grab_online_servers())


def grab_current_lan_ip():
    output = run(
        "ipconfig", capture_output=True).stdout.decode()
    _, output = output.split("IPv4 Address. . . . . . . . . . . : 192")
    output, _ = output.split("Subnet Mask")
    current_lan_ip = "192" + output.strip()
    return current_lan_ip


print(grab_current_lan_ip())

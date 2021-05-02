from subprocess import run
output = run("arp -a", capture_output=True).stdout.decode()
# print(output)

list_ips = []
with open("servers.txt", "r") as f:
    lines = f.readlines()
    for ip in lines:
        if ip.strip() in output:
            list_ips.append(ip.strip())

print(list_ips)

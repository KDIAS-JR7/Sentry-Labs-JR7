# Day 03 – Exporting Collected Data and Golden State Baseline

> **Date:** 02 Mar 2026 · **Topic:** Harvesting configs and the case for a static management IP · **Takeaway:** Data you can't export is data you can't monitor — and a DHCP lease is a ticking clock.

[↑ Journal Index](../../README.md)

## The Goal

- For the next step of the project, we need to export the collected data into a text file within the physical environment(project folder).
- To achieve this, the **check_connection.py** script is once again updated.

```python
from netmiko import ConnectHandler
from datetime import datetime
import os

device = {
    'device_type': 'cisco_ios',
    'host': 'R1',
    'username': 'admin',
    'password': 'cisco123',
    'ssh_config_file': '/root/.ssh/config',
}

# Ensure a logs directory exists
os.makedirs('logs', exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

try:
    print(f"--- Sentry-Pod: Harvesting Data from R1 [{timestamp}] ---")
    connection = ConnectHandler(**device)

    # Capture the full config
    config_data = connection.send_command("show run")

    # Save to the shared volume
    filename = f"logs/R1_golden_config_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(config_data)

    print(f"Success! Data saved to: {filename}")
    connection.disconnect()

except Exception as e:
    print(f"Extraction Failed: {e}")
```

- The new python script now polls, collects, and exports information as a text file readable by an AI.
- The current output creates the **Golden State Baseline**; the network baseline that will be used later for the *drift detection* function. Notice how the *connection.send_command* method now sends the **show run** IOS command, which outputs the entire **running configuration** of the Cisco device.

```text
Building configuration...

Current configuration : 1199 bytes
!
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname R1
!
boot-start-marker
boot-end-marker
!
!
!
no aaa new-model
no ip icmp rate-limit unreachable
ip cef
!
!
!
!
!
!
no ip domain lookup
ip domain name sentrypod.local
no ipv6 cef
!
!
multilink bundle-name authenticated
!
!
!
!
!
!
!
username admin privilege 15 secret 5 $1$cq3C$tHhgI.FZKbou5e/O.0138.
!
!
ip tcp synwait-time 5
ip ssh rsa keypair-name SENTRY_KEY
ip ssh version 2
!
!
!
!
!
!
!
!
!
!
!
interface FastEthernet0/0
 no ip address
 shutdown
 speed auto
 duplex auto
!
interface FastEthernet0/1
 ip address dhcp
 speed auto
 duplex auto
!
interface FastEthernet1/0
 no ip address
 shutdown
 speed auto
 duplex auto
!
interface FastEthernet1/1
 no ip address
 shutdown
 speed auto
 duplex auto
!
interface GigabitEthernet2/0
 no ip address
 shutdown
 negotiation auto
!
ip forward-protocol nd
!
!
no ip http server
no ip http secure-server
!
!
!
!
control-plane
!
!
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line vty 0 4
 login local
 transport input ssh
!
!
end
```

## The Struggle

### Static IP to Edge Router

- The current configuration uses DHCP to connect the edge router to the NAT node.

```text
interface FastEthernet0/1
 ip address dhcp
 speed auto
 duplex auto
!
```

- However, once the DHCP lease expires, this IP address could change, breaking the connection.
- To remediate this, Fa0/1 interface on R1 is given a static IP address.

```text
R1(config-if)#ip address 192.168.122.254 255.255.255.0
```

- Then the SSH config file is altered accordingly.

```text
Host R1
    HostName 192.168.122.254
    User admin
    Ciphers +aes128-cbc
    KexAlgorithms +diffie-hellman-group14-sha1
    HostKeyAlgorithms +ssh-rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

- And finally, the container is rebuilt with,

```bash
podman build -t sentry-watchman:v2 .
```

```text
─[kaveesh@fedora] - [~/Documents/University/University notes/2nd Year/4th semester/Obsidian/FIS smester 4/Capstone Project/Lab] - [Mon Mar 02, 15:56]
└─[$] <> podman build -t sentry-watchman:v2 .
STEP 1/8: FROM alpine:latest
STEP 2/8: RUN apk add --no-cache openssh-client python3 py3-pip build-base python3-dev
--> Using cache 144704f781fe538732873b42a176db4ad6f52d5a8b4482e93e705abf02e869fe
--> 144704f781fe
STEP 3/8: RUN pip install --no-cache-dir netmiko --break-system-packages
--> Using cache bebbe4486f39340e808b9d5a318dfaa3571fd374ee685a3d384a95500ce98a2e
--> bebbe4486f39
STEP 4/8: RUN mkdir -p /root/.ssh
--> Using cache 5b63bd10ec20d24df9d7d3cd3f7a3b95266c5b36e0468e53dcefc04c483b9602
--> 5b63bd10ec20
STEP 5/8: COPY ssh_config /root/.ssh/config
--> Using cache 5ee4c3b743bafa3baf3946c0851ddc0e135b943207057f357d79afcd602ab168
--> 5ee4c3b743ba
STEP 6/8: RUN chmod 600 /root/.ssh/config
--> Using cache 3a45c9189c5fd2781b47e7053d68df13d14011d59e686f8cd2b1ca799f97fdb4
--> 3a45c9189c5f
STEP 7/8: WORKDIR /app
--> Using cache 3101375d9613b2d118281d24446a6f893851f098f50bf78afd0c4c5e8880fe51
--> 3101375d9613
STEP 8/8: CMD ["sh"]
--> Using cache 79bb4c7d1cb140110436cefc20ac8ca0a6f5f1cc380f488e9255264c8e66b77a
COMMIT sentry-watchman:v2
--> 79bb4c7d1cb1
Successfully tagged localhost/sentry-watchman:v2
Successfully tagged localhost/netmiko-alpine:latest
79bb4c7d1cb140110436cefc20ac8ca0a6f5f1cc380f488e9255264c8e66b77a
┌─[kaveesh@fedora] - [~/Documents/University/University notes/2nd Year/4th semester/Obsidian/FIS smester 4/Capstone Project/Lab] - [Mon Mar 02, 15:56]
└─[$] <> podman run -it --rm --network=host -v .:/app:Z sentry-watchman:v2
/app # ssh R1
Warning: Permanently added '192.168.122.254' (RSA) to the list of known hosts.
(admin@192.168.122.254) Password:

R1#
```

- This new change is now seen in the **running config**.

```text
interface FastEthernet0/1
 ip address 192.168.122.254 255.255.255.0
 speed auto
 duplex auto
!
```

## Artifacts

- [check_connection.py](../../artifacts/netmiko/check_connection.py) — the data harvesting script

---
← [Day 02 · Persistent Environment](02-persistent-environment.md) | [Day 04 · Three-Tier Topology & VLSM](04-topology-three-tier-vlsm.md) →

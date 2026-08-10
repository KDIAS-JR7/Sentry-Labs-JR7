# Day 11 – Management VLAN

> **Date:** 11 Apr 2026 · **Topic:** The loopback trick stops at layer 2 — enter the Management VLAN · **Takeaway:** A subtle routing concept ("longest match") silently broke pings, and the fix was to remove an interface, not add one.

[↑ Journal Index](../../README.md)

## The Goal

- The layer 3 devices from the edge to the distribution layer can be managed through the loopback interfaces assigned with addresses in the 10.0.0.0/24 address range.
- However, the access layer consists of layer 2 switches and switched links instead of routed interfaces, meaning the loopback interface approach is not applicable.
- But, we still need to manage these devices over ssh, a requirement for ansible automation throughout all three layers.
- Therefore, we will instead be utilizing the concept of the Management VLAN.
- The Management VLAN is a special VLAN created for the sole purpose of managing the devices, and not data transfer.

## Configuring the Management VLAN

### Distribution Layer

#### 1. Creating the management VLAN

```bash
ESW3#vlan data
ESW3#vlan database
ESW3(vlan)#vlan 99 name managementVLAN
VLAN 99 added:
   Name: managementVLAN
ESW3(vlan)#exit
APPLY completed.
Exiting....
```

- We're creating the management vlan as vlan 99 and naming it managementVLAN.

#### 2. Configuring trunk links

```bash
ESW3#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW3(config)#int f1/2
ESW3(config-if)#sw
ESW3(config-if)#switchport trunk allowed vlan add 99
ESW3(config-if)#exit
```

- We're adding the newly created managementVLAN to the trunk link between ESW3 and ESW8.
- We can also make sure that the configurations were correctly applied with,

```bash
ESW3#sh int f1/2 switchport
Name: Fa1/2
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Negotiation of Trunking: Disabled
Access Mode VLAN: 0 ((Inactive))
Trunking Native Mode VLAN: 1 (default)
Trunking VLANs Enabled: ALL
Trunking VLANs Active: 1,7-8,99
Priority for untagged frames: 0
Override vlan tag priority: FALSE
Voice VLAN: none
Appliance trust: none
```

#### 3. Configuring the SVI

```bash
ESW3#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW3(config)#int vlan 99
ESW3(config-if)#
*Mar  2 07:14:10.932: %LINEPROTO-5-UPDOWN: Line protocol on Interface Vlan99, cha
nged state to up
ESW3(config-if)#no shut
ESW3(config-if)#ip ad
ESW3(config-if)#ip address 10.1.99.3 255.255.255.0
```

#### 4. Advertising via OSPF

```bash
SW3(config-if)#router ospf 1
ESW3(config-router)#net
ESW3(config-router)#network 10.1.99.0 0.0.0.255 area 0
```

- We're advertising the managementVLAN network 10.1.99.0 /24 over ospf.

### Access Layer

#### 1. Creating the management VLAN

```bash
ESW8#vlan dat
ESW8#vlan database
ESW8(vlan)#vlan 99 name managementVLAN
VLAN 99 added:
   Name: managementVLAN
ESW8(vlan)#exit
APPLY completed.
Exiting....
```

- We're once again creating the same management vlan as vlan 99.
- For this purpose, both devices must be in the same vlan.

#### 2. Configuring Trunk Links

```bash
ESW8(config-if)#int f1/0
ESW8(config-if)#switchport trunk allowed vlan add 99
```

#### 3. Configuring SVI

```bash
ESW8(config)#int vlan 99
ESW8(config-if)#ip ad
ESW8(config-if)#ip address 10.1.99.8 255.255.255.0
ESW8(config-if)#no shut
```

#### 4. Default gateway

- In order for a layer 2 device to communicate with other networks using IP addresses, it needs a default gateway.

```bash
ESW8(config)#ip default-gateway 10.1.99.3
```

- The default gateway we are providing is the IP address of ESW3's SVI

#### 5. Disabling Loopback interfaces

```text
Loopback0                10.0.0.90       YES NVRAM  up                   up

ESW9#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW9(config)#int loop
ESW9(config)#int loopback 0
ESW9(config-if)#no ip ad
ESW9(config-if)#no ip address 10.0.0.90
% Incomplete command.

ESW9(config-if)#no ip address 10.0.0.90 255.255.255.0
ESW9(config-if)#
```

- Disabling the loopback interfaces on the access layer switches ensures that no routing issues occure due to the concept of 'longest match' in routing.
- Otherwise, this will happen,

```bash
ESW10#ping 10.0.0.1

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.1, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
```

- ESW10 cannot ping R1, however,

```bash
R1#ping 10.1.99.10
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.1.99.10, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/77/116 ms
R1#
```

- R1 can ping ESW10. But after disabling the loopback interface..

```bash
ESW10(config)#int loopback 0
ESW10(config-if)#shut
ESW10(config-if)#
*Mar  1 04:17:51.862: %LINK-5-CHANGED: Interface Loopback0, changed state to admi
nistratively down
*Mar  1 04:17:52.862: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback0,
changed state to down
ESW10(config-if)#^Z
ESW10#ping 10.0.0.1
*Mar  1 04:17:54.746: %SYS-5-CONFIG_I: Configured from console by console
ESW10#ping 10.0.0.1

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 36/60/76 ms
ESW10#ping
```

- ESW10 can now also ping 10.0.0.1 or R1.

## First Ping Test

```bash
ESW8#ping 10.1.99.3

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.1.99.3, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 64/260/1048 ms
ESW8#ping 10.1.99.3

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.1.99.3, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 60/62/64 ms
ESW8#ping 10.0.0.1

Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 28/47/68 ms
ESW8#
```

- As seen here, ESW8 is able to ping 10.0.0.1 successfully. This is the edge router R1's loopback address.
- Furthermore,

```bash
traceroute 10.1.99.8
traceroute to 10.1.99.8 (10.1.99.8), 30 hops max, 60 byte packets
1  192.168.122.252 (192.168.122.252)  7.794 ms  7.773 ms  7.759 ms
2  10.1.0.2 (10.1.0.2)  118.619 ms  128.665 ms  138.737 ms
3  10.1.0.6 (10.1.0.6)  148.915 ms  158.929 ms  169.005 ms
4  10.1.99.8 (10.1.99.8)  179.068 ms  189.183 ms  199.215 ms
```

- The physical environment can also ping the access layer switch, which is required for ansible automation.

## FHRP

- Each access layer switch is also connected to two distribution layer switches for redundancy.
- This has already been used for the data vlan, but can also be used to provide redundancy for the managementVLAN.

```bash
ESW3(config-if)#no ip address 10.1.99.3 255.255.255.0
Invalid address
ESW3(config-if)#no ip address 10.1.99.1 255.255.255.0
*Mar  1 01:51:23.787: %HSRP-5-STATECHANGE: Vlan99 Grp 0 state Active -> Init
ESW3(config-if)#standby ip 10.1.99.1
ESW3(config-if)#ip address 10.1.99.3 255.255.255.0
ESW3(config-if)#
*Mar  1 01:52:11.319: %HSRP-5-STATECHANGE: Vlan99 Grp 0 state Speak -> Standby
*Mar  1 01:52:11.819: %HSRP-5-STATECHANGE: Vlan99 Grp 0 state Standby -> Active
ESW3(config-if)#
```

- We will be using 10.1.99.1 as the HSRP address for ESW3 and 4.

```bash
ESW7(config)#ip default-gateway 10.1.99.1
```

## Summary for ManagementVLAN

### 1. Distribution layer

| **Switch** | **SVI IP address** | **HSRP virtual IP** | **Interfaces in ManagementVLAN** |
| ---------- | ------------------ | ------------------- | -------------------------------- |
| ESW3       | 10.1.99.3          | 10.1.99.1           | f1/1 - 4                         |
| ESW4       | 10.1.99.4          | 10.1.99.1           | f1/1 - 4                         |
| ESW5       | 10.2.99.5          | 10.2.99.1           | f1/1 - 4                         |
| ESW6       | 10.2.99.6          | 10.2.99.1           | f1/1 - 4                         |

### 2. Access Layer

| **Switch** | **SVI IP address** | **Default gateway** | **Interfaces in ManagementVLAN** |
| ---------- | ------------------ | ------------------- | -------------------------------- |
| ESW7       | 10.1.99.7          | 10.1.99.1           | f1/0 - 1                         |
| ESW8       | 10.1.99.8          | 10.1.99.1           | f1/0 - 1                         |
| ESW9       | 10.1.99.9          | 10.1.99.1           | f1/0 - 1                         |
| ESW10      | 10.1.99.10         | 10.1.99.1           | f1/0 - 1                         |
| ESW11      | 10.2.99.11         | 10.2.99.1           | f1/0 - 1                         |
| ESW12      | 10.2.99.12         | 10.2.99.1           | f1/0 - 1                         |
| ESW13      | 10.2.99.13         | 10.2.99.1           | f1/0 - 1                         |
| ESW14      | 10.2.99.14         | 10.2.99.1           | f1/0 - 1                         |

---
← [Day 10 · Access Layer and L2 Connectivity](10-access-layer-l2-connectivity.md) | [Day 12 · Access Layer VLANs via Ansible](12-access-layer-vlans-ansible.md) →

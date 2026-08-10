# Day 10 – Access Layer and L2 Connectivity

> **Date:** 11 Apr 2026 · **Topic:** Broadcast domains, VLANs, trunks, SVIs, and the first HSRP virtual gateway · **Takeaway:** Layer 2 switches can't route — so every design decision (default gateway, redundancy) has to be solved somewhere else in the stack.

[↑ Journal Index](../../README.md)

## The Goal

- The access layer consists of Layer 2 switches. Since these switches are incapable of layer 3 routing, the division of broadcast domains at layer two is done through VLANS, to create independent LANs southbound of the access layer.

## Creating VLANs

```bash
ESW8#
ESW8#vlan database
ESW8(vlan)#vlan 8 name Technology
VLAN 8 added:
   Name: Technology
ESW8(vlan)#
```

- In EtherSwitch switches, creating VLANs is done through a separate mode accessed with *vlan database* command.
- Inside this mode, the commands to create VLANs are exactly the same as with a usual layer 2 switch.
- *vlan 8 name Technology* creates the VLAN number 8 in the VLAN database with the name Technology to easily identify it.
- However in order for devices in this vlan to communicate with other networks, layer 3 capabilities need to be provided through a default gateway as well as configuring access and trunk interfaces.

```bash
ESW8#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW8(config)#int r f1/0 - 1
ESW8(config-if-range)#switchport
ESW8(config-if-range)#switchport mode trunk
ESW8(config-if-range)#swit
*Mar  2 04:28:43.164: %DTP-5-TRUNKPORTON: Port Fa1/0 has become dot1q trunk
*Mar  2 04:28:43.972: %DTP-5-TRUNKPORTON: Port Fa1/1 has become dot1q trunk
ESW8(config-if-range)#swit
ESW8(config-if-range)#switchport trunk al
ESW8(config-if-range)#switchport trunk allowed vl
ESW8(config-if-range)#switchport trunk allowed vlan 8
Command rejected: Bad VLAN allowed list. You have to include all default vlans, e
.g. 1-2,1002-1005.
Command rejected: Bad VLAN allowed list. You have to include all default vlans, e
.g. 1-2,1002-1005.
ESW8(config-if-range)#switchport trunk allowed vlan ?
 WORD    VLAN IDs of the allowed VLANs when this port is in trunking mode
 add     add VLANs to the current list
 all     all VLANs
 except  all VLANs except the following
 remove  remove VLANs from the current list

ESW8(config-if-range)#switchport trunk allowed vlan add ?
 WORD  VLAN IDs of the allowed VLANs when this port is in trunking mode

ESW8(config-if-range)#switchport trunk allowed vlan add 8
ESW8(config-if-range)#
```

- F1/1 and F1/0 connect to the distribution layer switches ESW3 and 4. Therefore, these two interfaces of ESW8 are configured as trunk links.

## Inter VLAN routing

- In this topology, inter vlan routing is done via layer 3 distribution layer switches.
- This is done using the switch virtual interfaces, SVIs. However, before that ESW3 and 4 also needs VLAN 8 in their database.

| **ESW3** | **ESW4** |
| --- | --- |
| ESW3#vlan data <br>ESW3#vlan database <br>ESW3(vlan)#vlan 8 name Technology <br>VLAN 8 added: <br>   Name: Technology <br>ESW3(vlan)# | ESW4#vlan dat <br>ESW4#vlan database <br>ESW4(vlan)#vlan 8 name Technology <br>VLAN 8 added: <br>   Name: Technology <br>ESW4(vlan)# |

- Then configuring the trunk links,

| **ESW3** | **ESW4** |
| --- | --- |
| ESW3(config)#int f1/2 <br>ESW3(config-if)#swit <br>ESW3(config-if)#switchport <br>ESW3(config-if)#swit <br>ESW3(config-if)#switchport mode tr <br>ESW3(config-if)#switchport mode trunk <br>ESW3(config-if)#swit <br>ESW3(config-if)#switchport t <br>Mar  2 05:30:52.104: %DTP-5-TRUNKPORTON: Port Fa1/2 has become dot1q trunk <br>Mar  2 05:30:52.604: %LINEPROTO-5-UPDOWN: Line protocol on Interface Vlan8, chan <br>ged state to up <br>ESW3(config-if)#switchport trunk allowed vlan add 8 <br>ESW3(config-if)# | ESW4(config)#int f1/2 <br>ESW4(config-if)#swit <br>ESW4(config-if)#switchport <br>ESW4(config-if)#swit <br>ESW4(config-if)#switchport mode trunk <br>ESW4(config-if)#switc <br>Mar  2 05:33:23.088: %DTP-5-TRUNKPORTON: Port Fa1/2 has become dot1q trunk <br>ESW4(config-if)#switchport trunk alloed vlan add 8 <br>                    ^ <br>% Invalid input detected at '^' marker. <br>ESW4(config-if)#switchport trunk allowed vlan add 8 <br>ESW4(config-if)# |

- Configuring SVIs

| **ESW3** | **ESW4** |
| --- | --- |
| ESW3(config-if)#interface vlan 8 <br>ESW3(config-if)#ip addr <br>ESW3(config-if)#ip address 10.1.8.1 255.255.255.0 | ESW4(config-if)#int vlan 8 <br>ESW4(config-if)#ip ad <br>ESW4(config-if)#ip address <br>Mar  2 05:37:27.224: %LINEPROTO-5-UPDOWN: Line protocol on Interface Vlan8, chan <br>ged state to up <br>ESW4(config-if)#ip address 10.1.8.2 255.255.255.0 |

## FHRP with HSRP

- Each access layer switch only has one VLAN. But each of them has two connections to two distribution layer switches.
- In inter VLAN routing with SVIs, each VLAN should get one default gateway.
- The two connections emulate the spine leaf topology's redundancy feature, but here, it complicates inter VLAN routing as both distribution layer switches are providing different IP addresses although the VLAN can only use one. And if just one is chosen, the other link becomes useless.
- A solution to this can be created using FHRP, a technology meant to provide redundancy at the fist hop, usually at the edge router level.
- HSRP, a FHRP technology by CISCO does this by giving two physical router interfaces one shared logical IP address. Therefore, we can use this feature of HSRP to combine these two links into one layer 3 link.

```bash
ESW3(config-if)#standby 8 ip 10.1.8.3
ESW3(config-if)#
*Mar  2 05:37:20.988: %HSRP-5-STATECHANGE: Vlan8 Grp 8 state Speak -> Standby
*Mar  2 05:37:21.488: %HSRP-5-STATECHANGE: Vlan8 Grp 8 state Standby -> Active
ESW3(config-if)#
```

```bash
ESW4(config-if)#stand
ESW4(config-if)#standby 8 ip 10.1.8.3
ESW4(config-if)#
*Mar  2 05:39:25.552: %HSRP-5-STATECHANGE: Vlan8 Grp 8 state Speak -> Standby
ESW4(config-if)#
```

```bash
ESW3#sh ip int br
Interface                IP-Address      OK? Method Status              Proto
col
FastEthernet0/0          unassigned      YES NVRAM  administratively down down

FastEthernet0/1          unassigned      YES NVRAM  administratively down down

FastEthernet1/0          10.1.0.6        YES NVRAM  up                   up

----skipped----

Vlan1                    unassigned      YES NVRAM  administratively down down

Vlan7                    10.1.7.1        YES manual up                   up

Vlan8                    10.1.8.1        YES manual up                   up

Loopback0                10.0.0.30       YES NVRAM  up                   up

ESW3#
```

```bash
ESW4#sh ip int br
Interface                IP-Address      OK? Method Status              Proto
col
FastEthernet0/0          unassigned      YES NVRAM  administratively down down

FastEthernet0/1          unassigned      YES NVRAM  administratively down down

FastEthernet1/0          10.1.0.10       YES NVRAM  up                   up

----skipped----

Vlan1                    unassigned      YES NVRAM  administratively down down

Vlan7                    10.1.7.2        YES manual up                   up

Vlan8                    10.1.8.2        YES manual up                   up

Loopback0                10.0.0.40       YES NVRAM  up                   up

ESW4#
```

## Configuring Access interfaces

```bash
ESW8(config-if-range)#int f1/2
ESW8(config-if)#swit
ESW8(config-if)#switchport
ESW8(config-if)#swi
ESW8(config-if)#switchport mode ac
ESW8(config-if)#switchport mode access
ESW8(config-if)#sw
ESW8(config-if)#switchport access vlan 8
ESW8(config-if)#no shut
```

- This makes the interface f1/2 an access interface for the vlan 8. This interface can now be connected to an end device.

```bash
ESW8(config-if)#do show ip int br
Interface                IP-Address      OK? Method Status              Proto
col
FastEthernet0/0          unassigned      YES NVRAM  administratively down down

FastEthernet0/1          unassigned      YES NVRAM  administratively down down

FastEthernet1/0          unassigned      YES unset  up                   up

FastEthernet1/1          unassigned      YES unset  up                   up

FastEthernet1/2          unassigned      YES unset  up                   up
```

- Configuring IP addressing on a GNS3 VPC can be done through,

```bash
PC2> ip 10.1.8.4/24 10.1.8.3
Checking for duplicate address...
PC2 : 10.1.8.4 255.255.255.0 gateway 10.1.8.3
```

- As seen in the following output, PC2 can ping its default gateway which is 10.1.8.3 as well as the individual IP addresses of the two distribution layer interfaces

```bash
PC2> ping 10.1.8.3

84 bytes from 10.1.8.3 icmp_seq=1 ttl=255 time=39.768 ms
84 bytes from 10.1.8.3 icmp_seq=2 ttl=255 time=6.571 ms
^C
PC2> ping 10.1.8.1

84 bytes from 10.1.8.1 icmp_seq=1 ttl=255 time=19.771 ms
84 bytes from 10.1.8.1 icmp_seq=2 ttl=255 time=5.653 ms
^C
PC2> ping 10.1.8.2

84 bytes from 10.1.8.2 icmp_seq=1 ttl=255 time=9.935 ms
84 bytes from 10.1.8.2 icmp_seq=2 ttl=255 time=5.918 ms
^C
PC2>
```

- But not R1,

```bash
PC2> ping 10.0.0.1

10.0.0.1 icmp_seq=1 timeout
^C
```

- This can be fixed by advertising the network on the distribution layer switches on OSPF area 0.

```bash
ESW3#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW3(config)#router ospf 1
ESW3(config-router)#network 10.1.8.0 0.0.0.255 area 0
ESW3(config-router)#
```

- Afterwards, in R1 routing table, we have an entry for 10.1.8.0 /224 network,

```text
R1#sh ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
      D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
      N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
      E1 - OSPF external type 1, E2 - OSPF external type 2
      i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
      ia - IS-IS inter area, * - candidate default, U - per-user static route
      o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
      + - replicated route, % - next hop override

Gateway of last resort is not set

     10.0.0.0/8 is variably subnetted, 19 subnets, 3 masks
C       10.0.0.1/32 is directly connected, Loopback0
O       10.0.0.2/32 [110/2] via 10.0.0.14, 1d06h, FastEthernet0/1
O       10.0.0.10/32 [110/2] via 10.1.0.2, 1d06h, FastEthernet0/0
C       10.0.0.12/30 is directly connected, FastEthernet0/1
L       10.0.0.13/32 is directly connected, FastEthernet0/1
O       10.0.0.20/32 [110/3] via 10.0.0.14, 1d06h, FastEthernet0/1
O       10.0.0.30/32 [110/3] via 10.1.0.2, 1d06h, FastEthernet0/0
O       10.0.0.40/32 [110/3] via 10.1.0.2, 1d06h, FastEthernet0/0
O       10.0.0.50/32 [110/4] via 10.0.0.14, 1d06h, FastEthernet0/1
O       10.0.0.60/32 [110/4] via 10.0.0.14, 1d06h, FastEthernet0/1
C       10.1.0.0/30 is directly connected, FastEthernet0/0
L       10.1.0.1/32 is directly connected, FastEthernet0/0
O       10.1.0.4/30 [110/2] via 10.1.0.2, 1d06h, FastEthernet0/0
O       10.1.0.8/30 [110/2] via 10.1.0.2, 1d06h, FastEthernet0/0
O       10.1.7.0/24 [110/3] via 10.1.0.2, 06:31:45, FastEthernet0/0
O       10.1.8.0/24 [110/3] via 10.1.0.2, 00:01:04,
----skipped----
```

- And on PC2 we have the ability to ping R1,

```bash
PC2> ping 10.0.0.1

84 bytes from 10.0.0.1 icmp_seq=1 ttl=253 time=29.535 ms
84 bytes from 10.0.0.1 icmp_seq=2 ttl=253 time=37.889 ms
84 bytes from 10.0.0.1 icmp_seq=3 ttl=253 time=36.329 ms
^C
```

- We also have communication between this VPC at the very bottom of the virtual network and the physical environment.

```bash
traceroute 10.1.8.4
traceroute to 10.1.8.4 (10.1.8.4), 30 hops max, 60 byte packets
1  192.168.122.252 (192.168.122.252)  11.463 ms  11.434 ms  11.416 ms
2  10.1.0.2 (10.1.0.2)  112.105 ms  122.110 ms  132.185 ms
3  10.1.0.10 (10.1.0.10)  142.236 ms  152.277 ms  162.355 ms
4  10.1.8.4 (10.1.8.4)  172.407 ms  192.637 ms  202.631 ms
```

---
← [Day 09 · Ansible Day 1](09-ansible-first-playbook.md) | [Day 11 · Management VLAN](11-management-vlan.md) →

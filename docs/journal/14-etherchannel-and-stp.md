# Day 14 – EtherChannel and Spanning Tree

> **Date:** 24 Apr 2026 · **Topic:** Two redundancy mechanisms that actively worked against each other · **Takeaway:** Redundancy is not "set it and forget it" — STP and HSRP have their own elections, and they don't automatically agree on who should be active.

[↑ Journal Index](../../README.md)

## The Goal

- Each distribution layer switch is part of a pair sharing the same network and group of vlans.
- In order to have fast, direct communication between the two switches that will not be blocked by Spanning Tree Protocol(STP), we will be creating an ether channel link between the two switches by combining two fast ethernet interfaces.

## Ether channel creation

```bash
ESW4#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW4(config)#int r f1/14 - 15
ESW4(config-if-range)#channe
ESW4(config-if-range)#channel-group 1 ?
 mode  Etherchannel Mode of the interface

ESW4(config-if-range)#channel-group 1 mode on
```

- This bundles the fast ethernet 14 and 15 interfaces into one ether channel link.

## Verification

```bash
ESW4#sh interfaces port-channel 1
Port-channel1 is up, line protocol is up
 Hardware is EtherChannel, address is c006.12cd.f10e (bia c006.12cd.f10e)
 MTU 1500 bytes, BW 200000 Kbit, DLY 1000 usec,
    reliability 255/255, txload 1/255, rxload 1/255
 Encapsulation ARPA, loopback not set
 Keepalive set (10 sec)
 Full-duplex, 100Mb/s
 Members in this channel: Fa1/14 Fa1/15
 ARP type: ARPA, ARP Timeout 04:00:00
 Last input 00:00:00, output never, output hang never
 Last clearing of "show interface" counters never
 Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
 Queueing strategy: fifo
 Output queue: 0/40 (size/max)
 5 minute input rate 0 bits/sec, 0 packets/sec
 5 minute output rate 0 bits/sec, 0 packets/sec
    0 packets input, 0 bytes, 0 no buffer
    Received 0 broadcasts, 0 runts, 0 giants, 0 throttles
    0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
    0 input packets with dribble condition detected
    0 packets output, 0 bytes, 0 underruns
    0 output errors, 0 collisions, 3 interface resets
    0 babbles, 0 late collision, 0 deferred
    0 lost carrier, 0 no carrier
    0 output buffer failures, 0 output buffers swapped out
ESW4#conf
```

- The above output confirms that the EtherChannel has been created.

## The Struggle

### Manual Spanning tree and HSRP

- However, due to how the topology was designed, ESW3 and ESW 5 were chosen as the spanning tree root bridges for the 10.1.99.0 and 10.2.99.0 networks, while, ESW4 and 6 were chosen as the Active routers for HSRP.
- Due to the many redundant links, unfortunately, STP on the access layer switches blocked the links to the HSRP active routers since they were not the STP root bridges.
- This happened due to ESW3 and 5 having lower MAC address than ESW4 and 6, making them have a higher priority for STP root bridge, while being configured with a lower IP address for HSRP; wheres HSRP priorities the router with the *greater* IP address for active router.
- To solve this, we manually set the STP root bridges to also become the HSRP active routers by manually changing the HSRP priority of ESW3 and 5 to 110, as HSRP chooses the highest priority router to become the active router.
- Then we manually set them to preempt, and restart the HSRP active router election process.

```text
ESW6#sh standby br
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  100    Active   local          10.2.11.1      10.2.11.3
Vl12        12  100    Active   local          10.2.12.1      10.2.12.3
Vl13        13  100    Active   local          10.2.13.1      10.2.13.3
Vl14        14  100    Active   local          10.2.14.1      10.2.14.3
Vl99        0   100    Standby  10.2.99.5      local          10.2.99.1
```

- Here, ESW6 is the active router for HSRP.
- However,

```bash
ESW14#sh spanning-tree blockedports

Name                Blocked Interfaces List
-------------------- ------------------------------------
VLAN1               Fa1/1
VLAN14              Fa1/1
VLAN99              Fa1/1

Number of blocked ports (segments) in the system : 3
```

- Spanning tree on ESW14 is blocking fa1/1, which connects to ESW6

```bash
ESW14#sh cdp neighbors
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                 S - Switch, H - Host, I - IGMP, r - Repeater

Device ID       Local Intrfce    Holdtme    Capability  Platform  Port I
D
ESW6.lab.local  Fas 1/1           158        R S I       2691      Fas 1/
4
ESW5.lab.local  Fas 1/0           157        R S I       2691      Fas 1/
4
```

- Due to this, pc8 cannot even reach its default gateway.

```bash
PC8> ping 10.2.14.3

host (10.2.14.3) not reachable
```

## The Solution

- Therefore, we will make ESW5, the root bridge for STP, also the active router for HSRP.

```bash
ESW5#conf t
Enter configuration commands, one per line.  End with CNTL/Z.
ESW5(config)#int vlan 14
ESW5(config-if)#standb
ESW5(config-if)#standby 14 pre
ESW5(config-if)#standby 14 prio
ESW5(config-if)#standby 14 priority 110
ESW5(config-if)#standb
ESW5(config-if)#standby 14 pre
ESW5(config-if)#standby 14 preempt
ESW5(config-if)#
*Mar  1 00:48:29.323: %HSRP-5-STATECHANGE: Vlan14 Grp 14 state Standby -> Active
ESW5(config-if)#
```

- For SVI vlan 14, ESW5 is now the active HSRP router.

```text
ESW6#sh standby br
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  100    Active   local          10.2.11.1      10.2.11.3
Vl12        12  100    Active   local          10.2.12.1      10.2.12.3
Vl13        13  100    Active   local          10.2.13.1      10.2.13.3
Vl14        14  100    Active   local          10.2.14.1      10.2.14.3
Vl99        0   100    Standby  10.2.99.5      local          10.2.99.1
ESW6#sh standby br
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  100    Active   local          10.2.11.1      10.2.11.3
Vl12        12  100    Active   local          10.2.12.1      10.2.12.3
Vl13        13  100    Active   local          10.2.13.1      10.2.13.3
Vl14        14  100    Speak    10.2.14.1      unknown        10.2.14.3
Vl99        0   100    Standby  10.2.99.5      local          10.2.99.1
ESW6#
*Mar  1 00:48:29.143: %HSRP-5-STATECHANGE: Vlan14 Grp 14 state Active -> Speak
ESW6#sh standby br
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  100    Active   local          10.2.11.1      10.2.11.3
Vl12        12  100    Active   local          10.2.12.1      10.2.12.3
Vl13        13  100    Active   local          10.2.13.1      10.2.13.3
Vl14        14  100    Speak    10.2.14.1      unknown        10.2.14.3
Vl99        0   100    Standby  10.2.99.5      local          10.2.99.1
ESW6#sh standby br
*Mar  1 00:48:39.139: %HSRP-5-STATECHANGE: Vlan14 Grp 14 state Speak -> Standby
ESW6#sh standby br
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  100    Active   local          10.2.11.1      10.2.11.3
Vl12        12  100    Active   local          10.2.12.1      10.2.12.3
Vl13        13  100    Active   local          10.2.13.1      10.2.13.3
Vl14        14  100    Standby  10.2.14.1      local          10.2.14.3
Vl99        0   100    Standby  10.2.99.5      local          10.2.99.1
ESW6#
```

- The above output shows HSRP electing a new active router.
- Then,

```bash
PC8> ping 10.2.14.3

84 bytes from 10.2.14.3 icmp_seq=1 ttl=255 time=29.572 ms
84 bytes from 10.2.14.3 icmp_seq=2 ttl=255 time=16.230 ms
84 bytes from 10.2.14.3 icmp_seq=3 ttl=255 time=7.111 ms
84 bytes from 10.2.14.3 icmp_seq=4 ttl=255 time=16.124 ms
84 bytes from 10.2.14.3 icmp_seq=5 ttl=255 time=7.038 ms
```

## Ansible

- However.. there are 4 SVIs in one switch, with two switches, making it 8 SVIs that we have to configure manually to become the HSRP active router for that VLAN.
- This is tedious. We will instead use an Ansible playbook.

### Playbook

```yaml
- name: Configure HSRP active routers

hosts: HSRP_Routers

gather_facts: false


tasks:

- name: Configure active routers

cisco.ios.ios_config:

lines:

- interface vlan {{ item.id }}

- standby {{ item.id }} priority 110

- standby {{ item.id }} preempt

loop: "{{ vlans }}"

when: vlans is defined
```

### Output

```text
ansible-playbook -i hosts.ini HSRP_active.yml

PLAY [Configure HSRP active routers] ********************************************************************************************************************

TASK [Configure active routers] *************************************************************************************************************************
changed: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3'})
changed: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3'})
changed: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3'})
changed: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3'})
changed: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3'})
changed: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3'})
changed: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3'})
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3'})

PLAY RECAP **********************************************************************************************************************************************
ESW3                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

- We can also see this take into effect on the Switches,

```bash
ESW6#
*Mar  1 01:49:38.231: %HSRP-5-STATECHANGE: Vlan11 Grp 11 state Active -> Speak
ESW6#
*Mar  1 01:49:41.155: %HSRP-5-STATECHANGE: Vlan12 Grp 12 state Active -> Speak
ESW6#
*Mar  1 01:49:47.243: %HSRP-5-STATECHANGE: Vlan13 Grp 13 state Active -> Speak
*Mar  1 01:49:48.231: %HSRP-5-STATECHANGE: Vlan11 Grp 11 state Speak -> Standby
ESW6#
*Mar  1 01:49:51.155: %HSRP-5-STATECHANGE: Vlan12 Grp 12 state Speak -> Standby
ESW6#
*Mar  1 01:49:57.243: %HSRP-5-STATECHANGE: Vlan13 Grp 13 state Speak -> Standby
ESW6#
```

```bash
ESW5#sh standby brief
                    P indicates configured to preempt.
                    |
Interface   Grp Prio P State    Active         Standby        Virtual IP
Vl11        11  110  P Active   local          10.2.11.2      10.2.11.3
Vl12        12  110  P Active   local          10.2.12.2      10.2.12.3
Vl13        13  110  P Active   local          10.2.13.2      10.2.13.3
Vl14        14  110  P Active   local          10.2.14.2      10.2.14.3
Vl99        0   110  P Active   local          10.2.99.6      10.2.99.1
ESW5#
```

- The playbook has successfully configured ESW5 as the HSRP active router for all its VLAN SVIs.

## Artifacts

- [HSRP_active.yml](../../artifacts/ansible/playbooks/HSRP_active.yml) — the playbook

---
← [Day 13 · Inter-VLAN Routing via Ansible](13-inter-vlan-routing-ansible.md) | [Day 15 · HSRP and Default Gateways via Ansible](15-hsrp-default-gateways-ansible.md) →

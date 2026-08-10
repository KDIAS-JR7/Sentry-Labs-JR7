# Day 17 – Access Layer Interface Configuration

> **Date:** 24 Apr 2026 · **Topic:** End-device ports + OSPF distribution — and a typo that idempotency caught · **Takeaway:** Ansible's idempotency turned my own config mistake into a non-event: fix one file, rerun, only the broken device changes.

[↑ Journal Index](../../README.md)

## The Goal

- For the purpose of this lab, we will be using end devices strictly on the F1/2 interfaces of the access layer switches.
- As we are using the same interface, in every switch we will instead automate this process.

## Configuring F1/2 interface

### Playbook

```yaml
- name: Configure End device port

hosts: Access_Switches

gather_facts: false


tasks:

- name: Configure ports

cisco.ios.ios_config:

lines:

- interface f1/2

- shut

- switchport mode access

- switchport access vlan {{ vlan_id }}

- no shut
```

- This playbook is written to configure the end device facing interface on each switch, according to the unique VLAN each switch supports.

### output

```text
ansible-playbook -i hosts.ini endDevice.yml

PLAY [Configure End device port] ************************************************************************************************************************

TASK [Configure ports] **********************************************************************************************************************************
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [Esw11]
changed: [ESW9]
changed: [ESW12]
changed: [ESW7]
changed: [ESW8]
changed: [ESW10]
changed: [ESW13]
changed: [ESW14]

PLAY RECAP **********************************************************************************************************************************************
ESW10                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## OSPF

- The access layer switches are now configured, meaning, an end device connected to f1/2 on a switch can ping its default gateway and the two distribution layer switches.
- However, in order for these devices to reach the host environment, the core layer switches must have an routing table entry for them.

```text
ESW2#sh ip route
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
      D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
      N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
      E1 - OSPF external type 1, E2 - OSPF external type 2
      i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
      ia - IS-IS inter area, * - candidate default, U - per-user static route
      o - ODR, P - periodic downloaded static route

Gateway of last resort is not set

O     192.168.122.0/24 [110/3] via 10.2.0.1, 02:38:59, FastEthernet1/0
     10.0.0.0/8 is variably subnetted, 19 subnets, 3 masks
C      10.2.0.8/30 is directly connected, FastEthernet1/2
O      10.0.0.10/32 [110/4] via 10.2.0.1, 02:38:59, FastEthernet1/0
O      10.1.8.0/24 [110/5] via 10.2.0.1, 02:38:59, FastEthernet1/0
O      10.1.0.8/30 [110/4] via 10.2.0.1, 02:38:59, FastEthernet1/0
O      10.0.0.12/30 [110/2] via 10.2.0.1, 02:38:59, FastEthernet1/0
C      10.2.0.0/30 is directly connected, FastEthernet1/0
O      10.0.0.2/32 [110/2] via 10.2.0.1, 02:39:01, FastEthernet1/0
O      10.1.0.0/30 [110/3] via 10.2.0.1, 02:39:01, FastEthernet1/0
O      10.0.0.1/32 [110/3] via 10.2.0.1, 02:39:01, FastEthernet1/0
C      10.2.0.4/30 is directly connected, FastEthernet1/1
O      10.1.7.0/24 [110/5] via 10.2.0.1, 02:39:01, FastEthernet1/0
O      10.1.0.4/30 [110/4] via 10.2.0.1, 02:39:05, FastEthernet1/0
O      10.0.0.30/32 [110/5] via 10.2.0.1, 02:39:05, FastEthernet1/0
C      10.0.0.20/32 is directly connected, Loopback0
O      10.0.0.40/32 [110/5] via 10.2.0.1, 02:39:05, FastEthernet1/0
O      10.0.0.60/32 [110/2] via 10.2.0.10, 02:39:05, FastEthernet1/2
O      10.0.0.50/32 [110/2] via 10.2.0.6, 02:39:05, FastEthernet1/1
O      10.1.99.0/24 [110/5] via 10.2.0.1, 02:39:05, FastEthernet1/0
O      10.2.99.0/24 [110/2] via 10.2.0.10, 02:39:05, FastEthernet1/2
                    [110/2] via 10.2.0.6, 02:39:05, FastEthernet1/1
```

- Which they do not.
- And as usual, we will be using a playbook to fix this.

### playbook

```yaml
- name: configure ospf routes

hosts: Distribution_Switches

gather_facts: false


tasks:

- name: distribute routes

cisco.ios.ios_config:

parents: router ospf 1

lines:

- network {{ item.network }} 0.0.0.255 area 0

loop: "{{ vlans }}"

when: vlans is defined
```

### output

```text
ansible-playbook -i hosts.ini ospf.yml

PLAY [configure ospf routes] ****************************************************************************************************************************

TASK [distribute routes] ********************************************************************************************************************************
ok: [ESW6] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3', 'network': '10.2.11.0'})
ok: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3', 'network': '10.1.7.0'})
ok: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3', 'network': '10.1.8.0'})
ok: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3', 'network': '10.2.11.0'})
ok: [ESW4] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3', 'network': '10.1.7.0'})
ok: [ESW4] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3', 'network': '10.1.8.0'})
changed: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3', 'network': '10.1.9.0'})
changed: [ESW6] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3', 'network': '10.2.12.0'})
changed: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3', 'network': '10.2.12.0'})
changed: [ESW4] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3', 'network': '10.1.9.0'})
changed: [ESW6] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3', 'network': '10.2.13.0'})
changed: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3', 'network': '10.2.13.0'})
ok: [ESW6] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3', 'network': '10.2.11.0'})
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3', 'network': '10.1.10.0'})
ok: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3', 'network': '10.2.11.0'})
changed: [ESW4] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3', 'network': '10.1.10.0'})

PLAY RECAP **********************************************************************************************************************************************
ESW3                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## The Struggle

- However, by accident, I have made a mistake in the ESW5 configuration file, leading to just the 10.2.14.0 network not being advertised. However, Ansible is idempotent. Therefore, we can just rerun the playbook and just change the configuration for ESW5, as follows.

```text
└─[$] <> ansible-playbook -i hosts.ini ospf.yml

PLAY [configure ospf routes] ****************************************************************************************************************************

TASK [distribute routes] ********************************************************************************************************************************
ok: [ESW4] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3', 'network': '10.1.7.0'})
ok: [ESW6] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3', 'network': '10.2.11.0'})
ok: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3', 'network': '10.2.11.0'})
ok: [ESW4] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3', 'network': '10.1.8.0'})
ok: [ESW6] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3', 'network': '10.2.12.0'})
ok: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3', 'network': '10.2.12.0'})
ok: [ESW4] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3', 'network': '10.1.9.0'})
ok: [ESW6] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3', 'network': '10.2.13.0'})
ok: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3', 'network': '10.2.13.0'})
ok: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3', 'network': '10.1.7.0'})
ok: [ESW4] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3', 'network': '10.1.10.0'})
ok: [ESW6] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3', 'network': '10.2.11.0'})
ok: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3', 'network': '10.1.8.0'})
ok: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3', 'network': '10.1.9.0'})
ok: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3', 'network': '10.1.10.0'})
changed: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3', 'network': '10.2.14.0'})
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device

PLAY RECAP **********************************************************************************************************************************************
ESW3                       : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## What I Learned

```text
traceroute 10.2.14.4
traceroute to 10.2.14.4 (10.2.14.4), 30 hops max, 60 byte packets
1  192.168.122.252 (192.168.122.252)  12.363 ms  12.235 ms  12.212 ms
2  10.0.0.14 (10.0.0.14)  29.461 ms  29.464 ms  29.443 ms
3  10.2.0.2 (10.2.0.2)  190.575 ms  190.568 ms  190.562 ms
4  10.2.0.6 (10.2.0.6)  190.547 ms  220.724 ms  220.718 ms
5  10.2.14.4 (10.2.14.4)  281.296 ms  311.465 ms  341.663 ms
```

- As we can see, we can now reach the VPC end devices from our host device.

### Saving the Configuration files

- Thanks to the universal write playbook we created earlier, saving the configuration details to all devices is now just executing a simple playbook.

```text
ansible-playbook -i hosts.ini write.yml

PLAY [Write to NVRAM] ***********************************************************************************************************************************

TASK [Create a backup of the running-config] ************************************************************************************************************
ok: [R1]
ok: [R2]
ok: [ESW2]
ok: [ESW1]
ok: [ESW3]
ok: [ESW5]
ok: [ESW4]
ok: [ESW6]
ok: [ESW7]
ok: [Esw11]
ok: [ESW9]
ok: [ESW8]
ok: [ESW10]
ok: [ESW12]
ok: [ESW14]
ok: [ESW13]

TASK [Save the running-config to a file] ****************************************************************************************************************
changed: [ESW2]
changed: [R1]
changed: [R2]
changed: [ESW3]
changed: [ESW1]
changed: [ESW4]
changed: [ESW8]
changed: [ESW7]
changed: [ESW6]
changed: [ESW5]
changed: [ESW9]
changed: [ESW10]
changed: [Esw11]
changed: [ESW12]
changed: [ESW13]
changed: [ESW14]

TASK [Copy running-config to startup-config] ************************************************************************************************************
ok: [R1]
ok: [R2]
ok: [ESW4]
ok: [ESW1]
ok: [ESW2]
ok: [ESW6]
ok: [ESW7]
ok: [ESW8]
ok: [ESW9]
ok: [ESW10]
ok: [Esw11]
ok: [ESW3]
ok: [ESW12]
ok: [ESW14]
ok: [ESW13]
ok: [ESW5]

TASK [print output] *************************************************************************************************************************************
ok: [R1] => {
    "msg": "R1: [['Warning: Attempting to overwrite an NVRAM configuration previously written', 'by a different version of the system image.', 'Overwrite the previous NVRAM configuration?[confirm]', 'Building configuration...', '[OK]']]"
}
ok: [R2] => {
    "msg": "R2: [['Warning: Attempting to overwrite an NVRAM configuration previously written', 'by a different version of the system image.', 'Overwrite the previous NVRAM configuration?[confirm]', 'Building configuration...', '[OK]']]"
}
ok: [ESW1] => {
    "msg": "ESW1: [['Building configuration...', '[OK]']]"
}
ok: [ESW2] => {
    "msg": "ESW2: [['Building configuration...', '[OK]']]"
}
ok: [ESW3] => {
    "msg": "ESW3: [['Building configuration...', '[OK]']]"
}
ok: [ESW4] => {
    "msg": "ESW4: [['Building configuration...', '[OK]']]"
}
ok: [ESW5] => {
    "msg": "ESW5: [['Building configuration...', '[OK]']]"
}
ok: [ESW6] => {
    "msg": "ESW6: [['Building configuration...', '[OK]']]"
}
ok: [ESW7] => {
    "msg": "ESW7: [['Building configuration...', '[OK]']]"
}
ok: [ESW8] => {
    "msg": "ESW8: [['Building configuration...', '[OK]']]"
}
ok: [ESW9] => {
    "msg": "ESW9: [['Building configuration...', '[OK]']]"
}
ok: [ESW10] => {
    "msg": "ESW10: [['Building configuration...', '[OK]']]"
}
ok: [Esw11] => {
    "msg": "Esw11: [['Building configuration...', '[OK]']]"
}
ok: [ESW12] => {
    "msg": "ESW12: [['Building configuration...', '[OK]']]"
}
ok: [ESW13] => {
    "msg": "ESW13: [['Building configuration...', '[OK]']]"
}
ok: [ESW14] => {
    "msg": "ESW14: [['Building configuration...', '[OK]']]"
}

PLAY RECAP **********************************************************************************************************************************************
ESW1                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW10                      : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW2                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW3                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R1                         : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R2                         : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Artifacts

- [endDevice.yml](../../artifacts/ansible/playbooks/endDevice.yml) — end-device port playbook
- [ospf.yml](../../artifacts/ansible/playbooks/ospf.yml) — OSPF distribution playbook

---
← [Day 16 · A Universal "Write" Playbook](16-universal-write-playbook.md) | [Day 18 · Syslog](18-syslog.md) →

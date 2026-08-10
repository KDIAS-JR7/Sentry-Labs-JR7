# Day 13 – Inter VLAN Routing via Ansible

> **Date:** 13 Apr 2026 · **Topic:** The `host_vars` folder — 16 SVIs without a 16-step copy-paste ritual · **Takeaway:** When per-device data gets too complex for a one-line inventory entry, Ansible gives you a dedicated place to put it.

[↑ Journal Index](../../README.md)

## The Goal

- In order for the newly created VLANs to communicate between each other, we need to set up inter VLAN routing.
- As before, this is done by creating an SVI in the distribution layers switches for each VLAN, setting up HSRP between the pairs of distribution layer switches connecting to one access layer switch to provide a single common IP address to be used as the default IP address.
- However.. Since we have 8 unique VLANs, four on each switch, the entire process must be repeated 4 x 4 times, of 16 times.
- This is a very long configuration process, which could also introduce human error due to its lengthy nature.
- Therefore, we will once again use an Ansible playbook for this.

## Ansible Playbook

```yaml
- name: Configure Inter-Vlan routing

hosts: Distribution_Switches

gather_facts: false


tasks:

- name: Create VLANs

cisco.ios.ios_command:

commands:

- command: 'vlan database'

- command: 'vlan {{ item.id }} name {{ item.name }}'

- command: 'exit'

loop: "{{vlans}}"

when: vlans is defined

- name: configure Trunks

cisco.ios.ios_config:

lines:

- interface range f1/1 - 4

- switchport mode trunk

- switchport trunk allowed vlan add {{ item.id }}

loop: "{{ vlans}}"

when: vlans is defined
```

- This playbook is written in order to configure each distribution layer switch with the corresponding VLANs.

## The Struggle

### A new problem

- However, there is slight deviation here from previous playbooks.
- Each distribution layer switch needs to be configured with 4 VLANs.
- For the access layer, we could just add the vlan ID, default gateway and name of each vlan directly to the line describing the inventory item in the hosts.ini file as follows.
>ESW7 ansible_host=10.1.99.7 vlan_id=7 vlan_name=Computing defaultGateway=10.1.7.3
- But we cannot follow the same method as there are four unique vlans to be configured for each switch compared to the single one in the access layer.

## The Solution

### host_vars folder

- To solve this, we will be using a host_vars folder which will contain a yaml file for each distribution layer switch detailing all of its VLANs.
>drwxr-xr-x. 1 kaveesh kaveesh 80 Apr 13 18:20 host_vars

#### Individual yaml files

- Each yaml file would look like follows

```yaml
vlans:

- id: 11

name: Computing

ip: 10.2.11.2

standby: 10.2.11.3


- id: 12

name: Technology

ip: 10.2.12.2

standby: 10.2.12.3


- id: 13

name: Agriculture

ip: 10.2.13.2

standby: 10.2.13.3

- id: 14

name: Engineering

ip: 10.2.14.2

standby: 10.2.14.3
```

- This file describes each vlan ESW6 will contain.

```bash
ls -l
total 16
-rw-r--r--. 1 kaveesh kaveesh 304 Apr 13 17:13 ESW3.yml
-rw-r--r--. 1 kaveesh kaveesh 304 Apr 13 17:13 ESW4.yml
-rw-r--r--. 1 kaveesh kaveesh 313 Apr 13 17:16 ESW5.yml
-rw-r--r--. 1 kaveesh kaveesh 313 Apr 13 17:17 ESW6.yml
-rw-r--r--. 1 kaveesh kaveesh   0 Apr 13 18:23 ESW7.yml
```

- The playbook loops through all the devices looking for the *vlans* item, then using item.id and item.date, it creates every VLAN automatically.

## Output

```text
ansible-playbook -i hosts.ini VLANDist.yml

PLAY [Configure Inter-Vlan routing] *****************************************************************************************************************

TASK [Create VLANs] *********************************************************************************************************************************
ok: [ESW6] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.2', 'standby': '10.2.11.3'})
ok: [ESW4] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.2', 'standby': '10.1.7.3'})
ok: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3'})
ok: [ESW4] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.2', 'standby': '10.1.8.3'})
ok: [ESW6] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.2', 'standby': '10.2.12.3'})
ok: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3'})
ok: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3'})
ok: [ESW4] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.2', 'standby': '10.1.9.3'})
ok: [ESW6] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.2', 'standby': '10.2.13.3'})
ok: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3'})
ok: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3'})
ok: [ESW6] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.2', 'standby': '10.2.14.3'})
ok: [ESW4] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.2', 'standby': '10.1.10.3'})
ok: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3'})
ok: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3'})
ok: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3'})

TASK [configure Trunks] *****************************************************************************************************************************
changed: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3'})
changed: [ESW4] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.2', 'standby': '10.1.7.3'})
changed: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3'})
changed: [ESW6] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.2', 'standby': '10.2.11.3'})
changed: [ESW4] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.2', 'standby': '10.1.8.3'})
changed: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3'})
changed: [ESW6] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.2', 'standby': '10.2.12.3'})
changed: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3'})
changed: [ESW4] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.2', 'standby': '10.1.9.3'})
changed: [ESW6] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.2', 'standby': '10.2.13.3'})
changed: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3'})
changed: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3'})
changed: [ESW6] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.2', 'standby': '10.2.14.3'})
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [ESW4] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.2', 'standby': '10.1.10.3'})
changed: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3'})
changed: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3'})

PLAY RECAP ******************************************************************************************************************************************
ESW3                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Artifacts

- [VLANDist.yml](../../artifacts/ansible/playbooks/VLANDist.yml) — the playbook
- [host_vars/ESW3.yml](../../artifacts/ansible/host_vars/ESW3.yml) — example per-device VLAN data

---
← [Day 12 · Access Layer VLANs via Ansible](12-access-layer-vlans-ansible.md) | [Day 14 · EtherChannel and Spanning Tree](14-etherchannel-and-stp.md) →

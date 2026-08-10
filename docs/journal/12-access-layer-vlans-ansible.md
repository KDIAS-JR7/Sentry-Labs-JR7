# Day 12 – Completing Access Layer VLAN Configurations

> **Date:** 13 Apr 2026 · **Topic:** 8 switches × 8 unique VLANs — by hand, or with one playbook · **Takeaway:** The moment Ansible stops being a demo and becomes the only sane way to do the job.

[↑ Journal Index](../../README.md)

## The Goal

- The access layer is made up of 8 switches. Each switch belongs to one unique VLAN from the list,
	1. vlan 7 - Computing
	2. vlan 8 - Technology
	3. vlan 9 - Agriculture
	4. vlan 10 - Engineering
	5. vlan 11 - AppliedScience
	6. vlan 12 - Management
	7. vlan 13 - Medicine
	8. vlan 14 - SocialScience
- The traditional way to complete this task is to iterate the steps found in [Day 10 – Access Layer and L2 Connectivity](10-access-layer-l2-connectivity.md#creating-vlans) for every switch.
- But since this method does not scale well with increasing number of switches, which in this case is 8, as there is a considerably lengthy configuration process that needs to be iterated.
- However, since the Management VLAN is now configured, we can now use Ansible.
- Therefore we will be using an Ansible playbook to automate this task instead.

## Automation using Ansible

### 1. Playbook

```yaml
- name: Configure unique VLANs

hosts: Access_Switches

gather_facts: false


tasks:

- name: Configure Vlans if not already configured

cisco.ios.ios_command:

commands:

- command: 'vlan database'

- command: 'vlan {{ vlan_id }} name {{ vlan_name }}'

- command: 'exit'

- command: 'show vlan-switch'

register: vlan_output

- name: configure trunk links

cisco.ios.ios_config:

lines:

- interface r f1/0 - 1

- switchport mode trunk

- switchport trunk allowed vlan add {{ vlan_id }}

- name: confirmation of vlan configuration

copy:

dest: "./test1Reports/{{inventory_hostname}}_vlan_report.txt"

content: |

===================================================================================================

Report for {{inventory_hostname}}

===================================================================================================

TASK: [Vlan configuration]

---------------------------------------------------------------------------------------------------

{{vlan_output.stdout_lines | to_nice_json}}
```

- This playbook uses two plays to create the unique VLANs in every switch and then also configure the trunk links.
- However, to run this, the hosts.ini file has to modified.

### 2. Hosts.ini

```ini
[allHosts]

R1 ansible_host=192.168.122.252

R2 ansible_host=10.0.0.2

ESW1 ansible_host=10.0.0.10

ESW2 ansible_host=10.0.0.20

ESW3 ansible_host=10.0.0.30

ESW4 ansible_host=10.0.0.40

ESW5 ansible_host=10.0.0.50

ESW6 ansible_host=10.0.0.60

ESW7 ansible_host=10.1.99.7

ESW8 ansible_host=10.1.99.8

ESW9 ansible_host=10.1.99.9

ESW10 ansible_host=10.1.99.10

Esw11 ansible_host=10.2.99.11

ESW12 ansible_host=10.2.99.12

ESW13 ansible_host=10.2.99.13

ESW14 ansible_host=10.2.99.14


[Edge_routers]

R1 ansible_host=192.168.122.252

R2 ansible_host=10.0.0.2


[Core_Switches]

ESW1 ansible_host=10.0.0.10

ESW2 ansible_host=10.0.0.20


[Distribution_Switches]

ESW3 ansible_host=10.0.0.30

ESW4 ansible_host=10.0.0.40

ESW5 ansible_host=10.0.0.50

ESW6 ansible_host=10.0.0.60


[Access_Switches]

ESW7 ansible_host=10.1.99.7 vlan_id=7 vlan_name=Computing

ESW8 ansible_host=10.1.99.8 vlan_id=8 vlan_name=Technology

ESW9 ansible_host=10.1.99.9 vlan_id=9 vlan_name=Agriculture

ESW10 ansible_host=10.1.99.10 vlan_id=10 vlan_name=Geomatics

Esw11 ansible_host=10.2.99.11 vlan_id=11 vlan_name=AppliedScience

ESW12 ansible_host=10.2.99.12 vlan_id=12 vlan_name=Management

ESW13 ansible_host=10.2.99.13 vlan_id=13 vlan_name=Medicine

ESW14 ansible_host=10.2.99.14 vlan_id=14 vlan_name=SocialScience


[allHosts:vars]

ansible_network_os=cisco.ios.ios

ansible_connection=network_cli

ansible_user=admin

ansible_password=cisco

ansible_become=yes

ansible_become_method=enable
```

- The file has been modified to include every IOS device in *allHosts*, while also using seperate lists for each layer(access,distribution,core and edge)
- The access layer switches now include each of their unique VLANs in the form of VLAN id and name.
- The playbook uses these two variables to create each VLAN and configure the trunk links.

## Output

```text
ansible-playbook -i hosts.ini vlans.yml

PLAY [Configure unique VLANs] ***********************************************************************************************************************

TASK [Configure Vlans if not already configured] ****************************************************************************************************
ok: [Esw11]
ok: [ESW12]
ok: [ESW9]
ok: [ESW10]
ok: [ESW8]
ok: [ESW7]
ok: [ESW13]
ok: [ESW14]

TASK [configure trunk links] ************************************************************************************************************************
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [Esw11]
changed: [ESW12]
changed: [ESW13]
changed: [ESW10]
changed: [ESW7]
changed: [ESW8]
changed: [ESW9]
changed: [ESW14]

TASK [confirmation of vlan configuration] ***********************************************************************************************************
ok: [ESW8]
ok: [Esw11]
ok: [ESW10]
ok: [ESW7]
ok: [ESW9]
ok: [ESW12]
ok: [ESW13]
ok: [ESW14]

PLAY RECAP ******************************************************************************************************************************************
ESW10                      : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Artifacts

- [vlans.yml](../../artifacts/ansible/playbooks/vlans.yml) — the playbook
- [hosts.ini](../../artifacts/ansible/hosts.ini) — inventory with layer groups + per-host VLAN vars

---
← [Day 11 · Management VLAN](11-management-vlan.md) | [Day 13 · Inter-VLAN Routing via Ansible](13-inter-vlan-routing-ansible.md) →

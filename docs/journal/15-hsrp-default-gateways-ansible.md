# Day 15 – HSRP and Default Gateways through Ansible

> **Date:** 15 Apr 2026 · **Topic:** 16 HSRP instances + 8 default gateways, done by playbook · **Takeaway:** What was a fragile, repetitive manual task on Day 10 is now a looping playbook fed by `host_vars`.

[↑ Journal Index](../../README.md)

## The Goal

- As previously stated in the [Day 13 – Inter VLAN routing via Ansible Problem Statement](13-inter-vlan-routing-ansible.md#the-goal), the next objective is to setup HSRP.
- To complete this task, we will be using yet another Ansible playbook as well as once again utilizing the host_vars folder.

## HSRP

### Playbook

```yaml
- name: configure HSRP for Inter Vlan Routing

hosts: Distribution_Switches

gather_facts: false


tasks:

- name: setup HSRP

cisco.ios.ios_config:

lines:

- interface vlan {{ item.id }}

- ip address {{ item.ip}} 255.255.255.0

- standby {{ item.id }} ip {{ item.standby }}

loop: "{{ vlans }}"

when: vlans is defined
```

- We are using the ios_config module to enter three commands in the global config mode to setup HSRP.
- The config files in the host_vars folder provide the item.id which is the VLAN id for the SVI, item.ip which is the IP address of the SVI as well as the item.standby, which is the standby IP for the HSRP instance.

### Output

```text
ansible-playbook -i hosts.ini VlanHSRP.yml

PLAY [configure HSRP for Inter Vlan Routing] ********************************************************************************************************

TASK [setup HSRP] ***********************************************************************************************************************************
changed: [ESW4] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.2', 'standby': '10.1.7.3'})
changed: [ESW5] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.1', 'standby': '10.2.11.3'})
changed: [ESW3] => (item={'id': 7, 'name': 'Computing', 'ip': '10.1.7.1', 'standby': '10.1.7.3'})
changed: [ESW6] => (item={'id': 11, 'name': 'Computing', 'ip': '10.2.11.2', 'standby': '10.2.11.3'})
changed: [ESW4] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.2', 'standby': '10.1.8.3'})
changed: [ESW5] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.1', 'standby': '10.2.12.3'})
changed: [ESW6] => (item={'id': 12, 'name': 'Technology', 'ip': '10.2.12.2', 'standby': '10.2.12.3'})
changed: [ESW3] => (item={'id': 8, 'name': 'Technology', 'ip': '10.1.8.1', 'standby': '10.1.8.3'})
changed: [ESW4] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.2', 'standby': '10.1.9.3'})
changed: [ESW3] => (item={'id': 9, 'name': 'Agriculture', 'ip': '10.1.9.1', 'standby': '10.1.9.3'})
changed: [ESW5] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.1', 'standby': '10.2.13.3'})
changed: [ESW6] => (item={'id': 13, 'name': 'Agriculture', 'ip': '10.2.13.2', 'standby': '10.2.13.3'})
changed: [ESW4] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.2', 'standby': '10.1.10.3'})
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [ESW3] => (item={'id': 10, 'name': 'Engineering', 'ip': '10.1.10.1', 'standby': '10.1.10.3'})
changed: [ESW5] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.1', 'standby': '10.2.14.3'})
changed: [ESW6] => (item={'id': 14, 'name': 'Engineering', 'ip': '10.2.14.2', 'standby': '10.2.14.3'})

PLAY RECAP ******************************************************************************************************************************************
ESW3                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

- As seen in the output the playbook succefuly setup HSRP for 4 SVIs in each switch for four switches; which means ran the HSRP configuration 16 times automatically.

## Default gateways

- Now that each distribution layer switch is properly configured, the next step is to log into each access layer switch and configure the respective default gateways...

### Playbook

- Or use another playbook,

```yaml
- name: setup Default Gateways

hosts: Access_Switches

gather_facts: false


tasks:

- name: Enter Default Gateway

cisco.ios.ios_config:

lines:

- ip default-gateway {{defaultGateway}}
```

### Output

```text
ansible-playbook -i hosts.ini defaultGateway.yml

PLAY [setup Default Gateways] ***********************************************************************************************************************

TASK [Enter Default Gateway] ************************************************************************************************************************
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [Esw11]
changed: [ESW12]
changed: [ESW9]
changed: [ESW10]
changed: [ESW8]
changed: [ESW7]
changed: [ESW13]
changed: [ESW14]

PLAY RECAP ******************************************************************************************************************************************
ESW10                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Artifacts

- [VlanHSRP.yml](../../artifacts/ansible/playbooks/VlanHSRP.yml) — HSRP playbook
- [defaultGateway.yml](../../artifacts/ansible/playbooks/defaultGateway.yml) — default gateway playbook

---
← [Day 14 · EtherChannel and Spanning Tree](14-etherchannel-and-stp.md) | [Day 16 · A Universal "Write" Playbook](16-universal-write-playbook.md) →

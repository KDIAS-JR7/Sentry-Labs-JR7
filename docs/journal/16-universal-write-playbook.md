# Day 16 – A Universal "Write" Playbook

> **Date:** 15 Apr 2026 · **Topic:** The single most simple, yet most useful playbook in the project · **Takeaway:** Saving config on 16 devices is exactly the kind of "trivial" task that human memory is worst at — automation turns anxiety into a log.

[↑ Journal Index](../../README.md)

## The Goal

- One of the most daunting task in managing and configuring a large network is to save the configuration changes from RAM to NVRAM.
- This is done by logging into each device and entering either,
	1. write
	2. do write, if you are in a higher level
	3. copy run start
- This is very tedious, and since we have 16 device in our network topology, we have to repeat this process 16 times.
- This could also mean that we could accidentally forget one device along the way and also lead to much anxiety of telling ourselves that we did in fact save the configuration on each device, after all, its such a simple command, right?
- This is where I decided to offload this to Ansible instead, by using what I consider as the single most simple, yet most useful playbook I will be writing in this project.

## The playbook

```yaml
- name: Write to NVRAM

hosts: allHosts

gather_facts: true


tasks:

- name: Create a backup of the running-config

cisco.ios.ios_command:

commands:

- command: 'show running-config'

register: running_config_output

- name: Save the running-config to a file


copy:

content: "{{ running_config_output.stdout | to_nice_json }}"

dest: "./runningConfigs/backup_{{ inventory_hostname }}_{{ now(utc=true,fmt='%Y-%m-%d %H:%M:%S') }}.txt"

- name: Copy running-config to startup-config

cisco.ios.ios_command:

commands:

- command: 'write'

prompt: '[confirm]'

answer: "\r"


register: write_output

- name: print output

debug:

msg: "{{ inventory_hostname }}: {{ write_output.stdout_lines }}"
```

- This playbook loops through the entire network and does an extremely simple thing. Enter 'write'.
- However, the Edge routers R1 and R2 requires us to enter a confirmation for the write command. We fix this by using this block,

```yaml
prompt: '[confirm]'

answer: "\r"
```

- Now, if any device asks for 'confirm' when write is given, the playbook will press enter and complete the process.
- It also creates a backup of the current running config in the NVRAM first, as a safety measure.

## Output

```text
ansible-playbook -i hosts.ini write.yml

PLAY [Write to NVRAM] *******************************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************
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
ok: [ESW8]
ok: [ESW9]
ok: [ESW12]
ok: [ESW10]
ok: [ESW13]
ok: [ESW14]

TASK [Create a backup of the running-config] ********************************************************************************************************
ok: [ESW2]
ok: [ESW1]
ok: [ESW3]
ok: [R1]
ok: [R2]
ok: [ESW4]
ok: [ESW5]
ok: [ESW6]
ok: [ESW7]
ok: [ESW8]
ok: [ESW9]
ok: [Esw11]
ok: [ESW10]
ok: [ESW12]
ok: [ESW13]
ok: [ESW14]

TASK [Save the running-config to a file] ************************************************************************************************************
changed: [ESW3]
changed: [ESW1]
changed: [ESW2]
changed: [R1]
changed: [R2]
changed: [ESW4]
changed: [ESW7]
changed: [ESW6]
changed: [ESW5]
changed: [ESW8]
changed: [ESW9]
changed: [Esw11]
changed: [ESW10]
changed: [ESW12]
changed: [ESW13]
changed: [ESW14]

TASK [Copy running-config to startup-config] ********************************************************************************************************
ok: [R2]
ok: [R1]
ok: [ESW2]
ok: [ESW1]
ok: [ESW3]
ok: [ESW4]
ok: [ESW5]
ok: [ESW7]
ok: [ESW6]
ok: [ESW8]
ok: [ESW9]
ok: [ESW10]
ok: [Esw11]
ok: [ESW12]
ok: [ESW13]
ok: [ESW14]

TASK [print output] *********************************************************************************************************************************
ok: [R1] => {
    "msg": "R1: [['Building configuration...', '[OK]']]"
}
ok: [R2] => {
    "msg": "R2: [['Building configuration...', '[OK]']]"
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

PLAY RECAP ******************************************************************************************************************************************
ESW1                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW10                      : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW2                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW3                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R1                         : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R2                         : ok=5    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## What I Learned

- And with that, we have taken logging into 16 different switches to a single command to run an Ansible playbook.
- At the same time,

```bash
ls -l
total 64
-rw-r--r--. 1 kaveesh kaveesh 3045 Apr 15 12:52 'backup_ESW10_2026-04-15 07:22:00.txt'
-rw-r--r--. 1 kaveesh kaveesh 3045 Apr 15 12:52 'backup_Esw11_2026-04-15 07:22:00.txt'
-rw-r--r--. 1 kaveesh kaveesh 3183 Apr 15 12:51 'backup_ESW1_2026-04-15 07:21:57.txt'
-rw-r--r--. 1 kaveesh kaveesh 3045 Apr 15 12:52 'backup_ESW12_2026-04-15 07:22:00.txt'
-rw-r--r--. 1 kaveesh kaveesh 3045 Apr 15 12:52 'backup_ESW13_2026-04-15 07:22:00.txt'
-rw-r--r--. 1 kaveesh kaveesh 3045 Apr 15 12:52 'backup_ESW14_2026-04-15 07:22:01.txt'
-rw-r--r--. 1 kaveesh kaveesh 3117 Apr 15 12:51 'backup_ESW2_2026-04-15 07:21:57.txt'
-rw-r--r--. 1 kaveesh kaveesh 3837 Apr 15 12:51 'backup_ESW3_2026-04-15 07:21:57.txt'
-rw-r--r--. 1 kaveesh kaveesh 3872 Apr 15 12:52 'backup_ESW4_2026-04-15 07:21:59.txt'
-rw-r--r--. 1 kaveesh kaveesh 3750 Apr 15 12:52 'backup_ESW5_2026-04-15 07:21:59.txt'
-rw-r--r--. 1 kaveesh kaveesh 3710 Apr 15 12:52 'backup_ESW6_2026-04-15 07:21:59.txt'
-rw-r--r--. 1 kaveesh kaveesh 3123 Apr 15 12:52 'backup_ESW7_2026-04-15 07:21:59.txt'
-rw-r--r--. 1 kaveesh kaveesh 3069 Apr 15 12:52 'backup_ESW8_2026-04-15 07:21:59.txt'
-rw-r--r--. 1 kaveesh kaveesh 3042 Apr 15 12:52 'backup_ESW9_2026-04-15 07:22:00.txt'
-rw-r--r--. 1 kaveesh kaveesh 1737 Apr 15 12:51 'backup_R1_2026-04-15 07:21:57.txt'
-rw-r--r--. 1 kaveesh kaveesh 1656 Apr 15 12:51 'backup_R2_2026-04-15 07:21:57.txt'
```

- It also created the backup files for the previous running config files as well.

## Artifacts

- [write.yml](../../artifacts/ansible/playbooks/write.yml) — the universal write playbook

---
← [Day 15 · HSRP and Default Gateways via Ansible](15-hsrp-default-gateways-ansible.md) | [Day 17 · Access Layer Interface Configuration](17-access-layer-interface-config.md) →

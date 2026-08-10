# Day 09 – Ansible Day 1

> **Date:** 04 Apr 2026 · **Topic:** The tool that makes "16 devices" a non-issue · **Takeaway:** Idempotency is not a buzzword — it's the reason re-running a playbook is safe.

[↑ Journal Index](../../README.md)

## The Goal

Stop logging into devices one at a time.

## Why automate?

- Large enterprise networks consists of dozens of routers and switches spread across a large area.
- Traditionally, even a simple command such as *show ip int br* which outputs all the ip addresses installed in a device requires one to manually connect into said device either through a console cable or ssh, type and run the command.
- For an extremely simple network, this is fine. But, this traditional method scales poorly with network size.
- For a network of 10 + devices and multiple subnets, even a simple command such as the above requires a large amount of time and effort and also introduces many more chances for human error.
- Network automation allows to simplify this process to almost a single command.

## Ansible?

- [ ] Ansible is an industry standard, open source automation platform.
- With ansible playbooks, one can manage a large number of devices with a single command right from their own computer.

## Ansible Installation

- On fedora systems, ansible can be installed with a simple,

```bash
$ sudo dnf install ansible
```

- It can also be installed through pip as well.
- The ansible-core can also be installed instead for a minimal installation if required.

## Ansible usage

### Hosts.ini

- Ansible uses hosts.ini file to detail the devices the playbooks will be managing.
- Multiple hosts.ini files can be used to manage different groups of devices if needed, however, for this project, only one file will be used.

```ini
[routers]

R1 ansible_host=10.0.0.1

R2 ansible_host=10.0.0.2

ESW1 ansible_host=10.0.0.10

ESW2 ansible_host=10.0.0.20

ESW3 ansible_host=10.0.0.30

ESW4 ansible_host=10.0.0.40

ESW5 ansible_host=10.0.0.50

ESW6 ansible_host=10.0.0.60


[routers:vars]

ansible_network_os=cisco.ios.ios

ansible_connection=network_cli

ansible_user=admin

ansible_password=cisco

ansible_become=yes

ansible_become_method=enable
```

- Each device is includes as an *ansible_host* in the format,
> name ansible_host = ip addresses
- In the file, all routers and multilayer switches are included under routers.
- Additional details such as the username and passwords for ssh are currently included under routers:vars

### ansible.cfg

- Ansible.cfg is a configuration file for ansible.

```ini
[defaults]

# This skips the 'yes/no' prompt

host_key_checking = False


[ssh_connection]

# This adds the algorithms your Fedora laptop normally blocks

ssh_args = -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa


# Optional: Stop those annoying deprecation warnings

deprecation_warnings = False


# Ensure it uses the right Python interpreter

interpreter_python = auto_silent
```

- This ansible.cfg file is important for the project specifically for the,
>ssh_args = -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa
- This ensures that ios devices that use older encryption standard can still be used within the project.

### First playbook

```yaml
- name: Practice 1 - Execute show via ssh

hosts: routers

gather_facts: false


tasks:

- name: show ip interface brief

cisco.ios.ios_command:

commands:

- show ip interface brief

register: router_output


- name: print report

copy:

dest: "./test1Reports/{{inventory_hostname}}_report.txt"

content: |

===================================================================================================

Report for {{inventory_hostname}}

===================================================================================================

TASK: [Show ip interface brief]

---------------------------------------------------------------------------------------------------

{{router_output.stdout_lines[0] | to_nice_json}}
```

- Ansible playbooks are written in YAML language.
- This simple playbook is used to connect to each device in the hosts file and execute *sh ip int brief*, then save each output into a separate text file.
- The output for a running this sample playbook,

```text
ansible-playbook -i hosts.ini practice1.yml

PLAY [Practice 1 - Execute show via ssh] *************************************************************************************************************************************

TASK [show ip interface brief] ***********************************************************************************************************************************************
ok: [R2]
ok: [R1]
ok: [ESW2]
ok: [ESW1]
ok: [ESW3]
ok: [ESW4]
ok: [ESW5]
ok: [ESW6]

TASK [print report] **********************************************************************************************************************************************************
changed: [R2]
changed: [ESW3]
changed: [R1]
changed: [ESW2]
changed: [ESW1]
changed: [ESW5]
changed: [ESW4]
changed: [ESW6]

PLAY RECAP *******************************************************************************************************************************************************************
ESW1                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW2                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW3                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R1                         : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R2                         : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

- However, if we ran it again without changing the network configurations..

```text
ansible-playbook -i hosts.ini practice1.yml

PLAY [Practice 1 - Execute show via ssh] ************************************************************************************************************************************************************************************

TASK [show ip interface brief] **********************************************************************************************************************************************************************************************
ok: [R1]
ok: [R2]
ok: [ESW2]
ok: [ESW1]
ok: [ESW3]
ok: [ESW5]
ok: [ESW4]
ok: [ESW6]

TASK [print report] *********************************************************************************************************************************************************************************************************
ok: [ESW2]
ok: [ESW3]
ok: [R1]
ok: [ESW1]
ok: [R2]
ok: [ESW5]
ok: [ESW4]
ok: [ESW6]

PLAY RECAP ******************************************************************************************************************************************************************************************************************
ESW1                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW2                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW3                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R1                         : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R2                         : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## What I Learned

- Here, none of the files were changed. why? because ansible is idempotent. Which means, if there is no modification to be made, ansible will not touch the files. This is a feature of ansible that further establishes as an industry standard.
- As stated above, the playbook saves the output into a text file.

```bash
ls -l
total 32
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW1_report.txt
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW2_report.txt
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW3_report.txt
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW4_report.txt
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW5_report.txt
-rw-r--r--. 1 kaveesh kaveesh 2279 Apr  4 22:48 ESW6_report.txt
-rw-r--r--. 1 kaveesh kaveesh  961 Apr  4 22:48 R1_report.txt
-rw-r--r--. 1 kaveesh kaveesh  961 Apr  4 22:48 R2_report.txt
```

```text
===================================================================================================
Report for R1
===================================================================================================

TASK: [Show ip interface brief]
---------------------------------------------------------------------------------------------------
[
    "Interface              IP-Address      OK? Method Status                Protocol",
    "FastEthernet0/0        10.1.0.1        YES NVRAM  up                    up      ",
    "FastEthernet0/1        10.0.0.13       YES NVRAM  up                    up      ",
    "FastEthernet1/0        unassigned      YES NVRAM  administratively down down    ",
    "FastEthernet1/1        unassigned      YES NVRAM  administratively down down    ",
    "GigabitEthernet2/0     192.168.122.252 YES NVRAM  up                    up      ",
    "Loopback0              10.0.0.1        YES NVRAM  up                    up"
]
```

## Artifacts

- [practice1.yml](../../artifacts/ansible/playbooks/practice1.yml) — the first playbook

---
← [Day 08 · Topology Redesign — Spine-Leaf](08-topology-redesign-spine-leaf.md) | [Day 10 · Access Layer and L2 Connectivity](10-access-layer-l2-connectivity.md) →

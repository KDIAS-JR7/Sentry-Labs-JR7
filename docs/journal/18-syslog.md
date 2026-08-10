# Day 18 – Syslog

> **Date:** 30 Apr 2026 · **Topic:** Shipping syslog off-box to the host · **Takeaway:** IOS gives you syslog for free in the terminal — getting it off the device onto your own collector is a networking problem too (UDP, ports, firewalls).

[↑ Journal Index](../../README.md)

## The Goal

- A major requirement in the project is to show syslog messages within the web gui interface.
- Syslog messages are also important for troubleshooting purposes and to alert the user of an undesirable event straight from the gui.
- Therefor, a proper syslog implementation is necessary.

## Syslog in IOS

```bash
ESW14(config-if)#no shut
ESW14(config-if)#
.Apr 30 11:30:52.664: %LINK-3-UPDOWN: Interface FastEthernet1/3, cha
nged state to up
```

- The above snippet shows how syslog is automatically implemented within Cisco IOS.
- The particular message is the result of the FastEthernet1/3 interface being administratively turned on.
- However, this is only available in the terminal interface of IOS.
- What we need is to transport this message to our host machine.

## Playbook - syslog.yml

```yaml
- name: configure syslog

hosts: allHosts

gather_facts: false


tasks:

- name: push syslog configuration

cisco.ios.ios_config:

lines:

- logging host 192.168.122.1 transport udp port 10514

- logging trap 5

- logging facility local7

- service timestamps log datetime msec
```

- This playbook configures all 16 IOS devices(allHosts) to transport their syslog messages to the host device which is listening on virbr0 interface through IP address 192.168.122.1.
- We're sending every syslog message from level 5 and above.
	- **0 - Emergency (Panic):** The system is unusable.
	- **1 - Alert:** Immediate action is required.
	- **2 - Critical:** Critical conditions, such as hard device errors.
	- **3 - Error:** Error conditions.
	- **4 - Warning:** Warning messages.
	- **5 - Notice:** Significant, normal, or non-critical events.
	- **6 - Informational:** General information messages.
	- **7 - Debug:** Messages useful for debugging.
- We're also including timestamps in the syslog messages.

### output

```text
ansible-playbook -i hosts.ini syslog.yml

PLAY [configure syslog] ***********************************************************************************************************************

TASK [push syslog configuration] **************************************************************************************************************
[WARNING]: To ensure idempotency and correct diff the input configuration lines should be similar to how they appear if present in the running
configuration on device
changed: [R1]
changed: [R2]
changed: [ESW2]
changed: [ESW1]
changed: [ESW4]
changed: [ESW5]
changed: [ESW6]
changed: [ESW3]
changed: [ESW7]
changed: [Esw11]
changed: [ESW9]
changed: [ESW10]
changed: [ESW8]
changed: [ESW12]
changed: [ESW13]
changed: [ESW14]

PLAY RECAP ************************************************************************************************************************************
ESW1                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW10                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW12                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW13                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW14                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW2                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW3                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW4                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW5                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW6                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW7                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW8                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
ESW9                       : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
Esw11                      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R1                         : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
R2                         : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## The Solution

### Syslog-ng

- In order to catch and log syslog messages within the host machine we will be using the syslog-ng tool.

#### Custom config file - gns3_lab.conf

```text
# 1. Define where to listen

source s_gns3_network {

udp(ip("192.168.122.1") port(10514) so-rcvbuf(1048576));

};

# 2. Define where and how to save the files

destination d_gns3_nodes {

file("/home/kaveesh/Documents/University/University notes/2nd Year/4th semester/Obsidian/FIS smester 4/Capstone Project/Ansible/Test 1/syslog/$HOST/debug.log" create-dirs(yes));

};

# 3. Bind them together

log {

source(s_gns3_network);

destination(d_gns3_nodes);

};
```

- Above is the custom syslog-ng config file we will be using.
- It matches the port and source Ip address we previously configured on IOS using the playbook.
- We can start the syslog-ng process with,
>syslog-ng -F -f gns3_lab.conf --stderr
- Here, gns3_lab.conf is the custom config file we are using.

```text
syslog-ng -F -f gns3_lab.conf --stderr
[2026-04-30T12:05:12.914613] Setting current version as config version; version='4.9'
[2026-04-30T12:05:12.914613] syslog-ng starting up; version='4.9.0'
```

### Firewalld

- On fedora, Firewalld the firewall is extremely strict. Therefore we have to tell firewalld to allow syslog-ng.

```bash
sudo firewall-cmd --permanent --add-port=10514/udp
success
┌─[kaveesh@fedora] - [~] - [Thu Apr 30, 16:59]
└─[$] <> sudo firewall-cmd --reload
success
```

## Artifacts

- [syslog.yml](../../artifacts/ansible/playbooks/syslog.yml) — the syslog playbook

---
← [Day 17 · Access Layer Interface Configuration](17-access-layer-interface-config.md) | [Day 18 · End](18-syslog.md) →

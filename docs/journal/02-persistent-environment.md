# Day 02 – Persistent Environment

> **Date:** 02 Mar 2026 · **Topic:** From throwaway `--rm` containers to a persistent, reproducible build · **Takeaway:** Every ad-hoc fix you don't make persistent is a tax you pay on every future run.

[↑ Journal Index](../../README.md)

## The Goal

Stop re-downloading and re-configuring the container every single time.

## The Problem

- Previously, the Alpine Linux container was created using the **podman run --rm** command.
- This command destroyed the container once the task was complete, which created a number of issues;
	1. Having to download packages every time(ex: openssh)
	2. Having to configure everything all over again
- In order to remediate this issue, we'll be moving onto using a docker file and a persistent container instead.

```dockerfile
FROM alpine:latest

# Install all dependencies at build time so they are ready for the demo
RUN apk add --no-cache openssh-client python3 py3-pip

# Create the SSH directory and copy your pre-configured shortcut
RUN mkdir -p /root/.ssh
COPY ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config

# Set the work directory for your Python/Ansible scripts
WORKDIR /app

# Start in a shell
CMD ["sh"]
```

- The created docker file can be used to initialize and run a the podman container using

```bash
podman run -it --name sentry-demo --network=host sentry-watchman:v1
```

## Abstraction of SSH

- Instead of typing a 3-line command with complex encryption flags, we will be using a **Configuration Alias**.
- A ssh config file is used for this.

```text
Host R1
    HostName 192.168.122.30
    User admin
    Ciphers +aes128-cbc
    KexAlgorithms +diffie-hellman-group14-sha1
    HostKeyAlgorithms +ssh-rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

- Using this, the SSH connection into R1 can be achieved through a simple **ssh R1** command within the Alpine container.
- This also further complements the next the step of the project; integration of the Netmiko python library.

## Netmiko Integration

- To integrate Netmiko, the docker file is changed slightly.

```dockerfile
FROM alpine:latest

# Install system dependencies
RUN apk add --no-cache openssh-client python3 py3-pip build-base python3-dev

# Install Netmiko (The automation engine)
RUN pip install --no-cache-dir netmiko --break-system-packages

# Create the SSH directory and copy your pre-configured shortcut
RUN mkdir -p /root/.ssh
COPY ssh_config /root/.ssh/config
RUN chmod 600 /root/.ssh/config

WORKDIR /app
CMD ["sh"]
```

- This creates a new Alpine container with Netmiko built-in.
- A python script(**check_connection.py**) is created in the project directory to use the built-in Netmiko to poll the router R1 and output information.

```python
from netmiko import ConnectHandler

# Define the device using the alias we set up in ssh_config
device = {
    'device_type': 'cisco_ios',
    'host': 'R1',
    'username': 'admin',
    'password': 'cisco123',
    'ssh_config_file': '/root/.ssh/config', # Explicitly point to our "Abstraction" file
}

try:
    print("--- Connecting to Sentry-Pod Node: R1 ---")
    connection = ConnectHandler(**device)

    # Send a command to verify
    output = connection.send_command("show ip int br")

    print("Connection Successful! Output:")
    print("-" * 30)
    print(output)
    print("-" * 30)

    connection.disconnect()
except Exception as e:
    print(f"Connection Failed: {e}")
```

- The container is then rebuilt with all the dependencies(Ex; openssh and Netmiko)

```bash
podman build -t sentry-watchman:v2 .
```

```bash
podman build -t sentry-watchman:v2 .
STEP 1/8: FROM alpine:latest
STEP 2/8: RUN apk add --no-cache openssh-client python3 py3-pip build-base python3-dev
( 1/50) Installing libgcc (15.2.0-r2)
( 2/50) Installing jansson (14.14.0-r0)
( 3/50) Installing libstdc++ (15.2.0-r2)
( 4/50) Installing zstd-libs (1.5.7-r2)
( 5/50) Installing binutils (2.45.1-r0)
( 6/50) Installing libmagic (5.46-r2)
( 7/50) Installing file (5.46-r2)
( 8/50) Installing libgomp (15.2.0-r2)
( 9/50) Installing libatomic (15.2.0-r2)
(10/50) Installing gmp (6.3.0-r4)
(11/50) Installing isl26 (0.26-r1)
(12/50) Installing mpfr4 (4.2.2-r0)
(13/50) Installing mpc1 (1.3.1-r1)
(14/50) Installing gcc (15.2.0-r2)
(15/50) Installing libstdc++-dev (15.2.0-r2)
(16/50) Installing musl-dev (1.2.5-r21)
(17/50) Installing g++ (15.2.0-r2)
(18/50) Installing make (4.4.1-r3)
(19/50) Installing fortify-headers (1.1-r5)
(20/50) Installing patch (2.8-r0)
(21/50) Installing build-base (0.5-r3)
(22/50) Installing openssh-keygen (10.2_p1-r0)
(23/50) Installing ncurses-terminfo-base (6.5_p20251123-r0)
(24/50) Installing libncursesw (6.5_p20251123-r0)
(25/50) Installing libedit (20251016.3.1-r0)
(26/50) Installing openssh-client-common (10.2_p1-r0)
(27/50) Installing openssh-client-default (10.2_p1-r0)
(28/50) Installing libbz2 (1.0.8-r6)
(29/50) Installing libexpat (2.7.4-r0)
(30/50) Installing libffi (3.5.2-r0)
(31/50) Installing gdbm (1.26-r0)
(32/50) Installing xz-libs (5.8.2-r0)
(33/50) Installing mpdecimal (4.0.1-r0)
(34/50) Installing libpanelw (6.5_p20251123-r0)
(35/50) Installing libncursesw (6.5_p20251123-r0)
(36/50) Installing readline (8.3.1-r0)
(37/50) Installing sqlite-libs (3.51.2-r0)
(38/50) Installing python3 (3.12.12-r0)
(39/50) Installing python3-pycache-pyc0 (3.12.12-r0)
(40/50) Installing pyc (3.12.12-r0)
(41/50) Installing py3-setuptools-pyc (80.9.0-r2)
(42/50) Installing py3-pip-pyc (25.1.1-r1)
(43/50) Installing py3-packaging-pyc (25.0-r0)
(44/50) Installing python3-pyc (3.12.12-r0)
(45/50) Installing py3-parsing (3.2.5-r0)
(46/50) Installing py3-parsing-pyc (3.2.5-r0)
(47/50) Installing py3-packaging (25.0-r0)
(48/50) Installing py3-setuptools (80.9.0-r2)
(49/50) Installing py3-pip (25.1.1-r1)
(50/50) Installing pkgconf (2.5.1-r0)
Executing busybox-1.37.0-r30.trigger
OK: 378.4 MiB in 66 packages
--> 144704f781fe
STEP 3/8: RUN pip install --no-cache-dir netmiko --break-system-packages
Collecting netmiko
 Downloading netmiko-4.6.0-py3-none-any.whl.metadata (8.2 kB)
Collecting ntc-templates>=3.1.0 (from netmiko)
 Downloading ntc_templates-9.0.0-py3-none-any.whl.metadata (4.2 kB)
Collecting paramiko>=2.9.5 (from netmiko)
 Downloading paramiko-4.0.0-py3-none-any.whl.metadata (3.9 kB)
Collecting pyserial>=3.3 (from netmiko)
 Downloading pyserial-3.5-py2.py3-none-any.whl.metadata (1.6 kB)
Collecting pyyaml>=6.0.2 (from netmiko)
 Downloading pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl.metadata (2.4 kB)
Collecting rich>=13.8 (from netmiko)
 Downloading rich-14.3.3-py3-none-any.whl.metadata (18 kB)
Collecting ruamel.yaml>=0.17 (from netmiko)
 Downloading ruamel_yaml-0.19.1-py3-none-any.whl.metadata (16 kB)
Collecting scp>=0.13.6 (from netmiko)
 Downloading scp-0.15.0-py2.py3-none-any.whl.metadata (4.3 kB)
Collecting textfsm>=1.1.3 (from netmiko)
 Downloading textfsm-2.1.0-py2.py3-none-any.whl.metadata (2.7 kB)
Collecting bcrypt>=3.2 (from paramiko>=2.9.5->netmiko)
 Downloading bcrypt-5.0.0-cp39-abi3-musllinux_1_2_x86_64.whl.metadata (10 kB)
Collecting cryptography>=3.3 (from paramiko>=2.9.5->netmiko)
 Downloading cryptography-46.0.5-cp311-abi3-musllinux_1_2_x86_64.whl.metadata (5.7 kB)
Collecting invoke>=2.0 (from paramiko>=2.9.5->netmiko)
 Downloading invoke-2.2.1-py3-none-any.whl.metadata (3.3 kB)
Collecting pynacl>=1.5 (from paramiko>=2.9.5->netmiko)
 Downloading pynacl-1.6.2-cp38-abi3-musllinux_1_2_x86_64.whl.metadata (10.0 kB)
Collecting cffi>=2.0.0 (from cryptography>=2.9.5->paramiko>=2.9.5->netmiko)
 Downloading cffi-2.0.0-cp312-cp312-musllinux_1_2_x86_64.whl.metadata (2.6 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography>=3.3->paramiko>=2.9.5->netmiko)
 Downloading pycparser-3.0-py3-none-any.whl.metadata (2.8 kB)
Collecting markdown-it-py>=2.2.0 (from rich>=13.8->netmiko)
 Downloading markdown_it_py-4.0.0-py3-none-any.whl.metadata (7.3 kB)
Collecting pygments<3.0.0,>=2.13.0 (from rich>=13.8->netmiko)
 Downloading pygments-2.19.2-py3-none-any.whl.metadata (2.5 kB)
Collecting mdurl~=0.1 (from markdown-it-py>=2.2.0->rich>=13.8->netmiko)
 Downloading mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Downloading netmiko-4.6.0-py3-none-any.whl (262 kB)
Downloading ntc_templates-9.0.0-py3-none-any.whl (642 kB)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 642.1/642.1 kB 1.3 MB/s eta 0:00:00
Downloading paramiko-4.0.0-py3-none-any.whl (223 kB)
Downloading bcrypt-5.0.0-cp39-abi3-musllinux_1_2_x86_64.whl (359 kB)
Downloading cryptography-46.0.5-cp311-abi3-musllinux_1_2_x86_64.whl (4.7 MB)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.7/4.7 MB 1.3 MB/s eta 0:00:00
Downloading cffi-2.0.0-cp312-cp312-musllinux_1_2_x86_64.whl (221 kB)
Downloading invoke-2.2.1-py3-none-any.whl (160 kB)
Downloading pynacl-1.6.2-cp38-abi3-musllinux_1_2_x86_64.whl (1.4 MB)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 1.7 MB/s eta 0:00:00
Downloading pyserial-3.5-py2.py3-none-any.whl (90 kB)
Downloading pyyaml-6.0.3-cp312-cp312-musllinux_1_2_x86_64.whl (790 kB)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 790.2/790.2 kB 1.2 MB/s eta 0:00:00
Downloading rich-14.3.3-py3-none-any.whl (310 kB)
Downloading pygments-2.19.2-py3-none-any.whl (1.2 MB)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 1.2 MB/s eta 0:00:00
Downloading markdown_it_py-4.0.0-py3-none-any.whl (87 kB)
Downloading mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Downloading ruamel_yaml-0.19.1-py3-none-any.whl (118 kB)
Downloading scp-0.15.0-py2.py3-none-any.whl (8.8 kB)
Downloading textfsm-2.1.0-py2.py3-none-any.whl (44 kB)
Downloading pycparser-3.0-py3-none-any.whl (48 kB)
Installing collected packages: textfsm, pyserial, ruamel.yaml, pyyaml, pygments, pycparser, ntc-templates, mdurl, invoke, bcrypt, markdown-it-py, cffi, rich, pynacl, cryptography, paramiko, scp, netmiko

Successfully installed bcrypt-5.0.0 cffi-2.0.0 cryptography-46.0.5 invoke-2.2.1 markdown-it-py-4.0.0 mdurl-0.1.2 netmiko-4.6.0 ntc-templates-9.0.0 paramiko-4.0.0 pycparser-3.0 pygments-2.19.2 pynacl-1.6.2 pyserial-3.5 pyyaml-6.0.3 rich-14.3.3 ruamel.yaml-0.19.1 scp-0.15.0 textfsm-2.1.0
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
--> bebbe4486f39
STEP 4/8: RUN mkdir -p /root/.ssh
--> 5b63bd10ec20
STEP 5/8: COPY ssh_config /root/.ssh/config
--> 18fd11d5744b
STEP 6/8: RUN chmod 600 /root/.ssh/config
--> 108184a1d305
STEP 7/8: WORKDIR /app
--> 276646055106
STEP 8/8: CMD ["sh"]
COMMIT sentry-watchman:v2
--> 4175d3b3271d
Successfully tagged localhost/sentry-watchman:v2
4175d3b3271d487d98a102425cc38f4ed4b5a6cf86813ccaca282a7e283adfdf
```

- The output further emphasize the need for a persistent container. Otherwise, **378.4 MiB in 66 packages** will happen every time the container is started.
- Run and map the current directory to /app inside the container

```bash
podman run -it --rm --network=host -v .:/app:Z sentry-watchman:v2 python3 check_connection.py
```

- The **check_connection.py** script uses *connection.send_command()* as an interface to send a command to R1.
- Currently the *connection.send_command()* uses an *ios command* **show ip int br**, short for **show ip interface brief**. The command polls the *running config* and displays a short report on the current state of the layer 3 interfaces.
- The `:Z` suffix in the volume mapping is utilized to relabel the files for SELinux compatibility on the Fedora host, ensuring the container has the necessary permissions to read the Python scripts

```text
[kaveesh@fedora] - [~/Documents/University/University notes/2nd Year/4th semester/Obsidian/FIS smester 4/Capstone Project/Lab/day 1] - [Mon Mar 02, 11:17]
└─[$] <> podman run -it --rm --network=host -v .:/app:Z sentry-watchman:v2 python3 check_connection.py
--- Connecting to Sentry-Pod Node: R1 ---
Connection Successful! Output:
------------------------------
Interface             IP-Address      OK? Method Status               Protocol
FastEthernet0/0       unassigned      YES NVRAM  administratively down down
FastEthernet0/1       192.168.122.30  YES DHCP   up                   up
FastEthernet1/0       unassigned      YES NVRAM  administratively down down
FastEthernet1/1       unassigned      YES NVRAM  administratively down down
GigabitEthernet2/0    unassigned      YES NVRAM  administratively down down
```

## What I Learned

- By utilizing Netmiko's `ConnectHandler`, the system automatically manages SSH session timing and prompt detection, which is a significant upgrade over standard SSH libraries that often hang on legacy Cisco buffers.

---
← [Day 01 · Router Init](01-router-init-and-first-contact.md) | [Day 03 · Golden State Baseline](03-golden-state-baseline.md) →

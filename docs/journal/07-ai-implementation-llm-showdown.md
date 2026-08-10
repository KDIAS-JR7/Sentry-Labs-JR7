# Day 07 – AI Implementation (Phase 1): The LLM Showdown

> **Date:** 30 Mar 2026 · **Topic:** Choosing the model that will translate natural language into Cisco IOS · **Takeaway:** Three out of four LLMs hallucinate Cisco CLI in ways a human network engineer immediately catches. DeepSeek-R1 earned its place by refusing to guess.

[↑ Journal Index](../../README.md)

## The Goal

Find an LLM accurate enough to be the AI brain of the NMS.

## Introduction to APIs

- The AI implementation is done through APIs.
- A sample API call looks like,

```python
import os
import requests
from dotenv import load_dotenv
load_dotenv()
import json

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
prompt = input(f"What do you want me to do? \n")
print(f"Gotcha! Let me work on that for you...\n")

response = query({
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text":  f"{prompt}"
                }
            ]
        }
    ],
    "model": "google/gemma-3-12b-it-qat-q4_0-unquantized:featherless-ai"
})


# Assuming 'response' is the variable from your previous code
message_data = response["choices"][0]["message"]

# 1. Extract the content
raw_content = message_data["content"]

# 2. Print a Header
print(f"{'='*20} AI RESPONSE {'='*20}\n")

# 3. Printing the content directly will interpret the '\n' correctly
print(raw_content)

print(f"\n{'='*53}")
```

- To call an API, one must first provide an API key.
- API keys are must be kept secure at all times, hence blindly pasting an API key into an API call is non-negotiable. This is because, should anyone else get their hands on a private API key, it can be a serious security vulnerability.
- The python-dotenv library is used to remedy this.
- A **.env** file(the file itself is *.env*. No file name, no other extension) is created in the project directory and the API key is included there.
- The API key is then used in the API call using the load_dotenv function.

## Choosing API providers

- To use an LLM API, one must first pick an API provider.
- There are many API free API providers to choose from. However, many of these free tiers come with significant drawbacks. For example, though easy to implement, google Gemini models on the free tier collect user data for LLM training, which is unacceptable.
- After careful consideration, hugging face was chosen as the API provider.

## LLM showdown

- Hugging face provides a large quantity of free LLMs to try.
- However, for a LLM to be worth using in the context an NMS, it has to be extremely accurate at understanding advanced computer networking related prompts and provide accurate answers.
- In order to pick a model that fits these criteria, the models were tested with advanced computer networking related prompts and each ones' output was evaluated.
- The structure follows the order of.
	1. Output
	2. Highlight if hallucination was found
	3. Conclusion

## LLAMA

- The LLAMA LLM by Meta struggled hilariously with the provided prompt.

```text
What do you want me to do?
Give me a step by step list of instructions on how to block youtube on a cisco switch for vlan 10 using named ACLs. Order the output into a Ordered list. Begin from the absolute basics such as enable commands. Include every command clearly.
==================== AI RESPONSE ====================

**Blocking YouTube on a Cisco Switch using Named ACLs**

**Step 1: Connect to the Switch**

1. Open the terminal or command prompt and connect to the switch using the console cable or network cable.
2. Type `telnet <switch_ip>` (replace `<switch_ip>` with the IP address of the switch) and press Enter.

**Step 2: Login to the Switch**

1. Type `username <username> password <password>` (replace `<username>` and `<password>` with your username and password) and press Enter.
2. Type `enable` and press Enter to enter privileged mode.
3. Type `enable password <password>` (replace `<password>` with your enable password) and press Enter.

**Step 3: Create a Named ACL**

1. Type `ip access-list extended no_youtube` and press Enter to create a new named ACL.
2. The `no_youtube` name can be changed to any descriptive name you prefer.

Step
1. Type `permit tcp any any eq 443` and press Enter to allow HTTPs traffic.
2. Type `deny tcp any any eq 443` and press Enter to block YouTube traffic.
3. Type `remark Block YouTube` and press Enter to add a remark to the ACL.
4. Type `exit` and press Enter to exit the ACL configuration mode.

**Step 5: Apply the ACL to VLAN 10**

1. Type `vlan database` and press Enter to enter VLAN configuration mode.
2. Type `vlan 10` and press Enter to select VLAN 10.
3. Type `ip access-group no_youtube in` and press Enter to apply the ACL to VLAN 10.

**Step 6: Verify the ACL**

1. Type `show access-lists` and press Enter to verify the ACL.

**Step 7: Save the Configuration**

1. Type `copy running-config startup-config` and press Enter to save the configuration.

**Step 8: Verify the Configuration**

1. Type `show running-config` and press Enter to verify the configuration.

**Complete Configuration**

```markdown
Switch#  enable
Switch#  ip access-list extended no_youtube
Switch(config-ext-nacl)#  permit tcp any any eq 443
Switch(config-ext-nacl)#  deny tcp any any eq 443
Switch(config-ext-nacl)#  remark Block YouTube
Switch(config-ext-nacl)#  exit
Switch#  vlan database
Switch(vlan-config)#  vlan 10
Switch(vlan-config)#  ip access-group no_youtube in
Switch(vlan-config)#  exit
Switch#  show access-lists
Switch#  copy running-config startup-config
Switch#  show running-config
```
```

### Highlight

- As seen in the above output;

```text
> 1. Type `permit tcp any any eq 443` and press Enter to allow HTTPs traffic.
> 2. Type `deny tcp any any eq 443` and press Enter to block YouTube traffic.
> 3. Type `remark Block YouTube` and press Enter to add a remark to the ACL.
> 4. Type `exit` and press Enter to exit the ACL configuration mode.
```

- LLAMA recommends to use **permit tcp any any eq 443** to allow http traffic, while **deny tcp any any eq 443** will disable youtube.
- This is extremely inaccurate as the second ACE would deny HTTP itself, not just Youtube. And the two ACEs are also counter intuitive, as the later is the inverse of the prior.

### Conclusion

- LLAMA is not suitable for the project

## Gemma-3

- Gemma 3 also provided some wild recommendations

```text
==================== AI RESPONSE ====================

Blocking ICMP echo messages on a Cisco switch using named ACLs involves several steps. Here's a step-by-step guide to achieve this on VLAN 10 using named ACLs:

1. **Enable the CLI on the switch**:
   - Step: Enter the enable mode by typing `enable` followed by your enable password.
   - Reasoning: Enable mode is required to make configuration changes to the switch.

   ```
   switch# enable
   Password:
   switch#
   ```

2. **Check the current configuration**:
   - Step: Type `show running-config` to view the current configuration of the switch.
   - Reasoning: Verify the current configuration to ensure no ACLs are already applied to VLAN 10.

   ```
   switch# show running-config
   ```

3. **Create a new named ACL**:
   - Step: Type `ip access-list extended icmp-block` to create a new extended ACL named `icmp-block`. The `extended` keyword allows us to specify the protocol (ICMP in this case).
   - Reasoning: Use a descriptive name for the ACL to make it easier to manage and troubleshoot.

   ```
   switch# ip access-list extended icmp-block
   ```

4. **Configure the ACL to block ICMP echo messages**:
   - Step: Type `deny icmp any any echo` to block ICMP echo messages. The `deny` keyword denies the specified traffic, and `icmp any any echo` matches any ICMP echo packet (ICMP type 8, code 0).
   - Reasoning: Block ICMP echo messages to prevent ICMP pings from reaching the switch.

   ```
   switch(ip-access-list-extended)# deny icmp any any echo
   ```

5. **Save the ACL**:
   - Step: Type `exit` to exit the ACL configuration mode and save the ACL changes.
   - Reasoning: Save the ACL to apply the changes.

   ```
   switch(ip-access-list-extended)# exit
   ```

6. **Apply the ACL to VLAN 10**:
   - Step: Type `vlan access-map icmp-block vlan 10` to create a new VLAN access map named `icmp-block` for VLAN 10.
   - Reasoning: Apply the ACL to the VLAN.

   ```
   switch# vlan access-map icmp-block vlan 10
   ```

7. **Configure the VLAN access map to permit traffic**:
   - Step: Type `match ip address name icmp-block` to match the ACL we created earlier.
   - Reasoning: Apply the ACL to the VLAN access map.

   ```
   switch(vlan-access-map-icmp-block)# match ip address name icmp-block
   ```

8. **Configure the VLAN access map to forward traffic**:
   - Step: Type `action forward` to forward traffic that matches the ACL.
   - Reasoning: Forward traffic that doesn't match the ACL.

   ```
   switch(vlan-access-map-icmp-block)# action forward
   ```

9. **Save the VLAN access map**:
   - Step: Type `exit` to exit the VLAN access map configuration mode and save the VLAN access map changes.
   - Reasoning: Save the VLAN access map to apply the changes.

   ```
   switch(vlan-access-map-icmp-block)# exit
   ```

10. **Apply the VLAN access map to VLAN 10**:
    - Step: Type `vlan database` to enter the VLAN database configuration mode.
    - Reasoning: Apply the VLAN access map to the VLAN.

    ```
    switch# vlan database
    ```

11. **Apply the VLAN access map**:
    - Step: Type `vlan 10` to apply the VLAN access map to VLAN 10.
    - Reasoning: Apply the VLAN access map to the VLAN.

    ```
    switch(vlan)# vlan 10
    ```

12. **Exit the VLAN database configuration mode**:
    - Step: Type `exit` to exit the VLAN database configuration mode.
    - Reasoning: Exit the VLAN database configuration mode.

    ```
    switch(vlan)# exit
    ```

13. **Verify the configuration**:
    - Step: Type `show vlan access-map` to verify the VLAN access map configuration.
    - Reasoning: Verify the configuration to ensure the ACL is properly applied to VLAN 10.

    ```
    switch# show vlan access-map
    ```

Please note that these steps assume you are using a Cisco switch running IOS or a similar platform. If you are using a different platform or version, the commands and configuration may vary. Additionally, always back up your configuration before making any changes.

=====================================================
```

### Highlight

```text
save the ACL**:
   - Step: Type `exit` to exit the ACL configuration mode and save the ACL changes.
   - Reasoning: Save the ACL to apply the changes.
   switch(ip-access-list-extended)# exit
```

- Here, Gemma recommends to use *exit* to save an configuration. In cisco IOS, saving a configuration change from RAM to NVRAM can be dine using,
	1. **copy running-config startup-config** in privileged exec mode
	2. **write** in privileged exec mode
	3. Either of the above commands with the *do* keyword in any other mode higher than privileged exec. Ex: do write
- *Exit* is not one of them. It merely exits from the current execution level and moves onto the previous level. Ex: from global config mode to privileged exec.

### Conclusion

- Gemma-3 is not suitable

## QWEN

```text
 /usr/bin/python "/home/kaveesh/Documents/Hugging face/Qwen/Qwen2.5-7B-Instruct.py"
What do you want me to do?
Give me a step by step list of instructions on how to block ICMP echo messages on a cisco switch for vlan 10 using named ACLs. Order the output into a Ordered list. Begin from the absolute basics such as enable commands. Include every command clearly. State your reasoning for each step for debugging and documentation purposes. If any part of this request is impractical by a cisco ios cli standpoint, do not improvise, state the error and stop the response.
Gotcha! Let me work on that for you...

==================== AI RESPONSE ====================

Certainly! Here is a step-by-step list of instructions to block ICMP echo messages (ping) on a Cisco switch for VLAN 10 using named Access Control Lists (ACLs). This process assumes you are using a Cisco IOS-based switch.

### Step-by-Step Instructions

1. **Enter Global Configuration Mode:**
   ```shell
   enable
   configure terminal
   ```
   **Reasoning:** This command sequence enters the global configuration mode, which is necessary to configure the switch.

2. **Enter VLAN Configuration Mode:**
   ```shell
   vlan 10
   ```
   **Reasoning:** This command enters the configuration mode for VLAN 10, where you can apply ACLs to this specific VLAN.

3. **Create a Named ACL:**
   ```shell
   ip access-list extended BLOCK_ICMP_ECHO
   ```
   **Reasoning:** This command creates a named ACL named `BLOCK_ICMP_ECHO`. The `extended` keyword indicates that this ACL will be based on IP addresses and protocols.

4. **Deny ICMP Echo Requests:**
   ```shell
   deny icmp any any echo
   ```
   **Reasoning:** This command denies all ICMP echo requests (ping) from any source to any destination within VLAN 10.

5. **Apply the ACL to the VLAN:**
   ```shell
   ip access-group BLOCK_ICMP_ECHO in
   ```
   **Reasoning:** This command applies the `BLOCK_ICMP_ECHO` ACL to the ingress traffic of VLAN 10. This means that the ACL will be checked for incoming packets.

6. **Save Configuration:**
   ```shell
   write memory
   ```
   **Reasoning:** This command saves the current configuration to the switch's startup configuration, ensuring that the changes persist after a reboot.

7. **Verify Configuration:**
   ```shell
   show ip access-lists
   show ip interface brief
   ```
   **Reasoning:** These commands verify that the ACL has been correctly applied and that the interface configuration is as expected.

### Summary of Commands

1. Enter Global Configuration Mode:
   ```shell
   enable
   configure terminal
   ```

2. Enter VLAN Configuration Mode:
   ```shell
   vlan 10
   ```

3. Create a Named ACL:
   ```shell
   ip access-list extended BLOCK_ICMP_ECHO
   ```

4. Deny ICMP Echo Requests:
   ```shell
   deny icmp any any echo
   ```

5. Apply the ACL to the VLAN:
   ```shell
   ip access-group BLOCK_ICMP_ECHO in
   ```

6. Save Configuration:
   ```shell
   write memory
   ```

7. Verify Configuration:
   ```shell
   show ip access-lists
   show ip interface brief
   ```

This sequence of commands will effectively block ICMP echo messages (ping) on VLAN 10 of your Cisco switch.

=====================================================
```

### Highlight

```text
Enter VLAN Configuration Mode:
   ```shell
   vlan 10
   ```

3. Create a Named ACL:
   ```shell
   ip access-list extended BLOCK_ICMP_ECHO
   ```
```

- QWEN attempts to create an ACL within VLAN config mode.

### Conclusion

- QWEN is not suitable

## Deepseek R1

```text
 /usr/bin/python "/home/kaveesh/Documents/Hugging face/deepseek-ai/DeepSeek-R1.py"
What do you want me to do?
Give me a step by step list of instructions on how to block ICMP echo messages on a cisco router, into vlan 10 using named ACLs; blocking ping attempts to this vlan. Order the output into a Ordered list. Begin from the absolute basics such as enable commands. Include every command clearly. State your reasoning for each step for debugging and documentation purposes. If any part of this request is impractical by a cisco ios cli standpoint, do not improvise, state the error and stop the response.
Gotcha! Let me work on that for you...

==================== THINKING PHASE ====================

Okay, let's tackle this problem. The user wants to block ICMP echo messages (pings) into VLAN 10 on a Cisco router using a named ACL. I need to provide a step-by-step list starting from the absolute basics, including every command, reasoning, and handling any impractical steps.

First, I remember that to configure a Cisco router, you start by accessing privileged EXEC mode with 'enable'. Then, enter global configuration mode with 'configure terminal'.

Next, creating a named ACL. Since we're blocking traffic to VLAN 10, the ACL should be applied inbound on the interface facing the external network or wherever the traffic is coming from. Named ACLs can be either standard or extended, but since ICMP is a protocol (layer 3), an extended ACL is needed. So the command would be 'ip access-list extended BLOCK_ICMP_ECHO'.

Then, the ACL entry: 'deny icmp any any echo' would block incoming ICMP echo requests. Wait, but the destination is VLAN 10. So maybe the destination should be the VLAN 10 subnet. Hmm, the user mentioned VLAN 10, but on a router, VLANs are typically on sub-interfaces or switch interfaces. Wait, the router might have a VLAN interface, like a SVI (Switch Virtual Interface) if it's a layer 3 switch. But if it's a router, maybe it's a sub-interface with VLAN 10. So the ACL should deny ICMP echo requests to the VLAN 10 network. So maybe the destination should be the VLAN's subnet address with wildcard mask. For example, if VLAN 10 is 192.168.10.0/24, the destination would be 192.168.10.0 0.0.0.255. But the user hasn't specified the IP address, so maybe I should use 'any' as the destination. Wait, no—if the ACL is applied inbound on the interface where the traffic is entering the router destined for VLAN 10, then 'any' as the destination might not be precise. Alternatively, if the ACL is applied on the VLAN 10 interface itself, then inbound there would apply to traffic coming into VLAN 10. Wait, but typically, on a router, you apply the ACL inbound on the interface where the traffic enters the router. So if the traffic is coming from outside into VLAN 10, the ACL should be applied inbound on the external interface. But maybe the VLAN 10 is on a different interface. This is getting a bit confusing.

Wait, the user wants to block pings to VLAN 10. So the ACL should deny ICMP echo requests destined to any host in VLAN 10. So the ACL entry should be 'deny icmp any [vlan10_subnet] echo'. But since the user hasn't provided the specific subnet, maybe using 'any' as the destination isn't correct. But perhaps I can structure the ACL to block any ICMP echo requests going to VLAN 10's network. However, without knowing the specific IP range of VLAN 10, I might need to make an assumption here. Alternatively, maybe the user expects the ACL to be applied to the VLAN interface. But in a router, VLANs are usually handled via sub-interfaces or SVIs. Let's assume that the VLAN 10 interface is configured with an IP address, say 192.168.10.1/24. Then the ACL should deny icmp any 192.168.10.0 0.0.0.255 echo. But since the user didn't specify the IP, maybe the answer should prompt that the specific subnet is needed. Wait, but the user says to not improvise if something is impractical. If the VLAN 10's subnet isn't known, the ACL can't be accurately created. But maybe the user expects to use 'any' as the destination. However, that would block all ICMP echo requests anywhere, which isn't desired. So perhaps the answer must assume that the VLAN 10's subnet is known, but the user hasn't provided it. This is a problem.

Wait, the instruction says to block ping attempts to this VLAN. So the ACL should be applied inbound on the interface(s) that receive the traffic destined to VLAN 10. The ACL entry would deny ICMP echo requests (which are type 8) to the VLAN's subnet. But without knowing the subnet, I can't specify the exact ACL command. This might be an issue. If the user expects me to proceed, maybe I should note that the specific subnet is required. But the original request says to include every command clearly, so perhaps the answer must include variables. Hmm. Alternatively, maybe the user is okay with using a placeholder for the subnet and wildcard mask.

Another point: Cisco IOS applies ACLs to interfaces. So after creating the named ACL, it needs to be applied to the appropriate interface. But which interface? If the VLAN is a SVI (interface Vlan10), then applying the ACL inbound on that interface would affect traffic destined to the VLAN. However, applying an inbound ACL on a VLAN interface would filter traffic coming into that VLAN from other interfaces. Wait, maybe traffic entering the router through other interfaces destined to VLAN 10. Let me think. If the router has an interface connected to the external network (e.g., GigabitEthernet0/0), and the VLAN 10 is on another interface (e.g., GigabitEthernet0/1), then applying the ACL inbound on GigabitEthernet0/0 would filter traffic coming from outside to the VLAN 10. Alternatively, applying it on the VLAN 10 interface itself as an inbound ACL would filter traffic coming into VLAN 10 from other parts of the router. That might not be the right approach.

Wait, the goal is to block incoming ping attempts to VLAN 10. So the ACL should be applied to the interface where the external traffic enters the router, inbound, to block ICMP echo requests destined for VLAN 10. Therefore, the ACL is applied inbound on the external interface. But without knowing the specific interfaces, maybe the answer should reference the interface connected to the source of the pings. Alternatively, applying it to the VLAN 10 interface outbound would not be effective.

This is getting complicated. Let's outline the steps:

1. Access privileged EXEC mode (enable)
2. Enter global config (conf t)
3. Create an extended named ACL (ip access-list extended BLOCK_ICMP_ECHO)
4. Deny icmp any <vlan10_network> echo
5. Permit other traffic (implicit deny any, but need to allow other traffic)
Wait, ACLs have an implicit deny at the end. So if we just have a deny for ICMP echo, everything else is denied. That's a problem. So we need to add a 'permit ip any any' after the deny statement to allow other traffic. Otherwise, all traffic would be blocked. So the ACL should have:

deny icmp any <vlan10_subnet> echo
permit ip any any

But again, <vlan10_subnet> needs to be specified. If the user's VLAN 10 subnet is, say, 192.168.10.0/24, then the command would be:

deny icmp any 192.168.10.0 0.0.0.255 echo
permit ip any any

But without knowing this, the commands can't be written accurately. Therefore, this is a point where the user's request is impractical because the VLAN 10 subnet is not specified. So according to the instructions, if any part is impractical, state the error and stop. But maybe the user expects the answer to proceed with placeholders. However, since the VLAN subnet is essential and not provided, the correct approach is to note that error and stop.

Wait, but maybe the VLAN 10 interface's IP is the destination. For example, if the router's VLAN 10 interface is 192.168.10.1, then the ACL could target that specific IP. But the user wants to block pings to the entire VLAN, not just the router's interface. So blocking all hosts in VLAN 10. Therefore, the ACL must target the subnet.

Therefore, without knowing the subnet, the step to create the ACL cannot be correctly formulated. Hence, the response should state that error and stop. However, the user provided the VLAN number (10), but not the IP subnet. Therefore, the request is missing critical information, making it impractical.

Alternatively, maybe the answer can structure the ACL using variables, explaining that the subnet must be substituted. But according to the user's instruction, if any part is impractical, do not improvise. So the assistant should check if creating a named ACL to block ICMP echo to a VLAN is possible without knowing the subnet. Since it's not possible, the assistant should state that error and stop.

But maybe the user is using the VLAN as an interface on the router, like interface Vlan10, and the ACL can be applied to that interface. Let's see. If the router has an SVI for VLAN 10 (interface Vlan10), then applying an inbound ACL on that interface would filter packets destined to the router's Vlan10 IP address. But if the goal is to block pings to any host in VLAN 10, that's different. Because the router's ACL can only filter traffic through the router, not between hosts in the same VLAN if they are on a switch. Wait, but if the router is the default gateway for VLAN 10, then traffic from other networks to VLAN 10 would go through the router. In that case, applying an inbound ACL on the external interface to block ICMP echo requests to the VLAN 10 subnet would work.

But again, without knowing the subnet, the ACL can't be written. Therefore, the answer must indicate that the subnet is required. Hence, the steps would proceed until the point where the ACL is being configured, then stop due to missing information.

Wait, let me check Cisco's documentation. Can you apply an ACL to a VLAN interface on a router? Yes, if it's a layer 3 SVI. So, applying the ACL inbound on interface Vlan10 would apply to packets destined to the router's Vlan10 IP. But if you want to protect all hosts in VLAN 10, you need to apply the ACL on the interface where the traffic enters the router. For example, if traffic comes in through GigabitEthernet0/0, destined for VLAN 10's subnet, applying the ACL inbound on Gi0/0 would block it. But again, the subnet is needed for the ACL.

So, compiling all this, the steps would be:

1. Enable
2. configure terminal
3. Create extended named ACL:
   ip access-list extended BLOCK_ICMP_ECHO
   deny icmp any [vlan10_subnet] echo
   permit ip any any
4. Apply the ACL inbound on the appropriate interface.

But since [vlan10_subnet] isn't provided, the step is impractical. Thus, in the response, after step 3, the assistant should note that the VLAN 10 subnet is required, and without it, the ACL can't be created, hence stopping.

Alternatively, if the user expects to apply the ACL to the VLAN interface itself, maybe they just want to block pings to the router's VLAN 10 IP, in which case the destination would be 'host [vlan10_ip]'. But again, without that IP, it's impossible.

Therefore, the correct response should proceed until the point where the subnet is needed, then state that the command cannot be completed without that information and halt.


=====================================================

==================== AI RESPONSE ====================

Here's a structured guide to block ICMP echo messages (pings) to VLAN 10 using a named ACL on a Cisco router. **The process stops at Step 3 due to missing critical information**:

---

### Step-by-Step Instructions

1. **Access Privileged EXEC Mode**
   **Command**:
   ```bash
   enable
   ```
   **Reasoning**:
   Enters privileged EXEC mode, granting administrative access to configure the router.

2. **Enter Global Configuration Mode**
   **Command**:
   ```bash
   configure terminal
   ```
   **Reasoning**:
   Allows modification of the router's global configuration settings.

3. **Create an Extended Named ACL**
   **Command**:
   ```bash
   ip access-list extended BLOCK_ICMP_ECHO
   ```
   **Reasoning**:
   Begins configuration of an extended named ACL. Extended ACLs are required to filter ICMP traffic (Layer 3/4).

4. **Define the ACL Rule to Block ICMP Echo Requests**
   **Practical Error**:
   To block ICMP echo messages sent **to VLAN 10**, you must specify **VLAN 10's IP subnet** (e.g., `192.168.10.0 0.0.0.255`).
   **Missing Information**:
   The VLAN 10 subnet or specific IP range is not provided. Without this, the ACL cannot accurately target traffic destined for VLAN 10.

   **Example (Incomplete Due to Missing Subnet)**:
   ```bash
   deny icmp any [VLAN_10_SUBNET] echo
   permit ip any any
   ```
   **Reasoning**:
   - `deny icmp any [VLAN_10_SUBNET] echo` blocks inbound ICMP echo requests to VLAN 10.
   - `permit ip any any` ensures other traffic is allowed (avoids implicit "deny all").

---

### Why the Process Stops Here
- **Critical Error**: The command `deny icmp any [VLAN_10_SUBNET] echo` requires **VLAN 10's subnet** (e.g., `192.168.10.0 0.0.0.255`) to function.
- **Cisco CLI Limitation**: Subnet information is mandatory for ACLs targeting specific networks. Improvising without this data would misconfigure the ACL and potentially block unintended traffic.

---

### Next Steps (If Subnet is Provided)
If the VLAN 10 subnet is known, proceed with:

5. **Apply the ACL to the Correct Interface**
   **Example**:
   ```bash
   interface GigabitEthernet0/1  # Replace with the inbound interface facing external traffic
   ip access-group BLOCK_ICMP_ECHO in
   ```
   **Reasoning**:
   Applies the ACL inbound on the interface where external traffic enters the router, ensuring ICMP echo requests to VLAN 10 are filtered.

---

### Summary
The request is **impractical** without the VLAN 10 subnet. Cisco IOS requires explicit subnet definitions in ACLs to avoid misconfiguration. Provide the VLAN 10 subnet to complete the process.

=====================================================
```

- Deepseek R1 is a powerful reasoning model. Compared to the previous models, this powerful model is much more accurate.

### Conclusion

- Deepseek R1 is suitable

## Showdown Summary

| **Model**    | **Verdict**      | **Primary Failure/Success**                                                    |
| ------------ | ---------------- | ----------------------------------------------------------------------------- |
| **LLAMA**    | Rejected         | Circular logic; would result in a total port block.                           |
| **Gemma-3**  | Rejected         | Hallucinated CLI commands (`exit` to save).                                   |
| **Qwen**     | Rejected         | Invalid command hierarchy (ACL inside VLAN mode).                             |
| **DeepSeek R1** | **Selected** | **Success:** Identified missing subnet data and refused to "guess."           |

## Deepseek R1 API call

- Since DeepSeek-R1 is the current best model, the following API call is used to implement this model.

```python
import os
import requests
from dotenv import load_dotenv
load_dotenv()
import json

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

prompt = input(f"What do you want me to do? \n")
print(f"Gotcha! Let me work on that for you...\n")

response = query({
    "messages": [
        {
            "role": "user",
            "content": f"{prompt}"
        }
    ],
    "model": "deepseek-ai/DeepSeek-R1:novita"
})

# Assuming 'response' is the variable from your previous code
message_data = response["choices"][0]["message"]

# Print thinking phase if available
if "reasoning_content" in message_data:
    thinking = message_data["reasoning_content"]
    print(f"{'='*20} THINKING PHASE {'='*20}\n")
    print(thinking)
    print(f"\n{'='*53}\n")

# 1. Extract the content
raw_content = message_data["content"]

# 2. Print a Header
print(f"{'='*20} AI RESPONSE {'='*20}\n")

# 3. Printing the content directly will interpret the '\n' correctly
print(raw_content)

print(f"\n{'='*53}")
```

- The reasoning phase is also included in this version of the API call script for transparency.

---
← [Day 06 · Dynamic Routing with OSPF](06-ospf-dynamic-routing.md) | [Day 08 · Topology Redesign — Spine-Leaf](08-topology-redesign-spine-leaf.md) →

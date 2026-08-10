# Day 06 – Dynamic Routing with OSPF

> **Date:** 20 Mar 2026 · **Topic:** Making routers find each other without a spreadsheet of static routes · **Takeaway:** Static routing "appears straightforward" — but it does not scale, and it is unidirectional.

[↑ Journal Index](../../README.md)

## The Goal

Get the routers talking across networks they are not directly connected to.

## Why Routing?

- The routers have SSH connectivity and can SSH into each other while in the same network.
- Ex: R1 can SSH into R2 and R3 as they're both in the 10.0.0.0 /24 network, but not R4 as it is in the 10.0.1.0 /16 network.
- For a router to send packets to a different network, the router needs to know the route to that network in its routing table.

## Static routes and Why not use them?

- Static routing can be used to manually add a route into a routers routing table.
- Static routing can be enabled with a simple;

```text
ip route add 10.0.0.0/8 via 192.168.122.254
```

- This method appears straightforward, and is often much more secure, but static routing has one glaring weakness.
- In large enterprise networks, comprising a large number of layer 3 devices, manually entering the route to each subnet within the network into each device is inefficient, cumbersome and error prone.
- This is further emphasized by the unidirectional nature of Static routing. That entering a static route in one device does not mean that the other network also knows how to access that routers network.
- Meaning that even though a network is entered as a static route in one router X, that routers network has to be entered again in the previous router Y for each router to finally see each other.

## Dynamic Routing and OSPF

- Dynamic routing protocols were created to solve this issue.
- These protocols automates the route learning process, making the task much more efficient.
- OSPF is one such routing protocol.
- OSPF allows routers to broadcast networks they are directly connected to within an OSPF area, allowing all other routers to dynamically learn the route to those networks and populate their routing tables.

## Single Area OSPF network

- OSPF can be configured as both single area and Multi area. However, as the lab environment used here is not complex enough, single area OSPF suffice.
- In single area OSPF, **all routers must share one OSPF area.**
- In this context, all routers will be using the OSPF area 0.

```text
R3(config)#router ospf 1
R3(config-router)#network 10.0.0.0 0.0.0.255 area 0
R3(config-router)#
*Mar 20 12:51:41.570: %OSPF-5-ADJCHG: Process 1, Nbr 10.1.1.0 on GigabitEthernet2/0 from LOADING to FULL, Loading Done
R3(config-router)#f==
*Mar 20 12:51:44.362: %OSPF-5-ADJCHG: Process 1, Nbr 192.168.122.254 on GigabitEthernet2/0 from LOADING to FULL, Loading Done
R3(config-router)#network 10.2.0.0 0.0.255.255 area 0
R3(config-router)#
```

- In this snippet, OSPF has been enabled on R3 and it is advertising the 10.2.0.0 network which only it has direct access to.
- As seen in the output, R3 has dynamically learned the route to 10.1.1.0 network, which it is not directly connected to.

```text
R1#show ip route
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
      D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
      N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
      E1 - OSPF external type 1, E2 - OSPF external type 2
      i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
      ia - IS-IS inter area, * - candidate default, U - per-user static route
      o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
      + - replicated route, % - next hop override

Gateway of last resort is 192.168.122.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 192.168.122.1
     10.0.0.0/8 is variably subnetted, 4 subnets, 4 masks
C       10.0.0.0/24 is directly connected, FastEthernet0/0
L       10.0.0.1/32 is directly connected, FastEthernet0/0
O       10.0.1.0/30 [110/2] via 10.0.0.2, 1d11h, FastEthernet0/0
O       10.2.0.0/16 [110/2] via 10.0.0.3, 1d13h, FastEthernet0/0
     192.168.122.0/24 is variably subnetted, 2 subnets, 2 masks
C       192.168.122.0/24 is directly connected, FastEthernet0/1
L       192.168.122.254/32 is directly connected, FastEthernet0/1
```

- The **show ip route** command shows a routers routing table. As seen here, R1 has indeed learned the 10.2.0.0 /16 network that R3 had broadcasted.

---
← [Day 05 · Topology Update](05-topology-update.md) | [Day 07 · AI Implementation (LLM Showdown)](07-ai-implementation-llm-showdown.md) →

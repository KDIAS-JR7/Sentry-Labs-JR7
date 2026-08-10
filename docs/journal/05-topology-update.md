# Day 05 – Topology Update

> **Date:** 22 Mar 2026 · **Topic:** Growing the network and standardising SSH everywhere · **Takeaway:** Consistency (same credentials, same SSH setup) is what makes the later automation possible at all.

[↑ Journal Index](../../README.md)

## The Goal

- The previous topology had three core layer routers connected on the 10.0.0.0 /24 network as
	R1 - 10.0.0.1
	R2 - 10.0.0.2
	R3 - 10.0.0.3
- R1 connected to an additional network 192.168.122.0 /24, the gns3 NAT node network over the ip address 192.168.122.254.

![Topology](../../assets/images/topology.png)

- The updated topology now includes the 10.0.1.0 /16 network
	R4, with 10.0.1.0 through f0/1 interface with IP address 10.0.1.2
	R2 with 10.0.1.0 through f0/0 interface with IP address 10.0.1.1
- SSH has now been configured on each of the 4 routers with the same credentials. (username = admin, password = cisco123)

---
← [Day 04 · Three-Tier Topology & VLSM](04-topology-three-tier-vlsm.md) | [Day 06 · Dynamic Routing with OSPF](06-ospf-dynamic-routing.md) →

# Dual-Stack SR-MPLS

This lab topology describes a simple dual-stack 3-node network using SR-MPLS with IS-IS. It uses a custom P2P pool and IPv6 prefixes on loopback interfaces.

![3-node SR-MPLS with IS-IS topology](../../images/intro-topology.png)

| Node/Interface | IPv4 Address | IPv6 Address | Description |
|----------------|-------------:|-------------:|-------------|
| **pe1** |  10.0.42.1/32 | 2001:db8:0:1::1/64 | Loopback |
| eth1 | 192.168.42.1/31 | 2001:db8:cafe::2/64 | pe1 -> p |
| **p** |  10.0.42.2/32 | 2001:db8:0:2::1/64 | Loopback |
| eth1 | 192.168.42.0/31 | 2001:db8:cafe::1/64 | p -> pe1 |
| eth2 | 192.168.42.2/31 | 2001:db8:cafe:1::1/64 | p -> pe2 |
| **pe2** |  10.0.42.3/32 | 2001:db8:0:3::1/64 | Loopback |
| eth1 | 192.168.42.3/31 | 2001:db8:cafe:1::2/64 | pe2 -> p |

For general instructions on starting labs, connecting to devices, and generating reports with `netlab`, see [Using the Labs](../../docs/use.md) document.

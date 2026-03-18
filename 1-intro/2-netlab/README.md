# Simple SR-MPLS with IS-IS

This lab topology describes a simple 3-node network using SR-MPLS with IS-IS.

![](../../images/intro-topology.png)

Start the lab with Arista EOS containers:

```
netlab up
```

Start the lab with an alternate device (for example, frr)

```
netlab up -d _device_
```

Connect to devices with

```
netlab connect _node_
```

Create reports:

* **netlab report wiring** -- lab nodes and links
* **netlab report addressing** -- lab addressing
* **netlab report isis-node** -- IS-IS routing
* **netlab report mgmt** -- Management access to lab devices

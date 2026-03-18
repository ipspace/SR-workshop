# Using the Labs

The repository contains _netlab_ lab topologies and related usage instructions. You can start your labs in GitHub Codespaces, or [install netlab locally](https://netlab.tools/install/) or in a [cloud VM](https://netlab.tools/install/cloud/).

To start a lab:

* Change current directory to the lab directory
* Execute `netlab up` to start the lab with Arista cEOS containers (default settings) or `netlab up -d _device_` to start the lab with [another device](https://netlab.tools/platforms/).
* Connect to lab devices with `netlab connect _nodename_`.

Use these commands to create lab topology reports:

* **netlab report wiring** -- lab nodes and links
* **netlab report addressing** -- lab addressing
* **netlab report isis-node** -- IS-IS routing
* **netlab report mgmt** -- Management access to lab devices

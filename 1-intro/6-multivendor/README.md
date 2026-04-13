# Multivendor SR-MPLS with IS-IS

This lab topology describes a multivendor (Arista EOS, FRRouting, Nokia SR Linux) 3-node network running SR-MPLS with IS-IS.

![](../../images/intro-topology.png)

For general instructions on starting labs, connecting to devices, and generating reports with `netlab`, see [Using the Labs](../../docs/use.md) document.

Edit `topology.yml` file to change the devices used in this lab. You can use any device [supported](https://netlab.tools/module/sr-mpls/#supported-platforms) by the netlab [SR-MPLS module](https://netlab.tools/module/sr-mpls/).

**Note:** Nokia SR Linux requires a local license file to run MPLS or SR-MPLS. If you use SR Linux in this lab, obtain the license from Nokia and save it as `~/.netlab/license_srlinux.txt` before starting the lab. If you do not have that file, change the topology to use other supported SR-MPLS platforms.

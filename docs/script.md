# Segment Routing Workshop -- Instructor Notes

## Containerlab demo (1-intro/1-clab)

containerlab deploy
docker exec -it clab-intro-p FastCLI
ssh clab-intro-p
containerlab destroy

## Simple SR-MPLS (1-intro/2-netlab)

netlab up
netlab report addressing
netlab report isis-nodes

netlab connect pe1
show run section router isis
show run section interface Loopback0
show isis database detail
show isis segment-routing
show isis segment-routing prefix-segments
show mpls route
show isis segment-routing global-blocks

netlab down

## Dual-Stack SR-MPLS (1-intro/3-ds)

netlab up
netlab report addressing
netlab report isis-nodes

netlab connect pe1
show mpls table
show isis database detail
show ipv6 route

netlab down

## SR-MPLS over Unnumbered Interfaces (1-intro/4-unnumbered)

netlab up
netlab report addressing

netlab connect pe1
show ip int brief
show isis neighbor
show isis segment-routing prefix-segments
show isis segment-routing adjacency-segments

netlab down

## SR-MPLS with OSPFv2 (1-intro/5-ospf)

netlab up
netlab report ospf-areas

netlab connect pe1
show ip ospf segment-routing prefix-segments
show ip ospf segment-routing bindings

netlab down

## Multivendor SR-MPLS (1-intro/6-multivendor)

netlab up
netlab show reports
netlab report devices

netlab connect pe1
show isis segment-routing global-blocks
show mpls route

netlab down

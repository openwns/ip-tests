# import the WNS module. Contains all sub-classes needed for
# configuration of WNS
import wns.WNS
import wns.Distribution
import ip
from constanze.Constanze import Constanze, CBR
from constanze.Node import ConstanzeComponent, IPBinding, IPListenerBinding, Listener
from ip.BackboneHelpers import Router_10BaseT, Station_10BaseT
from ip.VirtualARP import VirtualARPServer
from ip.VirtualDNS import VirtualDNSServer
from ip.VirtualDHCP import VirtualDHCPServer
from ip.Address import ipv4Address
from ip.IP import IP
import copper.Copper
import glue
import glue.support.Configuration

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()
WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE

# number of stations (min = 3)
numSubnets = 10

# Routing test (numSubnets defined size of scenario)
# You need at least 3 subnets
#
#                 router(n-1)                      router(n)                     router(n+1)
#                  |  |      192.168.(n-1).254      |  |192.168.n.1                  |  |
#                  |  |                             |  |                             |  |
#                  |  |                             |  |                             |  |
#                  |  |                             |  |                             |  |
#                  |  |                             |  |                             |  |
#                  |  |      station(n-1)           |  |      station(n)             |  |
#                  |  |          |192.168.(n-1).2   |  |          |192.168.n.2       |  |
#                  |  |          |                  |  |          |                  |  |
#  .. _____________o  o__________o__________________o  o__________o__________________o  o____________ ..
#  Subnets:                   192.168.(n-1).0                  192.168.n.0                   192.168.(n+1).0
#
#
# The scenario is cyclic. That is router(numSubnets) is connected to subnet0
#
# The default router of each station n is router n
#
# Routers only have one default route which results in clock-wise routing (from subnet n-1 to subnet n)
#
# Each station n sends traffic to station n-2. Since routing is done clock-wise
# traffic is send through the whole subnet ring.

subnets = []
routers = []
stations = []
wires = []


# Create subnet addresses
for i in xrange(numSubnets):
    subnetAddress = ipv4Address("192.168.0.0") + (i+1) * (2**8)
    subnets.append( subnetAddress )

# Populate subnets
hostnum = 1
STATION    = 1
ROUTER     = 2
ARPSERVER  = 3
DHCPSERVER = 4
DNSSERVER  = 5

for subnet in subnets:
    wire = copper.Copper.Wire(str(subnet) + ".wire")
    defaultRouterAddress = subnet + 1
    domainName = "Host" + str(hostnum) + ".wns.org"
    station = Station_10BaseT(name = domainName + ".ip",
                              _wire = wire,
                              _domainName = domainName,
                              _defaultRouter = str(defaultRouterAddress))
    station.addConstantContextProvider("nodeType", STATION)

    router = Router_10BaseT(_name = "Router" + str(hostnum) + ".wns.org",
                            _domainName = str(subnet + 1))
    router.addConstantContextProvider("nodeType", ROUTER)

    varp = VirtualARPServer("vARP"+str(hostnum)+"@", wire.name)
    varp.addConstantContextProvider("nodeType", ARPSERVER)

    vdhcp = VirtualDHCPServer("vDHCP" + str(hostnum) + "@",
                              wire.name,
                              subnet + 10, subnet + 240,
                              "255.255.255.0")
    vdhcp.addConstantContextProvider("nodeType", DHCPSERVER)

    WNS.nodes.append(vdhcp)

    WNS.nodes.append(varp)
    wires.append(wire)
    stations.append(station)
    routers.append(router)
    hostnum += 1

# Connect subnets with routers
routernum = 1
for i in xrange(numSubnets):
    domainNameRight = "Router" + str(routernum) + "right"
    domainNameLeft = "Router" + str(routernum) + "left"
    leftAddress = str( subnets[i] + 1)
    rightAddress = str( subnets[i-1] + 254)
    routers[i].plugOnWire(domainNameLeft, wires[i], leftAddress)
    routers[i].plugOnWire(domainNameRight,wires[i-1], rightAddress)
    routernum += 1

# Build routing tables
routernum = 1
for i in subnets:
    dataTransmissionService = routers[subnets.index(i)].ip.dataLinkLayers[0].dllDataTransmission
    routers[subnets.index(i)].addRoute("0.0.0.0", "0.0.0.0", str(i + 254), "Router" + str(routernum) + "left")
    routernum += 1

# Create traffic mixes
for i in range(len(stations)):
    source= stations[i].ip.domainName
    destination = stations[i-2].ip.domainName
    ipBinding = IPBinding(source, destination)

    constanze = ConstanzeComponent(stations[i], source + ".constanze")
    constanze.addTraffic(ipBinding, CBR(0.00001, 1024, 1024))

    listener = Listener(source + ".listener")
    ipListenerBinding = IPListenerBinding(source)
    constanze.addListener(ipListenerBinding, listener)


# Add nodes to scenario
vdns = VirtualDNSServer("vDNS", "ip.DEFAULT.GLOBAL")
vdns.addConstantContextProvider("nodeType", DNSSERVER)
WNS.nodes.append(vdns)
WNS.nodes += stations + routers

WNS.maxSimTime = 1000.0

wns.Logger.globalRegistry.setAttribute("IP", "enabled", True)

# disable old style probes
WNS.modules.ip.probes = {}

# add new style probes of ip
# since we have 10BaseT here maxBitThroughPut of 10E6 Bit is sufficient
ipSubTrees = ip.Probes.getPDFSubTrees(maxPacketDelay = 0.5,     # s
                                      maxPacketSize = 2000*8,   # Bit
                                      maxBitThroughput = 10E6,  # Bit/s
                                      maxPacketThroughput = 1E6 # Packets/s
                                      )

WNS.environment.probeBusRegistry.insertSubTrees(ipSubTrees)

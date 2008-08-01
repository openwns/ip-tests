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
import ip.evaluation.default
import copper.Copper
import glue
import glue.support.Configuration

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()
WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE

domainName1 = "vpnclient.ip.wns.org"
wire1 = copper.Copper.Wire("public1.wire")
node1 = Station_10BaseT(name = domainName1 + ".ip",
                        _wire = wire1,
                        _domainName = domainName1,
                        _defaultRouter = "64.233.167.1")

node1.ip.clearRoutingTable()
node1.ip.addTunnel("tun1", "137.226.5.42", "65.233.167.17")
node1.ip.addRoute("137.226.5.0", "255.255.255.0", "137.226.5.42", "tun1")
node1.ip.addRoute("65.233.0.0", "255.255.0.0", "64.233.167.1", "glue")

router1 = Router_10BaseT(_name = "publicRouter.ip.wns.org",
                         _domainName = "64.233.167.1")

router1.plugOnWire("publicRouterLeft.ip.wns.org", wire1, "64.233.167.1")
wire2 = copper.Copper.Wire("public2.wire")
router1.plugOnWire("publicRouterRight.ip.wns.org", wire2, "65.233.167.1")

domainName2 = "vpnserver.ip.wns.org"
wire3 = copper.Copper.Wire("intern.wire")

router2 = Router_10BaseT(_name = "vpnserver.ip.wns.org",
                         _domainName = "65.233.167.17")

router2.plugOnWire("vpnserver.ip.wns.org", wire2, "65.233.167.17")
router2.plugOnWire("vpnintern.ip.wns.org", wire3, "137.226.5.1")
router2.ip.addTunnel("tun1", "127.0.0.1", "127.0.0.1")

domainName3 = "protected.ip.wns.org"
node2 = Station_10BaseT(name = domainName3 + ".ip",
                        _wire = wire3,
                        _domainName = domainName3,
                        _defaultRouter = "137.226.5.1")


varp1 = VirtualARPServer("vARP1@", wire1.name)
vdhcp1 = VirtualDHCPServer("vDHCP1@",
                          wire1.name,
                          "64.233.167.10", "64.233.167.100",
                          "255.255.255.0")
vdhcp2 = VirtualDHCPServer("vDHCP2@",
                          wire3.name,
                          "137.226.5.10", "137.226.5.100",
                          "255.255.255.0")

varp2 = VirtualARPServer("vARP2@", wire2.name)

varp3 = VirtualARPServer("vARP3@", wire3.name)

varp4 = VirtualARPServer("vARPTUN@", "tunnel")

vdns = VirtualDNSServer("vDNS", "ip.DEFAULT.GLOBAL")


source= node1.ip.domainName
destination = node2.ip.domainName
ipBinding = IPBinding(source, destination)

constanze1 = ConstanzeComponent(node1, source + ".constanze")
constanze1.addTraffic(ipBinding, CBR(0.01, 1024, 1024))

constanze2 = ConstanzeComponent(node2, destination + ".constanze")
listener = Listener(destination + ".listener")
ipListenerBinding = IPListenerBinding(destination)
constanze2.addListener(ipListenerBinding, listener)

WNS.nodes += [node1, router1, router2, node2, vdns, varp1, varp2, varp3, varp4, vdhcp1, vdhcp2]

WNS.maxSimTime = 100.0

# add new style probes of ip
# since we have 10BaseT here maxBitThroughPut of 10E6 Bit is sufficient
ip.evaluation.default.installEvaluation(sim = WNS,
                                        maxPacketDelay = 0.5,     # s
                                        maxPacketSize = 2000*8,   # Bit
                                        maxBitThroughput = 10E6,  # Bit/s
                                        maxPacketThroughput = 1E6 # Packets/s
                                 )


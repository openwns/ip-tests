import openwns
import openwns.logger
import ip
import ip.evaluation.default
import copper.Copper
from ip.BackboneHelpers import Station_10BaseT
from ip.BackboneHelpers import Router_10BaseT
from ip.VirtualARP import VirtualARPServer
from ip.VirtualDHCP import VirtualDHCPServer
from ip.VirtualDNS import VirtualDNSServer

import constanze.node
import constanze.traffic
import constanze.evaluation.default

leftWire = copper.Copper.Wire("LeftWire")
rightWire = copper.Copper.Wire("RightWire")
middleWire = copper.Copper.Wire("MiddleWire")

leftStation = Station_10BaseT(name = "LeftStation",
                              _wire = leftWire,
                              _domainName = "leftStation.wns.org",
                              _defaultRouter = "192.168.0.254")

rightStation = Station_10BaseT(name = "RightStation",
                              _wire = rightWire,
                              _domainName = "rightStation.wns.org",
                              _defaultRouter = "192.168.2.254")

router1 = Router_10BaseT(_name = "router1",
                        _domainName = "router1Left.wns.org")

router1.plugOnWire(_interfaceName = "glueLeft",
                   _wire = leftWire,
                   _ipAddress = "192.168.0.254")

router1.plugOnWire(_interfaceName = "glueRight",
                   _wire = middleWire,
                   _ipAddress = "192.168.1.254")

router1.addRoute("0.0.0.0", "0.0.0.0", "192.168.1.253", "glueRight")

router2 = Router_10BaseT(_name = "router2",
                        _domainName = "router2Left.wns.org")

router2.plugOnWire(_interfaceName = "glueLeft",
                   _wire = middleWire,
                   _ipAddress = "192.168.1.253")

router2.plugOnWire(_interfaceName = "glueRight",
                   _wire = rightWire,
                   _ipAddress = "192.168.2.254")

leftARP  = VirtualARPServer(name = "leftARP",
	                    subnetIdentifier = leftWire.name)

leftDHCP = VirtualDHCPServer(name = "leftDHCP@",
                             subnetIdentifier = leftWire.name,
                             startAddress = "192.168.0.2",
		             endAddress = "192.168.0.250",
                             subnetMask = "255.255.255.0")

middleARP  = VirtualARPServer(name = "middleARP",
	                      subnetIdentifier = middleWire.name)

middleDHCP = VirtualDHCPServer(name = "middleDHCP@",
                               subnetIdentifier = middleWire.name,
                               startAddress = "192.168.1.2",
		               endAddress = "192.168.1.250",
                               subnetMask = "255.255.255.0")

rightARP  = VirtualARPServer(name = "rightARP",
	                    subnetIdentifier = rightWire.name)

rightDHCP = VirtualDHCPServer(name = "rightDHCP@",
                             subnetIdentifier = rightWire.name,
                             startAddress = "192.168.2.2",
		             endAddress = "192.168.2.250",
                             subnetMask = "255.255.255.0")

dns = VirtualDNSServer(name = "DNS",
		       zoneIdentifier = "ip.DEFAULT.GLOBAL")

# Traffic Configuration
ipBinding = constanze.node.IPBinding("leftStation.wns.org", "rightStation.wns.org")
leftConstanze = constanze.node.ConstanzeComponent(leftStation, "leftStation.constanze")
leftConstanze.addTraffic(ipBinding, constanze.traffic.CBR(offset = 0.01,
                                                            throughput = 1024,
                                                            packetSize = 1024))
# Traffic Sink Configuration
listener = constanze.node.Listener("rightStation.listener")
ipListenerBinding = constanze.node.IPListenerBinding("rightStation.wns.org")
rightConstanze = constanze.node.ConstanzeComponent(rightStation, "rightStation.constanze")
rightConstanze.addListener(ipListenerBinding, listener)

WNS = openwns.Simulator(simulationModel = openwns.node.NodeSimulationModel())
WNS.outputStrategy = openwns.simulator.OutputStrategy.DELETE

WNS.simulationModel.nodes = [leftStation, rightStation,
             router1, router2,
	     leftARP, leftDHCP, rightARP, rightDHCP, middleARP, middleDHCP, dns]
WNS.maxSimTime = 100.0

openwns.logger.globalRegistry.setAttribute("IP", "enabled", True)


# add new style probes of ip
# since we have 10BaseT here maxBitThroughPut of 10E6 Bit is sufficient
constanze.evaluation.default.installEvaluation(sim = WNS,
                                               maxPacketDelay = 1.0,
                                               maxPacketSize = 16000,
                                               maxBitThroughput = 100e6,
                                               maxPacketThroughput = 10e6,
                                               delayResolution = 1000,
                                               sizeResolution = 2000,
                                               throughputResolution = 10000)


ip.evaluation.default.installEvaluation(sim = WNS,
                                       maxPacketDelay = 0.5,     # s
                                       maxPacketSize = 2000*8,   # Bit
                                       maxBitThroughput = 10E6,  # Bit/s
                                       maxPacketThroughput = 1E6 # Packets/s
                                       )

openwns.setSimulator(WNS)


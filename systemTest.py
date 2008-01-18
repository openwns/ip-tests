#! /usr/bin/env python2.4

# this is needed, so that the script can be called from everywhere
import os
import sys
base, tail = os.path.split(sys.argv[0])
os.chdir(base)

# Append the python sub-dir of WNS--main--x.y ...
sys.path.append(os.path.join('..', '..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages'))

# ... because the module WNS unit test framework is located there.
import pywns.WNSUnit

# create a system test
testSuite1 = pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                    executeable = "wns-core",
                                    configFile = 'config.py',
                                    shortDescription = 'A ring of three subnets to test IP',
                                    disabled = False,
#                                    readProbes = True,
                                    requireReferenceOutput = False,
                                    disabledReason = "")

# create a system test
testSuite2 = pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                    executeable = "wns-core",
                                    configFile = 'configTunnel.py',
                                    shortDescription = 'Simple Initial Tunneling Test',
                                    disabled = False,
#                                    readProbes = True,
                                    requireReferenceOutput = False,
                                    disabledReason = "")

# create a system test
testSuite3 = pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                    executeable = "wns-core",
                                    configFile = 'tutorial.py',
                                    shortDescription = 'Tutorial Scenario for IP module. Please update documentation if you modify things here!',
                                    requireReferenceOutput = False,
                                    disabled = False,
                                    disabledReason = "")

testSuite = pywns.WNSUnit.TestSuite()
testSuite.addTest(testSuite1)
testSuite.addTest(testSuite2)
testSuite.addTest(testSuite3)

if __name__ == '__main__':
    # This is only evaluated if the script is called by hand

    # if you need to change the verbosity do it here
    verbosity = 1

    pywns.WNSUnit.verbosity = verbosity

    # Create test runner
    testRunner = pywns.WNSUnit.TextTestRunner(verbosity=verbosity)

    # Finally, run the tests.
    testRunner.run(testSuite)

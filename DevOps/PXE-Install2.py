#!/usr/bin/python
#PXE-install
import os,sys,re,time

testbed = {}
testbed["10.94.193.83"] = "10.94.197.183"
testbed["10.94.193.183"] = "10.94.197.184"
testbed["10.94.193.84"] = "10.94.197.187"
testbed["10.94.193.184"] = "10.94.197.188"
testbed["10.94.193.85"] = "10.94.197.191"
testbed["10.94.193.185"] = "10.94.197.192"
testbed["10.94.193.86"] = "10.94.197.195"
testbed["10.94.193.186"] = "10.94.197.196"
testbed["10.94.193.87"] = "10.94.197.198"
testbed["10.94.193.88"] = "10.94.197.200"

cmd_status = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power status"
cmd_reset = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power reset"
cmd_poweron = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power on"
cmd_poweroff = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power off"
cmd_disk = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis bootdev disk"
cmd_pxe = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis bootdev pxe"

#PXE setting
list = testbed.values()
cmd = ""
res = ""
for ipmi in list:
    cmd = cmd_poweroff.replace("%s",ipmi)
    print cmd
    while True:
        res = os.popen(cmd).read()
        print "Debug::%s:%s" % (ipmi,res)
        if "Chassis Power Control: Down/Off" in res:
            res = ""
            break
        else:
            res = ""
            time.sleep(5)

time.sleep(10)

#
#for ipmi in list:
#    cmd = cmd_pxe.replace("%s",ipmi)
#    print cmd
#    while True:
#        res = os.popen(cmd).read()
#        print "Debug::%s:%s" % (ipmi,res)
#        if "Set Boot Device to pxe" in res:
#            res = ""
#            if ipmi == "10.94.197.183":
#                time.sleep(5)
#                res = os.popen(cmd).read()
#                print "Debug::%s:%s" % (ipmi,res)
#                res = ""
#            break
#        else:
#            res = ""
#            time.sleep(5)

for ipmi in list:
    cmd = cmd_pxe.replace("%s",ipmi)
    print cmd
    while True:
        res = os.popen(cmd).read()
        print "Debug::%s:%s" % (ipmi,res)
        if "Set Boot Device to pxe" in res:
            res = ""
            break
        else:
            res = ""
            time.sleep(5)

time.sleep(10)

for ipmi in list:
    cmd = cmd_poweron.replace("%s",ipmi)
    print cmd
    while True:
        res = os.popen(cmd).read()
        print "Debug::%s:%s" % (ipmi,res)
        if "Chassis Power Control: Up/On" in res:
            res = ""
            break
        else:
            res = ""
            time.sleep(5)

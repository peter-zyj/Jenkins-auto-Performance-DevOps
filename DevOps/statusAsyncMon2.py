#!/usr/local/bin/python3
import asyncio,time
import os,sys,re

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



ipList = list(testbed.values())

def norBoot(ip):
    os.popen("ipmitool -I lanplus -H %s -U admin -P rootroot chassis bootdev disk" % (ip))
    print ("ipmitool -I lanplus -H %s -U admin -P rootroot chassis bootdev disk" % (ip))
    time.sleep(5)
    os.popen("ipmitool -I lanplus -H %s -U admin -P rootroot chassis power on" % (ip))
    print ("ipmitool -I lanplus -H %s -U admin -P rootroot chassis power on" % (ip))




#@asyncio.coroutine
def statusChk():
    global ipList
    actionTag = {}
    for ip in ipList:
        actionTag[ip] = True
    while time.time()<t_end:
        if ipList == []:
            break
        try:
            ip = ipList.pop(0)
        except IndexError:
            continue
        
        try:
            res = os.popen("ipmitool -I lanplus -H %s -U admin -P rootroot chassis status" % (ip)).read()
            if actionTag[ip]:
                print ("ipmitool -I lanplus -H %s -U admin -P rootroot chassis status" % (ip))
                actionTag[ip] = False
        except Exception as e:
            res = "IPMI error"
            print ("IPMI error:%s:%s"%(ip,e))
            pass
        state = re.findall(r'(?<=System Power).*',res)[0].replace(":","").strip()
        if state not in ['off','on']:
            print ("[statusAsyncMon.py]something unexpected happend::",res)
            sys.exit(1)
        elif state == "off":
            print ("PXE installation Completed::",ip)
            print ("Boot from local disk::",ip)
            norBoot(ip)
        else:
            ipList.append(ip)
            time.sleep(5)

t_end = time.time() + 1800
statusChk()

if ipList != []:
    cmd = ""
    for ip in ipList:
        print ("****************Attention Please!******************")
        print ("1st::Not finish the PXE install::",ip)
        print ("****************Attention Done!******************")
    cmd_poweroff = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power off"
    cmd_pxe = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis bootdev pxe"
    cmd_poweron = "ipmitool -I lanplus -H %s -U admin -P rootroot chassis power on"

    for ipmi in ipList:
        cmd = cmd_poweroff.replace("%s",ipmi)
        print (cmd)
        try:
            res = os.popen(cmd).read()
            print (res)
        except Exception as e:
            print ("2nd IPMI error:%s:%s"%(ipmi,e))

    time.sleep(10)


    for ipmi in ipList:
        cmd = cmd_pxe.replace("%s",ipmi)
        print (cmd)
        try:
            res = os.popen(cmd).read()
            print (res)
        except Exception as e:
            print ("2nd IPMI error:%s:%s"%(ipmi,e))

    time.sleep(2)

    for ipmi in ipList:
        cmd = cmd_poweron.replace("%s",ipmi)
        print (cmd)
        try:
            res = os.popen(cmd).read()
            print (res)
        except Exception as e:
            print ("2nd IPMI error:%s:%s"%(ipmi,e))


    t_end = time.time() + 900
    statusChk()

    if ipList != []:
        for ip in ipList:
            print ("2nd::Not finish the PXE install::",ip)
            sys.exit(1)

#actions = [statusChk() for i in range(10)]
#
#loop = asyncio.get_event_loop()
#loop.run_until_complete(asyncio.wait(actions))

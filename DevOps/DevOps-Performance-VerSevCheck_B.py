#!/usr/local/bin/python3
import os,sys,re
import pexpect
import asyncio
import time,optparse

print ("################start B")
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

IPlist = list(testbed.keys())
dir = "/root/slave/configuration"

cont = ""
with open("/root/slave/global/BuildInfo.properties", "r") as f:
	cont  = f.read()
vertmp = re.compile(r"(?s)(?<=IMAGE_VALUE=).*?(?=::)").findall(cont)[0]

ver = vertmp.split(":")[0]

buildtmp = re.compile(r"(?<=IMAGE_VALUE=).*").findall(cont)[0]
build = buildtmp.split("-")[-1].strip()

os.popen("echo > /root/.ssh/known_hosts")



okTag = {}
async def onlineChk(condition, ip):
    global okTag
    print('onlineChk::Start: IP({}) probing'.format(ip))
    time1 = time.time()
    await asyncio.sleep(0.1)
    ip = ip.strip()
    okTag[ip] = False

    while time.time()-time1 <= 300:
        print (ip+":"+str(time.time()))
        res = os.popen("ping {} -c 1".format(ip)).read()
        if "bytes from {}".format(ip) in res:
            okTag[ip] = True
            with await condition:
                condition.notify_all()
            break
        else:
            okTag[ip] = False
            await asyncio.sleep(5)
            continue
    if not okTag[ip]:
        with await condition:
            condition.notify_all()
    print ('onlineChk::End: IP({}) probing'.format(ip))



async def verSevCheck(condition, ip, ver, build):
    global okTag
    print ("config::waiting for successful ping {} within 10min".format(ip))
    with await condition:
        await condition.wait()
        if okTag[ip]:
            print ("SevCheck::Start:{}".format(ip))
        else:
            print ("SevCheck::Ping failed {}".format(ip))
            return 1
#################
    serviceDict = {}
    serviceDict[ip] = {}
    servicepath = dir+"/"+ver+"/"+"services"
    contServ = ""
    with open(servicepath,"r") as f:
        contServ = f.read()
    for svs in contServ.split():
        if svs != "":
            name = svs.strip().split(":")[0]
            stat = svs.strip().split(":")[1]
            cmd = "service %s status" % (name)
            restartCmd = "service %s restart" % (name)
            num = 1
            staTag = None
            while num <=3:
                num = num + 1
                result = "Reset"
                ssh,result = Standard_Reply_SSHCmmand(ip,cmd)
                ssh.close()
                result = str(result)
                if (stat == "on" and "is running" not in result) or (stat == "off" and "is running" in result):
                    if "dead" in result:
                        ssh,result = Standard_Reply_SSHCmmand(ip,restartCmd)
                        ssh.close()
                        print {"%s:dead:IP=%s:result=%s:"%(num,ip,result)}
                        await asyncio.sleep(0.1)
                        time.sleep(30)
                        continue
                    if (name == "clm" and "Running" in result and "Not" not in result and stat == "on") or \
                        (name == "clm" and "Not running" in result and stat == "off"):
                        print ("Yijun:cmd:",cmd)
                        print ("Yijun:IP:",ip)
                        staTag = stat
                        break
                    await asyncio.sleep(0.1)
                    time.sleep(10)
                    continue
                else:
                    print ("Yijun:cmd:",cmd)
                    print ("Yijun:IP:",ip)
                    staTag = stat
                    break
            if staTag == None:
                 print ("Error:cmd:",cmd)
                 print ("Error:IP:",ip)  
                 print ("Error:result:",result) 
                 sys.exit(1)
            serviceDict[ip][name] = staTag
    print (serviceDict)

        




async def main(loop,IPlist,dir,ver,build):
    print ("Main::Monitor IP fist")
    actionDict = {}
    print ("Main::waiting for the probing completed")
    for ip in IPlist:
        condition = asyncio.Condition()
        actionDict[ip] = condition
        loop.create_task(onlineChk(condition,ip))

    actions2 = [verSevCheck(actionDict[ip],ip,ver,build) for ip in IPlist]

    await asyncio.wait(actions2)


def cosInitStopper(ip):
    print ("cosInitStopper::Start:{}".format(ip))
    cmd = "touch /opt/cisco/cos/config/cosinit_executed;echo yijun"
    ssh = pexpect.spawn('ssh root@%s "%s"' % (ip,cmd))
    ssh,result = Standard_Reply_SSH(ssh,ip)
    ssh.close()





########SSH logon stuff############
default_passwd = "rootroot"
prompt_firstlogin = "Are you sure you want to continue connecting \(yes/no\)\?"
prompt_passwd = "root@.*'s password:"
prompt_logined = "\[root@.*\]#"
prompt_percentage = ".*100%.*"
prompt_tested = "\[root@.*\]#"
prompt_init = "continue ? (yes/no) [y]:"


def Standard_Reply_SSH(ssh,IP):
    try:
        result = "Not Set"
        result = ssh.expect([prompt_firstlogin, prompt_passwd, prompt_logined, pexpect.TIMEOUT, prompt_percentage],timeout=10)
        ssh.logfile = None
        if result == 0:
          ssh.sendline('yes')
          ssh.expect(prompt_passwd)
          ssh.sendline(default_passwd)
          ssh.expect("yijun")
        elif result == 1:
          ssh.sendline(default_passwd)
          ssh.expect("yijun")
        elif result == 2:
          pass
        elif result == 3:
          print ("ssh to %s timeout" %IP)
        elif result == 4:
          pass
        return ssh,result
    except Exception as e:
        print ("%s:result is %s"%(ip,result))
        print (e)
        print ('Standard_Reply_SSH::Mismatch BTW default expect or unexpected things happen!')

def Standard_Reply_SSHCmmand(IP,cmd,prompt=prompt_logined):
    try:
        result = "Not Set"
        ssh = pexpect.spawn('ssh root@%s' % IP)
        result = ssh.expect([prompt_firstlogin, prompt_passwd, prompt, prompt_init, pexpect.TIMEOUT],timeout=10)

        ssh.logfile = None
        if result == 0:
            ssh.sendline('yes')
            ssh.expect(prompt_passwd)
            ssh.sendline(default_passwd)
            ssh.expect(prompt)
            ssh.sendline(cmd)
            ssh.expect(prompt)
        elif result == 1:
            ssh.sendline(default_passwd)
            ssh.expect(prompt)
            ssh.sendline("pwd")
            ssh.expect(prompt) 
            ssh.sendline(cmd)
            ssh.expect(prompt)            
        elif result == 2:
            pass
        elif result == 3:
            ssh.sendline('n')
            ssh.expect(prompt)
            ssh.sendline(cmd)
            ssh.expect(prompt)           
        elif result == 4:
            print ("Connection::"+"ssh to %s timeout" %IP)
            return ssh,result
        return ssh,ssh.before[:-1]
    except:
        if prompt_init in ssh.before[:-1]:
            try:
                ssh.sendline('n')
                ssh.expect(prompt)
                return ssh,None
            except:
                print ("Prompt_init Error:")
                debug = "Connection::"+ssh.before[:-1]
                print (debug)
                return debug,None
        else:
            print ("result is ",result)
            print ('SSHClient::Mismatch BTW default expect or unexpected things happen!')
            debug = "Connection::"+ssh.before[:-1]
            print (debug)
            return debug,None





event_loop = asyncio.get_event_loop()

try:
    event_loop.run_until_complete(main(event_loop,IPlist,dir,ver,build))
finally:
    event_loop.close()




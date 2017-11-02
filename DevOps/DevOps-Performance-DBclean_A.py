#!/usr/local/bin/python3
import os,sys,re
import pexpect
import asyncio
import time,optparse

print ("################start A")
testbed = {}
testbed["10.94.193.80"] = "10.94.193.187"
#testbed["10.94.193.81"] = "10.94.193.188"
#testbed["10.94.193.82"] = "10.94.193.189"


IPlist = list(testbed.keys())

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



async def dbClean(condition, ip):
    global okTag
    print ("config::waiting for successful ping {} within 10min".format(ip))
    with await condition:
        await condition.wait()
        if okTag[ip]:
            print ("dbClean::Start:{}".format(ip))
        else:
            print ("dbClean::Ping failed {}".format(ip))
            return 1

    await asyncio.sleep(0.1)

    resultDict = {}

    num = 1
    okTag = False
    while num <=3:
        num = num + 1
        ssh,result = Standard_Reply_SSHCmmand(ip,"cqlsh `hostname` -e \"DROP KEYSPACE cos\"")
        ssh.close()
        print ("SSH result for 'DROP KEYSPACE cos'::-->",result)

        if result not in [0,1,3]:
            time.sleep(5)
            continue
        else:
            okTag = True
            break
    resultDict[ip] = okTag

    print (resultDict)


    time.sleep(20)
    
    num = 1
    okTag = False
    while num <=3:
        num = num + 1
        ssh,result = Standard_Reply_SSHCmmand(ip,"cqlsh `hostname` -f /opt/cisco/cmc/etc/cos.cql")
        ssh.close()
        print ("SSH result for '-f /opt/cisco/cmc/etc/cos.cql'::-->",result)

        if result not in [0,1,3]:
            time.sleep(5)
            continue
        else:
            okTag = True
            break
    resultDict[ip] = okTag

    print (resultDict)

    time.sleep(20)


async def main(loop,IPlist):
    print ("Main::Monitor IP fist")
    actionDict = {}
    print ("Main::waiting for the probing completed")
    for ip in IPlist:
        condition = asyncio.Condition()
        actionDict[ip] = condition
        loop.create_task(onlineChk(condition,ip))

    actions2 = [dbClean(actionDict[ip],ip) for ip in IPlist]

    await asyncio.wait(actions2)






########SSH logon stuff############
default_passwd = "rootroot"
prompt_firstlogin = "Are you sure you want to continue connecting \(yes/no\)\?"
prompt_passwd = "root@.*'s password:"
prompt_logined = "\[root@.*\]#"
prompt_percentage = ".*100%.*"
prompt_tested = "\[root@.*\]#"
prompt_init = "continue ? (yes/no) [y]:"


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
            ssh.expect(prompt,timeout=30)
        elif result == 1:
            ssh.sendline(default_passwd)
            ssh.expect(prompt)
            ssh.sendline("pwd")
            ssh.expect(prompt) 
            ssh.sendline(cmd)
            ssh.expect(prompt,timeout=30)            
        elif result == 2:
            pass
        elif result == 3:
            ssh.sendline('n')
            ssh.expect(prompt)
            ssh.sendline(cmd)
            ssh.expect(prompt,timeout=30)           
        elif result == 4:
            print ("Connection::"+"ssh to %s timeout" %IP)
            return ssh,result
        return ssh,result
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
    event_loop.run_until_complete(main(event_loop,IPlist))
finally:
    event_loop.close()





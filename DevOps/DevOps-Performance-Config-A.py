#!/usr/local/bin/python3
import os,sys,re
import pexpect
import asyncio
import time,optparse


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

os.popen("echo > /root/.ssh/known_hosts")



okTag = {}
async def onlineChk(condition, ip):
    global okTag
    print('onlineChk::Start: IP({}) probing'.format(ip))
    time1 = time.time()
    await asyncio.sleep(0.1)
    ip = ip.strip()
    okTag[ip] = False

    while time.time()-time1 <= 360:
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



async def config(condition, ip, dir, ver):
    global okTag
    print ("config::waiting for successful ping {} within 10min".format(ip))
    with await condition:
        await condition.wait()
        if okTag[ip]:
            print ("config::Start:{}".format(ip))
        else:
            print ("config::Ping failed {}".format(ip))
            return 1

    resultDict = execute(ip,dir,ver)
    resultDict = serviceUP(ip,dir,ver)

        




async def main(loop,IPlist,dir,ver):
    print ("Main::Monitor IP fist")
    actionDict = {}
    print ("Main::waiting for the probing completed")
    for ip in IPlist:
        condition = asyncio.Condition()
        actionDict[ip] = condition
        loop.create_task(onlineChk(condition,ip))

    actions2 = [config(actionDict[ip],ip,dir,ver) for ip in IPlist]

    await asyncio.wait(actions2)


#ssh = pexpect.spawn("ssh root@10.94.193.88 'chkconfig --level 3 cosd on'")
#ssh,result = Standard_Reply_SSH(ssh,"10.94.193.88")
def serviceUP(ip,dir,ver):
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
           cmd = "chkconfig --level 3 %s %s;echo yijun" % (name,stat)
           num = 1
           staTag = None
           while num <=3:
               num = num + 1
               ssh = pexpect.spawn('ssh root@%s "%s"' % (ip,cmd))
               ssh,result = Standard_Reply_SSH(ssh,ip)
               #ssh,result = Standard_Reply_SSHCmmand(ip,cmd) # will meet with COS_init
               if result not in [0,1,2,4] :
                   ssh.close()
                   time.sleep(5)
                   continue
               else:
                   print ("Yijun:cmd:",cmd)
                   print ("Yijun:IP:",ip)
                   ssh.close()
                   staTag = stat
                   break
        serviceDict[ip][name] = staTag
    print (serviceDict)
    

def execute(ip,dir,ver):
    resultDict = {}
    resultDict[ip] = {}
    finalDir = dir+"/"+ver+"/"+ip
    pathpath = dir+"/"+ver+"/"+"path"
    for file in os.listdir(finalDir):
        file = file.strip()
        contPath = ""
        with open(pathpath,"r") as f:
            contPath = f.read()
        pattern = r"(?s)(?<=%s::).*?(?=\n)" % (file)
        try:
            destFile = re.compile(pattern).findall(contPath)[0]
        except:
            print ("[%s]::Error::No path specified in Path for::%s" % (ip,file))
            sys.exit(1)


        num = 1
        okTag = False
        sourFile = finalDir+"/"+file
        while num <=3:
            num = num + 1
            scp = pexpect.spawn('scp %s root@%s:%s' % (sourFile,ip,destFile))
            #print("debug:::scp",scp)
            #print("debug:::ip",ip)
            scp,result = Standard_Reply_SCP(scp,ip)
            scp.close()
            if result not in [0,1,2,4] :
                time.sleep(5)
                continue
            else:
                okTag = True
                break
        resultDict[ip][file] = okTag

    print (resultDict)


########SSH logon stuff############
default_passwd = "rootroot"
prompt_firstlogin = "Are you sure you want to continue connecting \(yes/no\)\?"
prompt_passwd = "root@.*'s password:"
prompt_logined = "\[root@.*\]#"
prompt_percentage = ".*100%.*"
prompt_tested = "\[root@.*\]#"
prompt_init = "continue ? (yes/no) [y]:"

def Standard_Reply_SCP(ssh,IP):
    try:
        result = "Not Set"
        result = ssh.expect([prompt_firstlogin, prompt_passwd, prompt_logined, pexpect.TIMEOUT, prompt_percentage],timeout=10)
        ssh.logfile = None

        if result == 0:
          ssh.sendline('yes')
          ssh.expect(prompt_passwd)
          ssh.sendline(default_passwd)
          ssh.expect(prompt_percentage)
        elif result == 1:
          ssh.sendline(default_passwd)
          ssh.expect(prompt_percentage)
        elif result == 2:
          pass
        elif result == 3:
          print ("ssh to %s timeout" %IP)
        elif result == 4:
          pass
        return ssh,result
    except Exception as e:
        print ("result is ",result)
        print (e)
        print ('Standard_Reply_SCP::Mismatch BTW default expect or unexpected things happen!')
        return ssh,result


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
    except:
        print ("result is ",result)
        print ('Standard_Reply_SSH::Mismatch BTW default expect or unexpected things happen!')
        return ssh,result


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
            return result
        return ssh,result
    except:
        if prompt_init in ssh.before[:-1]:
            try:
                ssh.sendline('n')
                ssh.expect(prompt)
                return ssh
            except:
                print ("Prompt_init Error:")
                debug = "Connection::"+ssh.before[:-1]
                print (debug)
                return debug
        else:
            print ("result is ",result)
            print ('SSHClient::Mismatch BTW default expect or unexpected things happen!')
            debug = "Connection::"+ssh.before[:-1]
            print (debug)
            return debug





event_loop = asyncio.get_event_loop()

try:
    event_loop.run_until_complete(main(event_loop,IPlist,dir,ver))
finally:
    event_loop.close()



#!/usr/bin/python
import time,pexpect
import os,sys,re
from multiprocessing import Process,Queue


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



ipList = list(testbed.keys())



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
          ssh.expect("yijun",timeout=120)
        elif result == 1:
          ssh.sendline(default_passwd)
          ssh.expect("yijun",timeout=120)
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



def statusChk():
    while time.time()<t_end:
        global ipList
        if ipList == []:
            return
        try:
            ip = ipList.pop(0)
        except IndexError:
            continue
        res = os.popen("ping %s -c 1" % (ip)).read()
        if "bytes from {}".format(ip) not in res:
            ipList.append(ip)
        else:
            print ("Server bootUP Completed::",ip)
   
def cserverClean(ip):
    cmd1 = "printf cleardir | /arroyo/test/run -C;echo yijun"
    print ("%s:%s"%(ip,cmd1))
    num = 1
	while num <=3:
	    num = num + 1
	    scp = pexpect.spawn('ssh root@%s "%s"' % (ip,cmd1))
	    scp,result = Standard_Reply_SSH(scp,ip)
	    scp.close()
	    if result not in [0,1,2,4] :
	        time.sleep(5)
	        continue
	    else:
	        break

cmd = "reboot;echo yijun"


act_job = []

for ip in ipList:
    p = Process(target=cserverClean, args=(ip,))
    p.start()
    act_job.append(p)

for p in act_job:
    p.join()



print "Debug::Sleep 5min"
time.sleep(300)

for ip in ipList:
    print ("%s:%s"%(ip,cmd))
	num = 1
	while num <=3:
	    num = num + 1
	    scp = pexpect.spawn('ssh root@%s "%s"' % (ip,cmd))
	    scp,result = Standard_Reply_SSH(scp,ip)
	    scp.close()
	    if result not in [0,1,2,4] :
	        time.sleep(5)
	        continue
	    else:
	        break

t_end = time.time() + 600
time.sleep(15)
statusChk()

if ipList != []:
    for ip in ipList:
        print ("Not Yet finish the server bootup::",ip)

	sys.exit(1)

print "Debug::Sleep 4min"
time.sleep(240)

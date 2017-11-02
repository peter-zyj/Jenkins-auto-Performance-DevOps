#!/usr/bin/python

import os,sys,re,time
import pexpect

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




Standard_Reply_SSHCmmand("10.94.137.89","hostname")
print "yijunzhu~~~~~~~~~~~~!!!!!!!!!!"

#!/usr/bin/python
import os,sys,re,random
##!  parameters for the builder##
#dirname = "/cds-build/3.7.0/"
dirname = "/cds-feature-build/slave10/releases"
statFile = "/cds-feature-build/slave10/status"
##~
print "Slave node is ",os.popen("hostname").read()
print "working dir::",os.getcwd()
wkdir = os.getcwd()

build_Queue = {}

BUILD_PATH = ""
IMAGE_PATH = ""
IMAGE_VALUE = ""
BUILD_URL = ""
build = iso = ""
os.chdir(dirname)


def update(name=None,build_Queue=None,build=None):
    contR = ""
    contW = ""
    with open(name,"r") as f:
        contR=f.read()

    if build != None:
        bbNum = build.split("::")[0].strip()
        if bbNum != "":
            contW = contR.replace("%s@"%(bbNum),"")
            contW = contW.replace(build+":"+"Idle",build+":"+"Occupied")

            with open(name,"w") as f:
                f.write(contW)

    if build_Queue != None:
        contW = contR
        for b in build_Queue.keys():
            bs = build_Queue[b][0]
            if b not in contR:
                "TBD"
                "insert record"
                "insert queue"
                contW = b+"::"+build_Queue[b][0]+":"+"Idle"+":"+"None"+"\n" + contW
                q = re.findall("Queue.*",contR)[0]
                contW = contW.replace(q,q+b+"@")

            elif bs not in contR:
                "TBD"
                "update record"
                record = re.findall("(?m)^%s.*"%(b),contR)[0]
                newRecoder = re.sub("(?<=::).*?(?=:)",bs,record)
                contW = contW.replace(record,newRecoder)

        with open(name,"w") as f:
            f.write(contW)

def creation(name,build_Queue):
    cont = ""
    Queue = []
    for b in build_Queue.keys():
        cont=cont+b+"::"+build_Queue[b][0]+":"+"Idle"+":"+"None"+"\n"
        Queue.append(b)
    cont = cont + "Queue::"+"@".join(Queue) + "@\n"
    with open(name,"w") as f:
        f.write(cont)

def buildPickup(name):
    with open(name,"r") as f:
        cont=f.read()
    targetBuild = ""
    if "Occupied" in cont:
        targetBuild = "Abort"
    else:
        try:
            buildHead = re.compile(r"(?<=Queue::).*?(?=@)").findall(cont)[0]
            targetBuild = re.compile(r"%s::.*?(?=:)"%(buildHead)).findall(cont)[0]
        except:
            print ("No candidate in the Queue")


    if targetBuild in [[],'']:
        print ("Build Random pickup!")
        verList = re.compile(r"(?m)^[^Q].*::.*?(?=:)").findall(cont)
        print "debug",verList
        factor = random.randrange(0, len(verList))
        print "debug,fac",factor
        targetBuild = verList[factor]

    return targetBuild

#Main
build_List = os.popen("ls").read().strip().split()
for b in build_List:
    build_Queue[b] = []
    bNum = os.popen("ls -tr %s| tail -n 1" %(b)).read().strip()
    build_Queue[b].append(bNum)
    print "the latest build is ",bNum



if os.path.exists(statFile):
    "TBD:: insert/update/delete"
    update(name=statFile,build_Queue=build_Queue)
    build = buildPickup(statFile)
    if build in ["","Abort"]:

        sys.exit(1)
    else:
        update(name=statFile,build=build)
else:
    "TBD:: Create"
    creation(statFile,build_Queue)
    build = buildPickup(statFile)
    if build in ["","Abort"]:
    	sys.exit(1)
    else:
        update(name=statFile,build=build)



print "DEBUG::",build
with open(statFile,"r") as f:
    print f.read()

if build in ["","Abort"]:
	sys.exit(1)
else:
    buildFolder = dirname.strip()+"/"+build.split("::")[0].strip()+"/"+build.split("::")[-1].strip()
    print "the selected Build is::",buildFolder
    try:
		os.chdir(buildFolder+"/target")
		iso = os.popen("ls cos_full-*iso").read()
    except:
		print "the path is incorrect::",buildFolder+"/target"
		sys.exit(1)
    BUILD_PATH = buildFolder.strip()
    IMAGE_PATH = BUILD_PATH+"/target/"+iso.strip()
    IMAGE_VALUE = build.strip()
    BUILD_URL = "http://wwwin-earmstools.cisco.com/logs/viewdir.php?external=1&path="+BUILD_PATH
    #"replace previous 'URL' groovy scripts"
    print "Framing URL"
    os.popen("echo 'Build_Information	%s' > %s/Build_Information.txt" % (BUILD_URL,wkdir))

    print "BUILD_PATH::",BUILD_PATH
    print "IMAGE_PATH::",IMAGE_PATH
    print "IMAGE_VALUE::",IMAGE_VALUE
    print "BUILD_URL::",BUILD_URL


    os.chdir(wkdir)
    os.popen("rm -rf *.iso")
    os.popen("cp %s ." % (IMAGE_PATH))
    Result = "passed"
##################
    
    try:
    	os.mkdir("/root/slave/global")
    except:
    	pass
    os.popen("echo 'RANGE=Full' > /root/slave/global/BuildInfo.properties")
    os.popen("echo 'TestSuite=auto-test' >> /root/slave/global/BuildInfo.properties")
    os.popen("echo 'BUILD_PATH=%s' >> /root/slave/global/BuildInfo.properties"%(BUILD_PATH))
    os.popen("echo 'IMAGE_PATH=%s' >> /root/slave/global/BuildInfo.properties"%(IMAGE_PATH))
    os.popen("echo 'BUILD_URL=%s' >> /root/slave/global/BuildInfo.properties"%(BUILD_URL))
    os.popen("echo 'IMAGE_VALUE=%s' >> /root/slave/global/BuildInfo.properties"%(IMAGE_VALUE))
    os.popen('cp -rf /root/slave/global/BuildInfo.properties /root/slave/workspace/DevOps-Performance-Build/.')




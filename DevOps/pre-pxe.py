import os,sys,re

targetBuildPath = sys.argvs[1]
#folder = sys.argv[1]

try:
    os.popen("umount /mnt")
except:
    pass

#mount Full-ISO
os.popen("mount -o loop %s /mnt"%(targetBuildPath))
##copy to local dir
#os.popen("cp -r /mnt/. /var/ftp/image/COS/%s/."%(folder))
##
#os.popen("rm -rf  /var/lib/tftpboot/cos/*" % (folder))
#
##update the hardlink to new kernel,softlink dont work for pxelinux
#os.popen("cp /var/ftp/image/COS/%s/images/pxeboot/initrd.img /var/lib/tftpboot/cos/initrd.img" % (folder))
#os.popen("cp /var/ftp/image/COS/%s/images/pxeboot/vmlinuz /var/lib/tftpboot/cos/vmlinuz" % (folder))
#
##shutdown server after the PXE install completed
#os.popen("echo 'poweroff' >> /var/ftp/image/COS/3.14.1/ks/ks_auto.cfg")

#copy to local dir
try:
    os.popen("rm -rf /var/ftp/image/COS" )
except:
    pass
os.makedirs("/var/ftp/image/COS")
os.popen("cp -r /mnt/. /var/ftp/image/COS/.")
#
os.popen("rm -rf  /var/lib/tftpboot/cos/*")

#update the hardlink to new kernel,softlink dont work for pxelinux
os.popen("cp /var/ftp/image/COS/images/pxeboot/initrd.img /var/lib/tftpboot/cos/initrd.img")
os.popen("cp /var/ftp/image/COS/images/pxeboot/vmlinuz /var/lib/tftpboot/cos/vmlinuz")
#update the pxelinux.cfg with correct build number


#shutdown server after the PXE install completed
os.popen("echo 'poweroff' >> /var/ftp/image/COS/ks/ks_auto.cfg")

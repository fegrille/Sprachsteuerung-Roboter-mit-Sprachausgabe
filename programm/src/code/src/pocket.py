#!/usr/bin/env python

import os
import subprocess
import signal
import rospy
from std_msgs.msg import String

rospy.init_node('pocket')        
pub = rospy.Publisher('pocket/cmd', String, queue_size=1)
if(rospy.has_param('/pocket/dic')):
    dic = rospy.get_param('/pocket/dic')
else:
    rospy.logerr('Can not start pocketsphinx. Please configure a dictionary.')
    exit(0)
if(rospy.has_param('/pocket/lm')):
    lm = rospy.get_param('/pocket/lm')
else:
    rospy.logerr('Can not start pocketsphinx. Please specify a language model.')
    exit(0)
if(rospy.has_param('/pocket/hmm')):
    hmm = rospy.get_param('/pocket/hmm')
else:
    rospy.logerr('Can not start pocketsphinx. Please specify a training directory.')
    exit(0)
#Pipe starten, welche pocketsphinx ausführt
com = subprocess.Popen(['pocketsphinx_continuous','-inmic', 'yes', '-dict', dic ,'-lm',lm, '-hmm', hmm], stdout=subprocess.PIPE)
#Auf eine neue Erkennung von Pocketsphinx warten
while(not rospy.is_shutdown()):
    rospy.loginfo('Got Command')
    line = com.stdout.readline()
    line = line.rstrip("\n")
    if(len(line) > 0):
        pub.publish(line.lower())
    


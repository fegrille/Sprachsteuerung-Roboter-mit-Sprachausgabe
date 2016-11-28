#!/usr/bin/env python

import rospy
import math

from std_msgs.msg import String
from geometry_msgs.msg import Twist

#Initialisieren von wichtigen Variablen
#Globale Variablen werden sowohl im Hauptprogramm als auch im Subscriber gebraucht
def init():
    global sp
    global rot
    global state
    global mode
    global time3
    global rate
    global stop
    global t
    global distance
    global degree
    global clockwise
    global done
    global exit
    global simulator
    rospy.loginfo("Init")
    if(rospy.has_param('/turtsim/speed')):
        sp = rospy.get_param('/turtsim/speed')
    else:
        sp = 0.5
    if(rospy.has_param('/turtsim/rotspeed')):
        rot = rospy.get_param('/turtsim/rotspeed')
    else:
        rot = 45
    if(rospy.has_param('/turtsim/distance')):
        distance = rospy.get_param('/turtsim/distance')
    else:
        distance = 1.0
    if(rospy.has_param('/turtsim/degree')):
        degree = rospy.get_param('/turtsim/degree')
    else:
        degree = 45
    if(rospy.has_param('/turtsim/simulator')):
        simulator = rospy.get_param('/turtsim/simulator')
    else:
        rospy.logerr('Can not start node. Please specify a simulator.')
        exit(0)
    state = 1
    mode = 0
    t = Twist()
    time3 = rospy.get_time()
    rate = rospy.Rate(100)
    stop = 0
    clockwise = 0
    done = 1
    exit = 0
    rospy.loginfo("Init done")
    rospy.loginfo("-------------------------------")
    rospy.loginfo("Current Values:")
    rospy.loginfo("Distance to move: " + str(distance))
    rospy.loginfo("Speed in meter per seconds: " + str(sp))
    rospy.loginfo("Degrees to turn: " + str(degree))
    rospy.loginfo("Rotatespeed in degrees per seconds: " + str(rot))
    rospy.loginfo("-------------------------------")
    degree = degreesToRadian(degree)
    return

#Bewegungsbeispiel
#Speed - Geschwindigkeit in Meter pro sekunde
#Distance - Distanz in Metern
def move():
    #Zeitsstempel vor der Ausfuehrung
    t0 = rospy.get_time()
    #Senderate bei alle 10 ms
    rate1 = rospy.Rate(100)
    #Distanzvariable
    dis = 0.0
    while(dis < distance and stop != 1 and exit != 1):
        #Schicke vektoren mit jeweiligen Koordinaten an den Roboter
        pub.publish(t)
        #Zeitsstempel waehrend der Ausfuehren
        t1 = rospy.get_time()
        #Berechne Distanz aus Geschwindigkeit * vergangene Zeit
        dis = abs(t.linear.x * (t1-t0))
        #10 ms warten
        rate1.sleep()
    #Nachdem Distanz erreicht ist lasse den Roboter stoppen
    return

#Bewegung mit Kurve
#Speed - Geschwindigkeit in Meter pro sekunde
#Distance - Distanz in Metern
#Degree - Gradzahl der Kurve
def moveLR():
    t0 = rospy.get_time()
    rate1 = rospy.Rate(100)
    dis = 0.0
    currentangle = 0.0
    while(dis < distance and currentangle < degree and stop != 1 and exit != 1):
        pub.publish(t)
        t1 = rospy.get_time()
        if(dis < distance):
            dis = abs(t.linear.x * (t1-t0))
        else:
            t.linear.x = 0
        if(currentangle < degree):
            currentangle = abs(t.angular.z * (t1-t0))
        else:
            t.angular.z = 0
        rate1.sleep()
    return

#Auf der Stelle drehen lassen
#Degree - Grad in Bogenmass um die Gedreht werden soll
#currentangle - Bisher gedrehte Grad in Bogenmass
#Vorzeitiges Beenden mit Stop oder Exit
def turn():
    t0 = rospy.get_time()
    rate1 = rospy.Rate(100)
    currentangle = 0.0
    while(currentangle < degree and stop != 1 and exit != 1):
        pub.publish(t)
        t1 = rospy.get_time()
        currentangle = abs(t.angular.z * (t1-t0))
        rate1.sleep()
    return

def degreesToRadian(degrees):
    return degrees * math.pi / 180.0

#Reaktion auf einen Eingang von pocket.py
#Der Befehl wird einsortiert und die richtigen Werte gesetzt
def callback(msg):
    global sp
    global rot
    global state
    global mode
    global time
    global time3
    global rate
    global stop
    global t
    global distance
    global degree
    global clockwise
    global done
    global exit
    time = rospy.get_time()
    command = msg.data.split()
    if(msg.data == "stop"):
        espeak.publish(msg.data)
        rospy.loginfo("Command: Stop")
        state = 0
        stop = 1
        setValues(0,0,0,0,0,0)
        time3 = rospy.get_time()
        #stoppe saemtliche bewegung des roboters
        pub.publish(t)
    if(msg.data == "start"):
        stop = 0
        espeak.publish(msg.data)
        rospy.loginfo("Command: Start")
    if(msg.data == "exit"):
        rospy.loginfo("Command: Exit")
        exit = 1
        stop = 1
        done = 1
        espeak.publish(msg.data)
    if(msg.data == "change mode"):
        espeak.publish(msg.data)
        rospy.loginfo("Command: Change mode")
        if(mode == 0):
            mode = 1 #Continous mode
            espeak.publish("Robot is now using continous mode")
            rospy.loginfo("Robot is now using continous mode")
        else:
            mode = 0 #Distance mode
            espeak.publish("Robot is now using distance mode")
            rospy.loginfo("Robot is now using distance mode")
    if(command[0] == "move" and len(command) == 2):
        if(command[1] == "forward"):
            state = 2
            #bewege dich mit fixer geschwindigkeit vorwaerts
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            clockwise = 0
            setValues(abs(sp),0,0,0,0,0)
            time3 = rospy.get_time()
            done = 0
        if(command[1] == "backward"):
            state = 3
            #bewege dich mit fixer geschwindigkeit rueckwaerts
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            clockwise = 1
            setValues(-abs(sp),0,0,0,0,0)
            time3 = rospy.get_time()
            done = 0
        if(command[1] == "left"):
            state = 4
            clockwise = 0
            #bewege dich mit fester geschwindigkeit und bestimmter grad zahl nach links
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            setValues(abs(sp),0,0,0,0,abs(degreesToRadian(rot)))
            time3 = rospy.get_time()
            done = 0
        if(command[1] == "right"):
            state = 5
            clockwise = 0
            #bewege dich mit fester geschwindigkeit und bestimmter grad zahl nach rechts
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            setValues(abs(sp),0,0,0,0,-abs(degreesToRadian(rot)))
            time3 = rospy.get_time()
            done = 0
        if(command[1] == "fast"):
            #Erhoehe Geschwindigkeit um 0.1 m/s
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            sp = sp + 0.1
            updateSpeed()
            espeak.publish("Speed is now at " + str(sp) + " meters per second")
            rospy.loginfo("-------------------------------")
            rospy.loginfo("Speed is now at " + str(sp) + " meters per second")
            rospy.loginfo("-------------------------------")
        if(command[1] == "slow"):
            #Verringer Geschwindigkeit um 0.1 m/s
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            if((sp - 0.1) == 0.0):
                espeak.publish("Speed can't be smaller than 0.0")
                rospy.loginfo("Speed can't be smaller than 0.0")
            else:
                sp = sp - 0.1
                updateSpeed()
                espeak.publish("Speed is now at " + str(sp) + " meters per second")
                rospy.loginfo("-------------------------------")
                rospy.loginfo("Speed is now at " + str(sp) + " meters per second")
                rospy.loginfo("-------------------------------")
    if(command[0] == "turn" and len(command) == 2):
        if(command[1] == "left"):
            state = 6
            #drehe um bestimmte grad zahl nach links
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            setValues(0,0,0,0,0,abs(degreesToRadian(rot)))
            time3 = rospy.get_time()
            done = 0
            return
        if(command[1] == "right"):
            state = 7
            #drehe um bestimmte grad zahl nach rechts
            rospy.loginfo("Command: " + msg.data)
            espeak.publish(msg.data)
            setValues(0,0,0,0,0,-abs(degreesToRadian(rot)))
            time3 = rospy.get_time()
            done = 0
    time2 = rospy.get_time()
    ti = time2 - time
    rospy.loginfo("Umsetzung des Commandos in Werte (in Sekunden):" + str(ti))

#Aktualisiert das Tempo entsprechend der Fahrrichtung   
def updateSpeed():
    if(t.linear.x != 0):
        if(clockwise == 0):
            t.linear.x = abs(sp)
        else:
            t.linear.x = -abs(sp)

#Setzt Werte der Twist Variable    
def setValues(linX,linY,linZ,angX,angY,angZ):
    t.linear.x = linX
    t.linear.y = linY
    t.linear.z = linZ
    t.angular.x = angX
    t.angular.y = angY
    t.angular.z = angZ
    return
    
    
#Routine bei CTRL+C zum Beenden der Programms
def clear():
    exit = 1
    stop = 1
    done = 1
    espeak.publish("Programm will shut down")
    
rospy.init_node('thesis')
rospy.on_shutdown(clear)
init()
rate = rospy.Rate(100)
sub = rospy.Subscriber('pocket/cmd', String, callback)
if(simulator == "gazebo"):
    pub = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=1)
if(simulator == "turtlesim"):
    pub = rospy.Publisher('turtle1/cmd_vel', Twist, queue_size=1)
espeak = rospy.Publisher('espeak_node/speak_line', String, queue_size=1)
while(exit == 0):
    while(stop == 0):
        if(mode == 0 and done == 0):
            if(state == 0): #Stop
                pub.publish(t)
                done = 1
            if(state == 2): #Move forward
                move()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            if(state == 3): #Move backward
                move()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            if(state == 4): #Move left
                moveLR()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            if(state == 5): #Move right
                moveLR()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            if(state == 6): #Turn left
                turn()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            if(state == 7): #Turn right
                turn()
                setValues(0,0,0,0,0,0)
                pub.publish(t)
                rate.sleep();
                done = 1
            time4 = rospy.get_time()
            past = time4 - time3
            rospy.loginfo('Time for execute Command (secs): ' + str(past))
        while(mode == 1 and stop == 0):
            pub.publish(t)
            done == 1
            time4 = rospy.get_time()
        setValues(0,0,0,0,0,0)
        pub.publish(t)
setValues(0,0,0,0,0,0)
pub.publish(t)

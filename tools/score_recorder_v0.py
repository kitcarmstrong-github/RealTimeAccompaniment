from __future__ import print_function
import threading
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time
import logging
import sys
import time
import rtmidi

import os

import matplotlib
import matplotlib.pyplot as plt
from rtmidi.midiutil import open_midiinput

from pynput import keyboard

time_start=time.time()
log=''
inputmsglog=[]
inputtiminglog=[]
receivednotelog=[]
scorelog=[] #before arranging order
outputscore=[] #final output




midiout = rtmidi.MidiOut()
print(midiout.get_ports())
midiout.open_port(1)

port = sys.argv[1] if len(sys.argv) > 1 else None
midiin, port_name = open_midiinput(port)

onoff=[]
notes=[]
scorepositions=[]

noteon_notes=[]
noteon_scorepositions=[]

quantize_per_beat=4

def inputreading():
    global running,eventnumber,scorelog
    global quantize_per_beat
    global inputmsglog,inputtiminglog,onoff,notes,scorepositions,noteon_notes,noteon_scorepositions
    print('\n inputreading starts ')
    beattime=range(1,101)
    print(beattime)
    beatplayed=np.zeros(100)

    current_time=0
    firstposition=0 #initiate the variable. this will be overwritten by the time at which the first note is actually played
    while running==1:# and current_time<9:
        time_stamp = time.time()            # Get current time.
        current_time = time_stamp - time_start

        for i in range(100):
            if beattime[i]<=current_time and beatplayed[i]==0:
                midiout.send_message([0x90,108,127])
                print('beat ',i)
                beatplayed[i]=1
        msg = midiin.get_message()
        if msg:
            current_time = time.time() - time_start
            inputmsglog+=[['Keyboard1',msg[0][0],msg[0][1],msg[0][2],current_time]]
            if True:
                onoff+=[msg[0][0]]
                notes+=[msg[0][1]]
                currentposition=round(current_time*quantize_per_beat)/quantize_per_beat
                if firstposition==0:
                    firstposition=currentposition
                scorepositions+=[currentposition-firstposition+3]
                scorelog+=[[msg[0][0],msg[0][1],currentposition-firstposition]]
            
            if msg[0][0]==144: #only noteon
                noteon_notes+=[msg[0][1]]
                currentposition=round(current_time*quantize_per_beat)/quantize_per_beat
                noteon_scorepositions+=[currentposition-firstposition+3]

         #midiout.send_message(msg[0])
        #  if msg[0][2]>0 and msg[0][0]>143:
        #      inputtiminglog+=[current_time]
         #print('\n inputreading writes:'+str(msg))


running=1
threading.Thread(target=inputreading).start()

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    global running,outputscore,scorelog
    if key == keyboard.Key.esc:
        #print("pressed ESC")
        running=0 #this stops the threads

        # print(onoff)
        # print(notes)
        # print(scorepositions)
        # print('\n noteon only')
        # print(noteon_notes)
        # print(noteon_scorepositions)

        print('\n score log')
        print(scorelog)

        #order the events
        eventnumber=0

        for t in np.arange(0,101,1/quantize_per_beat):
            thisbeat_events=[] #temporary array to contain all the events that happened on that beat
            for i in range(len(scorelog)):
                if scorelog[i][2]==t:
                    thisbeat_events+=[scorelog[i]]
            #print(str(t)+' thisbeat_events '+str(thisbeat_events))
            sort1=sorted(thisbeat_events, key=lambda x: x[1])
            sort2=sorted(sort1, key=lambda x: x[0])
            #print(str(t)+' sorted '+str(sort2))
            for event in sort2:
                outputscore+=[[eventnumber]+event]
                lastnotetiming=event[2]
                eventnumber+=1

        print('\n score log')
        print(scorelog)

        logdirectory="logs/score_recorder_"+str(time.time())
        os.makedirs(logdirectory)

        inputlogfile=open(logdirectory+"/inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()

        scorefile=open(logdirectory+"/outputscore.txt","w")
        scorefile.write(str(outputscore))
        scorefile.close()

        #plotting
        plt.figure(figsize=(2*lastnotetiming,15))

        on_x=[]
        on_y=[]
        off_x=[]
        off_y=[]
        hold_x=[]
        hold_y=[]
        annotate_txt=[]
        annotate_x=[]
        annotate_y=[]
        #make endpoints of each note
        for event in outputscore:
            if event[1]==144:
                on_x+=[event[3]]
                on_y+=[event[2]]
                annotate_txt+=[event[0]]
                annotate_x+=[event[3]]
                annotate_y+=[event[2]]
            if event[1]==128:
                off_x+=[event[3]]
                off_y+=[event[2]]
                annotate_txt+=[event[0]]
                annotate_x+=[event[3]]
                annotate_y+=[event[2]]
                found=0
                for t in np.arange(1/quantize_per_beat,101,0.5/quantize_per_beat):
                    for a in outputscore: #search backwards for the last noteon event
                        if a[2]==event[2] and a[3]==event[3]-t:
                            if a[1]==144: #if it's not, that means it finds a noteoff event first, i.e. the note had 0 duration. we hope this never happens.
                                plt.plot([a[3], event[3]],[event[2],a[2]],'m-')
                            found=1
                            break
                    if found==0:
                        hold_x+=[event[3]-t]
                        hold_y+=[event[2]]
                    else:
                        break
                            
        plt.plot(on_x, on_y,'o')
        plt.plot(off_x, off_y,'*')
        # plt.plot(hold_x, hold_y,'s')
        plt.xticks(np.arange(0, lastnotetiming+2))
        xmin, xmax, ymin, ymax = plt.axis()
        plt.yticks(np.arange(int(ymin), int(ymax)))
        for t in range(0,int(lastnotetiming)+2):
            plt.axvline(x=t)
        for i,txt in enumerate(annotate_txt):
            plt.annotate(txt,(annotate_x[i],annotate_y[i]+0.25)) #label each event with its number
        plt.savefig(logdirectory+'/plot.png')

        return False


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()




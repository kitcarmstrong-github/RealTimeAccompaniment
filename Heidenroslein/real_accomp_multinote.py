from __future__ import print_function
import threading
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time
import keyboard
import logging
import sys
import time
import rtmidi

from rtmidi.midiutil import open_midiinput

time_start=time.time()
log=''
inputmsglog=[]
inputtiminglog=[]
receivednotelog=[]
outputlog=''
noteon_outputtiminglog=[]
noteon_realoutputlog=[]
noteoff_outputtiminglog=[]
noteoff_realoutputlog=[]
workerlog=''
workertiminglog=[]
calculatingtiminglog=[]


OutputNoteIndex=0

def noteonoff_to_noteon(onoff,notes,scorepositions):
    noteon_notes=[]
    noteon_scorepositions=[]
    for i in range(len(onoff)):
        if onoff[i]==144:
            noteon_notes+=[notes[i]]
            noteon_scorepositions+=[scorepositions[i]]
    return [noteon_notes,noteon_scorepositions]

def remove_noteonoff_duplicates(onoff,notes,scorepositions):
    newonoff=[]
    newnotes=[]
    newscorepositions=[]
    for i in range(len(onoff)):
        dontcopy=0
        for j in range(len(onoff)):
            if notes[i]==notes[j] and onoff[i]==128 and onoff[j]==144 and scorepositions[i]==scorepositions[j]:
                dontcopy=1
                break
        if dontcopy==0:
            newonoff+=[onoff[i]]
            newnotes+=[notes[i]]
            newscorepositions+=[scorepositions[i]]
    return [newonoff,newnotes,newscorepositions]



accompaniment_onoff=[144, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 128, 144, 144, 144, 128, 128, 144, 144, 128, 128, 128, 144, 144, 144, 128, 128, 128, 144, 144, 144, 128, 144, 128, 128, 144, 128, 144, 144, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 144, 128, 128, 128]
accompaniment_notes=[74, 43, 74, 73, 73, 74, 74, 76, 47, 76, 74, 43, 47, 50, 72, 74, 72, 72, 50, 72, 55, 71, 72, 71, 76, 74, 76, 55, 74, 74, 55, 43, 74, 43, 55, 76, 60, 78, 76, 76, 78, 76, 74, 74, 76, 48, 78, 76, 60, 81, 78, 60, 48, 79, 81, 78, 79, 55, 60, 76, 78, 76, 74, 74, 76, 76, 74, 43, 55, 74, 43]
accompaniment_scorepositions=[3.0, 3.0, 3.625, 3.75, 3.75, 3.875, 3.875, 3.875, 4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.5, 5.5, 6.0, 6.0, 6.0, 6.0, 6.0, 6.25, 6.25, 6.5, 6.5, 6.75, 6.75, 6.875, 6.875, 7.0, 7.0, 7.0, 8.0, 8.875, 9.0, 9.0, 9.0, 9.5, 9.5, 9.625, 9.625, 9.75, 9.75, 9.875, 9.875, 10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 11.0, 11.5, 11.5, 12.0, 12.0, 12.0, 12.0, 12.5, 12.5, 12.75, 12.75, 12.875, 12.875, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0]

# input_onoff=[144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 128, 144, 144, 128, 128, 144, 128, 128, 144, 144, 128, 144, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 128, 144, 144, 144, 128, 128, 128, 128, 144, 144, 128, 144, 144, 144, 128, 128, 128, 128, 144, 144, 144, 128, 144, 144, 128, 128, 144, 128, 128, 144, 144, 144, 128, 128, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 144, 128, 128, 128]
# input_notes=[60,60,60,60,60,60,31, 55, 55, 59, 62, 59, 62, 55, 55, 35, 31, 55, 55, 62, 59, 59, 55, 62, 55, 38, 35, 54, 54, 62, 57, 62, 54, 57, 54, 38, 43, 55, 55, 59, 62, 59, 62, 55, 55, 43, 31, 55, 55, 59, 67, 59, 55, 67, 55, 66, 60, 66, 60, 57, 57, 65, 62, 65, 59, 62, 31, 59, 48, 55, 55, 64, 60, 55, 64, 60, 55, 48, 36, 55, 55, 66, 62, 55, 62, 66, 55, 36, 48, 55, 64, 55, 67, 55, 67, 64, 66, 48, 55, 62, 43, 55, 62, 66, 55, 64, 60, 64, 55, 60, 55, 43, 31, 62, 59, 59, 31, 62]
# input_scorepositions=[0,0.5,1,1.5,2,2.5,3.0, 3.25, 3.5, 3.5, 3.5, 3.75, 3.75, 3.75, 4.0, 4.0, 4.0, 4.25, 4.5, 4.5, 4.5, 4.75, 4.75, 4.75, 5.0, 5.0, 5.0, 5.25, 5.5, 5.5, 5.5, 5.75, 5.75, 5.75, 6.0, 6.0, 6.0, 6.25, 6.5, 6.5, 6.5, 6.75, 6.75, 6.75, 7.0, 7.0, 7.0, 7.25, 7.5, 7.5, 7.5, 7.75, 7.75, 7.75, 8.0, 8.0, 8.0, 8.25, 8.25, 8.25, 8.5, 8.5, 8.5, 8.75, 8.75, 8.75, 9.0, 9.0, 9.0, 9.25, 9.5, 9.5, 9.5, 9.75, 9.75, 9.75, 10.0, 10.0, 10.0, 10.25, 10.5, 10.5, 10.5, 10.75, 10.75, 10.75, 11.0, 11.0, 11.0, 11.25, 11.5, 11.5, 11.5, 11.75, 11.75, 11.75, 12.0, 12.0, 12.0, 12.0, 12.0, 12.25, 12.25, 12.25, 12.5, 12.5, 12.5, 12.75, 12.75, 12.75, 13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14.0]

input_onoff=[]
input_notes=[]
input_scorepositions=[]
for i in range(100):
    input_onoff+=[144]
    input_notes+=[i+48]
    input_scorepositions+=[i]

# input_onoff=[144, 128, 144, 128, 144, 128,144, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 128, 144, 144, 144, 128, 128, 144, 144, 128, 128, 128, 144, 144, 144, 128, 128, 128, 144, 144, 144, 128, 144, 128, 128, 144, 128, 144, 144, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 144, 128, 128, 128]
# input_notes=[60,60,60,60,60,60,74, 43, 74, 73, 73, 74, 74, 76, 47, 76, 74, 43, 47, 50, 72, 74, 72, 72, 50, 72, 55, 71, 72, 71, 76, 74, 76, 55, 74, 74, 55, 43, 74, 43, 55, 76, 60, 78, 76, 76, 78, 76, 74, 74, 76, 48, 78, 76, 60, 81, 78, 60, 48, 79, 81, 78, 79, 55, 60, 76, 78, 76, 74, 74, 76, 76, 74, 43, 55, 74, 43]
# input_scorepositions=[0,0.5,1,1.5,2,2.5,3.0, 3.0, 3.625, 3.75, 3.75, 3.875, 3.875, 3.875, 4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.5, 5.5, 6.0, 6.0, 6.0, 6.0, 6.0, 6.25, 6.25, 6.5, 6.5, 6.75, 6.75, 6.875, 6.875, 7.0, 7.0, 7.0, 8.0, 8.875, 9.0, 9.0, 9.0, 9.5, 9.5, 9.625, 9.625, 9.75, 9.75, 9.875, 9.875, 10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 11.0, 11.5, 11.5, 12.0, 12.0, 12.0, 12.0, 12.5, 12.5, 12.75, 12.75, 12.875, 12.875, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0]

# accompaniment_onoff=[ 144, 144, 128, 144, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 128, 144, 144, 128, 128, 144, 128, 128, 144, 144, 128, 144, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 128, 144, 144, 144, 128, 128, 128, 128, 144, 144, 128, 144, 144, 144, 128, 128, 128, 128, 144, 144, 144, 128, 144, 144, 128, 128, 144, 128, 128, 144, 144, 144, 128, 128, 128, 144, 144, 128, 144, 128, 128, 128, 144, 144, 144, 128, 128, 128]
# accompaniment_notes=[31, 55, 55, 59, 62, 59, 62, 55, 55, 35, 31, 55, 55, 62, 59, 59, 55, 62, 55, 38, 35, 54, 54, 62, 57, 62, 54, 57, 54, 38, 43, 55, 55, 59, 62, 59, 62, 55, 55, 43, 31, 55, 55, 59, 67, 59, 55, 67, 55, 66, 60, 66, 60, 57, 57, 65, 62, 65, 59, 62, 31, 59, 48, 55, 55, 64, 60, 55, 64, 60, 55, 48, 36, 55, 55, 66, 62, 55, 62, 66, 55, 36, 48, 55, 64, 55, 67, 55, 67, 64, 66, 48, 55, 62, 43, 55, 62, 66, 55, 64, 60, 64, 55, 60, 55, 43, 31, 62, 59, 59, 31, 62]
# accompaniment_scorepositions=[3.0, 3.25, 3.5, 3.5, 3.5, 3.75, 3.75, 3.75, 4.0, 4.0, 4.0, 4.25, 4.5, 4.5, 4.5, 4.75, 4.75, 4.75, 5.0, 5.0, 5.0, 5.25, 5.5, 5.5, 5.5, 5.75, 5.75, 5.75, 6.0, 6.0, 6.0, 6.25, 6.5, 6.5, 6.5, 6.75, 6.75, 6.75, 7.0, 7.0, 7.0, 7.25, 7.5, 7.5, 7.5, 7.75, 7.75, 7.75, 8.0, 8.0, 8.0, 8.25, 8.25, 8.25, 8.5, 8.5, 8.5, 8.75, 8.75, 8.75, 9.0, 9.0, 9.0, 9.25, 9.5, 9.5, 9.5, 9.75, 9.75, 9.75, 10.0, 10.0, 10.0, 10.25, 10.5, 10.5, 10.5, 10.75, 10.75, 10.75, 11.0, 11.0, 11.0, 11.25, 11.5, 11.5, 11.5, 11.75, 11.75, 11.75, 12.0, 12.0, 12.0, 12.0, 12.0, 12.25, 12.25, 12.25, 12.5, 12.5, 12.5, 12.75, 12.75, 12.75, 13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14.0]

input_onoff=[]
input_notes =  [71, 71, 71, 71, 71, 71, 71, 71, 74, 72, 72, 71, 69, 69, 69, 71, 72, 74, 79, 71, 71, 71, 71, 74, 73, 73, 71, 69, 74, 74, 76, 74, 73, 74, 76, 78, 74, 74, 78, 76, 74, 73, 71, 70, 71, 79, 73, 74, 69, 69, 71, 72, 74, 76, 78, 79, 76, 79, 72, 76, 67, 71, 69, 67]
input_scorepositions =  [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0, 8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 12.5, 13.0, 13.5, 14.0, 14.25, 14.5, 14.75, 15.0, 16.0, 16.5, 17.0, 17.75, 18.0, 18.25, 18.5, 18.75, 19.0, 20.0, 20.25, 20.5, 20.75, 21.0, 21.25, 21.5, 21.75, 22.0, 22.75, 23.0, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 26.75, 27.0, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 30.75, 31.0]     

for ii in range(len(input_scorepositions)):
    if input_scorepositions[ii] ==0: 
        input_scorepositions[ii] =input_scorepositions[ii]
    elif input_scorepositions[ii] ==1 or input_scorepositions[ii]==2 or input_scorepositions[ii]==3:    
        input_scorepositions[ii] =input_scorepositions[ii]/2
        
    else:
        input_scorepositions[ii]= input_scorepositions[ii]-2

    input_onoff+=[144]


accompaniment_onoff=[]
accompaniment_notes =  [55, 62, 67, 71, 55, 62, 67, 71, 55, 64, 69, 72, 55, 64, 69, 72, 54, 62, 69, 72, 48, 62, 66, 69, 47, 62, 67, 74, 43, 62, 67, 71, 55, 62, 67, 71, 55, 62, 67, 71, 55, 64, 69, 73, 55, 64, 69, 73, 54, 69, 74, 55, 71, 76, 57, 67, 73, 59, 66, 74, 54, 69, 74, 55, 71, 76, 57, 67, 73, 50, 66, 74, 50, 66, 69, 48, 62, 66, 69, 47, 62, 67, 74, 43, 62, 67, 71, 48, 64, 67, 72, 52, 60, 67, 72, 50, 62, 67, 71, 60, 66, 69, 55, 59, 67]
accompaniment_scorepositions =  [4.0, 4.5, 4.5, 4.5, 5.0, 5.5, 5.5, 5.5, 6.0, 6.5, 6.5, 6.5, 7.0, 7.5, 7.5, 7.5, 8.0, 8.5, 8.5, 8.5, 9.0, 9.5, 9.5, 9.5, 10.0, 10.5, 10.5, 10.5, 11.0, 11.5, 11.5, 11.5, 12.0, 12.5, 12.5, 12.5, 13.0, 13.5, 13.5, 13.5, 14.0, 14.5, 14.5, 14.5, 15.0, 15.5, 15.5, 15.5, 16.0, 16.5, 16.5, 17.0, 17.5, 17.5, 18.0, 18.5, 18.5, 19.0, 19.5, 19.5, 20.0, 20.5, 20.5, 21.0, 21.5, 21.5, 22.0, 22.5, 22.5, 23.0, 23.5, 23.5, 24.0, 24.5, 24.5, 25.0, 25.5, 25.5, 25.5, 26.0, 26.5, 26.5, 26.5, 27.0, 27.5, 27.5, 27.5, 28.0, 28.5, 28.5, 28.5, 29.0, 29.5, 29.5, 29.5, 30.0, 30.0, 30.0, 30.0, 30.5, 30.5, 30.5, 31.0, 31.0, 31.0]


for iii in range(len(accompaniment_scorepositions)):
    accompaniment_scorepositions[iii]= accompaniment_scorepositions[iii]-2
    accompaniment_onoff+=[144] 



#to fix: record the real accompaniment, with correct note on and note off.


[input_notes,input_scorepositions]=noteonoff_to_noteon(input_onoff,input_notes,input_scorepositions)
[accompaniment_onoff,accompaniment_notes,accompaniment_scorepositions]=remove_noteonoff_duplicates(accompaniment_onoff,accompaniment_notes,accompaniment_scorepositions)



print(input_notes)
print(input_scorepositions)



midiout = rtmidi.MidiOut()
print(midiout.get_ports())
midiout.open_port(0)

port = sys.argv[1] if len(sys.argv) > 1 else None
midiin, port_name = open_midiinput(port)

inputqueue = queue.Queue()

def inputreading():
    global inputmsglog,inputtiminglog
    print('\n inputreading starts ')
    while True:
     msg = midiin.get_message()
     if msg:
         current_time = time.time() - time_start
         inputqueue.put([[msg[0][0],msg[0][1],msg[0][2]],current_time])
         inputmsglog+=[['Input',msg[0][0],msg[0][1],msg[0][2],current_time]]
         if msg[0][2]>0 and msg[0][0]>143:
             inputtiminglog+=[current_time]
         #print('\n inputreading writes:'+str(msg))



q = []

def NoteOn(note):
    midiout.send_message([0x90,note[1],note[2]])

def NoteOff(note):
    midiout.send_message([0x80,note[1],note[2]])

def worker():
    print('\n worker starts ')
    global q
    global OutputNoteIndex
    global log,workerlog,workertiminglog,outputlog,noteon_outputtiminglog,noteon_realoutputlog,noteoff_outputtiminglog,noteoff_realoutputlog
    alreadyplayed=np.zeros(1000)
    while True:
        time_stamp = time.time()            # Get current time.
        current_time = time_stamp - time_start
        #print('q lenght',len(q))
        for i in range(len(q)):               # If there is data in queue.
            #workerlog+='\n'+str(current_time)+' queue has '+str(len(q))+'elements, looking at #'+str(i)
            try:
                note = q[i]
    #            workerlog+='\n'+str(current_time)+' processing element #'+str(i)+'= '+str(note)+' OutputNoteIndex is '+str(OutputNoteIndex)
                if (note[3] <= (current_time)):       # Check the time stamp
                                                            # of the data.
                    q.pop(i)
                    #workerlog+='\n'+str(current_time)+' popped from queue element #'+str(i)
                    if alreadyplayed[note[5]]==0: #don't play a note already played
                        if (note[0] == 'note_on'):
                            NoteOn(note)
                            print('OUTPUT',current_time,note)
                            noteon_outputtiminglog+=[note[3]] #[[note[3],note[5]]]
                            noteon_realoutputlog+=[current_time] #[[current_time,note[5]]]                            
                        elif (note[0] == 'note_off'):
                            NoteOff(note)
                            print('OUTPUT',current_time,note)
                            noteoff_outputtiminglog+=[note[3]] #[[note[3],note[5]]]
                            noteoff_realoutputlog+=[current_time] #[[current_time,note[5]]]                            
                        # if note[5]>OutputNoteIndex:
                        #     print(str(current_time)," ERROR: Expecting OutputNoteIndex ",OutputNoteIndex," already arrived at ", str(note))
                        OutputNoteIndex=note[5]+1
                        alreadyplayed[note[5]]=1
#                        log+='\n'+str(current_time)+' output from queue'+str(note)
#                        workerlog+='\n'+str(current_time)+' worker outputs'+str(note)
#                        outputlog+='\n'+str(current_time)+str(note)
                        break


            except:
                pass
        #workertiminglog+=[current_time]    

# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

threading.Thread(target=inputreading).start()

# test output
##for i in range(5):
##    q.put(['note_on',i+40,100,i,'test',i])


framerate=100
theta1=np.zeros(200*framerate)
theta2=np.zeros(200*framerate)
theta3=np.zeros(200*framerate)


def calculating():
    global q
    global calculatingcycletimes
    global theta1,theta2,theta3
    global log,receivednotelog,calculatingtiminglog
    global inputtimings,outputtimings
    print('\n calculating starts ')
    
    reactiontime=10 #in frames

    Omega2=0.002
    Omega3=0.002
    theta2[0]=0
    theta2[1]=Omega2
    theta3[0]=0
    theta3[1]=Omega2

    K21=0.05
    K23=0.05
    K32=0.05

    inputtimings=np.zeros(1000)
    inputoscillatorpositions=np.zeros(1000)
    inputvelocity=np.zeros(1000)
    outputtimings=np.zeros(1000)
    outputoscillatorpositions=np.zeros(1000)
    
    alreadyoff=np.zeros(1000)

    for NoteIndex in range(0,len(input_scorepositions)):
        #understand where we are in the score, based on the input
        inputoscillatorpositions[NoteIndex]=2*np.pi*(input_scorepositions[NoteIndex]+1) #NoteIndex starts at 0, scorepositions start at 0. Add 2 pi because we want the first note to be at 2 pi
    
    for i in range(0,len(accompaniment_scorepositions)):
        #understand where we are in the score, based on the input
        outputoscillatorpositions[i]=2*np.pi*(accompaniment_scorepositions[i]+1) #NoteIndex starts at 0, scorepositions start at 0. Add 2 pi because we want the first note to be at 2 pi
    
    NoteIndex=0

    lastpredictionframe=0

    #initialize the lastinputposition and nextinputposition variables
    lastinputposition=0
    for i in range(len(inputoscillatorpositions)):
        if inputoscillatorpositions[i]>lastinputposition:
            nextInputPositionAndIndex=[inputoscillatorpositions[i],i]
            break
    #print(nextInputPositionAndIndex)
    
    while True:
        #print('calculating thread is still alive',time.time())
        time_stamp = time.time()            # Get current time
        current_time = time_stamp - time_start
        #calculatingcycletimes+=[current_time]


        #first calculate inputtimings
        newNotesAppeared=[]

        while not inputqueue.empty():
            midi_data=inputqueue.get()
            #print(current_time,midi_data)

            # [0][2] is velocity, [0][1] is note number, [0][0] noteon off
            if midi_data[0][2]>0 and midi_data[0][0]>143: #i.e. it's a note-on event
                #does it correspond to one of the notes expected?
                backlimit=lastinputposition-np.pi
                forwardlimit=nextInputPositionAndIndex[0]+np.pi
                foundNote=0
                for i in range(0,min(NoteIndex+1,100)): #i.e. it starts searching backwards
                    if inputoscillatorpositions[NoteIndex-i]<backlimit: #search backwards only half a beat
                        break
                    if input_notes[NoteIndex-i]==midi_data[0][1] and inputtimings[NoteIndex-i]==0: #if the note matches, and it hasn't been played yet
                        foundNote=1
                        NoteIndex+=-i
                        break #so it only gets the first matching note it encounters
                if foundNote==0:
                    for i in range(1,min(len(inputoscillatorpositions)-NoteIndex,100)): # searching forwards
                        if inputoscillatorpositions[NoteIndex+i]>forwardlimit: #search forwards only half a beat beyond the next note/chord
                            break
                        if input_notes[NoteIndex+i]==midi_data[0][1] and inputtimings[NoteIndex+i]==0: #if the note matches, and it hasn't been played yet
                            foundNote=1
                            NoteIndex+=i
                            break #so it only gets the first matching note it encounters
                if foundNote==1:
                    inputtimings[NoteIndex]=midi_data[1]
                    inputvelocity[NoteIndex]=midi_data[0][2]
                    newNotesAppeared+=[NoteIndex]
                    lastinputposition=inputoscillatorpositions[NoteIndex]
                    for i in range(NoteIndex,len(inputoscillatorpositions)):
                        if inputoscillatorpositions[i]>lastinputposition:
                            nextInputPositionAndIndex=[inputoscillatorpositions[i],i]
                            break
                    print(current_time, 'received', midi_data, ' matched it NoteIndex', NoteIndex,inputoscillatorpositions[NoteIndex],'inputtiming',inputtimings[NoteIndex])
                if foundNote==0:
                    print(current_time, 'received', midi_data, ' cannot match it to any note between beats ', backlimit/np.pi,' and ',forwardlimit/np.pi)


        if len(newNotesAppeared)>0:
            currentframe=int(framerate*current_time)
            #print(str(current_time),'calculating frames', lastpredictionframe,currentframe)
            lastnoteframe=int(inputtimings[newNotesAppeared[-1]]*framerate)
            for t in range(lastpredictionframe,lastnoteframe+1):
                #calculate theta1 from inputtimings, starting from lastpredictionframe
                theta1[t]=theta1[lastpredictionframe]+(inputoscillatorpositions[newNotesAppeared[-1]]-theta1[lastpredictionframe])*(t-lastpredictionframe)/(inputtimings[newNotesAppeared[-1]]*framerate-lastpredictionframe)
            for t in range(lastnoteframe+1,currentframe+1):
                theta1[t]=inputoscillatorpositions[newNotesAppeared[-1]]
            for t in range(lastpredictionframe,currentframe+1):
                if t<100:
                    theta2[t+1]=theta2[t]+Omega2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                    theta3[t+1]=theta3[t]+Omega2+K32*(theta2[t]-theta3[t])
                if t>99:
                    theta2[t+1]=theta2[t]+(theta2[t]-theta2[t-100])/100+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                    theta3[t+1]=theta3[t]+(theta3[t]-theta3[t-100])/100+K32*(theta2[t]-theta3[t])

            lastpredictionframe=currentframe

            
#             lastnote_frame=0
#             if NoteIndex>1:
#                 lastnote_frame=int(inputtimings[NoteIndex-1])
#             thisnote_frame=int(inputtimings[NoteIndex])
#             elapsedframes=thisnote_frame-lastnote_frame



#             inputvelocity[NoteIndex]=midi_data[0][2]


# #            log+='\n'+str(current_time)+" received Note #"+str(NoteIndex)+", frames since previous note: "+str(elapsedframes)+', theta1 is at '+str(inputoscillatorpositions[NoteIndex]/(2*np.pi))+'*2pi, velocity: '+str(inputvelocity[NoteIndex])
#             receivednotelog+=[current_time]
            

#             for t in range(lastnote_frame,thisnote_frame+1):
#                 if lastnote_frame==thisnote_frame:
#                     theta1[t]=inputoscillatorpositions[NoteIndex-1]
#                     print(str(current_time),"at input NoteIndex: ",NoteIndex," ERROR: lastnote_frame=thisnote_frame")
#                 else:
#                     theta1[t]=inputoscillatorpositions[NoteIndex-1]+(inputoscillatorpositions[NoteIndex]-inputoscillatorpositions[NoteIndex-1])*(t-lastnote_frame)/elapsedframes #linear interpolation
#                 if t<100:
#                     theta2[t+1]=theta2[t]+Omega2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
#                     theta3[t+1]=theta3[t]+Omega2+K32*(theta2[t]-theta3[t])
#                 if t>99:
#                     theta2[t+1]=theta2[t]+(theta2[t]-theta2[t-100])/100+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
#                     theta3[t+1]=theta3[t]+(theta3[t]-theta3[t-100])/100+K32*(theta2[t]-theta3[t])
            

            predictionbeats=1.01
            # we predict when the following output notes (up until predictionbeats later) will occur. i.e. extrapolate theta3 until that multiple of 2pi. Make sure there is no gap in the input longer than this number.
            theta3slope=(theta3[currentframe]-theta3[currentframe-1])/1
            
            currentbeat=inputoscillatorpositions[NoteIndex]
            predictionbound=currentbeat+2*np.pi*(predictionbeats)

            velocity_range=[]
            for i in range(max(newNotesAppeared),0,-1): #search for notes in the last beat, starting from now and going back
                if inputoscillatorpositions[i]<(currentbeat-2*np.pi):
                    break
                if inputvelocity[i]>0: #velocity 0 means the note was not received
                    velocity_range+=[inputvelocity[i]]
            current_desired_velocity=min(127,1.4*np.mean(velocity_range))
            

            #calculate events and put them in temporary array
            q_temp=[]

            for i in range(OutputNoteIndex, len(accompaniment_notes)):
                if outputoscillatorpositions[i]>predictionbound:
                    break
                if outputtimings[i]>(currentframe+reactiontime)/framerate or outputtimings[i]==0: #notes that haven't been outputted yet, we'll revise their predicted output time
                    for t in range(currentframe):
                        if theta3[t]>=accompaniment_scorepositions[i]:
                            outputtimings[i]=t/framerate
                            break
                    relativepredictedframe=(outputoscillatorpositions[i]-theta3[currentframe])/theta3slope
                    #log+='\n'+str(current_time)+" accompaniment Note #"+str(i+1)+" expected in "+str(relativepredictedframe)+" frames "
                    outputrelativeframe=max(reactiontime,relativepredictedframe)
                    outputtimings[i]=current_time+outputrelativeframe/framerate
                    if accompaniment_onoff[i]==144:
                        note=['note_on',accompaniment_notes[i],current_desired_velocity,outputtimings[i],'accompaniment',i,accompaniment_scorepositions[i]]
                    if not accompaniment_onoff[i]==144:
                        note=['note_off',accompaniment_notes[i],current_desired_velocity,outputtimings[i]-0.001,'accompaniment',accompaniment_scorepositions[i]]
                    q_temp+=[note]
                    #print('\n'+str(current_time)+": queue accompaniment note"+str(note))

#                        log+='\n'+str(current_time)+": queue accompaniment Note #"+str(i+1)+" in "+str(outputrelativeframe)+" frames, i.e. "+str(note)
#                    log+='\n'+str(current_time)+": calculated new events "+str(note)

            #now put the newly calculated events into the queue, replacing the old ones

            q_temp_offloaded=np.zeros(len(q_temp))
            for i in range(len(q_temp)):
                for j in range(len(q)):
                    note=q[j]
                    note_temp=q_temp[i]
                    if [note[0],note[5]]==[note_temp[0],note_temp[5]]:
                        if note[3]>current_time+reactiontime/framerate: #only replace if it's after reaction period. Theoretically this line is not necessary, since anything to be replaced has original outputtiming>current_time+reactiontime/framerate
#                            log+='\n'+str(current_time)+": replacing q["+str(j)+']='+str(q[j])+' by q_temp['+str(i)+']='+str(q_temp[i])
                            q[j]=q_temp[i]
                        else:
                            print(str(current_time),' tried to replace ',note,' by ' ,note_temp, ' before reactiontime runs out')
                        q_temp_offloaded[i]+=1
                if q_temp_offloaded[i]==0: #it's a prediction for a note never yet predicted
                    q+=[q_temp[i]]
                if q_temp_offloaded[i]>1:
                    print(str(current_time),"at input NoteIndex: ",NoteIndex," ERROR: duplicate ",str(q_temp[i]))






calculatingcycletimes=[]

threading.Thread(target=calculating).start()




def on_press(event):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        print('\n this is inputtimings:',inputtimings,'\n this is outputtimings:',outputtimings)

        # inputtimingerror=[]
        # for i in range(min(len(inputtiminglog),len(receivednotelog))):
        #     inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        # print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        outputtimingerror=[]
        for i in range(min(len(noteon_outputtiminglog),len(noteon_realoutputlog))):
            outputtimingerror+=[np.abs(noteon_outputtiminglog[i]-noteon_realoutputlog[i])]
        print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))
        
        inputlogfile=open("inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        inputtimingsfile=open("inputtimings.txt","w")
        inputtimingsfile.write(str(inputtimings))
        inputtimingsfile.close()
        outputtimingsfile=open("outputtimings.txt","w")
        outputtimingsfile.write(str(outputtimings))
        outputtimingsfile.close()
        outputtiminglogfile=open("outputtiminglog.txt","w")
        outputtiminglogfile.write(str(noteon_outputtiminglog))
        outputtiminglogfile.close()
        realoutputlogfile=open("realoutputlog.txt","w")
        realoutputlogfile.write(str(noteon_realoutputlog))
        realoutputlogfile.close()
        
        workerlogfile=open("workerlog.txt","w")
        workerlogfile.write(workerlog)
        workerlogfile.close()
        logfile=open("log.txt","w")
        logfile.write(log)
        logfile.close()
        #print('\n this is outputtimings:',outputtimings)
        #print('calculatingtiming:',calculatingtiminglog,'workertiming:',workertiminglog)
        #line1.set_ydata(theta1)
        #line2.set_ydata(theta3)
        fig.canvas.draw()

        noteon_accompaniment_scorepositions=[]
        for i in range(len(accompaniment_scorepositions)):
            if accompaniment_onoff[i]==144:
                noteon_accompaniment_scorepositions+=accompaniment_scorepositions

        plt.scatter(np.array(inputtimings[0:len(input_scorepositions)])*framerate,input_scorepositions,c='b',marker='^',s=25,alpha=0.5)
        #plt.scatter(np.array(receivednotelog)*framerate,input_scorepositions[0:len(receivednotelog)],c='b',marker='o',s=25,alpha=0.5)
        plt.scatter(np.array(noteon_outputtiminglog)*framerate,noteon_accompaniment_scorepositions[0:len(noteon_outputtiminglog)],c='g',marker='*',s=25,alpha=0.5)
        plt.scatter(np.array(noteon_realoutputlog)*framerate,noteon_accompaniment_scorepositions[0:len(noteon_realoutputlog)],c='y',marker='^',s=25,alpha=0.5)
        plt.scatter(np.arange(0,len(theta3)),theta3/(2*np.pi)-1,c='g',s=1)
        plt.scatter(np.arange(0,len(theta1)),theta1/(2*np.pi)-1,c='y',s=1)
        ##plt.scatter(subjectoutput,accompaniment_scorepositions,c='r',marker='s',s=25,alpha=0.5)
        plt.show()


x=range(len(theta3))
# y=np.sin(x)

fig, ax = plt.subplots()

fig.canvas.mpl_connect('key_press_event', on_press)

# line1,=ax.plot(x,y,color='blue')
# line2,=ax.plot(x,y,color='green')
# for i in range(20):
#     ax.plot(x,np.sin(x)*0.001+i*2*np.pi,color='black')
ax.set_title('Press a key')
ax.set_ylim([-1,200])
plt.show()
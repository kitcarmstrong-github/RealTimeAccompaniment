#Little Star
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
import os

from rtmidi.midiutil import open_midiinput

time_start=time.time()
log=''
inputmsglog=[]
inputtiminglog=[]
receivednotelog=[]
outputlog=''
outputtiminglog=[]
realoutputlog=[]
workerlog=''
workertiminglog=[]
calculatingtiminglog=[]
outputtimings=np.zeros(1000)

input_notes = [72,72,72,72,72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72, 72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72, 79, 79, 77, 77, 76, 76, 74, 74, 79, 79, 77, 77, 76, 76, 74, 74, 72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72]
OutputNoteIndex=1

input_scorepositions=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66]
#variation2
accompaniment_scorepositions=[
4.00,4.25,4.50,4.75,
5.00,5.25,5.50,5.75,
6.00,6.25,6.50,6.75,
7.00,7.25,7.50,7.75,
8.00,8.25,8.50,8.75,
9.00,9.25,9.50,9.75,
10.00,10.25,10.50,10.75,
11.00,11.25,11.50,11.75,
12.00,12.25,12.50,12.75,
13.00,13.25,13.50,13.75,
14.00,14.25,14.50,14.75,
15.00,15.25,15.50,15.75,
16.00,16.25,16.50,16.75,
17.00,17.25,17.50,17.75,
18.00,19.00,
20.00,20.25,20.50,20.75,
21.00,21.25,21.50,21.75,
22.00,22.25,22.50,22.75,
23.00,23.25,23.50,23.75,
24.00,24.25,24.50,24.75,
25.00,25.25,25.50,25.75,
26.00,26.25,26.50,26.75,
27.00,27.25,27.50,27.75,
28.00,28.25,28.50,28.75,
29.00,29.25,29.50,29.75,
30.00,30.25,30.50,30.75,
31.00,31.25,31.50,31.75,
32.00,32.25,32.50,32.75,
33.00,33.25,33.50,33.75,
34.00,35.00,
36.00,36.25,36.50,36.75,
37.00,37.25,37.50,37.75,
38.00,38.25,38.50,38.75,
39.00,39.25,39.50,39.75,
40.00,40.25,40.50,40.75,
41.00,41.25,41.50,41.75,
42.00,42.25,42.50,42.75,
43.00,43.25,43.50,43.75,
44.00,44.25,44.50,44.75,
45.00,45.25,45.50,45.75,
46.00,46.25,46.50,46.75,
47.00,47.25,47.50,47.75,
48.00,48.25,48.50,48.75,
49.00,49.25,49.50,49.75,
50.00,50.25,50.50,50.75,
51.00,51.25,51.50,51.75,
52.00,52.25,52.50,52.75,
53.00,53.25,53.50,53.75,
54.00,54.25,54.50,54.75,
55.00,55.25,55.50,55.75,
56.00,56.25,56.50,56.75,
57.00,57.25,57.50,57.75,
58.00,58.25,58.50,58.75,
59.00,59.25,59.50,59.75,
60.00,60.25,60.50,60.75,
61.00,61.25,61.50,61.75,
62.00,62.25,62.50,62.75,
63.00,63.25,63.50,63.75,
64.00,64.25,64.50,64.75,
65.00,65.25,65.50,65.75,
66.00,67.00
]
accompaniment_notes=[
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    50, 62, 61, 62, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    48, 60, 
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    50, 62, 61, 62, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    48, 60, 
    55, 64, 63, 64, 65, 64, 63, 64, 
    55, 62, 61, 62, 64, 62, 61, 62,
    55, 67, 66, 67, 69, 67, 66, 67, 
    55, 65, 64, 65, 67, 65, 64, 65, 
    55, 64, 63, 64, 65, 64, 63, 64, 
    55, 62, 61, 62, 64, 62, 61, 62, 
    55, 60, 59, 60, 62, 60, 59, 60, 
    55, 59, 58, 59, 60, 59, 58, 59, 
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    45, 57, 56, 57, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    48, 36]

accompaniment_notes=[
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    48, 60, 59, 60, 62, 60, 59, 60, 
    45, 57, 56, 57, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    60, 48, 
    
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    48, 60, 59, 60, 62, 60, 59, 60, 
    45, 57, 56, 57, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    60, 48,
    
    55, 64, 63, 64, 65, 64, 63, 64, 
    55, 62, 61, 62, 64, 62, 61, 62, 
    55, 67, 66, 67, 69, 67, 66, 67, 
    55, 65, 64, 65, 67, 65, 64, 65, 
    55, 64, 63, 64, 65, 64, 63, 64, 
    55, 62, 61, 62, 64, 62, 61, 62, 
    55, 60, 59, 60, 62, 60, 59, 60, 
    55, 59, 58, 59, 60, 59, 58, 59, 
    48, 60, 59, 60, 62, 60, 59, 60, 
    52, 60, 59, 60, 62, 60, 59, 60, 
    53, 60, 59, 60, 62, 60, 59, 60, 
    48, 60, 59, 60, 49, 61, 59, 61, 
    50, 62, 61, 62, 47, 59, 58, 59, 
    48, 60, 59, 60, 45, 57, 56, 57, 
    41, 53, 52, 53, 43, 55, 54, 55, 
    60, 48]

#theme, if you need remove#
accompaniment_scorepositions=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66]
accompaniment_notes=[48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 60, 48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 60, 64, 55, 62, 55, 60, 55, 59, 55, 64, 55, 62, 55, 60, 55, 59, 55, 48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 48]


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
         inputqueue.put(msg)
         current_time = time.time() - time_start
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
    global log,workerlog,workertiminglog,outputlog,outputtiminglog,realoutputlog
    while True:
        time_stamp = time.time()            # Get current time.
        current_time = time_stamp - time_start
        for i in range(len(q)):               # If there is data in queue.
            #workerlog+='\n'+str(current_time)+' queue has '+str(len(q))+'elements, looking at #'+str(i)
            try:
                note = q[i]
    #            workerlog+='\n'+str(current_time)+' processing element #'+str(i)+'= '+str(note)+' OutputNoteIndex is '+str(OutputNoteIndex)
                if (note[3] <= (current_time)):       # Check the time stamp
                                                            # of the data.
                    q.pop(i)
                    #workerlog+='\n'+str(current_time)+' popped from queue element #'+str(i)
                    if (note[0] == 'note_on'):
                        if note[5]>=OutputNoteIndex-1: #don't play a note already played since note[5] starts at 0 and OutputNoteIndex starts at 1
                            NoteOn(note)
                            if note[5]>OutputNoteIndex-1:
                                print(str(current_time)," ERROR: OutputNoteIndex=",OutputNoteIndex," already arrived at ", str(note))
                            OutputNoteIndex=note[5]+2
    #                        log+='\n'+str(current_time)+' output from queue'+str(note)
    #                        workerlog+='\n'+str(current_time)+' worker outputs'+str(note)
                            outputlog+='\n'+str(current_time)+str(note)
                            outputtiminglog+=[note[3]]
                            realoutputlog+=[current_time]
                            break

                    elif (note[0] == 'note_off'):
                        if True: #note[5]==OutputNoteIndex-3:
                            NoteOff(note)
                            outputlog+='\n'+str(current_time)+str(note)

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
    global theta1,theta2,theta3
    global q
    global log,receivednotelog,calculatingtiminglog
    global outputtimings
    print('\n calculating starts ')
    
    reactiontime=10 #in frames

    Omega2=0.002
    Omega3=0.002
    theta2[0]=0
    theta2[1]=Omega2
    theta3[0]=0
    theta3[1]=Omega2

    K21=0.1
    K23=0.1
    K32=0.1

    reactiontime=4.711 #in frames
    K21=0.1000
    K23=0.0999
    K32=0.1000

    inputtimings=np.zeros(1000)
    inputoscillatorpositions=np.zeros(1000)
    velocity=np.zeros(1000)
    
    for NoteIndex in range(1,len(input_scorepositions)+1):
        #understand where we are in the score, based on the input
        inputscoreposition=input_scorepositions[NoteIndex-1] #NoteIndex starts at 1, scorepositions start at 0
        #corresponding oscillator (theta1) position
        inputoscillatorpositions[NoteIndex]=2*np.pi*(inputscoreposition+1) #first note is at 2 pi
    NoteIndex=1

    
    while True:
        #print('calculating thread is still alive',time.time())
        if not inputqueue.empty():
            midi_data=inputqueue.get()
            time_stamp = time.time()            # Get current time
            current_time = time_stamp - time_start

    #        log+='\n'+str(current_time)+" calculating thread received MIDI signal "+str(midi_data)

            ######### Main process###########
            # After getting the input data, empty the queue, then calculate the new responses
            # and put them into queue.

            if midi_data[0][2]>0 and midi_data[0][0]>143 and (midi_data[0][1]==input_notes[NoteIndex-1] or midi_data[0][1]==input_notes[NoteIndex]): #i.e. it's a note-on event
                inputtimings[NoteIndex]=current_time*framerate
                
                lastnote_frame=0
                if NoteIndex>1:
                    lastnote_frame=int(inputtimings[NoteIndex-1])
                thisnote_frame=int(inputtimings[NoteIndex])
                elapsedframes=thisnote_frame-lastnote_frame

                velocity[NoteIndex]=midi_data[0][2]


    #            log+='\n'+str(current_time)+" received Note #"+str(NoteIndex)+", frames since previous note: "+str(elapsedframes)+', theta1 is at '+str(inputoscillatorpositions[NoteIndex]/(2*np.pi))+'*2pi, velocity: '+str(velocity[NoteIndex])
                receivednotelog+=[current_time]
                

                for t in range(lastnote_frame,thisnote_frame+1):
                    if lastnote_frame==thisnote_frame:
                        theta1[t]=inputoscillatorpositions[NoteIndex-1]
                        print(str(current_time),"at input NoteIndex: ",NoteIndex," ERROR: lastnote_frame=thisnote_frame")
                    else:
                        theta1[t]=inputoscillatorpositions[NoteIndex-1]+(inputoscillatorpositions[NoteIndex]-inputoscillatorpositions[NoteIndex-1])*(t-lastnote_frame)/elapsedframes #linear interpolation
                    if t<100:
                        theta2[t+1]=theta2[t]+Omega2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                        theta3[t+1]=theta3[t]+Omega2+K32*(theta2[t]-theta3[t])
                    if t>99:
                        theta2[t+1]=theta2[t]+(theta2[t]-theta2[t-100])/100+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                        theta3[t+1]=theta3[t]+(theta3[t]-theta3[t-100])/100+K32*(theta2[t]-theta3[t])
                

                predictionbeats=1.01
                # we predict when the following output notes (up until predictionbeats later) will occur. i.e. extrapolate theta3 until that multiple of 2pi. Make sure there is no gap in the input longer than this number.
                theta3slope=(theta3[thisnote_frame]-theta3[thisnote_frame-1])/1
                
                currentbeat=inputoscillatorpositions[NoteIndex]
                predictionbound=currentbeat+2*np.pi*(predictionbeats)

                velocity_range=[]
                for i in range(0,len(inputoscillatorpositions)):
                    if inputoscillatorpositions[i]>=currentbeat-2*np.pi and inputoscillatorpositions[i]<=currentbeat and velocity[i]>0:
                        velocity_range+=[velocity[i]]
                current_desired_velocity=max(10,0.9*np.mean(velocity_range)-10)
                

                #calculate events and put them in temporary array
                q_temp=[]

                for i in range(0,len(accompaniment_notes)):
                    theta3target=(accompaniment_scorepositions[i]+1)*2*np.pi
                    if theta3target>=currentbeat and theta3target<=predictionbound:
                        relativepredictedframe=(theta3target-theta3[thisnote_frame])/theta3slope
                        #log+='\n'+str(current_time)+" accompaniment Note #"+str(i+1)+" expected in "+str(relativepredictedframe)+" frames "
                        outputrelativeframe=max(reactiontime,relativepredictedframe)
                        outputtimings[i]=current_time+outputrelativeframe/framerate
                        #  if i>0:
                        #     outputtimings[i]=max(current_time+outputrelativeframe/framerate,outputtimings[i-1]+0.001)
                        note=['note_on',accompaniment_notes[i],current_desired_velocity,outputtimings[i],'accompaniment',i]
                        q_temp+=[note]
                        if i>0 and not accompaniment_notes[i]==accompaniment_notes[i-1]:
                            q_temp+=[['note_off',accompaniment_notes[i-1],100,outputtimings[i]+0.001,'accompaniment',i-1]]
#                        log+='\n'+str(current_time)+": queue accompaniment Note #"+str(i+1)+" in "+str(outputrelativeframe)+" frames, i.e. "+str(note)
    #                    log+='\n'+str(current_time)+": calculated new events "+str(note)


                #now put the newly calculated events into the queue, replacing the old ones

                q_temp_offloaded=np.zeros(len(q_temp))
                for i in range(len(q_temp)):
                    for j in range(len(q)):
                        try:
                            note=q[j]
                            note_temp=q_temp[i]
                            if [note[0],note[5]]==[note_temp[0],note_temp[5]]:
                                if note[3]>current_time+reactiontime/framerate: #only replace if it's after reaction period
        #                            log+='\n'+str(current_time)+": replacing q["+str(j)+']='+str(q[j])+' by q_temp['+str(i)+']='+str(q_temp[i])
                                    q[j]=q_temp[i]
                                q_temp_offloaded[i]+=1
                        except:
                            pass
                    if q_temp_offloaded[i]==0:
                        q+=[q_temp[i]]
                    if q_temp_offloaded[i]>1:
                        print(str(current_time),"at input NoteIndex: ",NoteIndex," ERROR: duplicate ",str(q_temp[i]))
                
    #            log+='\n'+str(current_time)+": current q= "+str(q)
                
    #             for i in reversed(range(len(q))): # we want to start popping off the latest elements of the queue
    #                 log+='\n'+str(current_time)+' trying to pop '+str(i)
    #                 log+=str(q[i])
    # #                try:
    #                 note = q[i]
    #                 if note[3]>current_time+reactiontime/framerate:
    #                     q.pop(i)
    #                     log+=' POP SUCCESS'
    #                 # except:
    #                 #     log+=' CANT FIND IT'
    #                 #     pass

    #             if len(q)==0:
    #                 log+='\n'+str(current_time)+' queue is empty'                    

                

                
                NoteIndex=NoteIndex+1
        #calculatingtiminglog+=current_time





threading.Thread(target=calculating).start()


def on_press(event):
    print('press', event.key)
    sys.stdout.flush()
    if event.key == 'x':
        print('\n this is input log:',inputmsglog,'\n this is receivednotelog:',receivednotelog,'\n this is outputlog:',outputlog)

        inputtimingerror=[]
        for i in range(min(len(inputtiminglog),len(receivednotelog))):
            inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        outputtimingerror=[]
        for i in range(min(len(outputtiminglog),len(realoutputlog))):
            outputtimingerror+=[np.abs(outputtiminglog[i]-realoutputlog[i])]
        print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))
        
        logdirectory="logs/sec2_real_accomp_star_"+str(time.time())
        os.makedirs(logdirectory)

        inputlogfile=open(logdirectory+"/inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        receivednotelogfile=open(logdirectory+"/receivednotelog.txt","w")
        receivednotelogfile.write(str(receivednotelog))
        receivednotelogfile.close()
        outputtiminglogfile=open(logdirectory+"/outputtiminglog.txt","w")
        outputtiminglogfile.write(str(outputtiminglog))
        outputtiminglogfile.close()
        outputlogfile=open(logdirectory+"/outputlog.txt","w")
        outputlogfile.write(str(outputlog))
        outputlogfile.close()
        realoutputlogfile=open(logdirectory+"/realoutputlog.txt","w")
        realoutputlogfile.write(str(realoutputlog))
        realoutputlogfile.close()

        workerlogfile=open(logdirectory+"/workerlog.txt","w")
        workerlogfile.write(workerlog)
        workerlogfile.close()
        logfile=open(logdirectory+"/log.txt","w")
        logfile.write(log)
        logfile.close()
        #print('\n this is outputtimings:',outputtimings)
        #print('calculatingtiming:',calculatingtiminglog,'workertiming:',workertiminglog)
        #line1.set_ydata(theta1)
        #line2.set_ydata(theta3)
        fig.canvas.draw()

        plt.scatter(np.array(inputtiminglog)*framerate,input_scorepositions[0:len(inputtiminglog)],c='b',marker='^',s=25,alpha=0.5)
        plt.scatter(np.array(receivednotelog)*framerate,input_scorepositions[0:len(receivednotelog)],c='b',marker='o',s=25,alpha=0.5)
        plt.scatter(np.array(outputtiminglog)*framerate,accompaniment_scorepositions[0:len(outputtiminglog)],c='g',marker='*',s=25,alpha=0.5)
        plt.scatter(np.array(realoutputlog)*framerate,accompaniment_scorepositions[0:len(realoutputlog)],c='y',marker='^',s=25,alpha=0.5)
        plt.scatter(np.arange(0,len(theta3)),theta3/(2*np.pi)-1,c='g',s=1)
#        plt.scatter(np.arange(0,len(theta1)),theta1/(2*np.pi)-1,c='y',s=1)
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
#put''
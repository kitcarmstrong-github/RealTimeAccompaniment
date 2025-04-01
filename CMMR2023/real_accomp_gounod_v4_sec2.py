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
outputtiminglog=[]
realoutputlog=[]
workerlog=''
workertiminglog=[]
calculatingtiminglog=[]
outputtimings=np.zeros(1000)
input_notes=[60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 62, 69, 74, 77, 69, 74, 77, 60, 62, 69, 74, 77, 69, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 62, 69, 74, 77, 69, 74, 77, 60, 62, 69, 74, 77, 69, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 69, 76, 81, 69, 76, 81, 60, 64, 69, 76, 81, 69, 76, 81, 60, 62, 66, 69, 74, 66, 69, 74, 60, 62, 66, 69, 74, 66, 69, 74, 59, 62, 67, 74, 79, 67, 74, 79, 59, 62, 67, 74, 79, 67, 74, 79, 59, 60, 64, 67, 72, 64, 67, 72, 59, 60, 64, 67, 72, 64, 67, 72,
57, 60, 64, 67, 72, 64, 67, 72, 57, 60, 64, 67, 72, 64, 67, 72, 50, 57, 62, 66, 72, 62, 66, 72, 50, 57, 62, 66, 72, 62, 66, 72, 55, 59, 62, 67, 71, 62, 67, 71, 55, 59, 62, 67, 71, 62, 67, 71, 55, 58, 64, 67, 73, 64, 67, 73, 55, 58, 64, 67, 73, 64, 67, 73, 53, 57, 62, 69, 74, 62, 69, 74, 53, 57, 62, 69, 74, 62, 69, 74, 53, 56, 62, 65, 71, 62, 65, 71, 53, 56, 62, 65, 71, 62, 65, 71, 52, 55, 60, 67, 72, 60, 67, 72, 52, 55, 60, 67, 72, 60, 67, 72, 52, 53, 57, 60, 65, 57, 60, 65, 52, 53, 57, 60, 65, 57, 60, 65, 50, 53, 57, 60, 65, 57, 60, 65, 50, 53, 57, 60, 65, 57, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 48, 52, 55, 60, 64, 55, 60, 64, 48, 52, 55, 60, 64, 55, 60, 64, 48, 55, 58, 60, 64, 58, 60, 64, 48, 55, 58, 60, 64, 58, 60, 64,
41, 53, 57, 60, 64, 57, 60, 64, 41, 53, 57, 60, 64, 57, 60, 64, 42, 48, 57, 60, 63, 57, 60, 63, 42, 48, 57, 60, 63, 57, 60, 63, 43, 51, 59, 60, 63, 59, 60, 63, 43, 51, 59, 60, 63, 59, 60, 63, 44, 53, 59, 60, 62, 59, 60, 62, 44, 53, 59, 60, 62, 59, 60, 62, 43, 53, 55, 59, 62, 55, 59, 62, 43, 53, 55, 59, 62, 55, 59, 62, 43, 52, 55, 60, 64, 55, 60, 64, 43, 52, 55, 60, 64, 55, 60, 64, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 51, 57, 60, 66, 57, 60, 66, 43, 51, 57, 60, 66, 57, 60, 66,
43, 52, 55, 60, 67, 55, 60, 67, 43, 52, 55, 60, 67, 55, 60, 67, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 36, 48, 55, 58, 64, 55, 58, 64, 36, 48, 55, 58, 64, 55, 58, 64, 36, 48, 53, 57, 60, 65, 60, 57, 60, 57, 53, 57, 53, 50, 53, 50, 36, 47, 67, 71, 74, 77, 74, 71, 74, 71, 67, 71, 62, 65, 64, 62, 60]

OutputNoteIndex=1

input_scorepositions=np.arange(0,200,0.25)
accompaniment_scorepositions=[16,20,23.5,24,27,28,  32,34.5,35,35.5,36,37.5,38,  40,42.5,43,43.5,44,45.5,46,  48,50.5,51,51.5,52,53.5,54,55,56,   59,60,62.5,63,63.5,64,65.75,66,   68,70.5,71,71.5,72,73.75,74,   76,78.5,79,79.5,80,82.5,83,83.5,84,85.5,86,87,88,   91.5,92,94,95.75,96,98,  99.75,100,102,  103.75,104,106,  107.75,108,110,    112,114.5,115,115.5,116,117.75,118,   120,122.5,123,123.5,124,125.75,126,    128,130.5,131,131.5,132,134.5,135,135.5,136,138.5,139,139.5,140,140.5,141,141.5,142,142.5,143,143.5,144]
accompaniment_notes= [88, 89, 89, 91, 86, 88, 93, 81, 83, 84, 86, 88, 86, 91, 79, 81, 83, 84, 86, 84, 96, 84, 86, 88, 90, 88, 86, 81, 83, 86, 88, 88, 89, 91, 93, 81, 81, 86, 86, 88, 89, 91, 79, 79, 84, 84, 86, 88, 89, 89, 91, 93, 95, 93, 91, 86, 88, 88, 91, 88, 88, 93, 81, 93, 93, 84, 93, 96, 87, 96, 96, 86, 86, 86, 84, 83, 91, 88, 84, 89, 89, 88, 86, 98, 95, 91, 93, 93, 95, 96, 100, 96, 91, 88, 86, 93, 95, 93, 91, 98, 95, 91, 89, 86, 83, 79, 84]


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
    #                        outputlog+='\n'+str(current_time)+str(note)
                            outputtiminglog+=[note[3]]
                            realoutputlog+=[current_time]
                            break

                    elif (note[0] == 'note_off'):
                        if True: #note[5]==OutputNoteIndex-3:
                            NoteOff(note)
    #                        outputlog+='\n'+str(current_time)+str(note)

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

    K21=0.05
    K23=0.05
    K32=0.05

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
            # and put them into queue. [0][2] is velocity, [0][1] is note number, [0][0] noteon off
            if midi_data[0][2]>10 and midi_data[0][0]>143 and (midi_data[0][1]==input_notes[NoteIndex-1] or midi_data[0][1]==input_notes[NoteIndex]): #i.e. it's a note-on event
                if midi_data[0][1]==input_notes[NoteIndex] and not midi_data[0][1]==input_notes[NoteIndex-1]:
                    inputtimings[NoteIndex]=inputtimings[NoteIndex-1]
                    NoteIndex+=1

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
                

                predictionbeats=2.01
                # we predict when the following output notes (up until predictionbeats later) will occur. i.e. extrapolate theta3 until that multiple of 2pi. Make sure there is no gap in the input longer than this number.
                theta3slope=(theta3[thisnote_frame]-theta3[thisnote_frame-1])/1
                
                currentbeat=inputoscillatorpositions[NoteIndex]
                predictionbound=currentbeat+2*np.pi*(predictionbeats)

                velocity_range=[]
                for i in range(0,len(inputoscillatorpositions)):
                    if inputoscillatorpositions[i]>=currentbeat-2*np.pi and inputoscillatorpositions[i]<=currentbeat and velocity[i]>0:
                        velocity_range+=[velocity[i]]
                current_desired_velocity=min(127,20+1.2*np.mean(velocity_range))
                

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
                        note=q[j]
                        note_temp=q_temp[i]
                        if [note[0],note[5]]==[note_temp[0],note_temp[5]]:
                            if note[3]>current_time+reactiontime/framerate: #only replace if it's after reaction period
    #                            log+='\n'+str(current_time)+": replacing q["+str(j)+']='+str(q[j])+' by q_temp['+str(i)+']='+str(q_temp[i])
                                q[j]=q_temp[i]
                            q_temp_offloaded[i]+=1
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
        
        inputlogfile=open("inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        receivednotelogfile=open("receivednotelog.txt","w")
        receivednotelogfile.write(str(receivednotelog))
        receivednotelogfile.close()
        outputtiminglogfile=open("outputtiminglog.txt","w")
        outputtiminglogfile.write(str(outputtiminglog))
        outputtiminglogfile.close()
        realoutputlogfile=open("realoutputlog.txt","w")
        realoutputlogfile.write(str(realoutputlog))
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
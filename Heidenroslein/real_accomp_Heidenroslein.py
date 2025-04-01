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

OutputNoteIndex=1

input_notes =  [71, 71, 71, 71, 71, 71, 71, 71, 74, 72, 72, 71, 69, 69, 69, 71, 72, 74, 79, 71, 71, 71, 71, 74, 73, 73, 71, 69, 74, 74, 76, 74, 73, 74, 76, 78, 74, 74, 78, 76, 74, 73, 71, 70, 71, 79, 73, 74, 69, 69, 71, 72, 74, 76, 78, 79, 76, 79, 72, 76, 67, 71, 69, 67]
input_scorepositions =  [0.0, 1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0, 8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 12.5, 13.0, 13.5, 14.0, 14.25, 14.5, 14.75, 15.0, 16.0, 16.5, 17.0, 17.75, 18.0, 18.25, 18.5, 18.75, 19.0, 20.0, 20.25, 20.5, 20.75, 21.0, 21.25, 21.5, 21.75, 22.0, 22.75, 23.0, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 26.75, 27.0, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 30.75, 31.0]     

accompaniment_notes =  [55, 62, 67, 71, 55, 62, 67, 71, 55, 64, 69, 72, 55, 64, 69, 72, 54, 62, 69, 72, 48, 62, 66, 69, 47, 62, 67, 74, 43, 62, 67, 71, 55, 62, 67, 71, 55, 62, 67, 71, 55, 64, 69, 73, 55, 64, 69, 73, 54, 69, 74, 55, 71, 76, 57, 67, 73, 59, 66, 74, 54, 69, 74, 55, 71, 76, 57, 67, 73, 50, 66, 74, 50, 66, 69, 48, 62, 66, 69, 47, 62, 67, 74, 43, 62, 67, 71, 48, 64, 67, 72, 52, 60, 67, 72, 50, 62, 67, 71, 60, 66, 69, 55, 59, 67]
accompaniment_scorepositions =  [4.0, 4.5, 4.5, 4.5, 5.0, 5.5, 5.5, 5.5, 6.0, 6.5, 6.5, 6.5, 7.0, 7.5, 7.5, 7.5, 8.0, 8.5, 8.5, 8.5, 9.0, 9.5, 9.5, 9.5, 10.0, 10.5, 10.5, 10.5, 11.0, 11.5, 11.5, 11.5, 12.0, 12.5, 12.5, 12.5, 13.0, 13.5, 13.5, 13.5, 14.0, 14.5, 14.5, 14.5, 15.0, 15.5, 15.5, 15.5, 16.0, 16.5, 16.5, 17.0, 17.5, 17.5, 18.0, 18.5, 18.5, 19.0, 19.5, 19.5, 20.0, 20.5, 20.5, 21.0, 21.5, 21.5, 22.0, 22.5, 22.5, 23.0, 23.5, 23.5, 24.0, 24.5, 24.5, 25.0, 25.5, 25.5, 25.5, 26.0, 26.5, 26.5, 26.5, 27.0, 27.5, 27.5, 27.5, 28.0, 28.5, 28.5, 28.5, 29.0, 29.5, 29.5, 29.5, 30.0, 30.0, 30.0, 30.0, 30.5, 30.5, 30.5, 31.0, 31.0, 31.0]

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
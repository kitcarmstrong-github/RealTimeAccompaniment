from __future__ import print_function
import threading
import queue
import numpy as np
import time
import datetime
#nimport keyboard
import logging
import sys
import time
import rtmidi
import csv

from rtmidi.midiutil import open_midiinput

from pynput import keyboard


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


OutputNoteIndex=0

def noteonoff_to_noteon(onoff,notes,scorepositions):
    noteon_notes=[]
    noteon_scorepositions=[]
    for i in range(len(onoff)):
        if onoff[i]==144:
            noteon_notes+=[notes[i]]
            noteon_scorepositions+=[scorepositions[i]]
    return [noteon_notes,noteon_scorepositions]



#accompaniment_onoff=[144, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 144, 128, 128, 144, 144, 128, 128, 144, 144, 128, 144, 128, 128, 144, 128, 144, 144, 128, 144, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 128, 144, 144, 128, 128, 144, 144, 128, 144, 128, 144, 128, 144, 128, 128]
#accompaniment_notes=[48, 60, 48, 64, 60, 60, 64, 65, 60, 60, 65, 64, 60, 60, 64, 62, 60, 59, 62, 60, 59, 57, 60, 53, 57, 55, 53, 48, 55, 64, 48, 55, 64, 62, 55, 55, 62, 55, 60, 55, 60, 55, 59, 55, 59, 55, 64, 55, 64, 55, 62, 55, 62, 60, 55, 60, 60, 60, 62, 60, 62, 55, 59, 60, 48, 59, 55, 60, 48, 64, 60, 60, 64, 65, 60, 60, 65, 64, 60, 60, 64, 60, 62, 59, 62, 59, 60, 57, 60, 53, 57, 55, 53, 48, 55, 48]
#accompaniment_scorepositions=[3.0, 4.0, 4.0, 5.0, 5.0, 6.0, 6.0, 7.0, 7.0, 8.0, 8.0, 9.0, 9.0, 10.0, 10.0, 11.0, 11.0, 12.0, 12.0, 13.0, 13.0, 14.0, 14.0, 15.0, 15.0, 16.0, 16.0, 17.0, 17.0, 19.0, 19.0, 20.0, 20.0, 21.0, 21.0, 22.0, 22.0, 23.0, 23.0, 24.0, 24.0, 25.0, 25.0, 26.0, 26.0, 27.0, 27.0, 28.0, 28.0, 29.0, 29.0, 30.0, 30.0, 31.0, 31.0, 31.75, 32.0, 32.75, 32.75, 33.0, 33.0, 33.0, 34.0, 34.0, 35.0, 35.0, 35.0, 36.0, 36.0, 37.0, 37.0, 38.0, 38.0, 39.0, 39.0, 40.0, 40.0, 41.0, 41.0, 42.0, 42.0, 43.0, 43.0, 44.0, 44.0, 45.0, 45.0, 46.0, 46.0, 47.0, 47.0, 48.0, 48.0, 49.0, 49.0, 51.0]

# input_onoff=[144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 144, 128, 144, 128, 144, 128, 144, 128, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128, 144, 128]
# input_notes=[72, 72, 72, 72, 79, 79, 79, 79, 81, 81, 81, 81, 79, 79, 79, 79, 77, 77, 77, 77, 76, 76, 76, 76, 74, 74, 74, 76, 74, 72, 76, 79, 72, 79, 79, 79, 77, 77, 77, 77, 76, 76, 76, 76, 74, 74, 74, 74, 79, 79, 79, 79, 77, 77, 77, 77, 76, 76, 76, 77, 76, 76, 77, 74, 76, 72, 74, 72, 72, 72, 79, 79, 79, 79, 81, 81, 81, 81, 79, 79, 79, 79, 77, 77, 77, 77, 76, 76, 76, 76, 74, 74, 74, 74, 76, 76, 72, 72]
# input_scorepositions=[3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.75, 16.75, 17.0, 17.0, 19.0, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5, 32.0, 32.75, 32.75, 33.0, 33.0, 34.0, 34.0, 35.0, 35.0, 35.5, 36.0, 36.5, 37.0, 37.5, 38.0, 38.5, 39.0, 39.5, 40.0, 40.5, 41.0, 41.5, 42.0, 42.5, 43.0, 43.5, 44.0, 44.5, 45.0, 45.5, 46.0, 46.5, 47.0, 47.5, 48.0, 48.75, 48.75, 49.0, 49.0, 51.0]
# input_scorepositions=[x+1 for x in input_scorepositions]

# [input_notes,input_scorepositions]=noteonoff_to_noteon(input_onoff,input_notes,input_scorepositions)

# print(input_notes)
# print(input_scorepositions)

#input_notes don't need it
input_scorepositions=[]
phrase1=[0,1,2,3,4,5,6,7]
phrase2=[0,1,2,3,4,5,5.75,6]
phrase3=phrase1
phrase4=phrase2+[7]
input_scorepositions=phrase1+[x+8 for x in phrase2]+[x+16 for x in phrase1]+[x+24 for x in phrase2]+[x+32 for x in phrase3]+[x+40 for x in phrase4]+[x+48 for x in phrase1]+[x+56 for x in phrase2]
input_scorepositions=[x+4 for x in input_scorepositions]

print(input_scorepositions)


midiout = rtmidi.MidiOut()
print(midiout.get_ports())
midiout.open_port(0)

port = sys.argv[1] if len(sys.argv) > 1 else None
midiin, port_name = open_midiinput(port)

inputqueue = queue.Queue()

def inputreading():
    global running
    global inputmsglog,inputtiminglog
    print('\n inputreading starts ')
    while running==1:
     #print('inputreading alive')
     msg = midiin.get_message()
     if msg:
         current_time = time.time() - time_start
         inputqueue.put([[msg[0][0],msg[0][1],msg[0][2]],current_time])
         inputmsglog+=[['Input',msg[0][0],msg[0][1],msg[0][2],current_time]]
         if msg[0][2]>0 and msg[0][0]>143:
             inputtiminglog+=[current_time]
         print('\n inputreading writes:'+str(msg))
    print('\n inputreading ends ')



q = []

def NoteOn(note):
    midiout.send_message([0x90,note[1],note[2]])

def NoteOff(note):
    midiout.send_message([0x80,note[1],note[2]])

def worker():
    print('\n worker starts ')
    global running
    global q
    global OutputNoteIndex
    global log,workerlog,workertiminglog,outputlog,outputtiminglog,realoutputlog
    while running==1:
        #print('worker alive'+str(q))
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
                        print(note)#,'outputnoteindex', OutputNoteIndex)
                        if note[5]>=OutputNoteIndex-1: #don't play a note already played since note[5] starts at 0 and OutputNoteIndex starts at 1
                            NoteOn(note)
                            print('\n'+str(current_time)+str(note))
                            #if note[5]>OutputNoteIndex-1:
                             #   print(str(current_time)," ERROR: OutputNoteIndex=",OutputNoteIndex," already arrived at ", str(note))
                            OutputNoteIndex=note[5]+2
    #                        log+='\n'+str(current_time)+' output from queue'+str(note)
    #                        workerlog+='\n'+str(current_time)+' worker outputs'+str(note)
                            outputlog+='\n'+str(current_time)+str(note)
#                            outputtiminglog+=[note[3]]
#                            realoutputlog+=[current_time]
                            break

                    elif (note[0] == 'note_off'):
                        if True: #note[5]==OutputNoteIndex-3:
                            NoteOff(note)
                            outputlog+='\n'+str(current_time)+str(note)


            except:
                pass
        #workertiminglog+=[current_time]
    print('\n worker ends ')

# Turn-on the worker thread.
running=1

threading.Thread(target=worker, daemon=True).start()

threading.Thread(target=inputreading).start()


# test output
##for i in range(5):
##    q.put(['note_on',i+40,100,i,'test',i])


framerate=100
theta1=np.zeros(200*framerate)
theta2=np.zeros(200*framerate)
theta3=np.zeros(200*framerate)




#threading.Thread(target=calculating).start()  #don't need to calculate anything. Just define q to be the MIDI recording for playback.


# now "input" is considered to be the pre-recording. "output" is what the human plays.


q = []
noteRead = []
timeStampRead = []
durationRead = []
velocityRead = []
accompanimentSelect = 'Little Star LH 1.csv'

with open(accompanimentSelect, newline='') as csvfile:
  rows = csv.reader(csvfile)
  for row in rows:
    noteRead.append(int(row[0]))

with open(accompanimentSelect, newline='') as csvfile:
  rows = csv.reader(csvfile)
  for row in rows:
    timeStampRead.append(float(row[1])/2)

with open(accompanimentSelect, newline='') as csvfile:
  rows = csv.reader(csvfile)
  for row in rows:
    durationRead.append(float(row[2])/2)

with open(accompanimentSelect, newline='') as csvfile:
  rows = csv.reader(csvfile)
  for row in rows:
    velocityRead.append(int(row[3]))

#accompaniment_onoff=[]
accompaniment_notes=[]

#note: these arrays have only noteon events
accompaniment_scorepositions=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,    16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,    32,33,34,35,36,37,38,39,  40,41,42,43,44,45,45.75,46,46,47,    48,49,50,51,52,53,54,55,56,57,58,59,60,61,62]
accompaniment_scorepositions=[x+4 for x in accompaniment_scorepositions]
accompaniment_scorepositions=[0,1,2,3]+accompaniment_scorepositions

for i in range(len(noteRead)):
    q+=[['note_on', noteRead[i], velocityRead[i], 5+timeStampRead[i],                 'accompaniment', i]]
    accompaniment_notes+=[noteRead[i]]
    q+=[['note_off',noteRead[i], velocityRead[i], 5+timeStampRead[i]+durationRead[i], 'accompaniment', i]]
inputtimings = [x+5 for x in timeStampRead]



# inputtimings=[]
# for i in range(len(accompaniment_scorepositions)):
#     inputtimings+=[accompaniment_scorepositions[i]*0.5+4]

# q=[]
# for i in range(len(accompaniment_scorepositions)):
#     if accompaniment_onoff[i]==144:
#         on_or_off='note_on'
#     if accompaniment_onoff[i]==128:
#         on_or_off='note_off'
#     q+=[[on_or_off,accompaniment_notes[i],100,inputtimings[i],'accompaniment',i]]

#now we get rid of the note_off events, since for the simulation we only need the onsets
# inputonsettimings=[]
# for i in range(len(accompaniment_scorepositions)):
#     if accompaniment_onoff[i]==144:
#         inputonsettimings+=[inputtimings[i]]
# inputtimings=inputonsettimings


simulatelog=''

def simulate(K21,K23,K32,reactiontime):
    global simulatelog
#    print('simulating with K21,K23,K32,reactiontime=', K21,K23,K32,reactiontime, ', inputtimings',inputtimings, ', subjectoutput' , subjectoutput)
    output = []

    framerate=1000
    theta1=np.zeros(200*framerate)
    theta2=np.zeros(200*framerate)
    theta3=np.zeros(200*framerate)




    Omega2=0.002
    Omega3=0.002
    theta2[0]=0
    theta2[1]=Omega2
    theta3[0]=0
    theta3[1]=Omega2



    NoteIndex=1
    velocity=100

    inputoscillatorpositions=np.zeros(1000) #each successive entry corresponds to the theta1 position reached at that note
    inputoscillatorpositions[0]=2*np.pi #first note is at 2 pi

    for NoteIndex in range(1,len(inputtimings)):
        current_time = inputtimings[NoteIndex]

        lastnote_frame=0
        if NoteIndex>1:
            lastnote_frame=int(inputtimings[NoteIndex-1]*framerate)
        thisnote_frame=int(inputtimings[NoteIndex]*framerate)
        elapsedframes=thisnote_frame-lastnote_frame
        #print(NoteIndex)
        #understand where we are in the score, based on the input
        inputscoreposition=accompaniment_scorepositions[NoteIndex]
        #corresponding oscillator (theta1) position
        inputoscillatorpositions[NoteIndex]=2*np.pi*(inputscoreposition+1) #first note is at 2 pi







        for t in range(lastnote_frame,thisnote_frame+1):
            theta1[t]=inputoscillatorpositions[NoteIndex-1]+(inputoscillatorpositions[NoteIndex]-inputoscillatorpositions[NoteIndex-1])*(t-lastnote_frame)/elapsedframes #linear interpolation
            if t<100:
                theta2[t+1]=theta2[t]+Omega2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                theta3[t+1]=theta3[t]+Omega2+K32*(theta2[t]-theta3[t])
            if t>99:
                theta2[t+1]=theta2[t]+(theta2[t]-theta2[t-100])/100+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                theta3[t+1]=theta3[t]+(theta3[t]-theta3[t-100])/100+K32*(theta2[t]-theta3[t])

        #print('\n'+str(current_time)+" received Note #"+str(NoteIndex)+", frames since previous note: "+str(elapsedframes)+', theta1 is at '+str(inputoscillatorpositions[NoteIndex]/(2*np.pi))+'*2pi'+', theta3 is at '+str(theta3[thisnote_frame]/(2*np.pi))+'*2pi')


        predictionbeats=1.01
        # we predict when the following output notes (up until predictionbeats later) will occur. i.e. extrapolate theta3 until that multiple of 2pi
        theta3slope=(theta3[thisnote_frame]-theta3[thisnote_frame-1])/1

        predictionbound=inputoscillatorpositions[NoteIndex]+2*np.pi*(predictionbeats)
        for i in range(len(input_scorepositions)):
            theta3target=(input_scorepositions[i]+1)*2*np.pi
            if theta3target<=predictionbound:
                relativepredictedframe=(theta3target-theta3[thisnote_frame])/theta3slope
                #print('\n'+str(current_time)+" accompaniment Note #"+str(i+1)+" expected in "+str(relativepredictedframe)+" frames ")
                outputrelativeframe=max(reactiontime,relativepredictedframe)
                newnote=['note_on',72,velocity,current_time+outputrelativeframe/framerate,'accompaniment',i]

                already=0
                for notes in output:
                    if notes[5]==i and newnote[3]>notes[3]:
                        already=1
                if already==0:
                    output+=[newnote]





    for i in range(len(output)):
        for comparison in output:
            if output[i][5]==comparison[5] and output[i][3]>comparison[3]:
                output[i]= [0, 0, 0, 0, 0,0]
    ##
    new =[]
    for k in range(len(output)):
        if not output[k] == [0,0,0,0,0,0]:
            #print(k)
            new += [output[k][3]]

    e=0
    for i in range(min(len(new),len(subjectoutput))):
        e+=(new[i]-subjectoutput[i])**2

    print('tested ',K21,K23,K32,reactiontime,' error:',e)
    simulatelog+='\n tested '+str([K21,K23,K32,reactiontime])+'\n simulated output'+str(new)+'\n target output'+str(subjectoutput)+'\n error:'+str(e)
                                                                                                                                                   

    return e,new,theta3







def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

# def on_release(key):
#     print('{0} released'.format(
#         key))
#     if key == keyboard.Key.esc:
#         # Stop listener
#         return False

# # Collect events until released



def on_release(key):
    global running, subjectoutput, accompaniment_notes, accompaniment_scorepositions, simulatelog
    if key == keyboard.Key.esc:
        #print("pressed ESC")
        running=0 #this stops the threads

        print('\n this is input log:'+str(inputmsglog))
        #print('\n this is receivednotelog:',receivednotelog)
        print('\n this is output log:'+str(realoutputlog))

        # inputtimingerror=[]
        # for i in range(min(len(inputtiminglog),len(receivednotelog))):
        #     inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        # print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        # outputtimingerror=[]
        # for i in range(min(len(outputtiminglog),len(realoutputlog))):
        #     outputtimingerror+=[np.abs(outputtiminglog[i]-realoutputlog[i])]
        # print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))

        inputlogfile=open(str(time.time())+"sec3ign_inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        # receivednotelogfile=open("receivednotelog.txt","w")
        # receivednotelogfile.write(str(receivednotelog))
        # receivednotelogfile.close()
        # outputtiminglogfile=open("outputtiminglog.txt","w")
        # outputtiminglogfile.write(str(outputtiminglog))
        # outputtiminglogfile.close()
        outputlogfile=open(str(time.time())+"sec3ign_outputlog.txt","w")
        outputlogfile.write(str(outputlog))
        outputlogfile.close()

        # workerlogfile=open("workerlog.txt","w")
        # workerlogfile.write(workerlog)
        # workerlogfile.close()
        # logfile=open("log.txt","w")
        # logfile.write(log)
        # logfile.close()



        subjectoutput=inputtiminglog
        #turn accompaniment array into only noteon, since simulation only needs that
        #[accompaniment_notes,accompaniment_scorepositions]=noteonoff_to_noteon(accompaniment_onoff,accompaniment_notes,accompaniment_scorepositions)

        ## gradient descent


        print('inputtimings:'+str(inputtimings))
        print('input_scorepositions:'+str(input_scorepositions))
        print('accompaniment_scorepositions:'+str(accompaniment_scorepositions))
        print('subjectoutput:'+str(subjectoutput))
        return False


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

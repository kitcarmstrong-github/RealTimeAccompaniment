from __future__ import print_function
import threading
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time
import datetime
import logging
import sys
import time
import rtmidi
import os

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
input_notes = [72,72,72,72,72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72, 72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72, 79, 79, 77, 77, 76, 76, 74, 74, 79, 79, 77, 77, 76, 76, 74, 74, 72, 72, 79, 79, 81, 81, 79, 79, 77, 77, 76, 76, 74, 74, 72,1]
input_scorepositions=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,100]

OutputNoteIndex=0

#input_scorepositions=np.arange(0,200,0.25)
accompaniment_scorepositions=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66]
accompaniment_notes=[48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 60, 48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 60, 64, 55, 62, 55, 60, 55, 59, 55, 64, 55, 62, 55, 60, 55, 59, 55, 48, 60, 64, 60, 65, 60, 64, 60, 62, 59, 60, 57, 53, 55, 48]


midiout = rtmidi.MidiOut()
print(midiout.get_ports())
midiout.open_port(0)

port = sys.argv[1] if len(sys.argv) > 1 else None
midiin, port_name = open_midiinput(port)

inputqueue = queue.Queue()

def inputreading():
    global running
    global inputmsglog,inputtiminglog, outputlog
    print('\n inputreading starts ')
    inputtimings=np.zeros(1000)
    inputoscillatorpositions=np.zeros(1000)
    velocity=np.zeros(1000)


    for NoteIndex in range(1,len(input_scorepositions)+1):
        #understand where we are in the score, based on the input
        inputscoreposition=input_scorepositions[NoteIndex-1] #NoteIndex starts at 1, scorepositions start at 0
        #corresponding oscillator (theta1) position
        inputoscillatorpositions[NoteIndex]=2*np.pi*(inputscoreposition+1) #first note is at 2 pi
    
    NoteIndex=1
    outputnote=['note_off',10,10,0,'accompaniment',0]

    while running==1:
        msg = midiin.get_message()
        if msg:
            current_time = time.time() - time_start
            inputmsglog+=[['Input',msg[0][0],msg[0][1],msg[0][2],current_time]]
            if msg[0][2]>0 and msg[0][0]>143:
                inputtiminglog+=[current_time]
        #        log+='\n'+str(current_time)+" calculating thread received MIDI signal "+str(midi_data)
            # After getting the input data, empty the queue, then calculate the new responses
            # and put them into queue. [0][2] is velocity, [0][1] is note number, [0][0] noteon off
            midi_data=msg
            if midi_data[0][2]>10 and midi_data[0][0]>143 and (midi_data[0][1]==input_notes[NoteIndex-1] or midi_data[0][1]==input_notes[NoteIndex]): #i.e. it's a note-on event
                if midi_data[0][1]==input_notes[NoteIndex] and not midi_data[0][1]==input_notes[NoteIndex-1]:
                    inputtimings[NoteIndex]=inputtimings[NoteIndex-1]
                    print('Note #'+str(NoteIndex)+' received with skip at '+str(inputtimings[NoteIndex]))
                    NoteIndex+=1

                inputtimings[NoteIndex]=current_time
                #print('Note #'+str(NoteIndex)+' received at '+str(inputtimings[NoteIndex]))
                velocity[NoteIndex]=midi_data[0][2]

                velocity_range=[]
                for i in range(max(1,NoteIndex-3),NoteIndex):
                    velocity_range+=[velocity[i]]
                current_desired_velocity=max(10,0.9*np.mean(velocity_range)-10)



                for i in range(len(accompaniment_scorepositions)):
                    if accompaniment_scorepositions[i]==input_scorepositions[NoteIndex-1]:
                        NoteOff(outputnote)
                        outputlog+='\n'+str(current_time)+str(['note_off',outputnote[1],outputnote[2],outputnote[3],outputnote[4],outputnote[5]])
                        #print('noteoff',outputnote, 'accompaniment_scoreposition',accompaniment_scorepositions[i])
                        outputnote=['note_on',accompaniment_notes[i],current_desired_velocity,0,'accompaniment',i]
                        NoteOn(outputnote)
                        #print('noteon',outputnote)
                        #realoutputlog+=[outputnote]
                        outputlog+='\n'+str(current_time)+str(outputnote)
                        break

                NoteIndex+=1






q = []

def NoteOn(note):
    midiout.send_message([0x90,note[1],note[2]])

def NoteOff(note):
    midiout.send_message([0x80,note[1],note[2]])



running=1

#threading.Thread(target=worker, daemon=True).start()

threading.Thread(target=inputreading).start()




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
    global running, subjectoutput
    if key == keyboard.Key.esc:
        #print("pressed ESC")
        running=0 #this stops the threads

        print('\n this is input log:'+str(inputmsglog))
        #print('\n this is receivednotelog:',receivednotelog)
        print('\n this is output log:'+str(outputlog))

        # inputtimingerror=[]
        # for i in range(min(len(inputtiminglog),len(receivednotelog))):
        #     inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        # print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        # outputtimingerror=[]
        # for i in range(min(len(outputtiminglog),len(realoutputlog))):
        #     outputtimingerror+=[np.abs(outputtiminglog[i]-realoutputlog[i])]
        # print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))
        
        logdirectory="logs/sec3_real_accomp_star_obs_"+str(time.time())
        os.makedirs(logdirectory)


        inputlogfile=open(logdirectory+"/inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        # receivednotelogfile=open("receivednotelog.txt","w")
        # receivednotelogfile.write(str(receivednotelog))
        # receivednotelogfile.close()
        # outputtiminglogfile=open("outputtiminglog.txt","w")
        # outputtiminglogfile.write(str(outputtiminglog))
        # outputtiminglogfile.close()
        outputlogfile=open(logdirectory+"/outputlog.txt","w")
        outputlogfile.write(str(outputlog))
        outputlogfile.close()
        
        # workerlogfile=open("workerlog.txt","w")
        # workerlogfile.write(workerlog)
        # workerlogfile.close()
        # logfile=open("log.txt","w")
        # logfile.write(log)
        # logfile.close()




        return False


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

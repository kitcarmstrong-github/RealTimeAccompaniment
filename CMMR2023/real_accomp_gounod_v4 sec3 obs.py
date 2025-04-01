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
input_notes=[60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 62, 69, 74, 77, 69, 74, 77, 60, 62, 69, 74, 77, 69, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 62, 69, 74, 77, 69, 74, 77, 60, 62, 69, 74, 77, 69, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 59, 62, 67, 74, 77, 67, 74, 77, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 67, 72, 76, 67, 72, 76, 60, 64, 69, 76, 81, 69, 76, 81, 60, 64, 69, 76, 81, 69, 76, 81, 60, 62, 66, 69, 74, 66, 69, 74, 60, 62, 66, 69, 74, 66, 69, 74, 59, 62, 67, 74, 79, 67, 74, 79, 59, 62, 67, 74, 79, 67, 74, 79, 59, 60, 64, 67, 72, 64, 67, 72, 59, 60, 64, 67, 72, 64, 67, 72,
57, 60, 64, 67, 72, 64, 67, 72, 57, 60, 64, 67, 72, 64, 67, 72, 50, 57, 62, 66, 72, 62, 66, 72, 50, 57, 62, 66, 72, 62, 66, 72, 55, 59, 62, 67, 71, 62, 67, 71, 55, 59, 62, 67, 71, 62, 67, 71, 55, 58, 64, 67, 73, 64, 67, 73, 55, 58, 64, 67, 73, 64, 67, 73, 53, 57, 62, 69, 74, 62, 69, 74, 53, 57, 62, 69, 74, 62, 69, 74, 53, 56, 62, 65, 71, 62, 65, 71, 53, 56, 62, 65, 71, 62, 65, 71, 52, 55, 60, 67, 72, 60, 67, 72, 52, 55, 60, 67, 72, 60, 67, 72, 52, 53, 57, 60, 65, 57, 60, 65, 52, 53, 57, 60, 65, 57, 60, 65, 50, 53, 57, 60, 65, 57, 60, 65, 50, 53, 57, 60, 65, 57, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 48, 52, 55, 60, 64, 55, 60, 64, 48, 52, 55, 60, 64, 55, 60, 64, 48, 55, 58, 60, 64, 58, 60, 64, 48, 55, 58, 60, 64, 58, 60, 64,
41, 53, 57, 60, 64, 57, 60, 64, 41, 53, 57, 60, 64, 57, 60, 64, 42, 48, 57, 60, 63, 57, 60, 63, 42, 48, 57, 60, 63, 57, 60, 63, 43, 51, 59, 60, 63, 59, 60, 63, 43, 51, 59, 60, 63, 59, 60, 63, 44, 53, 59, 60, 62, 59, 60, 62, 44, 53, 59, 60, 62, 59, 60, 62, 43, 53, 55, 59, 62, 55, 59, 62, 43, 53, 55, 59, 62, 55, 59, 62, 43, 52, 55, 60, 64, 55, 60, 64, 43, 52, 55, 60, 64, 55, 60, 64, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 51, 57, 60, 66, 57, 60, 66, 43, 51, 57, 60, 66, 57, 60, 66,
43, 52, 55, 60, 67, 55, 60, 67, 43, 52, 55, 60, 67, 55, 60, 67, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 60, 65, 55, 60, 65, 43, 50, 55, 59, 65, 55, 59, 65, 43, 50, 55, 59, 65, 55, 59, 65, 36, 48, 55, 58, 64, 55, 58, 64, 36, 48, 55, 58, 64, 55, 58, 64, 36, 48, 53, 57, 60, 65, 60, 57, 60, 57, 53, 57, 53, 50, 53, 50, 36, 47, 67, 71, 74, 77, 74, 71, 74, 71, 67, 71, 62, 65, 64, 62, 60]

OutputNoteIndex=0

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
    global running
    global inputmsglog,inputtiminglog, realoutputlog
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
    outputnote=['note_on',10,10,0,'accompaniment',0]

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
                current_desired_velocity=min(127,20+1.2*np.mean(velocity_range))



                for i in range(len(accompaniment_scorepositions)):
                    if accompaniment_scorepositions[i]==input_scorepositions[NoteIndex-1]:
                        NoteOff(outputnote)
                        outputlog+='\n'+str(current_time)+str(outputnote)
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
        print('\n this is output log:'+str(realoutputlog))

        # inputtimingerror=[]
        # for i in range(min(len(inputtiminglog),len(receivednotelog))):
        #     inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        # print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        # outputtimingerror=[]
        # for i in range(min(len(outputtiminglog),len(realoutputlog))):
        #     outputtimingerror+=[np.abs(outputtiminglog[i]-realoutputlog[i])]
        # print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))
        
        inputlogfile=open(str(time.time())+"sec3obs_inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        # receivednotelogfile=open("receivednotelog.txt","w")
        # receivednotelogfile.write(str(receivednotelog))
        # receivednotelogfile.close()
        # outputtiminglogfile=open("outputtiminglog.txt","w")
        # outputtiminglogfile.write(str(outputtiminglog))
        # outputtiminglogfile.close()
        outputlogfile=open(str(time.time())+"sec3obs_outputlog.txt","w")
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

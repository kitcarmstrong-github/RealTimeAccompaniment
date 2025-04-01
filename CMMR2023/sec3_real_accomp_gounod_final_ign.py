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
# noteRead = []
# timeStampRead = []
# durationRead = []
# velocityRead = []
# accompanimentSelect = 'Little Star LH 1.csv'

# with open(accompanimentSelect, newline='') as csvfile:
#   rows = csv.reader(csvfile)
#   for row in rows:
#     noteRead.append(int(row[0]))

# with open(accompanimentSelect, newline='') as csvfile:
#   rows = csv.reader(csvfile)
#   for row in rows:
#     timeStampRead.append(float(row[1])/2)

# with open(accompanimentSelect, newline='') as csvfile:
#   rows = csv.reader(csvfile)
#   for row in rows:
#     durationRead.append(float(row[2])/2)

# with open(accompanimentSelect, newline='') as csvfile:
#   rows = csv.reader(csvfile)
#   for row in rows:
#     velocityRead.append(int(row[3]))

#accompaniment_onoff=[]
#accompaniment_notes=[]

#note: these arrays have only noteon events
#accompaniment_scorepositions=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,    16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,    32,33,34,35,36,37,38,39,  40,41,42,43,44,45,45.75,46,46,47,    48,49,50,51,52,53,54,55,56,57,58,59,60,61,62]
#accompaniment_scorepositions=[x+4 for x in accompaniment_scorepositions]
#accompaniment_scorepositions=[0,1,2,3]+accompaniment_scorepositions



gounodmelodyrecording=[['Keyboard1', 144, 96, 105, 12.362169742584229], ['Keyboard1', 128, 96, 121, 13.072378873825073], ['Keyboard1', 144, 96, 90, 13.209387063980103], ['Keyboard1', 128, 96, 123, 13.96531367301941], ['Keyboard1', 144, 96, 97, 14.070220708847046], ['Keyboard1', 128, 96, 121, 14.774722814559937], ['Keyboard1', 144, 96, 93, 14.901606798171997], ['Keyboard1', 128, 96, 125, 15.638835906982422], ['Keyboard1', 144, 76, 90, 28.9823157787323], ['Keyboard1', 144, 77, 95, 32.27484083175659], ['Keyboard1', 128, 76, 120, 32.28010606765747], ['Keyboard1', 128, 77, 122, 35.02513575553894], ['Keyboard1', 144, 77, 94, 35.17385768890381], ['Keyboard1', 144, 79, 94, 35.593929052352905], ['Keyboard1', 128, 77, 103, 35.60928273200989], ['Keyboard1', 144, 74, 90, 38.07866597175598], ['Keyboard1', 128, 79, 122, 38.08155703544617], ['Keyboard1', 144, 76, 88, 38.91960406303406], ['Keyboard1', 128, 74, 126, 38.9281370639801], ['Keyboard1', 144, 81, 99, 42.26162576675415], ['Keyboard1', 128, 76, 124, 42.26539587974548], ['Keyboard1', 128, 81, 121, 44.26699090003967], ['Keyboard1', 144, 69, 74, 44.313737869262695], ['Keyboard1', 144, 71, 85, 44.72567391395569], ['Keyboard1', 128, 69, 124, 44.727272033691406], ['Keyboard1', 144, 72, 90, 45.137661933898926], ['Keyboard1', 128, 71, 122, 45.14668869972229], ['Keyboard1', 144, 74, 93, 45.57091307640076], ['Keyboard1', 128, 72, 124, 45.587501764297485], ['Keyboard1', 144, 76, 86, 47.028772830963135], ['Keyboard1', 128, 74, 126, 47.03480291366577], ['Keyboard1', 144, 74, 93, 47.25000190734863], ['Keyboard1', 128, 76, 122, 47.28706192970276], ['Keyboard1', 144, 79, 93, 48.884992837905884], ['Keyboard1', 128, 74, 125, 48.886045932769775], ['Keyboard1', 128, 79, 119, 50.908287048339844], ['Keyboard1', 144, 67, 76, 50.94773578643799], ['Keyboard1', 144, 69, 85, 51.3565137386322], ['Keyboard1', 128, 67, 124, 51.36425185203552], ['Keyboard1', 144, 71, 88, 51.779117822647095], ['Keyboard1', 128, 69, 111, 51.786365032196045], ['Keyboard1', 144, 72, 93, 52.19671988487244], ['Keyboard1', 128, 71, 122, 52.224457025527954], ['Keyboard1', 144, 74, 93, 53.66150689125061], ['Keyboard1', 128, 72, 110, 53.67328596115112], ['Keyboard1', 144, 72, 88, 53.87883973121643], ['Keyboard1', 128, 74, 125, 53.879979848861694], ['Keyboard1', 128, 72, 124, 55.5152268409729], ['Keyboard1', 144, 84, 98, 55.53081679344177], ['Keyboard1', 128, 84, 121, 57.52271485328674], ['Keyboard1', 144, 72, 83, 57.55373978614807], ['Keyboard1', 144, 74, 92, 57.98573398590088], ['Keyboard1', 128, 72, 125, 58.000075817108154], ['Keyboard1', 144, 76, 90, 58.3941969871521], ['Keyboard1', 128, 74, 124, 58.41456580162048], ['Keyboard1', 144, 78, 96, 58.82513380050659], ['Keyboard1', 128, 76, 125, 58.83773398399353], ['Keyboard1', 128, 78, 120, 60.04809594154358], ['Keyboard1', 144, 76, 89, 60.06571078300476], ['Keyboard1', 128, 76, 124, 60.47789692878723], ['Keyboard1', 144, 74, 90, 60.485811948776245], ['Keyboard1', 128, 74, 125, 61.28670907020569], ['Keyboard1', 144, 69, 85, 61.31097984313965], ['Keyboard1', 144, 71, 88, 62.14300990104675], ['Keyboard1', 128, 69, 124, 62.14613199234009], ['Keyboard1', 128, 71, 124, 63.84823489189148], ['Keyboard1', 144, 74, 96, 64.6231198310852], ['Keyboard1', 144, 76, 95, 65.43425989151001], ['Keyboard1', 128, 74, 126, 65.45334196090698], ['Keyboard1', 128, 76, 123, 67.45292282104492], ['Keyboard1', 144, 76, 93, 67.54569983482361], ['Keyboard1', 144, 77, 95, 67.94712495803833], ['Keyboard1', 128, 76, 126, 67.95960187911987], ['Keyboard1', 144, 79, 94, 68.36266279220581], ['Keyboard1', 128, 77, 124, 68.38548469543457], ['Keyboard1', 144, 81, 99, 68.78483200073242], ['Keyboard1', 128, 79, 118, 68.82324481010437], ['Keyboard1', 128, 81, 115, 70.16059875488281], ['Keyboard1', 144, 69, 77, 70.23181295394897], ['Keyboard1', 128, 69, 121, 70.29540300369263], ['Keyboard1', 144, 69, 89, 70.43586897850037], ['Keyboard1', 144, 74, 96, 72.11902785301208], ['Keyboard1', 128, 69, 124, 72.13256502151489], ['Keyboard1', 128, 74, 125, 74.07457494735718], ['Keyboard1', 144, 74, 97, 74.18199396133423], ['Keyboard1', 144, 76, 94, 74.57723093032837], ['Keyboard1', 128, 74, 125, 74.60941910743713], ['Keyboard1', 144, 77, 98, 74.98297667503357], ['Keyboard1', 128, 76, 124, 75.01494407653809], ['Keyboard1', 144, 79, 96, 75.43111681938171], ['Keyboard1', 128, 77, 125, 75.44439888000488], ['Keyboard1', 128, 79, 115, 76.80337476730347], ['Keyboard1', 144, 67, 79, 76.87521481513977], ['Keyboard1', 128, 67, 120, 76.94318699836731], ['Keyboard1', 144, 67, 88, 77.08523082733154], ['Keyboard1', 144, 72, 95, 78.77185392379761], ['Keyboard1', 128, 67, 108, 78.77285408973694], ['Keyboard1', 128, 72, 121, 80.68854403495789], ['Keyboard1', 144, 72, 93, 80.78697991371155], ['Keyboard1', 144, 74, 96, 81.21605467796326], ['Keyboard1', 128, 72, 125, 81.23156309127808], ['Keyboard1', 144, 76, 95, 81.61717581748962], ['Keyboard1', 128, 74, 125, 81.6435489654541], ['Keyboard1', 128, 76, 124, 82.03033185005188], ['Keyboard1', 144, 76, 7, 82.06150579452515], ['Keyboard1', 144, 77, 96, 82.06521487236023], ['Keyboard1', 128, 76, 127, 82.06625699996948], ['Keyboard1', 128, 77, 121, 84.02639293670654], ['Keyboard1', 144, 77, 99, 84.12512683868408], ['Keyboard1', 144, 79, 99, 84.53200793266296], ['Keyboard1', 128, 77, 125, 84.55132484436035], ['Keyboard1', 144, 81, 101, 84.94416189193726], ['Keyboard1', 128, 79, 122, 84.98676371574402], ['Keyboard1', 128, 81, 123, 85.34272074699402], ['Keyboard1', 144, 83, 101, 85.37613487243652], ['Keyboard1', 144, 81, 97, 86.60105180740356], ['Keyboard1', 128, 83, 123, 86.62029910087585], ['Keyboard1', 144, 79, 97, 87.03444480895996], ['Keyboard1', 128, 81, 123, 87.04895496368408], ['Keyboard1', 128, 79, 123, 87.84603977203369], ['Keyboard1', 144, 74, 91, 87.85915803909302], ['Keyboard1', 128, 74, 119, 88.69096398353577], ['Keyboard1', 144, 76, 95, 88.69686102867126], ['Keyboard1', 128, 76, 125, 90.38370370864868], ['Keyboard1', 144, 76, 90, 91.57128095626831], ['Keyboard1', 144, 79, 95, 91.98898696899414], ['Keyboard1', 128, 76, 125, 92.00038409233093], ['Keyboard1', 144, 76, 93, 93.66942286491394], ['Keyboard1', 128, 79, 122, 93.6866888999939], ['Keyboard1', 128, 76, 125, 94.9440758228302], ['Keyboard1', 144, 76, 100, 95.08948087692261], ['Keyboard1', 144, 81, 101, 95.31427383422852], ['Keyboard1', 128, 76, 124, 95.3153989315033], ['Keyboard1', 128, 81, 118, 96.946053981781], ['Keyboard1', 144, 69, 86, 96.98203802108765], ['Keyboard1', 128, 69, 123, 98.24294185638428], ['Keyboard1', 144, 81, 100, 98.46110272407532], ['Keyboard1', 128, 81, 125, 98.51249384880066], ['Keyboard1', 144, 81, 84, 98.6702868938446], ['Keyboard1', 128, 81, 123, 100.34211587905884], ['Keyboard1', 144, 72, 94, 100.35813689231873], ['Keyboard1', 128, 72, 121, 101.5687370300293], ['Keyboard1', 144, 81, 100, 101.70421195030212], ['Keyboard1', 128, 81, 120, 101.77082991600037], ['Keyboard1', 144, 84, 115, 101.92410182952881], ['Keyboard1', 144, 75, 100, 103.63131189346313], ['Keyboard1', 128, 84, 109, 103.66249704360962], ['Keyboard1', 128, 75, 127, 104.91270089149475], ['Keyboard1', 144, 84, 98, 105.07551169395447], ['Keyboard1', 128, 84, 123, 105.13390803337097], ['Keyboard1', 144, 84, 86, 105.29224872589111], ['Keyboard1', 144, 74, 88, 106.9321837425232], ['Keyboard1', 128, 84, 117, 106.93318200111389], ['Keyboard1', 128, 74, 126, 108.17089676856995], ['Keyboard1', 144, 74, 99, 108.57556295394897], ['Keyboard1', 128, 74, 124, 110.5559287071228], ['Keyboard1', 144, 74, 26, 110.60476493835449], ['Keyboard1', 144, 74, 84, 110.62831497192383], ['Keyboard1', 144, 72, 92, 111.0521879196167], ['Keyboard1', 128, 74, 125, 111.06831073760986], ['Keyboard1', 144, 71, 95, 111.47256875038147], ['Keyboard1', 128, 72, 125, 111.47364687919617], ['Keyboard1', 144, 79, 95, 111.9063937664032], ['Keyboard1', 128, 71, 124, 111.9074318408966], ['Keyboard1', 144, 76, 87, 113.37339401245117], ['Keyboard1', 128, 79, 122, 113.39197087287903], ['Keyboard1', 128, 76, 124, 113.57568073272705], ['Keyboard1', 144, 72, 86, 113.60856080055237], ['Keyboard1', 128, 72, 125, 115.22781586647034], ['Keyboard1', 144, 77, 94, 115.24545001983643], ['Keyboard1', 128, 77, 115, 117.11631393432617], ['Keyboard1', 144, 77, 98, 117.28049898147583], ['Keyboard1', 144, 76, 97, 117.6905767917633], ['Keyboard1', 128, 77, 124, 117.70599675178528], ['Keyboard1', 128, 76, 125, 118.07007074356079], ['Keyboard1', 144, 74, 93, 118.09980297088623], ['Keyboard1', 128, 74, 125, 118.49925684928894], ['Keyboard1', 144, 86, 105, 118.53263282775879], ['Keyboard1', 144, 83, 99, 119.9692759513855], ['Keyboard1', 128, 86, 114, 119.98378086090088], ['Keyboard1', 144, 79, 97, 120.21971797943115], ['Keyboard1', 128, 83, 122, 120.22065901756287], ['Keyboard1', 144, 81, 101, 121.88670182228088], ['Keyboard1', 128, 79, 123, 121.90314888954163], ['Keyboard1', 128, 81, 113, 123.81911492347717], ['Keyboard1', 144, 81, 99, 123.9414930343628], ['Keyboard1', 144, 83, 105, 124.3473768234253], ['Keyboard1', 128, 81, 124, 124.36436581611633], ['Keyboard1', 144, 84, 103, 124.75340294837952], ['Keyboard1', 128, 83, 122, 124.78454780578613], ['Keyboard1', 144, 88, 111, 125.18133091926575], ['Keyboard1', 128, 84, 124, 125.2002649307251], ['Keyboard1', 128, 88, 123, 127.18368887901306], ['Keyboard1', 144, 84, 96, 127.23089170455933], ['Keyboard1', 144, 79, 96, 127.66543006896973], ['Keyboard1', 128, 84, 123, 127.6663990020752], ['Keyboard1', 128, 79, 118, 128.0814847946167], ['Keyboard1', 144, 76, 90, 128.091570854187], ['Keyboard1', 144, 74, 93, 128.51166081428528], ['Keyboard1', 128, 76, 125, 128.52403473854065], ['Keyboard1', 128, 74, 124, 130.5746147632599], ['Keyboard1', 144, 81, 93, 130.59144973754883], ['Keyboard1', 144, 83, 98, 130.99836587905884], ['Keyboard1', 128, 81, 121, 131.02392888069153], ['Keyboard1', 144, 81, 97, 131.4143397808075], ['Keyboard1', 128, 83, 123, 131.44604802131653], ['Keyboard1', 144, 79, 94, 131.81639575958252], ['Keyboard1', 128, 81, 121, 131.82797980308533], ['Keyboard1', 144, 86, 96, 132.24258279800415], ['Keyboard1', 128, 79, 121, 132.2604639530182], ['Keyboard1', 144, 83, 96, 132.64083003997803], ['Keyboard1', 128, 86, 124, 132.65460085868835], ['Keyboard1', 144, 79, 92, 133.03399682044983], ['Keyboard1', 128, 83, 122, 133.0350489616394], ['Keyboard1', 128, 79, 123, 133.47156190872192], ['Keyboard1', 144, 77, 95, 133.47636103630066], ['Keyboard1', 144, 74, 91, 133.87156295776367], ['Keyboard1', 128, 77, 124, 133.88319492340088], ['Keyboard1', 144, 71, 92, 134.28585767745972], ['Keyboard1', 128, 74, 125, 134.28822994232178], ['Keyboard1', 128, 71, 124, 134.66393184661865], ['Keyboard1', 144, 67, 82, 134.68953680992126], ['Keyboard1', 144, 72, 103, 135.15945076942444], ['Keyboard1', 128, 67, 124, 135.17232179641724], ['Keyboard1', 128, 72, 127, 138.52005195617676]]

i=0
for note in gounodmelodyrecording:
    if note[1]==144:
        noteonoff='note_on'
    else:
        noteonoff='note_off'
    q+=[[noteonoff, note[2]+12, note[3],note[4]-5,'accompaniment', i]]
    i+=1



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
        print('\n this is output log:'+str(outputlog))

        # inputtimingerror=[]
        # for i in range(min(len(inputtiminglog),len(receivednotelog))):
        #     inputtimingerror+=[np.abs(inputtiminglog[i]-receivednotelog[i])]
        # print('average input timing error: ',np.mean(inputtimingerror),'max: ',max(inputtimingerror))

        # outputtimingerror=[]
        # for i in range(min(len(outputtiminglog),len(realoutputlog))):
        #     outputtimingerror+=[np.abs(outputtiminglog[i]-realoutputlog[i])]
        # print('average output timing error: ',np.mean(outputtimingerror),'max: ',max(outputtimingerror))

        logdirectory="logs/sec3_real_accomp_gounod_ign"+str(time.time())
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



#        subjectoutput=inputtiminglog
        #turn accompaniment array into only noteon, since simulation only needs that
        #[accompaniment_notes,accompaniment_scorepositions]=noteonoff_to_noteon(accompaniment_onoff,accompaniment_notes,accompaniment_scorepositions)

        ## gradient descent


#        print('inputtimings:'+str(inputtimings))
#        print('input_scorepositions:'+str(input_scorepositions))
#        print('accompaniment_scorepositions:'+str(accompaniment_scorepositions))
#        print('subjectoutput:'+str(subjectoutput))
        return False


with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

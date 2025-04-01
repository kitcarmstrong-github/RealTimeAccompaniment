import sys
import time
import queue
import threading
import os
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, SYSTEM_EXCLUSIVE, END_OF_EXCLUSIVE
import numpy as np

import tools.score_grapher_v0 as score_grapher_v0
import tools.score_sort_v0 as score_sort_v0
import matplotlib.pyplot as plt



def jerk(interpretation):
    scorepositions=[]
    times=[]

    for event in interpretation:
        if event[1]==144 and event[4]>0:
            scorepositions+=[event[3]]
            times+=[event[4]]
    
    speed=[]
    for i in range(len(scorepositions)-1):
        speed+=[[(times[i+1]+times[i])/2,(scorepositions[i+1]-scorepositions[i])/(times[i+1]-times[i])]]
    print('speed='+str(speed))
    accel=[]
    for i in range(len(speed)-1):
        accel+=[[(speed[i+1][0]+speed[i][0])/2,(speed[i+1][1]-speed[i][1])/(speed[i+1][0]-speed[i][0])]]
    print('accel='+str(accel))
    jerk=[]
    for i in range(len(accel)-1):
        jerk+=[[(accel[i+1][0]+accel[i][0])/2,(accel[i+1][1]-accel[i][1])/(accel[i+1][0]-accel[i][0])]]
    print('jerk='+str(jerk))

    # plt.clf()
    # x=[]
    # y=[]
    # for entry in jerk:
    #     if abs(entry[1])<100:
    #         x+=[entry[0]] 
    #         y+=[entry[1]]
    # plt.plot(x,y,'o')

    # plt.show()

    totaljerk=0
    for entry in jerk:
        if abs(entry[1])<100:
            totaljerk+=entry[1]*entry[1]
    #print(totaljerk)
    return totaljerk

# datasetID=input('datasetID/in or out=?')

# with open('data/'+datasetID+'putinterpretation.txt') as f:
#         interpretation=eval(f.read())

# jerk(interpretation)




# #initialize arduino mirror
# arduinoarray=[[-1,0,0,0,0]]*50



# #get MIDI ports
# port = sys.argv[1] if len(sys.argv) > 1 else None
# try:
#     midiout, port_name_out = open_midioutput(port)
#     midiin, port_name_in = open_midiinput(port)
# except (EOFError, KeyboardInterrupt):
#     sys.exit()

# q = queue.Queue()

# def sendRealTimeStamp():
#     timeStamp = time.time_ns()
#     timeStampSysEx = []
#     timeStampSysEx.append(SYSTEM_EXCLUSIVE)
#     timeStampSysEx.append(0x00)
#     timeStampSysEx.append(0x00)
#     timeStampSysEx.append(0x00)
#     for i in str(timeStamp):
#         timeStampSysEx.append(int(i)) 
#     timeStampSysEx.append(END_OF_EXCLUSIVE)
#     midiout.send_message(timeStampSysEx)


# def sendEventTimeStamp(messageType, dataByte1, dataByte2,dataByte3, predictionTimeStamp):
#     timeStamp = predictionTimeStamp
#     timeStampSysEx = []
#     timeStampSysEx.append(SYSTEM_EXCLUSIVE)
#     timeStampSysEx.append(messageType - 127)
#     timeStampSysEx.append(dataByte1)
#     timeStampSysEx.append(dataByte2)
#     timeStampSysEx.append(dataByte3)
#     for i in str(timeStamp)[1:]:
#         timeStampSysEx.append(int(i)) 
#     timeStampSysEx.append(END_OF_EXCLUSIVE)
#     midiout.send_message(timeStampSysEx)
#     print(timeStampSysEx)

# def sendEvent(arduinoarrayElement,arrayPosition): #arduinoarrayElement has following structure: [index,type,note,time,velocity]
#                                                     #timeStampSysEx: [240,arrayposition,type-127,note,velocity,index,time...]
#     #print('writing arduinoarrayElement',arduinoarrayElement,' to array position',arrayPosition)
#     timeStamp = arduinoarrayElement[3]
#     timeStampSysEx = []
#     timeStampSysEx.append(SYSTEM_EXCLUSIVE)
#     timeStampSysEx.append(arrayPosition)
#     timeStampSysEx.append(arduinoarrayElement[1] - 127)
#     timeStampSysEx.append(arduinoarrayElement[2])
#     timeStampSysEx.append(arduinoarrayElement[4])
#     timeStampSysEx.append(arduinoarrayElement[0])
#     for i in str(timeStamp)[1:]:
#         timeStampSysEx.append(int(i)) 
#     timeStampSysEx.append(END_OF_EXCLUSIVE)
#     midiout.send_message(timeStampSysEx)
#     print(timeStampSysEx)


# framerate=100
# theta1=np.zeros(200*framerate)
# theta2=np.zeros(200*framerate)
# theta3=np.zeros(200*framerate)

# reactiontime=10 #in frames

# Omega2=0.002
# Omega3=0.002
# theta2[0]=0
# theta2[1]=Omega2
# theta3[0]=0
# theta3[1]=Omega2

# K21=0.1
# K23=0.1
# K32=0.1

# def calculating(stop_flag):
#     starttime=time.time_ns()/1000000000
#     global lastinputIndex,lastinputscorepositionIndex
#     global theta1,theta2,theta3
#     global outputinterpretation
#     global arduinoarray
#     while not stop_flag.is_set():
#         if not q.empty():
#             msg = q.get()
#             #sendEventTimeStamp(msg[0], msg[1]+4, msg[2], msg[3]+250000000)
#             #figure out which input note msg corresponds to. 
#             foundmatch=0
#             if msg[0]==144: 
#                 for note in inputinterpretation:
#                     if note[1]==144 and note[3]>=inputscorepositions[lastinputscorepositionIndex]-0.01 and note[3]<=inputscorepositions[lastinputscorepositionIndex+1]+0.51: #search between latest events' beat and next events' beat + 0.5
#                         if note[2]==msg[1] and note[4:]==[0,0]: #i.e. if it's the right note and hasn't been played yet
#                             note[4]=msg[3]/1000000000
#                             note[5]=msg[2]
#                             lastinputIndex=max(lastinputIndex,note[0])
#                             lastinputscorepositionIndex=inputscorepositions.index(inputinterpretation[lastinputIndex][3])
#                             #print('lastinputscorepositionIndex',lastinputscorepositionIndex)
#                             foundmatch=1
#                             print(str(time.time_ns())+'received '+str(msg)+' matched to '+str(note))
#                             break
#             if msg[0]==128:
#                 for note in reversed(inputinterpretation): #find the last time that note was played
#                     if note[1]==144 and note[2]==msg[1] and not note[4:]==[0,0]:
#                         for offnote in inputinterpretation[note[0]:]: #search forward to find the nearest noteoff event
#                             if offnote[1]==128 and offnote[2]==msg[1]:
#                                 if not offnote[4:]==[0,0]:
#                                     print('already got this noteoff')
#                                 offnote[4]=msg[3]/1000000000
#                                 offnote[5]=msg[2]
#                                 foundmatch=1
#                                 print(str(time.time_ns())+'received '+str(msg)+' matched to '+str(offnote))
#                                 break
#                         break



#             if foundmatch==0: #i.e. didn't find a match
#                 print('could not match '+str(msg))
#             else:
#                 #model
#                 #create piecewise linear theta1
#                 points=[[0,-1]]
#                 for position in inputscorepositions:
#                     timing=[]
#                     for note in inputinterpretation:
#                         if note[1]==144 and note[3]==position and not note[4:]==[0,0]:
#                             timing+=[note[4]-starttime]
#                         if note[3]>position:
#                             break
#                     if position>inputscorepositions[lastinputscorepositionIndex]+1:
#                         break
#                     if not len(timing)==0:
#                         points+=[[np.mean(timing),position]]
#                 points.sort(key = lambda x: x[0])
#                 #print('points',points)
#                 for i in range(1,len(points)):
#                     for t in range(int(points[i-1][0]*framerate),int(points[i][0]*framerate)):
#                         theta1[t]=points[i-1][1]+(t/framerate-points[i-1][0])*(points[i][1]-points[i-1][1])/(points[i][0]-points[i-1][0])

#                         if t<100:
#                             currentspeed2=Omega2
#                             currentspeed3=Omega2
#                         if t>99:
#                             currentspeed2=(theta2[t]-theta2[t-100])/100
#                             currentspeed3=(theta3[t]-theta3[t-100])/100
#                         theta2[t+1]=theta2[t]+currentspeed2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
#                         theta3[t+1]=theta3[t]+currentspeed3+K32*(theta2[t]-theta3[t])

#                 #predict output timings
#                 lastcalculatedtheta3frame=int(points[-1][0]*framerate)
#                 theta3slope=theta3[lastcalculatedtheta3frame]-theta3[lastcalculatedtheta3frame-1]
#                 theta3yIntercept=theta3[lastcalculatedtheta3frame]-theta3slope*lastcalculatedtheta3frame
#                 #print(theta3slope,' ',theta3yIntercept)
#                 for note in outputinterpretation:
#                     outputtime=starttime+(note[3]-theta3yIntercept)/theta3slope/framerate
#                     if note[4]<time.time_ns()/1000000000+reactiontime/framerate and note[4]>time.time_ns()/1000000000:
#                         pass
#                     else:
#                         note[4]=outputtime
#                         if note[4]<time.time_ns()/1000000000+reactiontime/framerate and note[4]>time.time_ns()/1000000000:
#                             note[4]=time.time_ns()/1000000000+reactiontime/framerate
#                     #figure out velocity (running average)
#                     velocity_range=[]
#                     for inputnote in inputinterpretation:
#                         if inputnote[1]==144 and inputnote[3]>=note[3]-1 and not inputnote[5]==0: #search for already played notes starting from 1 beat ago
#                             velocity_range+=[inputnote[5]]
#                     current_desired_velocity=int(min(127,20+1.2*np.mean(velocity_range)))
#                     note[5]=current_desired_velocity
#             # now outputting to arduinoarray
#                     wrotetoarray=0
#                     clearpositions=[]
#                     for i in range(50):
#                         if arduinoarray[i][0]==note[0]: #if the indices match, i.e. the note is to be overwritten with the new prediction, or the index is blank:
#                             arduinoarray[i]=[note[0],note[1],note[2],int(note[4]*1000000000),note[5]]
#                             sendEvent(arduinoarray[i],i)
#                             wrotetoarray=1
#                         #print(time.time_ns(),'event at position',i,'happens in',(arduinoarray[i][3]-time.time_ns())/1000000000)
#                         if arduinoarray[i][3]<time.time_ns()-1000000000: #i.e. if it should have already happened more than a second ago
#                             arduinoarray[i][1]=0 #make the array position ready to be assigned to a new event
#                             clearpositions+=[i]
#                             #print('cleared array position', i)
#                     if wrotetoarray==0 and note[4]>=time.time_ns()/1000000000-1:
#                         for i in clearpositions:
#                             arduinoarray[i]=[note[0],note[1],note[2],int(note[4]*1000000000),note[5]]
#                             sendEvent(arduinoarray[i],i)
#                             wrotetoarray=1
#                             break
#                     # if wrotetoarray==0:
#                     #     print('no space in arduinoarray')
#                 #print('outputinterpretation',outputinterpretation)


#             q.task_done()





# stop_flag = threading.Event()
# threading.Thread(target=calculating, args=(stop_flag,)).start()

# while True:
#     try:
#         sendRealTimeStamp()
#         msg = midiin.get_message()
#         if msg:
#             if msg[0][0] == NOTE_ON or msg[0][0] == NOTE_OFF:
#                 q.put((msg[0][0], msg[0][1], msg[0][2], time.time_ns()))
#     except (EOFError, KeyboardInterrupt):
#         stop_flag.set()
#         threading.Thread(target=calculating, args=(stop_flag,)).join
#         q.join()

#         logdirectory="logs/real_accomp_"+str(time.time())
#         os.makedirs(logdirectory)

#         inputfile=open(logdirectory+"/inputinterpretation.txt","w")
#         inputfile.write(str(inputinterpretation))
#         inputfile.close()

#         outputfile=open(logdirectory+"/outputinterpretation.txt","w")
#         outputfile.write(str(outputinterpretation))
#         outputfile.close()

#         combinedinterpretation=score_sort_v0.sort(4,inputinterpretation+outputinterpretation)

#         combinedfile=open(logdirectory+"/combinedinterpretation.txt","w")
#         combinedfile.write(str(combinedinterpretation))
#         combinedfile.close()

#         score_grapher_v0.graph(inputinterpretation,logdirectory+'/inputplot.png')
#         score_grapher_v0.graph(outputinterpretation,logdirectory+'/outputplot.png')
#         score_grapher_v0.graph(combinedinterpretation,logdirectory+'/combinedplot.png')

#         print('Exit')
#         sys.exit()        
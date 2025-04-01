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

import calculate_jerk
from sklearn.linear_model import LinearRegression as lr

piece1=[0.218775398,0.0909062688,0.114561203,-0.0224014174,0.0455063034,-0.0162781048,0.0000470016279,-0.101020121, -0.0193083658,  0.0435891844,  0.0438167828]

piece2=[0.13016205,  0.01219835,  0.00964969, -0.03048317,  0.03814289,  0.05801869,0.01771092,  0.12327689,  0.05563585, -0.01670137,  0.00073147]

piece3=[0.1418015 , 0.1482223,   0.10889317,  0.03587628,  0.05480198,  0.10952789,
  0.10936975, -0.04325428,  0.01246117,  0.13070191, -0.02330014]

x=[1,2,3,4,5,6,7,8,9,10,11]

plt.clf()

plt.figure(figsize=(3,3))
ax = plt.gca()
#ax.set_xlim([0, 12])
ax.set_ylim([-0.2, 0.3])
plt.stem(x,[0.25,0.25,0.25,0.25,0,0,0,0,0,0,0])
plt.xticks(x)
plt.show()

# fig, axs = plt.subplots(2, 2)
# axs[0, 0].stem(x, piece1)
# axs[0, 0].set_title('Axis [0, 0]')
# axs[0, 1].stem(x, piece2, 'tab:orange')
# axs[0, 1].set_title('Axis [0, 1]')
# axs[1, 0].stem(x, piece3, 'tab:green')
# axs[1, 0].set_title('Axis [1, 0]')
# axs[1, 1].stem(x, [0.25,0.25,0.25,0.25,0,0,0,0,0,0,0], 'tab:red')
# axs[1, 1].set_title('Axis [1, 1]')

#for (m,n), subplot in np.ndenumerate(axs):
#    subplot.set_ylim(-0.3,0.3)
#plt.stem(,piece1)
#plt.show()

# def plottimecurve(interpretation,savefile):
#     plt.clf()

#     plt.figure(figsize=(20,20))

#     plot_on_scorepositions=[]
#     plot_on_times=[]

#     plot_off_scorepositions=[]
#     plot_off_times=[]
#     for event in interpretation:
#         if event[1]==144:
#             plot_on_scorepositions+=[event[3]]
#             plot_on_times+=[event[4]]
#         else:
#             plot_off_scorepositions+=[event[3]]
#             plot_off_times+=[event[4]]

#     plt.plot(plot_on_scorepositions,plot_on_times,'o')
#     plt.plot(plot_off_scorepositions,plot_off_times,'x')

#     if savefile=='show':
#         plt.show()
#     else:
#         plt.savefig(savefile)
#     plt.clf()
#     return False


#datasetID=str(input('dataset ID?'))



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
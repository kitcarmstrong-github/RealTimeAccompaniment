import os
import numpy as np



#import performance
datasetID=str(input('dataset ID?'))
filename='data/'+datasetID+'/inputmsglog.txt'
with open(filename) as f:
    performance=eval(f.read())

os.rename(filename,'data/'+datasetID+'/inputmsglog_original.txt')

for event in performance:
    if event[0]=='Keyboard1':
        event[2]-=12

outputfile=open(filename,"w")
outputfile.write(str(performance))
outputfile.close()

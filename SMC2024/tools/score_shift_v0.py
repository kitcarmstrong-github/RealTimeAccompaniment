from __future__ import print_function
import numpy as np



def shift(shift_step,score):
        #order the events
    print('blah')
    outputscore=score
    for event in outputscore:
        event[3]=event[3]+shift_step
        print(event)
    return outputscore

if __name__ == "__main__":
    shift_step=int(input("how much shift\n"))
    #score=[[1,144,60,0],[2,144,70,5],[3,128,60,2],[4,144,61,2],[5,128,65,2]]
    score=eval(input("score\n"))
    #print(score)
    print('shifted:\n')
    print(shift(shift_step,score))

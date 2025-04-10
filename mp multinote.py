import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
from matplotlib.animation import FuncAnimation
import multiprocessing as mp
import time
import random
import tkinter as tk
import rtmidi
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, SYSTEM_EXCLUSIVE, END_OF_EXCLUSIVE
import numpy as np
from numpy.polynomial import Polynomial
from numpy.polynomial.polynomial import polyval

if __name__=='__main__':


    #import scores
    with open('logs/chopin_25_6_top/outputscore.txt') as f:
        inputscore=eval(f.read())

    with open('logs/chopin_25_6_2nd/outputscore.txt') as f:
        outputscore=eval(f.read())

    metadata={'tempo':100,'output gain':1,'time reactivity':1,'vel reactivity':0.5}
    #metadata={'tempo':100,'output gain':1.5,'time reactivity':0.5,'vel reactivity':0.5} #when 1 is output.

    print("will listen for input score:",inputscore)
    print("will play output score:",outputscore)
    #check that the scores are in proper order
    for index,note in enumerate(inputscore):
        if not note[0]==index:
            print("invalid inputscore")
            exit()
    for index,note in enumerate(outputscore):
        if not note[0]==index:
            print("invalid outputscore")
            exit()

    #in="0", out="1"
    def reset_interpretations():
        global inputinterpretation,outputinterpretation,conjectures
        inputinterpretation=[{'part':0,'index':event[0],'on_off':event[1],'note#':event[2],'score_pos':event[3],'time':None,'vel':None} for event in inputscore]
        outputinterpretation=[{'part':1,'index':event[0],'on_off':event[1],'note#':event[2],'score_pos':event[3],'time':None,'vel':None} for event in outputscore]
        conjectures=[]
        return inputinterpretation,outputinterpretation

    reset_interpretations()

    #make a list of all unique inputscorepositions
    inputscorepositions={-1:[]} #for each score position, which noteon indices have that position
    for note in inputinterpretation:
        if note.get('on_off')==144:
            entered=0
            for pos in inputscorepositions:
                if abs(note['score_pos']-pos)<0.01:
                    inputscorepositions[pos]+=[note['index']]
                    entered=1
                    break
            if entered==0:
                inputscorepositions[note['score_pos']]=[note['index']]
    inputscorepositions[10000]=[] #to avoid error when processing the last note
    #print(inputscorepositions)
    #lastinputIndex=-1
    #latest_input_posIndex=0

    #make a list of all unique outputscorepositions
    outputscorepositions={-1:[]} #for each score position, which noteon indices have that position
    for note in outputinterpretation:
        if note.get('on_off')==144:
            entered=0
            for pos in outputscorepositions:
                if abs(note['score_pos']-pos)<0.01:
                    outputscorepositions[pos]+=[note['index']]
                    entered=1
                    break
            if entered==0:
                outputscorepositions[note['score_pos']]=[note['index']]
    outputscorepositions[10000]=[] #to avoid error when processing the last note



    nextscoreposition={} #creates a dictionary such that by entering one position, it gives you the next position 
    for pos in inputscorepositions:
        candidates=[10000]
        for note in inputinterpretation:
            if note['score_pos']>pos and note.get('on_off')==144:
                candidates+=[note['score_pos']]
        #print(pos)
        nextscoreposition[pos]=min(candidates)
    #print(nextscoreposition)
    prevscoreposition={} #creates a dictionary such that by entering one position, it gives you the prev position 
    for pos in inputscorepositions:
        candidates=[-1]
        for note in inputinterpretation:
            if note['score_pos']<pos and note.get('on_off')==144:
                candidates+=[note['score_pos']]
        prevscoreposition[pos]=max(candidates)
    #print(prevscoreposition)

    #make a list of references for each output note
    references={} 
    ref_count=20
    for note in outputinterpretation:
        candidates=inputinterpretation[:]+outputinterpretation[:]
        candidates.sort(key=lambda candidate: abs(candidate['score_pos']-note['score_pos']))
        references[note['index']]=candidates[:ref_count]


    conjectures=[]
    typednote=None
    globalflag=False


    figure = plt.Figure(figsize=(16,10)) 
    ax=figure.add_subplot()
    ax.set_xlim([time.time_ns()/1000000000,20+time.time_ns()/1000000000])
    ax.set_ylim([20, 109])

    plot={}
    plotdata={}
    plotnames=['inputon','inputoff','outputon','outputoff','conjectureon','conjectureoff']
    plotcolors=['g','g','b','b','r','r']
    plotmarkers=['o','x','o','x','o','x']

    for i,name in enumerate(plotnames):
        plot[name]=ax.scatter([],[],c=plotcolors[i],marker=plotmarkers[i])

    now_line,=ax.plot([time.time_ns()/1000000000,time.time_ns()/1000000000],[-1,200])

    def update(i):
        if globalflag==True:
            ax.set_xlim([time.time_ns()/1000000000-30,30+time.time_ns()/1000000000])

            plotdata['inputon']=[[note['time'],note['note#']] for note in inputinterpretation if note['on_off']==144 and note.get('time')]
            plotdata['inputoff']=[[note['time'],note['note#']] for note in inputinterpretation if note['on_off']==128 and note.get('time')]

            plotdata['outputon']=[[note['time'],note['note#']] for note in outputinterpretation if note['on_off']==144 and note.get('time')]
            plotdata['outputoff']=[[note['time'],note['note#']] for note in outputinterpretation if note['on_off']==128 and note.get('time')]

            plotdata['conjectureon']=[[note['time'],note['note#']] for note in conjectures if note['on_off']==144 and note.get('time')]
            plotdata['conjectureoff']=[[note['time'],note['note#']] for note in conjectures if note['on_off']==128 and note.get('time')]

            for name in plotnames:
                try:
                    plot[name].set_offsets(plotdata[name])
                except: #usually, when plotdata is empty
                    plot[name].set_offsets([[0,0]])

            now_line.set_xdata([time.time_ns()/1000000000,time.time_ns()/1000000000])
        return False



    #GUI
    window=tk.Tk()
    window.title('title')

    buttons=tk.Frame(window)
    buttons.pack(side='top')

    columnindex=0

    def get_midi_ports():
#        global midiout,midiin,port_name_in,port_name_out
        midiin_label.config(text='MIDI IN\n'+str(midiin.get_ports()))
        midiout_label.config(text='MIDI OUT\n'+str(midiout.get_ports()))
        try:
            midiin.open_port( int(midiin_field.get()) )
        except Exception as error:
            midiin_field.delete(0,'end')
            print(error)
        try:
            midiout.open_port( int(midiout_field.get()) )
        except Exception as error:
            midiout_field.delete(0,'end')
            print(error)
    midiin = rtmidi.MidiIn()
    midiout = rtmidi.MidiOut()
    midiin_label=tk.Label(buttons,text='MIDI IN\n'+str(midiin.get_ports()))
    midiin_label.grid(row=1,column=columnindex)
    midiin_field=tk.Entry(buttons)
    midiin_field.grid(row=2,column=columnindex)
    midiout_label=tk.Label(buttons,text='MIDI OUT\n'+str(midiout.get_ports()))
    midiout_label.grid(row=3,column=columnindex)
    midiout_field=tk.Entry(buttons)
    midiout_field.grid(row=4,column=columnindex)
    tk.Button(buttons,command=get_midi_ports,text='get midi ports').grid(row=0,column=columnindex)
    columnindex+=1

    def execthebox():
        content=evaltextbox.get('1.0','end-1c')
        if not evaltextbox.get('1.0','end-1c')=='':
            print('executing', content)
            exec(content)
    evaltextbox=tk.Text(buttons,width=70)
    evaltextbox.grid(row=1,column=columnindex,rowspan=5)

    tk.Button(buttons,command=execthebox,text='execute').grid(row=0,column=columnindex)
    columnindex+=1

    def type_a_note():
        global typednote
        if not noteentry.get() in ['',None]:
            typednote=[[144,int(noteentry.get()),99]]
            print('typed',typednote)
        else:
            typednote=None
    #        generate(pulse_function=create_pulse_function(int(typednote)))
    def off_a_note():
        global typednote
        if not noteentry.get() in ['',None]:
            typednote=[[128,int(noteentry.get()),99]]
            print('typed',typednote)
        else:
            typednote=None
    noteentry=tk.Entry(buttons)
    noteentry.grid(row=1,column=columnindex,sticky='n')

    tk.Button(buttons,command=type_a_note,text='on this note').grid(row=0,column=columnindex)
    columnindex+=1

    tk.Button(buttons,command=off_a_note,text='off this note').grid(row=0,column=columnindex)
    columnindex+=1

    stringvar=tk.StringVar()
    stringvar.set('reactive')
    model='reactive'
    def choosemodel(stringvar):
        global model
        model=stringvar
    tk.OptionMenu(buttons,stringvar,'linear','cmmr','maezawa','maezawa2','reactive',command=choosemodel).grid(row=0,column=columnindex)
    columnindex+=1

    def start_listen():
        global globalflag,latest_input_pos,latest_output_pos,lastinputIndex,conjectures
        if globalflag==False:
            globalflag=True
            reset_interpretations()
            latest_input_pos=0 #initializing
            latest_output_pos=0 #initializing
            lastinputIndex=0 #initializing
            conjectures=[]
            print('call listen')
            listen(pipe_main)
            p=mp.Process(target=conjecture,args=[pipe_conjecture,model,metadata,inputinterpretation,outputinterpretation,inputscorepositions,outputscorepositions,nextscoreposition,prevscoreposition,references])
            p.start()
    tk.Button(buttons,command=start_listen,text='start listen').grid(row=0,column=columnindex)
    columnindex+=1

    def stop_listen():
        global globalflag
        midiout.send_message([0x80,77,100])
        if globalflag==True:
            pipe_main.send([False,0,0,0,0]) #terminate conjecture process
        globalflag=False
        for n in range(120):
            midiout.send_message([0x80,n,100])
            time.sleep(0.001)
    tk.Button(buttons,command=stop_listen,text='stop listen').grid(row=0,column=columnindex)
    columnindex+=1

    figure_canvas = FigureCanvasTkAgg(figure, master=window)
    figure_canvas.get_tk_widget().pack(side='bottom')
    anim = FuncAnimation(figure, update, [0.01], interval=100)


    def NoteOn(note):
        try:
            midiout.send_message([0x90,note['note#'],note['vel']])
        except:
            #print('midi problem')
            pass
    def NoteOff(note):
        try:
            midiout.send_message([0x80,note['note#'],note['vel']])
        except:
            #print('midi problem')
            pass

    pipe_main,pipe_conjecture=mp.Pipe(duplex=True)
    
    def listen(pipe):
        global msg,typednote,inputinterpretation,outputinterpretation,conjectures,latest_input_pos,latest_output_pos,lastinputIndex
        #print('called listen',time.time_ns())
        t_1=time.time_ns()
        if globalflag==True:
            msg=None
            #OUTPUT
            reactiontime=-10#0#.1
            if pipe.poll():
                new_conjectures=pipe.recv()
            else:
                new_conjectures=conjectures
            remaining_conjectures=[]
            conjectures=[note for note in conjectures if note['time']<=time.time_ns()/1000000000+reactiontime]+[note for note in new_conjectures if note['time']>time.time_ns()/1000000000+reactiontime]
            for note in conjectures:
                if note['time']<=time.time_ns()/1000000000 and outputinterpretation[note['index']].get('time') is None:# and note['score_pos']>=latest_output_pos-0.01:
                    #THEN PLAY IT
                    if note['on_off']==144:
                        NoteOn(note)
                        latest_output_pos=max(note['score_pos'],latest_output_pos)
                    else:
                        NoteOff(note)
                    outputinterpretation[note['index']]['time']=time.time_ns()/1000000000
                    outputinterpretation[note['index']]['vel']=note['vel']
                    lastoutput=note
                    pipe.send([True,latest_input_pos,latest_output_pos,None,lastoutput])
                    #print('playing',note,'delay',note['time']-time.time_ns()/1000000000)
                    #conjecture() # this is if we want self-aware feedback
                else:
                    remaining_conjectures+=[note]
            conjectures=remaining_conjectures[:]
            t_2=time.time_ns()

            #LISTENING
            try:
                msg = midiin.get_message()
            except:
                pass
            if typednote is not None:
                msg=typednote
                typednote=None
            if msg is not None:
                #print('msg is',msg)
                inputmsg=[msg[0][0], msg[0][1], msg[0][2], time.time_ns()/1000000000]
                foundmatch=0
                if inputmsg[0]==144:
                    index=min(inputscorepositions.get(latest_input_pos)) #we get all the notes, even if the score_pos is off by a float error, by def of inputscorepositions
                    while index<len(inputinterpretation) and inputinterpretation[index]['score_pos']<nextscoreposition[latest_input_pos]+0.51:
                        if [inputinterpretation[index]['on_off'],inputinterpretation[index]['note#']]==[144,inputmsg[1]] and inputinterpretation[index].get('time') is None:
                            inputinterpretation[index]['vel']=inputmsg[2]
                            inputinterpretation[index]['time']=inputmsg[3]
                            lastinputIndex=index
                            lastinput=inputinterpretation[index]
                            latest_input_pos=max(inputinterpretation[index]['score_pos'],latest_input_pos)
                            foundmatch=1
                            print(lastinput)
                            break
                        index+=1
                if inputmsg[0]==128:
                    index=max(inputscorepositions.get(latest_input_pos))+1
                    foundon=0
                    while index>0 and foundon==0: #search backwards
                        index-=1
                        if inputinterpretation[index]['note#']==inputmsg[1] and not inputinterpretation[index].get('time') is None: #it must be an on event (since can't have 2 offs in a row)
                            foundon=1
                    if foundon==1:
                        while index<len(inputinterpretation) and foundmatch==0: #search forwards, don't need a limit because any note on in the score will have a note off eventually
                            if [inputinterpretation[index]['on_off'],inputinterpretation[index]['note#']]==[128,inputmsg[1]] and inputinterpretation[index].get('time') is None:
                                inputinterpretation[index]['vel']=inputmsg[2]
                                inputinterpretation[index]['time']=inputmsg[3]
                                lastinputIndex=index
                                lastinput=inputinterpretation[index]
                                foundmatch=1
                                print(lastinput)
                            index+=1
                        #print(index)
                if foundmatch==1:
                    print('sending to conjecture: ',lastinput.get('index'),lastinput.get('score_pos'),'current latest:',latest_input_pos,latest_output_pos)
                    pipe.send([True,latest_input_pos,latest_output_pos,lastinput,None])

            window.after(1,lambda:listen(pipe_main)) #call the function again


def conjecture(pipe,model,metadata,inputinterpretation,outputinterpretation,inputscorepositions,outputscorepositions,nextscoreposition,prevscoreposition,references):
    conjectureflag=1

    start_time=time.time_ns()/1000000000
    np.set_printoptions(precision=11)
    #initialize CMMR model
    framerate=1000
    theta1=np.zeros(200*framerate)
    theta2=np.zeros(200*framerate)
    theta3=np.zeros(200*framerate)

    reactiontime=100 #in frames

    Omega2=0.02
    Omega3=0.02
    theta2[0]=0
    theta2[1]=Omega2
    theta3[0]=0
    theta3[1]=Omega2

    K21=0.01
    K23=0.01
    K32=0.01
    #end initialize

    #initialize reactive
    playedscorepos=[]
    eq_time=Polynomial([start_time,1])
    eq_vel=Polynomial([60])
    min_dt_dp=0.2
    #end initialize

    while conjectureflag==1:
        new_info={'input':[],'output':[]}
        while pipe.poll():
            t_1=time.time_ns()
            [flag,latest_input_pos,latest_output_pos,lastinput,lastoutput]=pipe.recv()
            if flag is False:
                conjectureflag=0
                print('terminating conjecture process')
                break
            else:
                if lastinput is not None:
                    inputinterpretation[lastinput.get('index')]=lastinput.copy()
                    new_info['input']+=[lastinput.get('index')]
                if lastoutput is not None:
                    outputinterpretation[lastoutput.get('index')]=lastoutput.copy()
                    new_info['output']+=[lastoutput.get('index')]
        if not new_info=={'input':[],'output':[]}:
            print('conjecture process received',new_info)
            

            if model=='linear':
                ref_count=2
                ref_found=[]
                testpos=latest_input_pos
                while len(ref_found)<ref_count and testpos>=0:
                    t=time.time_ns() #any huge number
                    f=None
                    for index in inputscorepositions[testpos]:
                        if inputinterpretation[index]['on_off']==144 and inputinterpretation[index].get('time') is not None:
                            if inputinterpretation[index].get('time')<t:
                                t=inputinterpretation[index].get('time')
                                f=inputinterpretation[index].get('vel')
                    if f is not None:
                        ref_found+=[[testpos,t,f]]
                    testpos=prevscoreposition[testpos]
                #print(ref_found)
                slope=1
                #x1 y1 x2 y2  x3 y3=y1+(x3-x1)*(y2-y1)/(x2-x1)
                if len(ref_found)>1:# and abs(ref_found[0][0]-ref_found[1][0])>0.01:
                    slope=(ref_found[0][1]-ref_found[1][1])/(ref_found[0][0]-ref_found[1][0])
                    #print((ref_found[0][1]-ref_found[1][1]),'/',(ref_found[0][0]-ref_found[1][0]),'=',slope)
                new=[]
                index=min(outputscorepositions[latest_output_pos])
                while index<len(outputinterpretation) and outputinterpretation[index]['score_pos']<latest_output_pos+2:
                    if outputinterpretation[index].get('time') is None:
                        note=outputinterpretation[index].copy()
                        note['time']=ref_found[-1][1]+(outputinterpretation[index]['score_pos']-ref_found[-1][0])*slope
                        #print(note['time']-time.time_ns()/1000000000,outputinterpretation[index]['score_pos'],ref_found[-1])
                        note['vel']=ref_found[0][2]
                        new+=[note]
                    index+=1
                pipe.send(new)
                t_2=time.time_ns()
                print(t_2-t_1)

            if model=='cmmr':
                if 144 in {inputinterpretation[index].get('on_off') for index in new_info['input']}: #if one of the newly heard events is a note-on input
                    conjectures=[]
                    playedscorepos=[[inputnote.get('score_pos'),inputnote.get('time'),inputnote.get('index')] for inputnote in inputinterpretation if inputnote.get('on_off')==144 and inputnote.get('time')]
                    thisnote_scorepos,thisnote_frame,lastnote_scorepos,lastnote_frame=-1,0,-1,0
                    for pos in playedscorepos:
                        if pos[0]>thisnote_scorepos+0.01:
                            lastnote_scorepos=thisnote_scorepos
                            lastnote_frame=thisnote_frame
                            thisnote_scorepos=pos[0]
                            thisnote_frame=int((pos[1]-start_time)*framerate)
                    thisnote_oscpos=2*np.pi*(thisnote_scorepos+1) #convert to oscillator position
                    lastnote_oscpos=2*np.pi*(lastnote_scorepos+1) #convert to oscillator position

                    t_2=time.time_ns()

                    for t in range(lastnote_frame,thisnote_frame+1):
                        if lastnote_frame==thisnote_frame:
                            theta1[t]=lastnote_oscpos
                        else:
                            theta1[t]=lastnote_oscpos+(thisnote_oscpos-lastnote_oscpos)*(t-lastnote_frame)/(thisnote_frame-lastnote_frame) #linear interpolation
                        if t<100:
                            theta2[t+1]=theta2[t]+Omega2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                            theta3[t+1]=theta3[t]+Omega2+K32*(theta2[t]-theta3[t])
                        if t>99:
                            theta2[t+1]=theta2[t]+(theta2[t]-theta2[t-100])/100+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                            theta3[t+1]=theta3[t]+(theta3[t]-theta3[t-100])/100+K32*(theta2[t]-theta3[t])
                    
                    t_3=time.time_ns()
                # print(theta1[lastnote_frame:thisnote_frame],theta3[lastnote_frame:thisnote_frame])
                    predictionbeats=2.01
                    # we predict when the following output notes (up until predictionbeats later) will occur. i.e. extrapolate theta3 until that multiple of 2pi. Make sure there is no gap in the input longer than this number.
                    theta3slope=(theta3[thisnote_frame]-theta3[thisnote_frame-1])/1
                    #print(theta3slope)
                    current_time=time.time_ns()/1000000000
                    predictionbound=thisnote_oscpos+2*np.pi*(predictionbeats)

                    velocity_range=[note.get('vel') for note in inputinterpretation if note.get('vel') and note['on_off']==144 and thisnote_scorepos-2<=note.get('score_pos')<=thisnote_scorepos]
                    #print(velocity_range)
                    current_desired_velocity=min(127,np.mean(velocity_range))
                    
                    for note in outputinterpretation:
                        theta3target=(note.get('score_pos')+1)*2*np.pi
                        if note.get('time') is None and thisnote_oscpos-0.01<=theta3target:
                            if theta3target<=predictionbound:
                                relativepredictedframe=(theta3target-theta3[thisnote_frame])/theta3slope
                                outputrelativeframe=max(reactiontime,relativepredictedframe)
                                outputtiming=current_time+outputrelativeframe/framerate
                                conjectures+=[{**note,'time':outputtiming,'vel':current_desired_velocity}]
                            else:
                                break
                    time.sleep(0*reactiontime/framerate)
                    pipe.send(conjectures)
                    t_4=time.time_ns()
                    #print(t_2-t_1,t_3-t_2,t_4-t_3)

            if model=='reactive':
                if 144 in {inputinterpretation[index].get('on_off') for index in new_info['input']}: #if one of the newly heard events is a note-on input
                    playedscorepos={inputnote.get('score_pos'):inputnote.get('index') for inputnote in inputinterpretation if inputnote.get('on_off')==144 and inputnote.get('time')}
                t_2=time.time_ns()
                if max(playedscorepos)-min(playedscorepos)<0.51: #when it's just started
                    eq_time=Polynomial([ inputinterpretation[min(playedscorepos.values())].get('time') , 60/metadata.get('tempo') ]) #60bpm default starting from first input time
                    eq_vel=Polynomial([60])
                    print('flag1')
                # elif not new_info['output']==[]:
                #     print('flag2')
                #     testindex=max(outputscorepositions[latest_output_pos])
                #     #outputfitref=[]
                #     fit_score_pos=[]
                #     fit_time=[]
                #     fit_vel=[]
                #     while testindex>=0 and (len(fit_score_pos)<4 or outputinterpretation[testindex].get('score_pos')>latest_output_pos-1):
                #         if outputinterpretation[testindex].get('on_off')==144 and outputinterpretation[testindex].get('time'):
                #             #outputfitref+=[outputinterpretation[testindex]]
                #             fit_score_pos+=[outputinterpretation[testindex].get('score_pos')]
                #             fit_time+=[outputinterpretation[testindex].get('time')]
                #             fit_vel+=[outputinterpretation[testindex].get('vel')]
                #         testindex-=1
                #     print('outputfitting',fit_score_pos,fit_time,fit_vel)
                #     if max(fit_score_pos)-min(fit_score_pos)>0.49:
                #         eq_time=Polynomial.fit(fit_score_pos,fit_time,domain=[-1,1],deg=1)#min(1,len(fit_time)-1))
                #         eq_vel=Polynomial.fit(fit_time,fit_vel,domain=[-1,1],deg=1)#min(1,len(fit_time)-1))
                print('old eq:',eq_time.coef,'vel',eq_vel.coef)
                t_3=time.time_ns()

                # testindex=max(inputscorepositions[latest_input_pos])
                # ref_score_pos=[]
                # ref_time=[]
                # expected_time=[]
                # ref_vel=[]
                # expected_vel=[]
                #while testindex>=0 and (inputinterpretation[testindex].get('score_pos')>latest_input_pos-4):
                for testindex in new_info['input']:
                    if inputinterpretation[testindex].get('on_off')==144:# and inputinterpretation[testindex].get('time'):
                        ref_score_pos,ref_time,ref_vel=[inputinterpretation[testindex].get(k) for k in ['score_pos','time','vel']]
                        expected_time=eq_time(ref_score_pos)
                        expected_vel=eq_vel(ref_time)
                        adjust_time_slope=max(-eq_time.coef[1]+min_dt_dp,(ref_time-expected_time)) #i.e. change the slope from Point of No Return (latest_output_pos) onwards: t_adjust=(pos-PNR)*(ref_time-expected_time), but not make the new slope negative
                        adjust_time=Polynomial([adjust_time_slope*(-latest_output_pos),adjust_time_slope]) #this tries to iron out the asynch after 1 beat
                        adjust_vel=Polynomial([(ref_vel-expected_vel)])
                        eq_time+=adjust_time*metadata.get('time reactivity') #reactivity
                        eq_vel+=adjust_vel*metadata.get('vel reactivity')
                        print('found input',ref_score_pos,ref_time,ref_vel,'time diff:',ref_time-expected_time)
                        print('new eq:',eq_time.coef)
                    #testindex-=1
                #adjust_time=sum([ (ref_time[i]-expected_time[i])*(latest_input_pos-ref_score_pos[i])])
                t_3=time.time_ns()

                new=[]
                index=min(outputscorepositions[latest_output_pos])
                while index<len(outputinterpretation) and outputinterpretation[index]['score_pos']<latest_input_pos+20:
                    if outputinterpretation[index].get('time') is None:
                        note=outputinterpretation[index].copy()
                        note['time']=eq_time(outputinterpretation[index]['score_pos'])
                        note['vel']=eq_vel(note['time'])*metadata.get('output gain')
                        new+=[note]
                    index+=1
                print('conjecture sending',[[note['index'],note['time']] for note in new])
                pipe.send(new)
                t_4=time.time_ns()
                #print(t_2-t_1,t_3-t_2,t_4-t_3)

                

        
if __name__=='__main__':
    def closing():
        pipe_main.send([False,0,0,0,0])
        window.destroy()
    window.protocol('WM_DELETE_WINDOW',closing)

    window.mainloop()

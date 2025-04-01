import numpy 
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import copy
import random
import string
import csv
import score_grapher_v0
import score_sort_v0


entry_fields={
    0:'index',
    1:'on_off',
    2:'note#',
    3:'score_pos'
}


columnweights=[1,1,1,1]
#columnweights=[0,0,0,1, 0,1,0,0, 0,0,0,0, 0,0,0,0, 1,1]
maxlength=[30]*len(entry_fields) #display how many characters
maxlength[10]=6


score=[{} for i in range(10000)]
quantize_per_beat=4 #default






#define generally useful backend functions

def newEvtNum():
    for i in range(len(score)):
        possible=1
        for event in score:
            if event.get('index')==i:
                possible=0
                break
        if possible==1:
            return i

def newSetNum():
    for i in range(len(score)):
        possible=1
        for event in score:
            if event.get('set')==i:
                possible=0
                break
        if possible==1:
            return i

def process_event(EvtNum,LastEnteredValue):
    mustfills=['amount','eur_net','vat%','vat','fx_rate']
    defaults=[0,0,0,0,1]
    for i,column in enumerate(mustfills):
        try:
            score[EvtNum][column]=float(score[EvtNum].get(column))
        except:
            score[EvtNum][column]=defaults[i]
    must_be_int_or_blank=['index','date','MM','set','set position']
    for field in must_be_int_or_blank:
        try:
            if not score[EvtNum].get(field) in ['',None]:
                score[EvtNum][field]=int(score[EvtNum].get(field))
            else:
                score[EvtNum][field]=None
        except:
            pass
        # if not score[EvtNum]=={}:
        #     print('wow thats strange,', EvtNum,'has no index but has score', score[EvtNum])
    if LastEnteredValue=='vat':
        newrate=100*score[EvtNum]['vat']/(score[EvtNum]['amount']-score[EvtNum]['vat'])
        if abs(newrate-score[EvtNum]['vat%'])>0.1: #only if the new entry makes a real difference in vat%. Otherwise it's just flop error
            score[EvtNum]['vat%']=newrate
    else:
        if LastEnteredValue=='eur_net':
            score[EvtNum]['vat']=score[EvtNum]['eur_net']*(score[EvtNum]['vat%']/100)/score[EvtNum]['fx_rate']
            score[EvtNum]['amount']=score[EvtNum]['vat']+(score[EvtNum]['eur_net']/score[EvtNum]['fx_rate'])
        else:
            score[EvtNum]['vat']=score[EvtNum]['amount']*score[EvtNum]['vat%']/(100+score[EvtNum]['vat%'])

    score[EvtNum]['eur_net']=(score[EvtNum]['amount']-score[EvtNum]['vat'])*score[EvtNum]['fx_rate']

def round_to_2(answer):
    return '{:0.2f}'.format(floatOrZero(answer))

    # existingdata=str(existingdata).split('.')
    # decimals='.'
    # try:
    #     decimals+=existingdata[1][0]
    # except:
    #     decimals+='0'
    # try:
    #     decimals+=existingdata[1][1]
    # except:
    #     decimals+='0'
    # existingdata=existingdata[0]+decimals






root = Tk()


general_buttons=Frame(root) 
general_buttons.pack(side='top',fill='x',expand=False)

#define general buttons' functions

oldscore=[copy.deepcopy(score)]
def addUndoPoint():
    global score, oldscore
    oldscore=oldscore+[copy.deepcopy(score)]
    if len(oldscore)>100:
        oldscore.pop(0)

def undo():
    global score, oldscore
    if len(oldscore)>0:
        score=oldscore[-1]
        oldscore.pop(-1)
    calc_table()
    calc_library(library_key,library_startview)
    
def printscore():
    with open(directory+'/outputscore.txt','w',newline='') as scorefile:
         scorefile.write(str(score))
    print('wrote score to txt')

def read_score():
    addUndoPoint()
    global score
    try:
        with open(directory+'/outputscore.txt','r',newline='') as scorefile:
            scorelist=eval(scorefile.readlines()[0])
    except:
        print('nooooo cant read')
    if scorelist[-1][1]=='q':
        quantize_per_beat=scorelist[-1][2]
    else:
        testq=1
        while testq<100:
            qmatched=1
            for event in scorelist:
                if 0.01<(event[3]*testq)%1<0.99: #i.e. is not close to an integer
                    qmatched=0
            if qmatched==1:
                quantize_per_beat=testq
                break
            testq+=1
        print('quantizing to ',quantize_per_beat)
        scorelist=score_sort_v0.sort(quantize_per_beat,scorelist)
    score=[{'index':event[0],'on_off':event[1],'note#':event[2],'score_pos':event[3]} for event in scorelist]
    calc_table()
    calc_library(library_key,library_startview)


def set_dir():
    global directory
    directory=filedialog.askdirectory()
    dirbutton.config(text='directory:'+directory)


def execthebox():
    addUndoPoint()
    content=evaltextbox.get('1.0','end-1c')
    if not evaltextbox.get('1.0','end-1c')=='':
        print('executing', content)
        exec(content)

def eval_anything():
    global evaltextbox,evalbutton, evalboxactive
    if evalboxactive==1:
        evalbutton.destroy()
        evaltextbox.destroy()
        evalboxactive=0
        evaltoggle.config(text='evaluate anything')
        return
    evalbutton=Button(general_buttons,text='go',command=execthebox)
    evalbutton.grid(row=0,column=evaltoggle.grid_info()['column']+1,sticky='n')
    evaltextbox=Text(general_buttons)
    evaltextbox.grid(row=0,column=evaltoggle.grid_info()['column']+2,sticky='n')
    evaltoggle.config(text='hide box')
    evalboxactive=1


#add general buttons

columnindex=0
undobutton = Button(general_buttons, text = 'undo', command=undo)
undobutton.grid(row=0,column=columnindex,sticky='n')
columnindex+=1

readscorebutton = Button(general_buttons, text = 'read score', command=read_score)
readscorebutton.grid(row=0,column=columnindex,sticky='n')
columnindex+=1

Button(general_buttons,text='write score',command=printscore).grid(row=0,column=columnindex,sticky='n')
columnindex+=1

directory=''
dirbutton = Button(general_buttons, text = 'directory:', command=set_dir)
dirbutton.grid(row=0,column=columnindex,sticky='n')
columnindex+=1

evaltoggle=Button(general_buttons, text = 'evaluate anything', command=eval_anything)
evaltoggle.grid(row=0,column=columnindex,sticky='n')
columnindex+=1
evalboxactive=0








current_set_frame=Frame(root)  #misnomer, it actually just contains buttons
current_set_frame.pack(side='top',fill='x',expand=False)


#define set table top buttons' functions

columnindex=0
oldsetnumbers=[]
def back():
    global current_set_number,oldsetnumbers
    if len(oldsetnumbers)>0:
        current_set_number=oldsetnumbers[-1]
        oldsetnumbers.pop(-1)
    calc_table()






def copy_last_table_event(): #copy first entry
    global score,current_set_table
    addUndoPoint()
    try:
        EvtNum=current_set_table[-1].get('index')#to be copied
        added=newEvtNum()
        score[added]=copy.deepcopy(score[EvtNum])
        score[added]['index']=added
        process_event(added,'type')
        calc_table()
    except:
        pass


def add_to_new_set():
    global score,current_set_table,current_set_number,oldsetnumbers
    addUndoPoint()
    added=newEvtNum()
    score[added]['index']=added
    process_event(added,'type')
    oldsetnumbers+=[current_set_number]
    current_set_number=added
    calc_table()
    calc_library(library_key,library_startview)


#add set table top buttons

backbutton = Button(current_set_frame, text = 'back', command=back)
backbutton.grid(row=1,column=columnindex)
columnindex+=1


copy_button = Button(current_set_frame, text = 'copy last row', command=copy_last_table_event)
copy_button.grid(row=1,column=columnindex)
columnindex+=1

new_button = Button(current_set_frame, text = 'new set', command=add_to_new_set)
new_button.grid(row=1,column=columnindex)
columnindex+=1


set_sum_label=Label(current_set_frame,text='set table sum amount')
set_sum_label.grid(row=1,column=columnindex)
columnindex+=1






set_rows_frame=Frame(root)
set_rows_frame.pack(side='top',fill='x',expand=False)#(row=1,column=0)

#creating table elements

for x in range(2):
    Label(set_rows_frame, borderwidth=1, relief='solid', text='x').grid(row=0,column=x,sticky='news')
for x in range(0,len(entry_fields)):
    Label(set_rows_frame, borderwidth=1, relief='solid', text=str(entry_fields[x])).grid(row=0,column=x+2,sticky='news')

current_set_table=[]
table_rows=0
cell=[Entry(set_rows_frame,width=1,bd=0,relief='flat') for i in range(10000)]
deletebutton=[Button(set_rows_frame,text='o') for i in range(100)]
for x in range(0,len(entry_fields)+2):
    set_rows_frame.grid_columnconfigure(x,weight=([0,0]+columnweights[:])[x])



#defining necessary functions for set table

def focus_down(event,x,y):
    cell[100*(min(len(current_set_table)-1,y+1))+x].focus_set()
#    cell[100*(min(len(current_set_table)-1,y+1))+x].selection_range(0,END)
def focus_up(event,x,y):
    cell[max(0,100*(y-1))+x].focus_set()
#    cell[max(0,100*(y-1))+x].selection_range(0,END)


def addRow(): #these are placing the GUI cells, not changing any score
    global table_rows
    y=table_rows
#    print('table currently has', table_rows)
    deletebutton[y]=Button(set_rows_frame, width=1,height=1,text = 'X',padx=0,pady=0, command=lambda y=y:delete_from_set(y))
    deletebutton[y].grid(row=y+1,column=0)

    for x in range(0,len(entry_fields)):
        cell[100*y+x]=Entry(set_rows_frame,width=1,bd=0,relief='flat')
        cell[100*y+x].grid(row=y+1,column=x+2, sticky='nsew')
        cell[100*y+x].bind('<Down>',lambda event,x=x,y=y:focus_down(event,x,y))
        cell[100*y+x].bind('<Up>',lambda event,x=x,y=y:focus_up(event,x,y))        
        cell[100*y+x].bind('<FocusIn>',lambda event,x=x,y=y:cell[100*y+x].selection_range(0,END))        
        cell[100*y+x].bind('<FocusOut>',lambda event,x=x,y=y:update_values(event,x,y))        
    table_rows+=1

def removeRow():
    global table_rows
    if table_rows>0:
        lastRowY=table_rows-1
        deletebutton[lastRowY].destroy()
        for x in range(len(entry_fields)):
            cell[100*lastRowY+x].destroy()
        table_rows-=1


def calc_table():
    global current_set_table, current_set_number,score,set_rows_frame,cell,table_rows
    current_set_table=[score[current_set_number]]

    candidates=[]
    for event in score:
        if event.get('note#')==current_set_table[0].get('note#'):
            candidates+=[event]
            
    noteon=0
    for event in candidates:
        if event['on_off']==144:
                noteon=1
        if event['on_off']==128:
                noteon=0
        if event['index']==current_set_number and score[current_set_number]['on_off']==128 and noteon==1:
            current_set_table+=[lastevent]
            break
        if event['index']>current_set_number and score[current_set_number]['on_off']==144 and noteon==0:
            current_set_table+=[event]
            break
        lastevent=event

    candidates.sort(key=lambda x: abs( float(x.get('score_pos'))-float(current_set_table[0].get('score_pos')) ) )
    for event in candidates:
        if [event.get('on_off'),current_set_table[0].get('on_off')]==[144,128] and float(x.get('score_pos'))-float(current_set_table[0].get('score_pos'))<=0:

    current_set_table.sort(key=lambda row: row.get('on_off'))
    format_table()

def format_table():
    global current_set_table, current_set_number,score,set_rows_frame,cell,table_rows
    while len(current_set_table)>table_rows:
        addRow()
    while len(current_set_table)<table_rows:
        removeRow()
    update_table()

def update_table(): #if no change to the structure of the table, can call starting here without calc_table and format_table
    global cell
    score_sort_v0.sort(quantize_per_beat,score)
    for y,row in enumerate(current_set_table):
        for x in range(0,len(entry_fields)):
            try:
                existingdata=''
                existingdata=row.get(entry_fields[x])
                cell[100*y+x].delete(0,END)
                cell[100*y+x].insert(0,existingdata)
            except:
                pass


def update_values(event,x,y):
    global score, current_set_table
    EvtNum=current_set_table[y].get('index')
    newscore=cell[100*y+x].get()
    if not score[EvtNum].get(entry_fields[x])==newscore:
        addUndoPoint()
        score[EvtNum][entry_fields[x]]=newscore
        process_event(EvtNum,entry_fields[x])
        current_set_table[y]=score[EvtNum]
        update_table()


#defining the functions called by each of set table rows' buttons

def delete_from_set(y):
    global score
    addUndoPoint()
    EvtNum=current_set_table[y].get('index')
    score[EvtNum].pop('set')
    calc_table()















library_rows_frame=Frame(root)
library_rows_frame.pack(side='bottom',fill='x',expand=False)



#define library top buttons' functions
def startview0():
    global library_startview
    library_startview=0
    draw_library()

def startviewminus():
    global library_startview
    library_startview=max(0,library_startview-20)
    draw_library()

def startviewplus():
    global library_startview
    library_startview+=20
    draw_library()

def startviewmax():
    global library_startview
    library_startview=max(0,len(library_table)-20)
    draw_library()

def refreshlibrary():
    calc_library(library_key,library_startview)

def identifysets():
    global score
    criteria=['category','amount','r_country']
    addUndoPoint()
    identified=0
    for row in score:
        if row.get('index') is None:
            break
        possibilities=[]
        if not isinstance(row.get('set'),int): #if it's already in a set, then don't do anything
            for compare_row in score:
                if compare_row.get('index') is None:
                    break
                #print(row.get('index'),compare_row.get('index'))
                if row.get('type')=='b' and compare_row.get('type')=='d' and not isinstance(compare_row.get('set'),int):
                    match=1
                    for test in criteria:
                        if not row.get(test)==compare_row.get(test) and not (row.get(test) in ['',None] or compare_row.get(test) in ['',None]): 
                            match=0
                            #print(test,'failed')
                            break
                        # if not row.get('date') is None and not compare_row.get('date') is None and abs(row.get('date')-compare_row.get('date'))>100:
                        #     match=0
                        #     break
                    if match==1:
                        possibilities+=[compare_row.get('index')]
            #now sort the possibilities by increasing date distance
            possibilities.sort(key=lambda EvtNum:( (score[EvtNum].get('date') is None or row.get('date') is None), abs(  floatOrZero(row.get('date')) - floatOrZero(score[EvtNum].get('date'))  ) ))
            #print(possibilities)
            if len(possibilities)>0:
                setnumber=newSetNum()
                row['set']=setnumber
                score[possibilities[0]]['set']=setnumber
                row['set position']=0
                score[possibilities[0]]['set position']=1
                print('put together',row['index'],score[possibilities[0]]['index'],' in set ',setnumber,' dates',str(row.get('date')),str(score[possibilities[0]].get('date')))
                identified+=1
    print('identified',identified,'sets')
    calc_table()
    calc_library(library_key,library_startview)

def hue(color): #str of form '#ffffff'
    if color in ['#ffffff','#eeeeee']:
        return 5 #white (not in a set) and blue (not in a double-sided set) treated the same
    else:
        return max(1,3,5,key=color.__getitem__) #returns 1 if red, 3 if green, 5 if blue

def sort_by_set():
    global library_table
    #calc_library(['set position','set'],library_startview)
    library_table.sort(key=lambda row: [0,5,1,3].index(hue(rowcolor[row.get('index')])))
    draw_library()

def checkeventfers():
    global score
    addUndoPoint()
    identified=0
    for i,row in enumerate(score):
        if row.get('index') is None or row.get('date') is None:
            break
        if row.get('category')=='eventfer':
            for compare_row in score[i+1:]:
                if compare_row.get('index') is None or compare_row.get('date') is None:
                    break
                if abs(row.get('date')-compare_row.get('date'))<10 and row.get('amount')==-compare_row.get('amount') and row.get('bank')[-3:] in compare_row.get('name'):
                    if not isinstance(row.get('set'),int) and not isinstance(compare_row.get('set'),int):
                        setnumber=newSetNum()
                        row['set']=setnumber
                        compare_row['set']=setnumber
                        row['set position']=0
                        compare_row['set position']=1
                        print('put together',row['index'],compare_row['index'],' in set# ',setnumber)
                        identified+=1
                        break
    print('identified',identified,'eventfer pairs')
    calc_table()
    calc_library(library_key,library_startview)


def update_fx():
    global score
    addUndoPoint()
    readin=[]
    #expecting 1st row to be curr names, 1st column to be YYYY-MM-DD dates, starting with most recent at top
    with open(directory+'/fx.csv', 'r',newline='') as csvfile:
        sreader = csv.reader(csvfile)
        for row in sreader:
            readin+=[row]
    for event in score:
        for i in range(len(readin[0])): #how many currencies are in the chart
            if event.get('curr')==readin[0][i]:
                print(event.get('index'),event['curr'])
                for row in readin: #find the closest date
                    currdate=''.join(str(row[0]).split('-'))
                    if event.get('date') in ['',None]:
                        print('no date for index',event.get('index'))
                        break
                    if str(20240000+event.get('date'))>currdate:
                        event['fx_rate']=round(1/float(row[i]),5)
                        process_event(event.get('index'),'fx_rate')
                        print('  2024',event.get('date'),'taking',currdate,row[i])
                        break
    calc_table()
    calc_library(library_key,library_startview)

def custom_library_table(dicts):
    global library_table
    library_table=[]
    for row in score:
        if not row.get('index')==None:
            for dict in dicts:
                putintable=1
                for field in dict:
                    if isinstance(dict[field],list):
                        wantedvalues=dict[field]
                    else:
                        wantedvalues=[dict[field]]
                    if not row.get(field) in wantedvalues:
                        putintable=0
                        # print(row,'failed',field)
                        break
                if putintable==1:
                    library_table+=[row]
                    break
    for var in option_var:
        var.set('all')
    sort_library([])
    
def search(match): #search current table
    global library_table
    library_table.sort(key=lambda event:(not match in str(event))) #matches go to the front
    draw_library()

library_nav_frame=Frame(root)
library_nav_frame.pack(side='bottom')
columnindex=0
library_startview_label=Label(library_nav_frame,text='showing ')
library_startview_label.grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='first 20',command=startview0).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='previous 20',command=startviewminus).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='next 20',command=startviewplus).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='last 20',command=startviewmax).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='recalc',command=refreshlibrary).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='identify sets',command=identifysets).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='sort by set',command=sort_by_set).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='check eventfers',command=checkeventfers).grid(row=0,column=columnindex)
columnindex+=1
Button(library_nav_frame,text='update fx',command=update_fx).grid(row=0,column=columnindex)
columnindex+=1



#creating library labels
for x in range(3):
    Label(library_rows_frame, borderwidth=1, relief='solid', text='x').grid(row=0,column=x,sticky='news')
for x in range(0,len(entry_fields)):
    Button(library_rows_frame,text=str(entry_fields[x]),command=lambda key=str(entry_fields[x]): sort_library([key])).grid(row=0,column=x+3,sticky='news')


#creating dropdown menu for each field
def modifiedoptions(stringvar): #need to define it before using
    calc_library(library_key,0)#library_startview)
options=[['all'] for field in entry_fields]
selectedoption=['' for field in entry_fields]
option_var=[StringVar() for field in entry_fields]
optionsmenu=[OptionMenu(library_rows_frame,option_var[i], *options[i],command=modifiedoptions) for i in range(len(entry_fields))]
for i,menu in enumerate(optionsmenu):
    menu.grid(row=1,column=i+3)
    option_var[i].set('all')

#creating library table elements
library_table=[]
lcell=[Label(library_rows_frame,text='',borderwidth=1,relief='solid',background='#ffdddd') for i in range(10000)]
for y in range(20):
    for x in range(0,len(entry_fields)):
        lcell[100*y+x].grid(row=y+2,column=x+3, sticky='nsew')
        lcell[100*y+x].config(anchor='w')
for x in range(len(entry_fields)+3):
    library_rows_frame.grid_columnconfigure(x,weight=([0,0,0]+columnweights[0:])[x])

addToCurrentSetbutton=[Button(library_rows_frame,text='o') for i in range(100)]
deleteEvtbutton=[Button(library_rows_frame,text='o') for i in range(100)]
#addToNewSetbutton=[Button(library_rows_frame,text='o') for i in range(100)]
showSetbutton=[Button(library_rows_frame,text='o') for i in range(100)]


#bottom row of library table is a sum
library_sum_label=Label(library_rows_frame,text='library table sum')
library_sum_label.grid(row=22,column=0,columnspan=10)
summable_fields={'amount':None,'vat':None,'eur_net':None}
for field in summable_fields:
    summable_fields[field]=Label(library_rows_frame,text='w')
    for i in entry_fields:
        if entry_fields[i]==field:
            summable_fields[field].grid(row=22,column=i+3)

#define necessary functions for library
rowcolor=['#ffffff']*len(score)

def floatOrZero(n): #for sorting
    try:
        a=float(n)
    except:
        a=0
    return a

def kill_singleton(): #get rid of singleton sets
    global score
    set_population={}
    for row in score: 
        if not row.get('set') is None:
            setNum=row.get('set')
            if set_population.get(setNum) is None:
                set_population[setNum]=[]
            set_population[setNum]+=[row.get('index')]
    for set in set_population:
        if len(set_population[set])==1 and not set==current_set_number: #if it's a singleton but not currently undergoing editing
            score[set_population[set][0]]['set']=None
            score[set_population[set][0]]['set position']=None
            print('killed singleton set',set)

def calc_library(keys,startview):
    global library_key,library_startview,library_table,rowcolor
    kill_singleton()
    library_table=[]
    for scoreindex,row in enumerate(score):
        if not row.get('index')==None:
            putintable=1
            for i in range(len(entry_fields)):
                field=entry_fields[i]
                if not str(option_var[i].get()) in ['all',str(row.get(field))]: #if the field value isn't what we selected
                    putintable=0
                    # print(row,'failed',field)
                    break
            if putintable==1:
                library_table+=[row]
            balance=float(row.get('amount'))*float(row.get('fx_rate')) #if it's not part of a set with both d and b, then make it blue
            samesetevent=1 #count how many event are added together to calculate balance
            biggestevent=0.01 #because we want discrepancy as a percent of biggest. 
            types=set()
            hasset=0
            if not row.get('set')==None: #if it's in a set, then get all the others in the same set
                hasset=1
                bsum,dsum=0,0
                samesetevent=0
                for event in score:
                    if event.get('set')==row.get('set') and not event.get('amount')==None:
                        value=float(event.get('amount'))*float(event.get('fx_rate'))
                        biggestevent=abs(max(biggestevent,abs(value)))
                        if event.get('type')=='d':
                            dsum+=value
                            types.add('d')
                        else:
                            bsum+=value
                            types.add('b')
                        samesetevent+=1
                balance=dsum-bsum
            if row.get('type')=='d':
                rowcolor[scoreindex]='#ffffff'
            else:
                rowcolor[scoreindex]='#eeeeee' #default. note that it doesn't overwrite for index=None but that doesn't matter because library_table only includes those with index
            if not types=={'d','b'} and hasset==1 and samesetevent>1: #part of a set with only d or only b (if not part of a set or singleton, then white)
                if row.get('type')=='d':
                    rowcolor[scoreindex]='#ddddff'
                else:
                    rowcolor[scoreindex]='#ccccee'
            if abs(balance)<abs(biggestevent*0.05): #even if not part of set, if 0 (like wh placeholder when there is no wh) then green
                if row.get('type')=='d':
                    rowcolor[scoreindex]='#ddffdd'
                else:
                    rowcolor[scoreindex]='#cceecc'
            if types=={'d','b'} and not abs(balance)<abs(biggestevent*0.05): #unbalanced set
                if row.get('type')=='d':
                    rowcolor[scoreindex]='#ffdddd'
                else:
                    rowcolor[scoreindex]='#eecccc'
            if types=={'d','b'} and abs(dsum)+abs(bsum)<abs(biggestevent*0.05): #zero set (like event + its cancellation)
                if row.get('type')=='d':
                    rowcolor[scoreindex]='#eeffdd'
                else:
                    rowcolor[scoreindex]='#ddeecc'
    library_startview=startview
    sort_library(keys)
    update_options()

def sort_library(keys):
    global library_key,library_startview,library_table,options
    #sort by previous key then by newly desired key
    library_key+=keys
    while len(library_key)>5:
        library_key.pop(0)
    print('calculating library',library_key)
    for nkey in ['set']+library_key:
        #print('nkey',nkey)
        if nkey in ['set','set position','index','amount','vat%','vat','eur_net','MM','date']: #these we have to sort like numbers, the other ones like strings
            library_table.sort(key=lambda row: (row.get(nkey)==None or row.get(nkey)=='',floatOrZero(row.get(nkey))))
        else:
            library_table.sort(key=lambda row: (row.get(nkey)==None or row.get(nkey)=='',str(row.get(nkey)).lower()))
    sum_library()
    draw_library()

def sum_library():
    for field in summable_fields:
        library_sum=0
        sumcount=0
        rejects=[]
        for event in library_table:
            if isinstance(event.get(field),float):
                library_sum+=event.get(field)
                sumcount+=1
            else:
                rejects+=[event.get('index')]
        # library_sum=str(library_sum).split('.')
        # decimals='.'
        # try:
        #     decimals+=library_sum[1][0]
        # except:
        #     decimals+='0'
        # try:
        #     decimals+=library_sum[1][1]
        # except:
        #     decimals+='0'
        # library_sum=library_sum[0]+decimals
        summable_fields[field].config(text=str(round_to_2(library_sum)))
    showtext='library table sum from '+str(sumcount)+' events'
    if not rejects==[]:
        showtext+='  ('+str(rejects)+' events without value)'
    library_sum_label.config(text=showtext)

def update_options():
    for i in range(len(entry_fields)):
        field=entry_fields[i] # enumerate doesn't work because it's a dictionary
        options[i]=[]
        for row in score:
            if not row.get(field) in [None,*options[i]]:
                options[i]+=[row.get(field)]
        if field in ['index','amount','vat%','vat','eur_net','MM','date']:
            options[i].sort(key=lambda a: floatOrZero(a))
        else:
            options[i].sort(key=lambda a: str(a).lower())
        options[i]=['all']+options[i]
#        print(options[i])
        optionsmenu[i].destroy()
        optionsmenu[i]=OptionMenu(library_rows_frame,option_var[i], *options[i],command=modifiedoptions)
        optionsmenu[i].grid(row=1,column=i+3)

def draw_library():
    library_startview_label.config(text=''.join(['starting ',str(library_startview)]))#,'-',str(min(library_startview+19,len(library_table)-1))]))
    for y in range(20):#,row in enumerate(library_table[startview:20+startview]):
        addToCurrentSetbutton[y].destroy()
        deleteEvtbutton[y].destroy()
        showSetbutton[y].destroy()

        #show the buttons for each row
        if library_startview+y<len(library_table):
            row=library_table[library_startview+y]
            EvtNum=row.get('index')
            addToCurrentSetbutton[y]=Button(library_rows_frame, width=1,height=1,text = '+',padx=0,pady=0, command=lambda EvtNum=EvtNum:add_to_set(EvtNum))
            addToCurrentSetbutton[y].grid(row=y+2,column=0)
            deleteEvtbutton[y]=Button(library_rows_frame, width=1,height=1,text = 'X',padx=0,pady=0, command=lambda EvtNum=EvtNum:deleteEvt(EvtNum))
            deleteEvtbutton[y].grid(row=y+2,column=1)
            showSetbutton[y]=Button(library_rows_frame, width=1,height=1,text = 'S',padx=0,pady=0, command=lambda EvtNum=EvtNum:show_set(EvtNum))
            showSetbutton[y].grid(row=y+2,column=2)

            for x in range(0,len(entry_fields)):
                lcell[100*y+x].config(text='')
                lcell[100*y+x].config(background=rowcolor[EvtNum])
                existingdata=row.get(entry_fields[x])
                if existingdata is None:
                    existingdata=''
                else:
                    existingdata=str(existingdata)
                lcell[100*y+x].config(text=existingdata[:min(len(existingdata),maxlength[x])])
        else:
            addToCurrentSetbutton[y]=Button(library_rows_frame, width=1,height=1,text = '0',padx=0,pady=0, command=lambda: None)
            addToCurrentSetbutton[y].grid(row=y+2,column=0)
            deleteEvtbutton[y]=Button(library_rows_frame, width=1,height=1,text = '0',padx=0,pady=0, command=lambda: None)
            deleteEvtbutton[y].grid(row=y+2,column=1)
            showSetbutton[y]=Button(library_rows_frame, width=1,height=1,text = '0',padx=0,pady=0, command=lambda: None)
            showSetbutton[y].grid(row=y+2,column=2)
            for x in range(0,len(entry_fields)):
                lcell[100*y+x].config(text='')
                lcell[100*y+x].config(background='#dddddd')


#define the functions called by each library row's buttons

def add_to_set(EvtNum):
    global score
    addUndoPoint()

    if not str(score[EvtNum].get('set'))=='None':
        thisset=score[EvtNum].get('set')
        for row in score:
            if row.get('set')==thisset:
                row['set']=current_set_number
                row['set position']+=100
    else:
        score[EvtNum]['set']=current_set_number
        score[EvtNum]['set position']=100
    calc_table()
    calc_library(library_key,library_startview)

def deleteEvt(EvtNum):
    global score
    addUndoPoint()
    score.pop(EvtNum)
    score+=[{}]
    for i in range(EvtNum,len(score)):
        try:
            #=copy(score[i+1])
            score[i]['index']-=1
        except:
            print('no index any more at score[',i,']')
            break
    calc_table()
    calc_library(library_key,library_startview)

def show_set(EvtNum):
    global score,current_set_number,oldsetnumbers
    if not score[EvtNum].get('set') in ['',None]:
        newset=score[EvtNum].get('set')
    else:
        newset=newSetNum()
        print('create newset',newset)
        score[EvtNum]['set']=newset
        score[EvtNum]['set position']=100
    oldsetnumbers+=[current_set_number]
    current_set_number=newset
    calc_table()







score[0]={
    'category':'fee',
    'amount':3000
}

for i in range(16):
    score[i]={'index': i,'category':'cat'+str(numpy.random.randint(4)),'name':random.choices(string.ascii_lowercase),'amount':numpy.random.randint(1000)}

# score[2]['set']=0
# score[2]['set position']=2
# score[9]['set']=0
# score[9]['set position']=3

for i,event in enumerate(score):
    process_event(i,'date')




current_set_number=0
calc_table()    

library_key=['category']
library_startview=0
calc_library(library_key,library_startview)





def ask_closing():
    if messagebox.askyesno('Quit?'):
        root.destroy()
root.title('Spreadsheet')
#root.protocol('WM_DELETE_WINDOW',ask_closing)
root.mainloop()
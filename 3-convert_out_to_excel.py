import pandas as pd
import os
import re

######################################## Inputs  ########################################
path = r'' #same path informed in script 1
out = ''
#########################################################################################

if out == '':
    out = os.path.join(path,'Result.xlsx')

df = pd.DataFrame()

Ins = []
X = []
Y = []
Z = []
TT = []
CY = []
t0 = 0

for i in os.listdir(path):
    if i.endswith('.out'):
        file = open(os.path.join(path,i))
        lines = file.read()#file.readlines()
        lines = lines.split('\n')
        x=''
        y=''
        ins=''
        cy = 0
        r = i.rfind('.')
        for a in range(r):
            if i[a].isnumeric():
                ins+=i[a]
        Ins.append(ins)

        while '' in lines:
            lines.remove('')
        
        for m in lines:
            if m.startswith('_total_solve_time'):
                s = m.split('=')[1]
                s = re.sub(' +', '', s)
                tt = float((s.replace(' ','')))
            elif m.startswith('z'):
                s = m.split('=')[1]
                s = re.sub(' +', '', s)
                z = int((s.replace(' ','')))
            elif m[0].isnumeric():
                s = re.sub(' +', ' ', m)
                s = s.split(' ')
                if int(s[1])==1:
                    x+=str(s[0])+','
                if int(s[2])==1:
                    y+=str(s[0])+','
                    cy+=1
        x = x[0:-1]
        y = y[0:-1]
        
        CY.append(cy)
        X.append(x)
        Y.append(y)
        Z.append(z)
        TT.append(tt)



n = max([len(i) for i in Ins])
def cvt_str(st):
    global n
    while len(st)<n:
        st = '0'+st
    return st

Ins = list(map(cvt_str,Ins))

df['Instancia']=Ins
df['X']=X
df['Y']=Y
df['Count_Y']=CY
df['Z']=Z
df['TT']=TT
df.sort_values("Instancia",inplace=True)
df.set_index("Instancia",drop=True,inplace=True)

T = [df["TT"][df.index[i+1]]-df["TT"][df.index[i]] for i in range(len(df)) if i+1<len(df)]
T.insert(0,df["TT"][df.index[0]])
df['T']=T

df.to_excel(out)

import sys
import pandas as pd
import math


filename = sys.argv[1]
weights = sys.argv[2]
impacts = sys.argv[3]

try:
    if(len(sys.argv) != 5):
        print('ERROR!!... Incorrect Number of Arguments')
        sys.exit(1)
    df=pd.read_csv(sys.argv[1])

except IOError as e:
    print('ERROR!!...Input file not found')
    sys.exit(1)


wts = sys.argv[2]
imp = sys.argv[3]
output_file = sys.argv[4]

try:
    weights = list(map(float, wts.split(",")))
    impacts = list(map(str, imp.split(",")))

except:
    print("ERROR!!Weights and impacts must be separated by comma")
    sys.exit(1)

for i in impacts:
    if i not in ('+', '-'):
        print("Invalid Impacts - Impacts must be + or -")
        sys.exit(1)

if(len(df.columns) < 3):
	raise Exception("ERROR!!Columns are less than 3")

df=df.drop(['Fund Name'], axis = 1)

if(len(weights)<len(df.columns)):
	raise Exception("ERROR!!weights are less in number!!")


if(len(impacts)<len(df.columns)):
   raise Exception("ERROR!!Impacts are less in number!!")

catCols = [col for col in df.columns if df[col].dtype=="O"]
if(len(catCols) != 0):
    print("Categorical values not allowed in columns")
    sys.exit(1)


s = sum(weights)
weights[:] = [x/s for x in weights]


i = 0


for column in df.columns:
    #sum of squares
	sq = df[column].pow(2).sum()

    #square root 
	sq = math.sqrt(sq)
	df[column] = df[column]*weights[i]/sq
    
	i= i + 1


#now we got weighted normalized decision matrix
#extract ideal best and ideal worst for every column

ideal_best=[]
ideal_worst=[]
i=0
for column in df.columns:
    if(impacts[i]=='+'):
        ideal_best.append(df[column].max())
        ideal_worst.append(df[column].min())
    else:
        ideal_best.append(df[column].min())
        ideal_worst.append(df[column].max())

    i+=1

row,column = df.shape   

plus=0
minus=0
sum_all=[]
for x in range(row):
    plus=0
    minus=0
    for y in range(column):
        plus+=(df.iloc[x][y]-ideal_best[y])**2
        minus+=(df.iloc[x][y]-ideal_worst[y])**2
    
    s_minus = math.sqrt(minus)    
    s_plus = math.sqrt(plus) 
    score=s_minus/(s_plus+s_minus)
    sum_all.append(score)


sum_all = pd.DataFrame(sum_all)

df1 = pd.read_csv(sys.argv[1])
df1.insert(column+1,"Topsis Score", sum_all)

sum_all = sum_all.rank(method='first',ascending=False)
sum_all
df1.insert(column+2,"Rank",sum_all,allow_duplicates=False)
df1['Rank'] = df1['Rank'].astype(int)

print(df1)

df1.to_csv(output_file, index=False)

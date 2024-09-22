# please can you give me a list of the number and its corresponding co-ordnate, 
# for example 1,2 - 500000 and 1,3 - 250000
# 1000000	100000	10000	1000
# 500000	50000	5000	500
# 250000	25000	2500	250
# 125000	12500	1250	125
# 62500	6250	625	63
# 31250	3125	313	31
# 15625	1563	156	16
# 7813	781	78	8

rows = open('Data.txt','r').readlines()

outlist = {}
for i in range(len(rows)):
    line = rows[i].strip()
    cols = line.split("\t")
    print(cols)
    for x in range(len(cols)):
        outlist[str(x+1)+","+str(i+1)] =  int(cols[x])

sortedout = sorted(outlist.items() , key=lambda x: x[1])
sortedout.reverse()
print(sortedout)
for item in sortedout:
    print (item[0])
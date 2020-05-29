import datetime
import re

# first let's deal with making a list of dates on the left, and on eht eifght
##These will be mutable
string_example = "12:12,14:01,false,,true,,true,,true,,true12:12,12:13,false00:12,00:44,false,"
startDate = datetime.date(2020, 6, 1)
eneDate = datetime.date(2020, 7, 1)
def runString(txt):
    txt = txt[:-1]
    ans = txt.split('true')
    #print(ans)
    for i in range(len(ans)):
        if ',,' in ans[i]:
            ans[i] = ans[i][:-2]
            #print(ans[i])
            ans[i] += ',true'
    for i in range(len(ans)):
        ans[i] = ans[i].split('false')
    #print(ans)
    answ = ""
    ans = ans[:-1]
    for i in ans:
        for j in i:
            answ += j
            answ += " "

    answ = answ.split(" ")
    sun = answ[:-1]
    print(sun)



runString(string_example)

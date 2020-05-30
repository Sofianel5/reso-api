import datetime

# first let's deal with making a list of dates on the left, and on eht eifght
##These will be mutable
string_example = "12:10,12:20,false,,true,,true,,true,,true,,true,,true,"
startDate = datetime.date(2020, 6, 1)
endDate = datetime.date(2020, 7, 1)
def runStringDays(txt):
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
    #print (ans)
    for i in ans:
        for j in i:
            answ += j
            answ += " "

    answ = answ.split(" ")
    #print(answ)
    hours = [0,0,0,0,0,0,0]
    for i in range(7):
        if (i == 6):
            hours[0] = answ[i]
        else:
            hours[i + 1] = answ[i]
    ##Ok now lets clean it up
    for i in range(7):
        if (hours[i] == ',true'):
            hours[i] = "true"
    #print(hours)
    return hours



runStringDays(string_example)

hoho = "2020-05-30,true14:55,14:59,Delete,Add Row,Submit,"

def runStringH(txt):
    #let's get rid of add and Submit
    dates = {}
    txt = txt[:-16]
    #print(txt)
    ans = txt.split('Delete')
    ans = ans[:-1]
    for i in range(len(ans)):
        if 'true' in ans[i]:
            date = ans[i].split(',true')[0]
            if date[0] == ',':
                date = date[1:]
            dates[date] = "true"
        else:
            date = ans[i].split(',false')[0]
            if date[0] == ',':
                date = date[1:]
            time = ans[i].split(',false')[1]
            dates[date] = time
    print(dates)
    return (dates)




#runStringH(hoho)


def generateJSON(s1, s2 = ""):
    ans = ""
    date = startDate
    reg = runStringDays(s1)
    h = {}
    if s2 != "":
        h = runStringH(s2)
    #print(h)
    while(date != endDate):
        if reg[date.weekday()] != 'true':
            ans += str(date)
            ans += ", "
            ans += reg[date.weekday()]
            ans += "\n"
        date = date + datetime.timedelta(1)
        #print(date)
    #ok now lets deal with hollidats
    ans = ans.split(",\n")
    #print(h)
    g = len(ans)
    i = 0
    while(i < g):
        #print(i)
        try:
            #print(ans[i])
            a = ans[i].split(', ')
            #print(a[0])
            if(a[0] in h):
                if (h[a[0]] == 'true'):
                    ans.pop(i)
                    i -=1
                else:
                    ans[i] = ans[i][:-11]
                    ans[i] += h[a[0]]


        except IndexError:
            1 + 1
        i +=1
    ans = ans[:-1]
    print(ans)
    ##ok lets json this
    answer = "{\n"
    for i in ans:
        a = i.split(', ')
        answer += a[0]
        answer += " :'"
        answer += a[1][:-1]
        answer += "',\n"
    print (answer+ "}")

    return answer



#generateJSON(string_example, hoho)




#def generateJSON(s1, s2=""):
    #string ans = ""
    #date = startDate
    #while (date < endDate):
        #date.weekday()

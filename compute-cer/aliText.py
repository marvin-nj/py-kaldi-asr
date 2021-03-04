# to union multi ASR system result, according to words frequency and confidence
#at 2021.01.15, by wangmanhong
#scores=a*C(w)+(1-a)*N(w)/N
#ony frequency part is ok. 2021.01.15

import sys
from datetime import datetime

def minDistance(word1, word2) -> int:
    if len(word1) == 0:
        return len(word2)
    elif len(word2) == 0:
        return len(word1)
    M = len(word1)
    N = len(word2)
    output = [[0] * (N + 1) for _ in range(M + 1)]
    for i in range(M + 1):
        for j in range(N + 1):
            if i == 0 and j == 0:
                output[i][j] = 0
            elif i == 0 and j != 0:
                output[i][j] = j
            elif i != 0 and j == 0:
                output[i][j] = i
            elif word1[i - 1] == word2[j - 1]:
                output[i][j] = output[i - 1][j - 1]
            else:
                output[i][j] = min(output[i - 1][j - 1] + 1, output[i - 1][j] + 1, output[i][j - 1] + 1)
    return output

def backtrackingPath(word1,word2):
    dp = minDistance(word1,word2)
    m = len(dp)-1
    n = len(dp[0])-1
    operation = []
    spokenstr = []
    writtenstr = []
    out1=[]
    out2=[]
    while n>=0 or m>=0:
        if n and dp[m][n-1]+1 == dp[m][n]:
            #print("insert %c\n" %(word2[n-1]))
            spokenstr.append("insert")
            writtenstr.append(word2[n-1])
            operation.append("NULLREF:"+word2[n-1])
            out1.append(symbol)
            out2.append(word2[n-1])
            n -= 1
            continue
        if m and dp[m-1][n]+1 == dp[m][n]:
            #print("delete %c\n" %(word1[m-1]))
            spokenstr.append(word1[m-1])
            writtenstr.append("delete")
            operation.append(word1[m-1]+":NULLHYP")
            out1.append(word1[m-1])
            out2.append(symbol)
            m -= 1
            continue
        if dp[m-1][n-1]+1 == dp[m][n]:
            #print("replace %c %c\n" %(word1[m-1],word2[n-1]))
            spokenstr.append(word1[m - 1])
            writtenstr.append(word2[n-1])
            operation.append(word1[m - 1] + ":"+word2[n-1])
            out1.append(word1[m-1])
            out2.append(word2[n-1])
            n -= 1
            m -= 1
            continue
        if dp[m-1][n-1] == dp[m][n]:
            spokenstr.append(' ')
            writtenstr.append(' ')
            operation.append(word1[m-1])
            out1.append(word1[m-1])
            out2.append(word2[n-1])
        n -= 1
        m -= 1
    spokenstr = spokenstr[::-1]
    writtenstr = writtenstr[::-1]
    operation = operation[::-1]
    return out1[::-1],out2[::-1]

#aligment more than two string form asr 
def aligmentMultiText(text):
    #ali=[[]for _ in range((sum-1)*2)]
    ali=[[]]  # 1 start
    #print(ali)
    sum=len(text)
    
    #step0: only two string
    if ( sum == 2 ) :
        out1,out2=backtrackingPath(text[0],text[1])
        ali.append(out1)
        ali.append(out2)
        return ali

    #step1: firt time compare
    line1=text[0]
    for i in range(1,sum):
        line2=text[i]
        out1,out2=backtrackingPath(line1,line2)
        ali.append(out1) 
        ali.append(out2)
    #print(ali)

    #step2: modify short case
    maxLen=0  
    pos=0
    for i in range(len(ali)): #get the longest aligment
        if (len(ali[i]) > maxLen):
            maxLen=len(ali[i])
            pos=i
    line1=''.join(ali[pos])
    for i in range(1,len(ali)):  
        if( len(ali[i]) < maxLen): #compare with longest aligment 
            line2=''.join(ali[i])
            out1,out2=backtrackingPath(line1,line2)
            ali[i]=out2
    return ali

# union aligmented string 
def aligmentFusion(ali):
    ret=[]
    #print("words counts:")
    for j in range(len(ali[0])):  #get word counts 
        count_map={}
        value=[]
        for i in range(len(ali)):
            value.append(ali[i][j])
        keys=set(value)
        for v in keys:
            count_map.update({v:value.count(v)})
        count_map=sorted(count_map.items(), key = lambda kv:(kv[1], kv[0]),reverse=True)  #sort by words counts
        #print("position",j+1,": ",end="")
        #print(count_map)
        c=count_map[0][0]
        ret.append(c)
    return ret

#scores=a*C(w)+(1-a)N(w)/N
def scores(confidence,frequency):
    pass

#main
def main():
  if( len(sys.argv) < 2 ):
      print("usage: sys.argv[0] input1 input2 ...")
      print("notice: need more than 2 input files")
      sys.exit()
  if( len(sys.argv) >= 2 ):  
      text=[]
      #read file , and move the max length string to first position
      for i in range(1,len(sys.argv)):
          text.append(open(sys.argv[i]).readline().strip().replace(' ',''))
      for i in range(len(text)-1,0,-1):
          if( len(text[i]) > len(text[i-1])):
              tmp=text[i-1]
              text[i-1]=text[i]
              text[i]=tmp
      global symbol
      symbol="*"
      if ( '\u4e00' <= text[0][0] <= '\u9fa5'):
          symbol="**"
      print("asr result:")
      for i in range(len(text)):
          print("asr",i+1,":",text[i])
      print("-------")
      ali=aligmentMultiText(text) 
      ali=list(set(tuple(i) for i in ali[1:]))   #多重列表去重
      print("aligment result: ")
      for x in ali:
          print (x)
      print("-------")
      result=aligmentFusion(ali)
      print("-------")
      print("final reslut:")
      print(result)

if __name__ == '__main__':
    t1=datetime.now()
    main()
    t2=datetime.now()
    print((t2-t1).microseconds)


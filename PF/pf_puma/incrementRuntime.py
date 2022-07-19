import copy
import os
import shutil
import argparse
import sys

def editRunLen(suitename, incrementRun, endRun):

    suitedir=os.path.join(os.path.expanduser('~'),"roses",suitename)

    confFile=suitedir+"/rose-suite.conf"
    oldFile=suitedir+"/rose-suite.conf_old"

    shutil.move(confFile, oldFile)

    

    fout=open(confFile,"w")
    fin=open(oldFile,"r")

    for line in fin:
       if line.startswith("RUNLEN="):
           nextend=doIncrement(line.split("=")[1].split(","), incrementRun.split(","))
           if  atEnd(nextend, endRun.split(",")):
              return 1
           edline="RUNLEN=%s,%s,%s,%s,%s,%s\n" %(nextend[0], nextend[1],nextend[2], nextend[3], nextend[4],nextend[5])
           fout.write(edline) 
       else:
          fout.write(line)
    fin.close()
    fout.close()
    return 0

def doIncrement ( runarray, inarray):
   rundata=list(map(int,runarray))
   indata=list(map(int,inarray))
   newdata=[]
   for ii in range(6):
      newdata.append(indata[ii]+rundata[ii])

   if newdata[5] >59:
       newdata[4]+=1
       newdata[5]-=60
   if newdata[4] >59:
       newdata[3]+=1
       newdata[4]-=60
   if newdata[3] >23:
       newdata[2]+=1
       newdata[3]-=24
   if newdata[2] >29:
       newdata[1]+=1
       newdata[2]-=24
   if newdata[1] >12:
       newdata[0]+=1
       newdata[1]-=12
   print "newdata:"
   print  newdata
   return list(map(str,newdata))

def atEnd ( runarray, endarray):
   rundata=list(map(int,runarray))
   enddata=list(map(int,endarray))
   for ii in range(6):
     if  rundata[ii] < enddata[ii]:
            return False
     elif  rundata[ii] > enddata[ii]:
            return True
   return False
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= "Edit run end in a suite's conf file")
    parser.add_argument("suitename",help="name of suite")
    parser.add_argument("increment_s", help="increment yr,mon,day,h,m,s")
    parser.add_argument("terminate_s", help="terminate yr,mon,day,h,m,s")

    args = parser.parse_args()

    status = editRunLen(args.suitename, args.increment_s, args.terminate_s)

    print "incrementRuntime.py end status %s" %status
    sys.exit(status)







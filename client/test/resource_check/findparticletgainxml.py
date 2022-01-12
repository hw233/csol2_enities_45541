import os
from os.path import getsize
import ResMgr
import operator
path = "D:/AB/csgame/datas/particles"
xmltgas = [] 
filexmls = []
filetgasize = {}
tgainxmls = {}
tganotuse = []


def find(path):
    def deal(path):
        for i in os.listdir(path[19:]):
            pathfile = path + "/" + i
            #print pathfile
            if os.path.isfile(pathfile):
                if "xml" in pathfile.split("/")[-1]:
                    a = pathfile.split("/")[-1]
                    p =  pathfile[19:]
                    sect = ResMgr.openSection(p)
                    for k, v in sect.items():
                        for k1, v1 in v.items():
                            if k1 == "Renderer":
                                for k2, v2 in v1.items():
                                    for k3, v3 in v2.items():
                                        if k3 == "textureName_":
                                            t = v3.asString.split("/")[-1]
                                            #print t
                                            if t not in xmltgas:
                                                xmltgas.append(t)
                                            if [a,t] not in filexmls:
                                                filexmls.append([a, t])
                                            if a not in tgainxmls:
                                                tgainxmls[a] = [t,]
                                            else:
                                                tgainxmls[a].append(t)
            elif os.path.isdir(pathfile):
                print pathfile
                deal(pathfile)
    deal(path)
    f = open("tgasinxml.txt","w")
    f1 = open("tgaandxml.txt", "w")
    f.writelines([line + "\n" for line in xmltgas])
    f1.writelines([line[0] + "   " + line[1] + "\n" for line in filexmls])
    f.close()
    f1.close()
    print "find deal over!!!!!!!!!!!!"
    
def find2(path):
    def deal(path):
        for i in os.listdir(path[19:]):
            pathfile = path + "/" + i
            #print pathfile
            if os.path.isfile(pathfile):
                #if "xml" in pathfile.split("/")[-1]:
                    #filexmls.append(pathfile.split("/")[-1])
                if "tga" in pathfile.split("/")[-1] or "dds" in pathfile.split("/")[-1] or "bmp" in pathfile.split("/")[-1]:
                    filetgasize.update( {pathfile.split("/")[-1]: getsize(pathfile) } )
            elif os.path.isdir(pathfile):
                print pathfile
                deal(pathfile)
    print "find2 deal over!!!!!!!!!!!!"
                
def deallist(l):
    tmp = ""
    for i in l:
        if i is not None:
            tmp = tmp + str(i)
    return tmp

find(path)
find2(path)
#tmp = sorted(filetgasize.iteritems(), key=operator.itemgetter(1), reverse=True) 
for k,v in tgainxmls.items():
    for i in v:
        tmp = 0 
        if i is not None:
            if i in filetgasize.keys():
                tmp = tmp + filetgasize[i]
    tgainxmls[k].insert(0, tmp)
    
for key in filetgasize.keys():
    if key not in xmltgas:
        if key not in tganotuse:
            tganotuse.append(kew)

tmp2 = sorted(tgainxmls.iteritems(), key = lambda d:d[1][0], reverse = True)


f = open("sizeofxmltga.txt","w")
f.writelines([item[0] + "   "  + str(item[1][0]) + "\n" + deallist(item[1][1:]) + "\n" for item in tmp2])
f.close()
f  = open("tganotuse.txt", "w")
f.writelines([i + "\n"  for i in tganotuse])
f.close()
print "all deal over!!!!!!!!!!!!"







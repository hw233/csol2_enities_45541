import os
import csv
filetgas = {}
tgainxml = {}
errortgas = []
f = open("tgafilessize.txt")
for line in f.readlines():
    key = line.split("   ")[0]
    value = int(line.split("   ")[1])
    #print "tgafilessize",value
    if key not in filetgas.keys():
        filetgas.update({key:value})
 

f.close()

f = open("tgaandxml.txt")
for line in f.readlines():
    key = line.split("   ")[0]
    value = line.split("   ")[1]
    value = value[:-4] + "dds"
    #print "tgaandxml",value
    if key not in tgainxml:
        tgainxml[key] = [value,]
    else:
        tgainxml[key].append(value)

f.close()

for key, value in tgainxml.items():
    tmp = 0
    for i in value:
        if "\n" in i:
            i = i.strip("\n")
        #print i
        if i in filetgas.keys():
            tmp = tmp + filetgas[i]
        else:
            if i not in errortgas:
                errortgas.append(i)
    tgainxml[key].insert(0, tmp)

tgainxml = sorted(tgainxml.iteritems(), key = lambda d:d[1][0], reverse = True)


def deallist(l):
    tmp = []
    if l and l[0] and l[1]:
        tmp.append(l[0])
        tmp.append(size(l[1][0]))
        for i in l[1][1:]:  
            tmp.append(str(i))
    return tmp

def size(tgasize):
    a =  int(tgasize)/1024/1024.0
    a = "%.2f" % a
    return float(a)




#f.writelines([item[0] + " "  + str(item[1][0]) + " " + deallist(item[1][1:]) + "\n" for item in tgainxml])
f10 = open("10.csv","wb")
w10 = csv.writer(f10)
w10.writerow(["xmlname","countsize(M)", "includetgafile"])
for item in tgainxml:
    if item[1]:
        if size(item[1][0])> 10.0:
            #print ">10",item[0], size(item[1][0]),type(size(item[1][0]))
            w10.writerow(deallist(item))
f10.close()

f5 = open("5.csv","wb")
w5 = csv.writer(f5)
w5.writerow(["xmlname","countsize(M)", "includetgafile"])

for item in tgainxml:
    if item[1]:
        if size(item[1][0])>5.0 and size(item[1][0])<= 10.0:
            #print ">5",item[0], size(item[1][0])
            w5.writerow(deallist(item))
f5.close()

f1 = open("1.csv","wb")
w1 = csv.writer(f1)
w1.writerow(["xmlname","countsize(M)", "includetgafile"])
for item in tgainxml:
    if item[1]:
        if size(item[1][0])>1.0 and size(item[1][0])<= 5.0:
            #print ">1",item[0], size(item[1][0])
            w1.writerow(deallist(item))
f1.close()

f_5 = open("_5.csv","wb")
w_5 = csv.writer(f_5)
w_5.writerow(["xmlname","countsize(M)", "includetgafile"])
for item in tgainxml:
    if item[1]:
        if size(item[1][0])>0.5 and size(item[1][0])<= 1.0:
            #print ">0.5",item[0], size(item[1][0])
            w_5.writerow(deallist(item))
f_5.close()

fd = open("fd.csv","wb")
wd = csv.writer(fd)
wd.writerow(["xmlname","countsize(M)", "includetgafile"])
for item in tgainxml:
    if item[1]:
        if size(item[1][0])<= 0.5:
            #print "<=0.5",item[0], size(item[1][0])
            wd.writerow(deallist(item))

fd.close()
f = open("errortga.txt","w")
f.writelines([str(i) + "\n" for i in errortgas])
f.close()

"""
w = Workbook()
w10_i = 1
w10_j = 2
w5_i = 1
w5_j = 2
w1_i = 1
w1_j = 2
w_5_i = 1
w_5_j = 2
wd_i = 1
wd_j = 2
w10 = w.add_sheet(u">10M")
w10.write(0,0, u"particlexml")
w10.write(0,1,u"size")
w10.write(0,2,u"tgainclude")
w5 = w.add_sheet(u">5M")
w5.write(0,0, u"particlexml")
w5.write(0,1,u"size")
w5.write(0,2,u"tgainclude")
w1 = w.add_sheet(u">1M")
w1.write(0,0, u"particlexml")
w1.write(0,1,u"size")
w1.write(0,2,u"tgainclude")
w_5 = w.add_sheet(u">0.5M")
w_5.write(0,0, u"particlexml")
w_5.write(0,1,u"size")
w_5.write(0,2,u"tgainclude") 
wd = w.add_sheet(u"<=0.5M")
wd.write(0,0, u"particlexml")
wd.write(0,1,u"size")
wd.write(0,2,u"tgainclude") 
def size(tgasize):
    a =  int(tgasize)/1024/1024.
    a = "%.2f" % a
    return a

def writexml(ws, w_i, w_j, v):
    ws.write(w_i,0,k)
    ws.write(w_i,1,str(size(v[0])))
    for j in v[1:]:
        j = j.strip("\n")
        ws.write(w_i,w_j,unicode(j))
        w_j += 1
    w_i += 1
    w_j = 2   

for item in tgainxml:  #k = item[0], v  = item[1]
    k = item[0]
    v = item[1]
    if v is not None:
        if size(v[0]) > 10 :
            writexml(w10, w10_i, w10_j, v)
            #print  ">10M",w10_i, w10_j, v
        elif size(v[0]) > 5: 
            writexml(w5, w5_i, w5_j, v)
            #print ">5M",w5_i, w5_j, v
        elif size(v[0]) > 1:
            writexml(w1, w1_i, w1_j, v)
            #print ">1M",w1_i, w1_j, v
        elif size(v[0] > 0.5):
            writexml(w_5, w_5_i, w_5_j, v)
            #print ">0.5M",w_5_i, w_5_j, v
        else:
            writexml(wd, wd_i, wd_j, v)
            #print "<=0.5M",wd_i, wd_j, v


w.save("c://sizeofparticlexml.xls")
"""
print "deal over!!!!!!!!!!!"
    


    
 
    

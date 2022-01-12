# -*- coding: gb18030 -*-
#使用时注意修改下面的PATH和PATHRES路径，或者在使用的时候setPATH和setPATHRES修改路径
import os
import csv
import ResMgr

PATH = "D:/love3/datas"
PATHRES = "D:/love3/res"
fileTypes  = []
animationNodes = {}  #{model:[nodes,]} 存储model的animation节点信息
sourceNotExist = {}  #某文件中有引用其它资源，但是资源文件不存在
sourceMapping = {}   #文件引用资源
TextureList = ["dye", "renderSet"]
files = []
TGAANDDDS = []


def addType(type_):
    if type_ not in fileTypes:
        fileTypes.append(type_)


def setPATH(path):
    global PATH
    PATH = path.split("datas")[0] + "datas"

def setPATHRES(path):
    global PATHRES
    PATHRES = path.split("datas")[0] + "res"
    

def fileType(path):
    if os.path.isfile(path):
        return os.path.splitext(path)[1][1:]  #".*"
    else:
        print path ,"is not file!"
    

def dealcallback(path, LeafKey = []):
    type_ = fileType(path)  # xml, model, visual, chunk
    import ResMgr
    if type_ in ["visual","model", "chunk", "xml", "gui"]:
        relativepath = path
        if "/datas/" in path:
            relativepath = path.split("datas/")[1]
        elif "/res/" in path:
            #print "111",relativepath
            relativepath = path.split("res/")[1]
            
        
        sect = ResMgr.openSection(relativepath)
        """
        if relativepath.startswith("avatar"): #处理avatar文件夹
            for k, v in sect.items():
                if k == "animation":
                    animationNode(path, v)
                elif k == "dye":
                    dealAvatarNode(path, v, "Texture")
                elif k == "renderSet":
                    dealAvatarNode(path, v,  "Texture")
        elif relativepath.split("/")[0] in ["creature", "dlwp", "gzawu", "monster", "monster1", "npc", "talisman","mount"]:
            for k, v in sect.items():
                if k == "animation":
                    animationNode(path, v)
                elif k == "renderSet":
                    dealother(path, v, ["Texture",])
        elif relativepath.startswith("universes"):
            for k, v in sect.items():
                dealother(path, v, LeafKey)
        else:
        """
        for k, v in sect.items():
            dealother(path, v, LeafKey)            
            


def dealother(path, value, LeafKey = [] ):
    if len(value.items()) > 0:
        for k, v in value.items():
            if k in LeafKey:
                if v.asString:
                    #if len(v.asString) == 35 and len(v.asString.split(".")) == 4: #对水资源、巡逻路线，镜头引用文件的判定
                        #print "v.asString =",v.asString, "path = ",path
                    filename = v.asString
                    filenamenew = v.asString
                    if filename[-4:] in ['.tga','.bmp','.jpg','.dds',".TGA",".DDS",".JPG",".BMP"]: #处理贴图资源
                        filename = filename[:-4] + ".dds"
                        filenamenew = filename[:-4] + ".tga"
                    
                    if pathExist(path, filename, filenamenew): #or后面的主要是处理水，镜头，巡逻路线的资源文件判定
                        addKV(sourceMapping, path, v.asString)   #保存有效资源的映射
                    else:
                        addKV(sourceNotExist, path, v.asString)
            else:
                dealother(path, v, LeafKey)
        
def pathExist(path, filename, filenamenew):
    #print "filename = ",filename,os.path.isfile(PATHRES + "/" +filename), "filenamenew = ", filenamenew, os.path.isfile(PATHRES + "/" +filenamenew)
    return os.path.isfile(PATH + "/" +filename) or os.path.isfile(PATH + "/" +filenamenew) or fileNameExist(path, filename) or os.path.isfile(PATHRES + "/" +filename) or os.path.isfile(PATHRES + "/" +filenamenew)

def fileNameExist(path, filename):
    if len(filename) == 35 and len(filename.split(".")) == 4:
        filename1 = filename + ".vlo"
        filename2 = filename + ".graph"
        if os.path.isfile(os.path.dirname(path) + "/" + filename1) or os.path.isfile(os.path.dirname(path) + "/" + filename2):
            return True
    elif len(filename.split("/")) > 2 and filename.split("/")[-2] == "animations":
        #print "pathExist", filename,PATH, os.path.isfile(PATH + "/" +filename)
        filename = filename + ".animation"
        if os.path.isfile(PATH + "/" +filename):
            return True
    return False

def dealAvatarNode(path, value, LeafKey):
    if len(value.items()) > 0:
        for k, v in value.items():
            if k in LeafKey:
                if v.asString:
                    filename = v.asString
                    root = ""
                    root1 = ""
                    if filename[-4:] in ['.tga','.bmp','.jpg']:
                        filename = filename[:-4] + ".dds"
                    if v.asString.startswith("maps"):
                        root = path.split("model")[0]
                    if v.asString.startswith("avatar"):
                        root1 = path.split("avatar")[0]
                    if os.path.isfile(root +filename) or os.path.isfile(root1 +filename) or os.path.isfile(PATH + "/" +filename):
                        addKV(sourceMapping, path, v.asString)   #保存有效资源的映射
                    else:
                        print "root =",root, "root1 =", root1, "filename=",filename 
                        addKV(sourceNotExist, path, v.asString)
                return v.asString
            else:
                dealAvatarNode(path, v, LeafKey)
    else:
        return value.asString
        
    

def animationNode(path, value):
    for k, v in value.items():
        if k == "nodes":
            if v.asString and os.path.exists(PATH + v.asString):
                addKV(animationNodes, k, v.asString)

def fileExist(path, sourcepath, type_ = ""):

    if sourcepath:
        root = path.split(sourcepath.split("/")[0])[0]
        if "." in sourcepath:
            tmp = os.path.splitext(sourcepath)
            if tmp[1] in [".tga", ".bmp", ".jpg"]: #有些文件是写的其它格式图片文件
                sourcepath = tmp[0] + ".dds"
                #print "11111", sourcepath
        if not os.path.exists(root + "/" + sourcepath + type_ ):
            if sourcepath:
                addKV(sourceNotExist, path, sourcepath + type_)  #处理无效资源
            return False
        return True
    return False


def addKV(d, key, value):
    if "/datas/" in key:
        key = key.split("datas/")[1]
    elif "/res/" in key:
        key = key.split("res/")[1]
    if value == "/" or value == "guis/" or ".cdata/" in value:
        return 
    if type(d) is dict:
        if key not in d.keys():
            d.update({key:[value,]})
        else:
            if value not in d[key]:
                d[key].append(value)

def dealFileNameType(path, key = None):
    type_ = os.path.splitext(path)[1]
    addType(type_)
    return type_

def dealdir(path, callback = None, key = None):
    #处理F:/csol/datas/***, F:/csol/res/***文件夹
    folder = path
    if "/datas/" in path:
        folder = path.split("datas/")[1]
    elif "/res/" in path:
        folder = path.split("res/")[1]
    for i in os.listdir(folder):
        newpath = path + "/" + i
        if i[0] == ".":  #pass .svn not see file
            continue
        else:
            if os.path.isfile(newpath):  #文件
                if os.path.splitext(newpath)[1] in [".chunk", ".model", ".visual", ".xml", ".visual", ".dds", ".tga", ".bmp", ".jpg", ".gui", ".texanim"]:
                    #print "444",newpath
                    if callback:
                        callback(newpath, key)
            elif os.path.isdir(newpath):  #目录
                print newpath
                dealdir(newpath, callback, key)


def writecsv(d, filename):
    #d = {key:[value,]}
    if not d:
        return
    f = open(filename, "wb")
    w = csv.writer(f)
    w.writerow([filename.split(".")[0],])
    if type(d) == dict:
        for key, value in d.items():
            tmp = []
            tmp.append(key)
            if len(value) > 1:
                tmp.extend(value)
            if len(value) ==1:
                tmp.append(value)
            w.writerow(tmp)
    elif type(d) == list:
        for item in d:
            w.writerow([item,])
    f.close()

def findFileType(path):          
    dealdir(path)
    f = open("fileType.csv","wb")
    w = csv.writer(f)
    w.writerow(["fileType",])
    for i in fileTypes:
        w.writerow([i,])
    f.close()
    


    
def addK(l, k):
    if k not in l:
        l.append(k)

def recordFile(path, LeafKey):
    print os.path.splitext(path)[1][1:], LeafKey
    if os.path.splitext(path)[1][1:] in LeafKey:
        if "datas" in path:
            addK(files, path.split("datas/")[1])
        if "res" in path:
            addK(files, path.split("res/")[1])
        
def findfiles(path, LeafKey):
    dealdir(path, recordFile, LeafKey)
    print "findfiles",files


def dealModelandVisual():
    #处理下面路径的model和visual文件
    #sourceNotExist = {}
    for i in ["avatar", "creature", "dlwp", "gzawu", "monster", "monster1", "npc", "talisman","mount", "weapon","environments"]:
        dealdir(PATH + "/" + i, dealcallback, ["nodes", "Texture"])
        print "deal path:",i, "over!!!!!"
    #print "sourceNotExist =",  sourceNotExist
    print "sourceMapping =", sourceMapping
    writecsv(sourceNotExist, "sourceNotExist.csv")
    print "dealModelandVisual deal over!!!!!!!!!!!"

def dealFolderenvironments():
    #处理environments文件夹
    import ResMgr
    #sourceNotExist = {}
    #dealdir(PATH + "/" + "environments", findfiles, ["visual", "dds"])  #处理目录下的model和visual文件
    path = PATH + "/" + "environments/flora.xml"
    sect = ResMgr.openSection(path.split("datas/")[1])
    for k,v in sect.items():
        dealother(path, v, ["texture","visual"])
        #dealother(path, v, "visual")
    #print "sourceMapping =", sourceMapping
    #print "sourceNotExist =",  sourceNotExist
    print "dealFolderenvironments all over!!!!!!!!!!!"
    
def dealFolderuniverses():
    #处理universes文件夹
    import ResMgr
    #sourceNotExist = {}
    path = PATH + "/" + "universes"
    dealdir(path, dealcallback, ["resource","modelFile","uid","patrolList"]) #模型或特效
    #dealdir(path, dealcallback, "modelFile") #模型或特效
    #dealdir(path, dealcallback, "uid")  #处理水资源 
    #dealdir(path, dealcallback, "patrolList")  #处理巡逻路线
    #for item in ["resource","modelFile","uid","patrolList"]:
        #dealdir(path, dealcallback, item)
    
    #print "sourceMapping =", sourceMapping
    #print "sourceNotExist =",  sourceNotExist
    #print "dealFolderuniverses all over!!!!!!!!!!!"

def dealFolderparticles():
    #处理particels文件夹
    path = PATH + "/" + "particles"
    dealdir(path, dealcallback, ["textureName_",])
    #print "sourceMapping =", sourceMapping
    #print "sourceNotExist =",  sourceNotExist   
    #writecsv(sourceNotExist,"particlessourceNotExist.csv") 
    print "dealFolderparticles all over!!!!!!!!!!!"

def dealFolderGUI():
    #处理guis和guis_v2文件夹
    path = PATHRES + "/" + "guis"
    path1 = PATHRES + "/" + "guis_v2"
    dealdir(path, dealcallback, ["textureName","texture",])
    dealdir(path1, dealcallback, ["textureName","texture",])
    #writecsv(sourceNotExist,"guisourceNotExist.csv") 
    #print "sourceMapping =", sourceMapping
    #print "sourceNotExist =",  sourceNotExist
    print "dealFolderGUI all over!!!!!!!!!!!"
    

def sourceCheck(pathDatas, pathRes):
    print "love3 or csol datas path: f:/csol/datas"
    print "love3 or csol datas path: f:/csol/res"
    global PATHRES
    global PATH
    PATH = pathDatas
    PATHRES = pathRes
    dealModelandVisual()
    dealFolderenvironments()
    dealFolderuniverses()
    dealFolderparticles()
    dealFolderGUI()
    writecsv(sourceNotExist,"sourceNotExist.csv") 
    print "sourceCheck deal over!!!!!!!!!!!"


#----------------------------------------------------------------------------------------------------
#新版
#-------------------------------------------------------------------------------------------------------  
def checkSource(path, DATASPATH):
    #path:要处理的文件夹, 如 F:/csol/datas/***,  或者F:/csol/res/**
    #DATASPATH：datas 或res路径
    #注意，242版本没有animation文件，已经打包了，只有AB的才有,所以下面的搜索如果是搜索242的，就要把nodes节点去掉
    global PATH
    PATH = DATASPATH
    checkDir(path, callback, [ "Texture","textureName","resource","modelFile","uid","patrolList","texture","visual","textureName_"])
    #writecsv(sourceNotExist,"sourceNotExist.csv") 
    print "checkSource deal over !!!!!!!!"
    
    
def checkDir(path, callback = None, LeafKey = None):
    relativepath = path
    if "datas/" in relativepath:
        relativepath = relativepath.split("datas/")[1]
    elif "res/" in relativepath:
        relativepath = relativepath.split("res/")[1]
    for i in os.listdir(relativepath):
        newpath = path + "/" + i
        if i[0] == ".":  #pass .svn not see file
            continue
        else:
            if os.path.isfile(newpath):  #文件
                if os.path.splitext(newpath)[1] in [".chunk", ".model", ".visual", ".xml",  ".gui", ".texanim"]:
                    #print "444",newpath
                    if callback:
                        callback(newpath, LeafKey)
            elif os.path.isdir(newpath):  #目录
                print newpath
                checkDir(newpath, callback, LeafKey)    


def callback(path, LeafKey = []):
    type_ = fileType(path)  # xml, model, visual, chunk
    import ResMgr
    if type_ in ["visual","model", "chunk", "xml", "gui"]:
        relativepath = path
        if "/datas/" in path:
            relativepath = path.split("datas/")[1]
        elif "/res/" in path:
            #print "111",relativepath
            relativepath = path.split("res/")[1]

        sect = ResMgr.openSection(relativepath)
        if not sect:
            print "relativepath",relativepath
            return 
        for k, v in sect.items():
            checkKey(path, v, LeafKey)  
            
def checkKey(path, value, LeafKey = [] ):
    if len(value.items()) > 0:
        for k, v in value.items():
            if k in LeafKey:
                if v.asString:
                    #if len(v.asString) == 35 and len(v.asString.split(".")) == 4: #对水资源、巡逻路线，镜头引用文件的判定
                        #print "v.asString =",v.asString, "path = ",path
                    filename = v.asString
                    filenamenew = v.asString
                    if filename[-4:] in ['.tga','.bmp','.jpg','.dds',".TGA",".DDS",".JPG",".BMP"]: #处理贴图资源
                        filename = filename[:-4] + ".dds"
                        filenamenew = filename[:-4] + ".tga"
                    
                    if pathExist(path, filename, filenamenew) and samePath(path, filename): #or后面的主要是处理水，镜头，巡逻路线的资源文件判定
                        addKV(sourceMapping, path, v.asString)   #保存有效资源的映射
                    else:
                        addKV(sourceNotExist, path, v.asString)
            else:
                dealother(path, v, LeafKey)
                
                
def samePath(path, filename):
    relativepath = path
    if "datas/" in relativepath:
        relativepath = relativepath.split("datas/")[1]
    elif "res/" in relativepath:
        relativepath = relativepath.split("res/")[1]
        
    relativefile = filename
    if "datas/" in relativepath:
        relativefile = relativefile.split("datas/")[1]
    elif "res/" in relativepath:
        relativefile = relativefile.split("res/")[1]    
        
    if (relativepath.split("/")[0] + "/") in relativefile: #一般的
        return True
        
    elif (relativepath.split("/")[1] + "/") == (relativepath.split("/")[1] + "/"):
        return True
        
    return False

def checkGUI(resPath):
    #处理guis和guis_v2文件夹
    global PATHRES
    PATHRES = resPath
    path = PATHRES + "/" + "guis"
    path1 = PATHRES + "/" + "guis_v2"
    dealdir(path, dealcallback, ["textureName","texture",])
    dealdir(path1, dealcallback, ["textureName","texture",])
    #writecsv(sourceNotExist,"guisourceNotExist.csv") 
    #print "sourceMapping =", sourceMapping
    #print "sourceNotExist =",  sourceNotExist
    print "dealFolderGUI all over!!!!!!!!!!!"

"""
for i in ["avatar", "creature", "dlwp", "gzawu", "monster", "monster1", "npc", "talisman","mount", "weapon","environments", "particles","universes","space"]:
    checkSource("D:/AB/csgame/datas/"+i, "D:/AB/csgame/datas")
    print "D:/AB/csgame/datas/"+i + "deal over !!!!!!!!!!"
checkGUI("D:/love3/res")
writecsv(sourceNotExist,"sourceNotExist.csv") 
print "checkGUI deal over!!!!!!!!!!!!"
"""

def findUseFileInUniverses(path = "entities/locale_default/config/server/gameObject/space"):
    #path  = "entities/locale_default/config/server/gameObject/space"
    usedDirs = []  #配置中使用的文件夹
    existDirs = [] #目录下的文件夹
    noUsedDirs= [] #没有用到的文件夹
    notExistDirs = []  #引用到了不存在的文件夹
    for i in os.listdir(path):
        newpath = path + "/" + i
        if newpath[-3:] == "xml":
            sect = ResMgr.openSection(newpath)
            for k,v in sect.items():
                if k == "dirMapping":
                    addK(usedDirs, v.asString)
    
    for i in os.listdir("universes"):
        newpath = "universes" + "/" + i
        if os.path.isdir(PATH + "/" + newpath):
            addK(existDirs, newpath)
    
    for i in usedDirs:
        if i not in existDirs:
            addK(notExistDirs, i)
    
    for i in existDirs:
        if i not in usedDirs:
            addK(noUsedDirs, i)
    
    #print "usedDirs =",usedDirs
    #print "existDirs =",existDirs       
    #print "noUsedDirs =",noUsedDirs
    #print "notExistDirs =", notExistDirs
    writecsv(noUsedDirs, "noUsedDirs.csv")
    if notExistDirs:
        writecsv(notExistDirs, "notExistDirs.csv")
    print "findUseFileInUniverses deal over!!!!!!!!"
    
            
                
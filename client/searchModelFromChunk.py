# -*- coding: gb18030 -*-

import math
import time
import BigWorld
import Math
import ResMgr
import os
import stat

def searchModel(modelname, minHight = -1000, maxHight = 1000, PATH = "universes/bei_ming/", BW_RES = "D:/AB/csgame/datas/", modelReplacePath = None):
	print "starttime =",time.ctime()
	os.chmod(BW_RES ,stat.S_IWRITE)
	for filename in os.listdir(PATH):  #/uiverses/xxxx/xxx
		path1 = PATH + filename
		if os.path.isfile(BW_RES + path1):   #/universes/beiming/00000000o.chunk
			dealChunkFile(path1 ,path1, modelname, minHight , maxHight, modelReplacePath , PATH)
		else: #基本上没有用，由于这个目录主要是处理天空盒的一些数据,但是也要以防其它的一此目录里有内容
			for file in os.listdir(path1):  #/universes/beiming/001x000x/
				path2 = path1 + "/" + file
				if os.path.isfile(BW_RES + path2): 
					dealChunkFile(path2, path2, modelname, minHight , maxHight, modelReplacePath , PATH)
				else:
					for f in os.listdir(path2):  #/universes/beiming/001x000x/seq/
						path3  = path2 + "/" + f
						if os.path.isfile(BW_RES + f):  #/universes/beiming/001x000x/seq/0010000ao.chnuk
							dealChunkFile(path3, path3, modelname, minHight , maxHight, modelReplacePath , PATH)	

	ResMgr.purge(PATH)
	print "deal over!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "endtime =",time.ctime()
	
	
def dealChunkFile(filename ,path, modelname, minHight , maxHight, modelReplacePath , PATH ):
	if filename.endswith("chunk"):
		file = open(filename, "r")
		if modelname in file.read():
			dealSect(path, modelname, minHight , maxHight, modelReplacePath , PATH )
		file.close()
		
			
def dealSect(path, modelname, minHight, maxHight, modelReplacePath, PATH):
	sect = ResMgr.openSection(path)
	for key, value in sect.items():
		if key == "model":
			tmp = []
			flag1 = False
			flag2 = False
			modelpath = None
			pos = None
			m = None
			for k, v in value.items():
				if k == "resource":
					m = v
					modelpath = v.asString  # resource使用的模型名称
					flag1 = True
				if k == "transform":
					pos = v.readString("row3")
					posx = float(pos.split(" ")[0])
					posy = float(pos.split(" ")[1])
					posz = float(pos.split(" ")[2])
					if posy > minHight and posy < maxHight:
						flag2 = True
			if flag1 and flag2:
				if modelname in modelpath:
					if modelReplacePath:
						m.asString = modelReplacePath
					tmp.append(path)
					tmp.append(modelpath)
					tmp.append(pos)
			if tmp:
				print tmp
		if modelReplacePath:
			sect.save()

	
						
			
					
								
		
	
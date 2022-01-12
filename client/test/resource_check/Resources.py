# -*- coding: gb18030 -*-

import ResMgr
import os
import sys
import csv
import pickle
import base64
import time
import re
import random
import Sources

PATHDATAS = "E:/love3/datas"
PATHRES = "E:/love3/res"
BIGWORLDRES = "E:/love3/bigworld/res"
ERRORMODELPATH = []
#graph �ؼ���������Ѳ��·�ߵģ� uid������ˮ��Դ��, skyDome��պ�·��
LeafKey = [ "Texture","textureName","resource","modelFile","texture","textureName_","nodes","visualName_","graph","uid", "skyDome","soundbankname","uvanim",]
sourcesMap = {}
filenameTopath = {}
allItems = {"model":{}, "gui":{}, "particle":{}, "map":{}, "sound":{}, "other":{}}
copypathes = {}
specialfiles = [] #����һЩû�����ó�������������Ϸ�л�ʹ�õ��ļ�����Ȼ�����˴�����ʹ�õ���Դ�����ǻ����в�����ͨ����������·��д�ģ����Դ������������Ľ������Ҫ���������

guiSourcePy = {}  #����gui����Դ���ֵ�
modelSourcePy = {} 
particleSourcePy = {}

sourcereplace = {}  #ת����Դ



def addK(d, key):
	if d is None:
		return 
	
	if type(key) is tuple or type(key) is list:
		key = list(key)
		for item in key:
			item = item.lower()
			if item not in d:
				d.append(item)
		return 
	key = key.lower()
	if key not in d:
		d.append(key)

def addKV(d, key, value):
	if value is None:
		return 
	if value == "/" or value == "guis/" or ".cdata/" in value:
		return 
	key = key.lower()
	value = value.lower()
	if "/datas/" in key:
		key = key.split("datas/")[1]
	elif "/res/" in key:
		key = key.split("res/")[1]
	if type(d) is dict:
		if key not in d.keys():
			d.update({key:[value,]})
		else:
			if value not in d[key]:
				d[key].append(value)

				
		
def transfer(path):
	if os.name == "nt":
		if "/" in path:
			return path.replace("/", "\\")
	else:
		if "\\" in path:
			return path.replace("\\", "/")
	return path

def getNormalPath(dir, path):
	return transfer( os.path.join(dir, path) )
	
	
def getType(path):
	if "." in path:
		type_ = os.path.splitext(path)[1]
		if len(type_) > 1:
			return type_[1:].lower()
	return None

def getSplit(path):
	if "\\" in path:
		return path.split("\\")
	elif "/" in path:
		return path.split("/")

def findSourceMap():
	#����datas, guis��guis_v2�����ļ���Դ����
	for item in os.listdir("../datas"):
		if item == "modelTransferConf" or getType(item) == "doc":
			continue
		dealdir(PATHDATAS + "/" + item, callback, LeafKey)
	for item in ["guis_v2","guis"]:
		dealdir(PATHRES + "/" + item, callback, LeafKey)
	writecsv(sourcesMap, "sourcesMap.csv")
	print "len(filenameTopath) =",len(filenameTopath) 
	print "len(sourcesMap) =",len(sourcesMap)

def readcsvTodict(path):
	tmp = {}
	csvfile = open(path, "rb")
	reader = csv.reader(csvfile)
	for line in reader:
		for item in line[1:]:
			addKV(tmp, line[0], item)
	csvfile.close()
	return tmp

def getRelativePath(path):
	if "datas/" in path:
		return path.split("datas/")[1]
	elif "datas\\" in path:
		return path.split("datas\\")[1].replace("\\", "/")
	elif "res/" in path:
		return path.split("/res/")[1]
	elif "res\\" in path:
		return path.split("res\\")[1].replace("\\","/")
	elif path.endswith("datas"):
		return "../datas"
	return path

def dealdir(path, callback = None, key = None):
	#����F:/csol/datas/***, F:/csol/res/***�ļ���
	folder = path
	
	if "/datas/" in path:
		folder = path.split("datas/")[1]
	elif "/res/" in path:
		folder = path.split("res/")[1]
	if path.endswith("datas"):
		folder = "../datas"
	for i in os.listdir(folder):
		newpath = path + "/" + i
		if os.path.isfile(newpath):  #�ļ�
			if i[0] == "."  or i.startswith("#") or "thumbnail" in i or i.endswith( ".original" ) or "~" in i:  #pass .svn not see file
				continue
			if getType(newpath) in ["mpg","bin","settings","localsettings"]:
				specialfiles.append(newpath)
			filename = os.path.basename(newpath)
			addKV(filenameTopath, filename, getRelativePath(newpath))
			if callback:
				callback(newpath, key)
		elif os.path.isdir(newpath):  #Ŀ¼
			print newpath
			dealdir(newpath, callback, key)

def searchCode(path):
	#����Ŀǰ���д��������õ���Դ path = "entities/client"
	for item in os.listdir(path):
		newpath = path + "/" + item
		abspath = PATHRES + "/" + newpath
		if os.path.isfile(abspath):
			if  getType(newpath) == "py":
				if "/hyw" not in newpath and "/tools" not in newpath and "resource_check" not in newpath:
					#continue
					#print "1111",newpath
					checkfile(newpath)
		elif os.path.isdir(abspath):
			#print "2222",newpath
			searchCode(newpath)
	
	
def checkfile(path):
	f = open(path)
	flog = open("entities/client/test/resource_check/testsource.log", "a+")
	filename = os.path.splitext(os.path.basename(path))[0].upper()
	
	for line in f.readlines():
		if line.startswith("#"):
			continue
		line = line.strip()
		line = line.replace(" ", "")
		line = line.replace("\t", "")
		allmatches = re.findall(r'"(.*?)"', line)	#��ȡ""�������
		tmp = re.findall(r"'(.*?)'", line)			#��ȡ''�������
		allmatches.extend(tmp)
		if line.find("GUI.load") > 0:
			guimatches = re.findall(r'"(.*?)"', line)
			if len(guimatches) >0:
				for item in guimatches:
					if "%" not in item:
						guifile = os.path.splitext(os.path.basename(item))[0].upper()
						addReplace("GUI", filename, guifile, item)
					else:
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)
			else:
				print "need specical deal, path[%s]"%path
		if len(allmatches) > 0:
			
			for item in allmatches:  # ��"Ϊ�ָ��
				type_ = getType(item)
				file = os.path.splitext(os.path.basename(item))[0]
				if '.dds' in item:
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:				
						addReplace("DDS", filename, file, item)
				elif '.tga' in item:
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:
						addReplace("TGA", filename, file, item)
				elif '.model' in item:
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:
						addReplace("MODEL", filename, file, item)
				elif '.gui' in item:
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:
						addReplace("GUI", filename, file, item)
				elif '.xml' in item and "particles" in item :
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:
						addReplace("PARTICLE", filename, file, item)
				elif ".texanim" in item:
					if "%" in item :
						dir = item.split("%")[0]
						addReplace("DIR", filename, dir, dir)	
					else:
						addReplace("TEXANIM", filename, file, item) 
				for i in ["guis/", "guis_v2/", "maps/", "icons/", "gzawu/", "dlwp/", "creature/", "particles/", "monster/", "monster1/", "mount/", "npc/", "talisman/" , "weapon/" ]:
					if i in item :
						type_ = getType(item)
						if "%" in item :
							dir = item.split("%")[0]
							addReplace("DIR", filename, dir, dir)
						else:
							addReplace(type_, filename, file, item)
		if '.dds"' in line or 	\
			'.tga"' in line or 	\
			'.model"' in line or		\
			'.xml"' in line or 		\
			'.gui"' in line or 		\
			'"guis/' in line or 		\
			'"guis_v2/' in line or 		\
			'"maps/' in line or 		\
			'"icons/' in line or 		\
			'"gzawu/' in line or		\
			'dlwp/"' in line or 		\
			'"creature/' in line or 		\
			'"particles/' in line or 		\
			'"monster/' in line or 		\
			'"monster1/"' in line or		\
			'"npc/' in line or		\
			'"talisman/' in line or		\
			'"weapon/' in line:
			 	flog.write(path+"\t\t"+line+"\r\n")
					 	 
				 	 
	f.close()
	flog.close()
				
def analysisline(type_, filename, source, item ):
	if "%" in item:
		dir = item.split("%")[0]
		addReplace("DIR", filename, dir, dir)
	else:
		file = os.path.splitext(os.path.basename(item))[0]
		addReplace(type_, filename, file, item)


def copytest(path, i):
	#����tga��dds�������Ҵ��ڵ�
	filename = os.path.splitext(i)[0]
	if os.path.isfile(PATHDATAS + "/" + i):  
		copyfile(getNormalPath(PATHDATAS, i), getNormalPath(path, i))
		return 
	if os.path.isfile(PATHRES + "/" + i):		
		copyfile(getNormalPath(PATHRES, i), getNormalPath(path, i))
		return	
	filetmp = i
	if getType(i) == "dds":
		filetmp = filename + ".tga"
	elif getType(i) == "tga":
		filetmp = filename + ".dds"
	if os.path.isfile(PATHDATAS + "/" + filetmp):
		copyfile(getNormalPath(PATHDATAS, filetmp), getNormalPath(path, filetmp))
		return
	if os.path.isfile(PATHRES + "/" +  filetmp): 
		copyfile(getNormalPath(PATHRES, filetmp), getNormalPath(path, filetmp))
		return		
	if os.path.isfile(BIGWORLDRES + "/" + filetmp):
		return 
	print "rsourcescheck: can't find pathfile[%s]! \r\n"%i, filename	
						
def copySourcesInCode(path):
	searchCode("entities/client")
	writePy2(sourcereplace, "source.py")
	for key, value in sourcereplace.items():
		copytest(path, value)
		
	#writecopybat()
		
						
				
				
def addReplace(type_, filename, file, item):
	if item.startswith(".") or item is None or item.endswith(".") or file == "":
		return 
	if type_ is None:
		type_ = "DIR_T"
	key = type_.upper() + "_" + filename.upper() + "_" + file.upper()
	if key.endswith("/"):
		key = key[:-1]
	if "/" in key:
		key = key.replace("/", "_")
	value = item
	if os.path.exists(PATHDATAS + "/" + item) or os.path.exists(PATHRES + "/" + item) or getType(item) in ["dds", "tga"]:
		if key not in sourcereplace.keys():
			sourcereplace[key] = value
		else:
			if value in sourcereplace.values():
				return 
			key = key + "__" + str(random.randint(1, 100))

			if key in sourcereplace.keys():
				print "sourcereplace has key[%s] and value[%s]"%(key, value)
			else:	
				sourcereplace[key] = value

def reWriteSources():
	searchCode("entities/client")
	tmp = readSources()
	f = open("entities/common/Sources.py","a+")
	f.write("\n")
	for key, value in sourcereplace.items():
		if key not in tmp.keys():
			f.write(key + "\t=\t" + '"' +  value + '"'+ "\n")
	f.close()
			
	
def readSources():
	f = open("entities/common/Sources.py")
	tmp = {}
	for line in f.readlines():
		if "=" in line:
			line = line.strip()
			line = line.replace(" ","")
			key = line.split("=")[0]
			value = line.split("=")[1]
			tmp[key] = value
	f.close()
	return tmp	

def callback(path, LeafKey = []):
	if getType(path) not in ["chunk", "model", "visual", "xml", "gui", "texanim", "settings","fdp"]:
		return 
	relativepath = path
	if "/datas/" in path:
		relativepath = path.split("/datas/")[1]
	elif "/res/" in path:
		#print "111",relativepath
		relativepath = path.split("/res/")[1]
	sect = ResMgr.openSection(relativepath)
	if not sect:
		print "relativepath",relativepath
		return 
		
	checkKey(path, sect, LeafKey) 
	if getType(path) in ["chunk", "model", "visual", "xml", "gui",] and relativepath not in sourcesMap.keys():
		addKV(sourcesMap, getRelativePath(path).lower(), "")
		 
			
def checkKey(path, value, LeafKey = [] ):
	
	if len(value.items()) > 0:
		for k, v in value.items():
			if k in LeafKey:
				relativepath = os.path.dirname(path)
				if k == "nodes" and os.path.isfile(transfer(os.path.join(PATHDATAS, v.asString + ".animation"))): #�����ļ�
					addKV(sourcesMap, path.lower(), v.asString + ".animation")
				if k == "graph" and os.path.isfile(transfer(os.path.join(relativepath, v.asString + ".graph"))):  #Ѳ��·��
					addKV(sourcesMap, path.lower(), getRelativePath( getNormalPath(relativepath, v.asString + ".graph")))
				if k == "uid" and os.path.isfile(transfer(os.path.join(relativepath, v.asString + ".vlo"))):	#ˮ��Դ
					addKV(sourcesMap, path.lower(), getRelativePath(getNormalPath(relativepath , v.asString + ".vlo")))
					addKV(sourcesMap, path.lower(), getRelativePath(getNormalPath(relativepath , v.asString + ".odata")))
				if k == "soundbankname": #���path��sound/cs_sound.fdp, ʵ����Ҫ���ļ���sound/cs_sound.fev
					filename = os.path.splitext(path)[0] + ".fev"
					addKV(sourcesMap, filename.lower(), getNormalPath("sound/",v.asString + ".fsb"))
				else:
					addKV(sourcesMap, path.lower(), v.asString)

					
			else:
				checkKey(path, v, LeafKey)

def searchSpecialfiles(pathdir, dstpath ,types_):
	#����һЩ���������õ��ļ�,��������ʹ�õ���Դ
	for i in os.listdir(getRelativePath(pathdir)):
		newpath = pathdir + "/" + i
		if os.path.isfile(newpath):
			#types_ ��һЩ������ļ���Ŀǰ����["settings","bin","graph"](space.settings)
			"""
			�ض����͵��ļ�,bin,graph,settings
			��Ϸ���Ͻǵ�С��ͼ��Դ
			����������Դ
			��պ�
			��ͼģ����Դ����
			��ͷ����
			"""
			
			if (getType(newpath) in types_    
				or "/minimaps/" in newpath 
				or "/startscreen" in newpath
				or "sky/" in newpath   
				or "/config.xml" in newpath
				or "fly.xml" in newpath):  
				copyfile(newpath, getNormalPath(dstpath, getRelativePath(newpath)))
			if "/maps/" in newpath:   #maps��ֱ�ӿ�����,����help_icons��ophelp_icons�ļ���
				if len(newpath.split("maps/")) > 1:
					relativedir = newpath.split("maps/")[1].split("/")[0]  #��ȡmaps���ļ�����
					if relativedir in ['bigmaps', 'emote', 'entity_signs', 'flow_maps', 
						'loading_grounds', 'monster_headers', 'npc_signs',
						'particle_2d', 'patheditor', 'questmarks', 
						'role_headers', 'signboard', 'skillnames', 'skillnames_micro',
						'startscreen', 'teleport_grounds', 'texture_detail_levels.xml',
						'tong_signs', 'water', 'weaponglow']:
						copyfile(newpath, getNormalPath(dstpath, getRelativePath(newpath))) 
			if "icons/" in newpath or "space/di_biao" in newpath:  #ͼ�ꡢ�ر���ͼ
				copyfile(newpath, getNormalPath(dstpath, getRelativePath(newpath))) 
			if pathdir.split("/")[-2] == "space" and getType(newpath) == "tga" :  #��ͼgui��ͼ
				copyfile(newpath, getNormalPath(dstpath, getRelativePath(newpath)))
			
			if "cursor" in newpath and getType(newpath) not in ["dds",]: #�������ʹ�õ�ת����ʽ��һ������Ҫtgaԭʼ�ļ��������ļ�
				copyfile(newpath, getNormalPath( dstpath, getRelativePath(newpath) ))
		elif os.path.isdir(newpath):
			searchSpecialfiles(newpath, dstpath, types_)


def createClass():
	#findSourceMap()
	for k, v in sourcesMap.items():
		k = k.lower()
		if getType(k) is None:
			continue
		if getType(k) == "":
			continue
		filename = os.path.splitext(k)[0]
		if getType(k) == "model":
			visualname = filename + ".visual"
			tmp = ModelItem()
			tmp.name = k
			tmp.modelsources = [k,]
			try:
				tmp.visualsources = [visualname,]
				for item in sourcesMap[visualname.lower()]:
					if not (item == ""):
						addItem(tmp, item)
			except KeyError:
				flog.write( "rsourcescheck: error visual file[%s] not exist! \r\n"%visualname)
			for item in sourcesMap[k]:
				if not (item == ""):
					addItem(tmp, item)
			allItems["model"].update({k: tmp})
			continue
		"""
		elif getType(k) == "visual": #��Ҫ�Ǵ�����Ч�е�particles/mesh_particle�е���Ч��û��.model�ļ�
			modelname = filename + ".model"
			if modelname not in sourcesMap.keys():
				tmp = ModelItem()
				tmp.name = k
				tmp.visualsources = sourcesMap[k]
				for item in sourcesMap[k]:
					addItem(tmp, item)		
				allItems["model"].update({k: tmp})  #�����Ч������ģ��Ҳ����model��ʵ���б���.
		"""
		if getType(k) == "gui":
			tmp = GUIItem()
			tmp.name = k
			tmp.guisources = k
			for item in sourcesMap[k]:
				if len(item) > 0:
					addItem(tmp, item)
			allItems["gui"].update({k: tmp})
			continue
		if getType(k) == "xml" and k.startswith("particles"):
			#�����©������xml���ã����ǲ�����Ч�����ļ�
			tmp = ParticleItem()
			tmp.name = k
			tmp.particlesources = [k,]
			for item in sourcesMap[k]:
				if not (item == ""):
					addItem(tmp, item)
			allItems["particle"].update({k: tmp})
			continue
		if getType(k) == "chunk":
			filename = k.split("/")[1]
			if filename not in allItems["map"].keys():
				tmp = MapItem()
				tmp.name = filename
				tmp.chunkitems.append(k)
				for item in sourcesMap[k]:
					if not (item == ""):
						addItem(tmp, item)
				allItems["map"].update({filename: tmp})
				continue
			else:
				ins = allItems["map"][filename]
				ins.chunkitems.append(k)
				for item in sourcesMap[k]:
					if not (item == ""):
						addItem(ins, item)
				allItems["map"].update({filename: ins})	
				continue			
		if getType(k) == "fev":
			tmp = SoundItem()
			tmp.name = k
			tmp.sounditems.append(k)
			for item in sourcesMap[k]:
				if not (item == ""):
					addItem(tmp, item)
			allItems["sound"].update({k: tmp})
			continue
		if getType(k) not in ["visual"]:
			tmp = OtherItem()
			tmp.name = k
			tmp.otheritems.append(k)
			for item in sourcesMap[k]:
				if not (item == ""):
					addItem(tmp, item)
			allItems["other"].update({k: tmp})
			
			

def addItem(ins, item):
	type_ = getType(item)
	if type_ is None:
		return 
	if type_ == "":
		return 
	if type_ in ["dds","DDS"]:
		additemToIns(ins, "dds", item)
	elif type_ in ["tga", "TGA"]:
		additemToIns(ins, "tga", item)
	elif type_ in ["animation"]:
		additemToIns(ins, "animation", item)
	else:
		additemToIns(ins, "other", item)
		"""
		if getType(item) in ["model","xml","gui","texanim","visual"]:
			try:
				for item_ in sourcesMap[item]:
					addItem(ins, item_)
			except KeyError:
				print "sourcesMap has keyerror [%s]"%item
		"""
				
def additemToIns(ins, type_ , item):
	if os.path.isfile(transfer(os.path.join(PATHDATAS, item))):
		addK(ins.datas_files[type_], item)
		return 
	elif os.path.isfile(transfer(os.path.join(PATHRES, item))):
		addK(ins.res_files[type_], item)
		return 
	elif os.path.isfile(transfer(os.path.join(BIGWORLDRES, item))):
		addK(ins.res_files[type_], item)
		return 
	else:
		newfile = item
		if type_ == "dds":
			newfile = os.path.splitext(item)[0] + ".tga"
			additemToIns(ins, "tga", newfile)
			return
		elif type == "tga":
			newfile = os.path.splitext(item)[0] + ".dds"
			additemToIns(ins, "dds", newfile)
			return 
	
	flog.write( "rsourcescheck: ins[%s] has error path[%s]! \r\n"%(ins.name  ,item))


	
			
def fileExist(filename, filenamenew):
	return os.path.isfile(PATHDATAS + "/" +filename) or os.path.isfile(PATHDATAS + "/" +filenamenew)  or os.path.isfile(PATHRES + "/" +filename) or os.path.isfile(PATHRES + "/" +filenamenew)				
			
def findItemIns(filename):
	if getType(filename) not in ["gui","xml","model","chunk"]:
		print "con't match type[%s]",getType(filename)
	else:
		return allItems[getType(filename)][filename]
	
def copyfile(srcfile, dstfile):
	#������·���Ǿ���·��
	if srcfile.endswith("datas\\"):
		return 
	dstdir = os.path.dirname(dstfile)
	try:
		if not os.path.isdir(dstdir):
			os.makedirs(dstdir)
	except:
		print "rsourcescheck: create dir %s failed"%dstdir

	srcfile = transfer(srcfile)
	dstfile = transfer(dstfile)
	#print "srcfile =",srcfile
	#print "dstfile =",dstfile 
	if srcfile not in copypathes.keys():

		copypathes.update({srcfile: dstfile})
	"""
	if os.name == "nt":
		try:
			if not os.system("copy  %s %s"%(srcfile, dstfile)):
				print "copy %s succeed"%dstfile
		except:
			print "copy file[%s] failed!"%srcfile
			writeErroFiles.append(dstfile)
	else:
		try:
			if not os.system("cp %s %s"%(srcfile, dstfile)):
				print "copy %s succeed"%dstfile
		except:
			print "copy file[%s] failed!"%srcfile
			writeErroFiles.append(dstfile)
	"""
#--------------------------save tools------------------------------------

def writecopybat():
	if len(copypathes) == 0:
		return 
	currentime = str(time.time())
	f = open("copy" +currentime + ".bat" ,"wb")
	i = 1
	lencopy = len(copypathes)
	for key, value in copypathes.items():
		f.write("copy" + " " + key + " " + value + "\n")
		f.write("echo " + str(i) + " / " + str(lencopy) + "\r\n")
		i = i + 1
	f.close()

def writetxt(dict,filename):
	#���ֵ�д���ļ���������ԣ�����ÿ�ζ�����
	tmp = pickle.dumps(dict)
	btmp = base64.b64encode(tmp)
	f = open(filename, "wb")
	f.write(btmp)
	f.close()
	
def readtxt(filename):
	#��ȡ�ļ����ֵ䣬��ȡ�������
	f = open(filename)
	tmp = f.read()
	f.close()
	btmp = base64.b64decode(tmp)
	dict = pickle.loads(btmp)
	return dict
	
def writecsv(d, filename):
	#d = {key:[value,]}
	if not d:
		return
	f = open(filename, "wb")
	w = csv.writer(f)
	#w.writerow([filename.split(".")[0],])
	if type(d) == dict:
		for key, value in sorted(d.items(), key = lambda d:d[0]):
			tmp = []
			tmp.append(key)
			if len(value) > 1:
				tmp.extend(value)
			if len(value) ==1:
				tmp.append(value[0])
			w.writerow(tmp)
	elif type(d) == list:
		for item in d:
			w.writerow([item,])
	f.close()

def writePy(d, filename):
	#���ֵ���б���Ϊpy�ļ� ��entities/client/test/resource_check/xxx.py
	f = open(filename, "wb")
	f.write("Datas = " + str(d) )
	f.close()


def writePy2(d, filename):
	list = sorted(d.iteritems(), key = lambda item:item[0])  #��key����
	f = open(filename, "w")
	for item in list:
		f.write(item[0] + "\t=\t" + '"""' +  item[1] + '"""'+ "\r\n")
	f.close()
	

	
#--------------------------save tools------------------------------------

def analysis(path):
	global flog 
	flog = open("analysis.log","wb")
	searchSpecialfiles(PATHDATAS, path, ["settings","bin","graph"])
	findSourceMap()
	#dealdir(PATHRES + "/" + "guis", callback, LeafKey)
	#dealdir(PATHRES + "/" + "guis_v2", callback, LeafKey)
	copySourcesInCode(path) #����������ֱ��ʹ����Դ
	createClass()

	flog.write("-------------" + str(time.time()) + "---------------" + "\r\n")
	for item in allItems["model"].values():
		item.copyTo(path)
		if item.getName() not in modelSourcePy.keys(): 
			modelSourcePy.update(item.getDict())
		else:
			flog.write("modelSourcePy has same key:" + item.name + "\r\n")
	for item in allItems["gui"].values():
		item.copyTo(path)
		if item.getName() not in guiSourcePy.keys(): 
			guiSourcePy.update(item.getDict())
		else:
			flog.write("guiSourcePy has same key:" + item.name + "\r\n")
	for item in allItems["map"].values():
		item.copyTo(path)
	for item in allItems["particle"].values():
		item.copyTo(path)
		if item.getName() not in particleSourcePy.keys():  
			particleSourcePy.update(item.getDict())
		else:
			flog.write("particleSourcePy has same key:" + item.name + "\r\n")
	for item in allItems["sound"].values():
		item.copyTo(path)
	for item in allItems["other"].values():
		item.copyTo(path)
	flog.close()
	currentime = str(time.time())
	#writetxt(sourcesMap,"sourcesMap.txt")
	#writetxt(ERRORMODELPATH, "errormodelpath.txt")
	#writetxt(filenameTopath,"filenameTopath.txt")
	#writetxt(copypathes, "copypathes.txt")
	for item in specialfiles:
		copypathes.update({item: getNormalPath(path, getRelativePath(item))})#����һЩ�����ļ�
	filename = "copy" +currentime + ".bat"
	f = open(filename ,"wb")
	i = 1
	for key, value in copypathes.items():
		f.write("copy" + " " + key + " " + value + "\r\n")
		f.write("echo " + str(i) + " / " + str(len(copypathes)) + "\r\n")
		i = i + 1
	f.close()	
	
	#writePy(guiSourcePy, "entities/client/test/resource_check/guiSource.py")
	#writePy(modelSourcePy, "entities/client/test/resource_check/modelSource.py")
	#writePy(particleSourcePy, "entities/client/test/resource_check/particleSource.py")
	#os.system("ping -n 3 172.16>nul")  #��ʱ3����ִ�п���
	#os.system(PATHRES + "/" + filename)
	#os.system("shutdown /s /t 30")	


class BaseResourceItem:
	"""
	animation�ļ��ļ��Ҫ�ڿ�ʼ���м��
	�����汾ֻ���dds�������tga
	"""
	def __init__( self ):
		"""
		"""
		self.name = ""
		self.guisources = []
		self.modelsources = []  #�洢ĳ��Դ���õ�ģ�͡�������texanim����Ч
		self.visualsources = []
		self.particlesources = []
		self.chunkitems = []
		self.sounditems = []
		self.otheritems = []
		self.datas_files = {  \
			"dds":[], \
			"animation":[],\
			"tga":[],\
			"other":[], \
		}
		self.res_files = {
			"dds":[], \
			"tga":[], \
			"animation":[],\
			"other":[], \
		}
		
	def getName(self):
		return self.name

	def getFileName(self):
		if "\\" in self.name:
			return self.name.replace("\\", "__")
		elif "/" in self.name:
			return self.name.replace("/", "__")
		return self.name
		
	def getGUI(self):
		return self.guisources
		
	def getModel(self):
		return self.modelsources
	
	def getVisual(self):
		return self.visualsources

	def getParticle(self):
		return self.particlesources
		
	def getChunk(self):
		return self.chunkitems
	
	def getDatas_files(self):
		return self.datas_files
		
	def getRes_files(self):
		return self.res_files
		
	def printAll(self):
		print "----------------------------------------------------"
		print "name is:",self.name
		print "contain guisources:",self.guisources
		print "contain modelsources:",self.modelsources
		print "contain visualsources:",self.visualsources
		print "contain particlesources:",self.particlesources
		print "contain chunkitems:",self.chunkitems
		print "contain sounditems:",self.sounditems
		print "contain otheritems:",self.otheritems
		print "contain datas_files:",self.datas_files
		print "contain res_files:",self.res_files
		print "----------------------------------------------------"

	def getRefSources(self):
		tmp = []
		for key, item in self.datas_files.items():
			addK(tmp, item)
		for key, item in self.res_files.items():
			addK(tmp, item)
		return tmp

	def getDict(self):
		return {self.getFileName(): self.getRefSources()}
		
	def copyTo( self ,path ):
		"""
		"""
		
		self.copydatas(path, self.datas_files)
		self.copydatas(path, self.res_files)
		
	def copydatas(self, path, dict):
		
		for key, item in dict.items():
			for i in item:
				i = i.lower()
				if getType(i) in ["dds","tga",]:
					self.copyddsortga(path, i, ".tga")
				elif getType(i) in  ["jpg","bmp"]:
					self.copyddsortga(path, i, ".dds")
				elif getType(i) in ["model", "visual","xml","texanim","uvanim"]:
					try:
						self.copydatas(path, {i:sourcesMap[i]}) #����������Դ
						if getType(i) == "model":
							visual = os.path.splitext(i)[0] + ".visual"
							self.copydatas(path, {visual:sourcesMap[visual]})
					except KeyError:
						flog.write( "rsourcescheck: sourcesMap has not key[%s]! \r\n"%i)
					#�����Լ�
					self.testCopy(path, i)

				else:
					self.testCopy(path, i)
			#����key
			self.testCopy(path, key)



	def testCopy(self, path, item):
		if len(item) <= 7 or getSplit(item) is None:  #ȥ��item���ļ�����ʱ�Ĵ�����־
			return 
		if os.path.isfile(getNormalPath(PATHRES, item)):	
			scrpath = getNormalPath(PATHRES, item)
			dstpath = getNormalPath(path, item)
			copyfile(scrpath, dstpath)	
			return 
		elif os.path.isfile(getNormalPath(PATHDATAS, item)):
			scrpath = getNormalPath(PATHDATAS, item)
			dstpath = getNormalPath(path, item)
			copyfile(scrpath, dstpath)	
		else:
			flog.write( "testcopy item[%s] to path[%s] failed! \r\n"%(item, path))		
				
	def copyddsortga(self, path, i, type_):
		#����tga��dds�������Ҵ��ڵ�
		filename = os.path.splitext(i)[0]
		if os.path.isfile(getNormalPath(PATHDATAS, i)):  
			copyfile(getNormalPath(PATHDATAS, i), getNormalPath(path, i))
			return 
		if os.path.isfile(getNormalPath(PATHRES, i)):
			copyfile(getNormalPath(PATHRES, i), getNormalPath(path, i))
			return
		filetmp = filename + type_
		if os.path.isfile(getNormalPath(PATHDATAS, filetmp)):
			copyfile(getNormalPath(PATHDATAS, filetmp), getNormalPath(path, filetmp))
			return
		if os.path.isfile(getNormalPath(PATHRES, filetmp)): 
			copyfile(getNormalPath(PATHRES, filetmp), getNormalPath(path, filetmp))
			return		
		if os.path.isfile(getNormalPath(BIGWORLDRES, filetmp)):
			return 
		flog.write( "rsourcescheck: can't find pathfile[%s]! \r\n"%i	)		
					



class ModelItem( BaseResourceItem ):
	"""
	"""
	def copyTo( self ,path ):
		"""
		"""
		filename = os.path.splitext(self.name)[0]
		self.testCopy(path, filename + ".model")
		self.testCopy(path, filename + ".visual")
		self.testCopy(path, filename + ".primitives")

		
		BaseResourceItem.copyTo(self, path)
		
		


class MapItem( BaseResourceItem ):
	"""
	"""

	def copyTo( self ,path ):
		"""
		"""
		for item in self.chunkitems:
			filename = item 
			try:
				filename = os.path.splitext(item)[0]
			except:
				continue
			self.testCopy(path, item)
			cdata = filename + ".cdata"
			self.testCopy(path, cdata)

			
		BaseResourceItem.copyTo(self, path)
			
	

class ParticleItem( BaseResourceItem ):
	def copyTo( self ,path ):
		"""
		"""
		for item in self.particlesources:
			scrparticlepath = getNormalPath(PATHDATAS, item)
			dstparticlepath = getNormalPath(path, item)
			copyfile(scrparticlepath, dstparticlepath)
			
		BaseResourceItem.copyTo(self, path)	
		


class GUIItem( BaseResourceItem ):
	"""
	"""
	def copyTo( self ,path ):
		"""
		"""
		scrguipath = getNormalPath(PATHRES, self.guisources)
		dstguipath = getNormalPath(path, self.guisources)
		copyfile(scrguipath, dstguipath)
			
		BaseResourceItem.copyTo(self, path)	
				
		
class SoundItem( BaseResourceItem ):
	"""
	"""
	def copyTo( self, path):
		for item in self.sounditems:
			self.testCopy(path, item)
			
		BaseResourceItem.copyTo(self, path)	
		
	
	
class OtherItem( BaseResourceItem ):
	"""
	"""
	def copyTo( self, path):
		for item in self.otheritems:
			self.testCopy(path, item)
			
			#scrsoundpath = getNormalPath(PATHDATAS, item)
			#dstsoundpath = getNormalPath(path, item )
			#copyfile(scrsoundpath, dstsoundpath)
			
		BaseResourceItem.copyTo(self, path)		
				

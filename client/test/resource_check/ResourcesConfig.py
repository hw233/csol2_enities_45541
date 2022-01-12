# -*- coding: gb18030 -*-
"""
configDict=
{
	"怪物配置"	  : (MonsterConfig, ["entities/locale_default/config/server/NPCMonster.xml",]),
	"空间配置"	  : (SpaceConfig, ["entities/locale_default/config/server/gameObject/space",]),
	"GUI01配置"	 : (GuiConfig, ["guis",]),
	"GUI02配置"	 : (GuiConfig, ["guis_v2",]),
	"icon配置"	  : (IconConfig, ["entities/locale_default/config/item/ItemData","entities/locale_default/config/client/SkillEffect/SpellEffect.py"),
	"weapon配置"	: (WeaponConfig, "entities/locale_default/config/item/ItemData"),
	"掉落物品配置"  : (dlwpConfig, "entities/locale_default/config/client/ItemModel.py"),
	"NPC配置"	   : (NPCConfig, "entities/locale_default/config/server/NPCObject.xml"),
	"特效配置"	  : (ParticleConfig, "entities/locale_default/config/client/SkillEffect/ParticleConfig.py"),
	#"弱化等效配置" : (BranchParticleConfig, "entities/locale_default/config/client/SkillEffect/BranchParticleConfig.py")
}
"""
import ResMgr
import os
import sys
import config.client.NPCModelConfig as nc
import config.client.SkillEffect.ParticlesConfig as pc
import config.client.ItemModel as im
from config.item.ItemData import *
from bwdebug import *
import  checkResource as cr

PATHDATAS = "D:/AB/csgame/datas"
PATHRES = "D:/love3/res"
ERRORMODELPATH = []
LeafKey = [ "Texture","textureName","resource","modelFile","texture","textureName_"]
sourcesMap = {}
filenameTopath = {}

def addK(d, key):
	if d is None:
		return 
	if d == "":
		return 
	if type(key) is tuple or type(key) is list:
		key = list(key)
		for item in key:
			if item not in d:
				d.append(item)
		return 
	if key not in d:
		d.append(key)

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
			return type_[1:]
	return None


def findSourceMap():
	for item in os.listdir("../datas"):
	#for item in ["avatar", "creature", "dlwp", "gzawu", "monster", "monster1", "npc", "talisman","mount", "weapon","environments",""]:
		if item == "modelTransferConf" or getType(item) == "doc":
			continue
		dealdir(PATHDATAS + "/" + item, callback, LeafKey)
	for item in ["guis_v2","guis"]:
		dealdir(PATHRES + "/" + item, callback, LeafKey)
	print "len(filenameTopath) =",len(filenameTopath) 
	print "len(sourcesMap) =",len(sourcesMap)

def getRelativePath(path):
	if "datas/" in path:
		return path.split("datas/")[1]
	elif "res/" in path:
		return path.split("res/")[1]
	elif path.endswith("datas"):
		return "../datas"

def dealdir(path, callback = None, key = None):
	#处理F:/csol/datas/***, F:/csol/res/***文件夹
	folder = path
	if "/datas/" in path:
		folder = path.split("datas/")[1]
	elif "/res/" in path:
		folder = path.split("res/")[1]
	for i in os.listdir(folder):
		newpath = path + "/" + i
		if i[0] == "."  or i.startswith("#") or "thumbnail" in i or i.endswith( ".original" ) or "~" in i:  #pass .svn not see file
			continue
		else:
			if os.path.isfile(newpath):  #文件
				filename = os.path.basename(newpath)
				addKV(filenameTopath, filename, getRelativePath(newpath))
				if os.path.splitext(newpath)[1] in [".chunk", ".model", ".visual", ".xml", ".visual", ".gui", ".texanim"]:
					#print "444",newpath
					if callback:
						callback(newpath, key)
			elif os.path.isdir(newpath):  #目录
				print newpath
				dealdir(newpath, callback, key)


def callback(path, LeafKey = []):
	type_ = getType(path)  # xml, model, visual, chunk
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
			if k in LeafKey:
				if v.asString:
					addKV(sourcesMap, path, v.asString)
			checkKey(path, v, LeafKey)  
			
def checkKey(path, value, LeafKey = [] ):
	if len(value.items()) > 0:
		for k, v in value.items():
			if k in LeafKey:
				if v.asString:
					#if len(v.asString) == 35 and len(v.asString.split(".")) == 4: #对水资源、巡逻路线，镜头引用文件的判定
						#print "v.asString =",v.asString, "path = ",path
					if typeInNeed(v.asString):
						addKV(sourcesMap, path, v.asString)
			else:
				checkKey(path, v, LeafKey)

def typeInNeed(path):
	if getType(path) is None:
		return False
	elif getType(path) in ["xml","dds","jpg","bmp","tga","model","visual","texanim"] or (len(path) == 35 and len(path.split(".")) == 4):
		return True
	return False 

class BaseConfig:
	"""
	"""
	def __init__( self, pathes):
		"""
		"""
		self.configpath = pathes
		self.modelpathes = []
		self.particlepathes = []
		self.tgaes = []
		self.ddses = []  #dds file path
		self.guis = []
		self.initialize()
		
	def initialize( self ):
		self.getModel()
		self.getMap()
		self.getGui()
		self.getParticle()
		self.getDds()
	
	
	def getModel( self ):
		"""
		"""
		"""
		for path in self.modelpathes:
			def dealpath(path):
				sect = ResMgr.openSection(path)
				if sect is None:
					addK(ERRORMODELPATH, modelpath)
				else:
					for k, v in sect.items():
						def search(v):
							if len(v.items()) > 0:
								for k1,v1 in v.items():
									if k1 in ["Texture",]:
										addK(self.tgas, v1.asString)
										if getType(v1.asString) in ["tga","TGA"]:
											addK(self.ddses, v1.asString[:-4] + ".dds")
									else:
										search(v1)
						search(v)
			dealpath(path)
			visualpath = os.path.splitext(path)[0] + ".visual"
			dealpath(visualpath)
		"""
		return self.modelpathes

	def getMap( self ):
		"""
		"""
		return []
		
	def getTga( self ):
		return []
		
	def getDds( self ):
		return []

	def getGui( self ):
		"""
		"""
		return []
		
	def getParticle( self ):
		"""
		"""
		return []
		

class MonsterConfig( BaseConfig ):
	"""
	"""
	def __init__( self, pathes ):
		"""
		"""
		self.modelkeys = []
		BaseConfig.__init__( self, pathes )
		#self.configpath = pathes
		#["entities/locale_default/config/server/gameObject/NPCMonster.xml","entities/locale_default/config/server/gameObject/NPCObject.xml"]
		
		
	
	def initialize( self ):
		self.getMonsterKeys()
		BaseConfig.initialize( self )
		
	def getModel( self ):
		"""
		"""
		for item in self.getMonsterKeys():
			modelpath = self.modelNumberToPath(item, "sources")
			addK(self.modelpathes, modelpath)
		return self.modelpathes


	def getParticle( self ):
		"""
		"""
		for item in self.getMonsterKeys():
			particlepath = self.modelNumberToPath(item, "particles")
			addK(self.particlepathes, particlepath)
		return self.particlepathes
	
	def getTga( self ):
		"""
		headtexture
		"""
		for item in self.getMonsterKeys():
			headtexture = self.modelNumberToPath(item , "head")
			headtexturedds = ""
			if headtexture:
				headtexturedds = os.path.splitext(headtexture)[0] + ".dds"
			addK(self.tgas, headtexture)
			addK(self.ddses, headtexturedds)
		return self.tgas
		
	def getDds( self ):
		self.getModel()
		for item in self.getMonsterKeys():
			headtexture = self.modelNumberToPath(item , "head")
			headtexturedds = ""
			if headtexture:
				headtexturedds = os.path.splitext(headtexture)[0] + ".dds"
			addK(self.ddses, headtexturedds)		
		return self.ddses
		
	def getMonsterKeys( self ):
		"""
		获取怪物modelNumber
		"""
		for item in self.configpath:
			sect = ResMgr.openSection(item)
			for k, v in sect.items():
				for k1, v1 in v.items():
					if k1 == "modelNumber":
						for k2, v2 in v1.items():
							if v2.asString is not None:
								addK(self.modelkeys, v2.asString)
		return self.modelkeys
						
	
	def modelNumberToPath(self, item, key):
		"""
		modelNumber to modelpath
		item: modelNumber
		key：sources, particles
		"""
		if item in nc.Datas.keys():
			if key in nc.Datas[item].keys():
				return nc.Datas[item][key]
		return ""


class MapConfig( BaseConfig ):
	"""
	"""
	def __init__( self, pathes ):
		"""
		"""
		self.mappathes = []
		BaseConfig.__init__( self, pathes )
		#self.configpath = ["entities/locale_default/config/server/gameObject/space",]
		
		

	def initialize(self):
		for item in self.getMap():
			def callback(value, LeafKey):
				if len(value.items()) > 0:
					for k, v in value.items():
						if k in LeafKey:
							self.add(v.asString)
						else:
							callback(v, LeafKey)
					
			def check(relativedir, callback, LeafKey):
				for path in os.listdir(relativedir):
					newpath = getNormalPath(relativedir, path)
					abspath = getNormalPath(PATHDATAS, newpath)
					if path[0] == ".":  #pass .svn not see file
						continue
					if os.path.isfile(abspath):
						if getType(abspath) in ["chunk", "CHUNK"]:
							sect = ResMgr.openSection(newpath)
							for k,v in sect.items():
								callback(v, LeafKey)
					elif os.path.isdir(abspath):
						check(newpath, callback, LeafKey)
			check(item, callback, ["resource","modelFile"])			
	
	def getMap( self ):
		"""
		"""
		for item in self.configpath:
			for path in os.listdir(item):
				newpath = transfer( os.path.join(item, path) )
				sect = ResMgr.openSection(newpath)
				for k,v in sect.items():
					if k == "dirMapping":
						addK(self.mappathes, v.asString)
		return self.mappathes
		
	def getModel( self ):
		return self.modelpathes
		
	def getParticle( self ):
		return self.particlepathes

	def add(self, path):
		type_  = getType(path)
		if type_ is None:
			return 
		if path.startswith("particles") and type_ == "xml":
			addK(self.particlepathes, path)
		elif type_ == "model":
			addK(self.modelpathes, path)


class GuiConfig( BaseConfig ):
	"""
	"""
	def __init__( self, pathes ):
		"""
		"""
		
		BaseConfig.__init__( self, pathes )
		#self.configpath = ["guis_v2","guis"]
		
		
	def initialize(self):
		for item in self.configpath:
			def callback(value, LeafKey):
				if len(value.items()) > 0:
					for k, v in value.items():
						if k in LeafKey:
							addK(self.ddses, v.asString)
						else:
							callback(v, LeafKey)
					
			def check(relativedir, callback, LeafKey):
				for path in os.listdir(relativedir):
					newpath = getNormalPath(relativedir, path)
					abspath = getNormalPath(PATHRES, newpath)
					if path[0] == ".":  #pass .svn not see file
						continue					
					if os.path.isfile(abspath):
						if getType(abspath) in ["gui", "GUI"]:
							addK(self.guis, newpath)
							sect = ResMgr.openSection(newpath)
							for k,v in sect.items():
								callback(v, LeafKey)
					elif os.path.isdir(abspath):
						check(newpath, callback, LeafKey)
			check(item, callback, ["textureName","texture"])
		BaseConfig.initialize( self )
	
	def getGui( self ):
		"""
		"""
		return self.guis
		
	def getDds( self ):
		return self.ddses
		
class ParticleConfig( BaseConfig ):
	def __init__( self, pathes ):
		"""
		"""
		BaseConfig.__init__( self, pathes )
		#self.configpath = ["entities/locale_default/config/client/SkillEffect/ParticleConfig.py",]
		
	
	def initialize( self ):
		
		for key, value in pc.Datas.items():
			for k1, v1 in value.items():
				if k1 == "particle_source":
					addK(self.particlepathes, v1)
		BaseConfig.initialize( self )

	def getParticle( self ):
		return self.particlepathes 
		
class ItemConfig( BaseConfig ):
	#武器，商品，
	def __init__( self, pathes ):
		BaseConfig.__init__( self, pathes )
		#self.configpath = ["entities/locale_default/config/item/ItemData"]
		
		
	def initialize( self ):
		for item in self.configpath:
			for file in os.listdir(item):
				filename = os.path.splitext(file)[0]
				if filename == "__init__":
					continue
				sys.path.append(item)
				module = __import__(filename)
				for key ,value in module.Datas.items():
					for k1, v1 in value.items():
						if k1 == "icon":
							path = transfer(os.path.join("icons", v1 + ".dds"))
							addK(self.ddses, path)
						elif k1 == "model":
							model = v1
							addK(self.modelpathes, self.getModelPath(model))
		BaseConfig.initialize( self )

	def getModelPath(self, model):
		
		if model == "": return None
		valList = model.split(";")
		vs = []
		for value in valList:
			val = value.split("-")
			try:
				v = int(val[0]) * 1000000
				v += int(val[1]) * 10000
				v += int(val[2])
				if im.Datas.get(v, None):
					for k1, v1 in im.Datas.get(v, None).items():
						if k1.startswith("model_drop") or k1.startswith("model_source"):
							addK(vs, v1)
			except Exception, errstr:
				ERROR_MSG( "'%s' is not right." % model )
				v = 0

		return vs
		
	def getModel( self ):
		return self.modelpathes
		
	def getDds( self ):
		return self.ddses
			
	
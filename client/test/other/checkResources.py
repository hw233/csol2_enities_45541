# -*- coding: gb18030 -*-
import os
import Language
import items
import Define
from bwdebug import *
from gbref import rds
from config.client import ItemModel
from config.client import NPCModelConfig
from config.client.SkillEffect import SpellEffect
from config.item.Items import Datas as g_ItemsData

class CheckResources:
	"""
	资源检测模块（CSOL-1458）
	"""
	__instance = None

	def __init__( self ):
		assert CheckResources.__instance is None

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = CheckResources()
		return SELF.__instance

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __loadObjResources( self ):
		"""
		Obj配置加载
		"""
		bigfiles = []
		sections = []
		filesPath = "config/server/gameObject/objPath.xml"
		sect = Language.openConfigSection( filesPath )
		if sect is None: raise SystemError, "can't load %s " % filesPath
		Language.purgeConfig( filesPath )
		if sect.has_key( "files" ):
			bigfiles = sect["files"].readStrings( "path" )
		for fileName in bigfiles:
			section = Language.openConfigSection( fileName )
			sections.append( section )
		return sections

	def __getObjModelDatas( self ):
		"""
		获取Obj所有模型编号数据
		@return {}  like as {className:[modelNumbers]....}
		"""
		modelDatas = {}
		sections = self.__loadObjResources()
		for section in sections:
			for className, sect in section.items():
				modelDatas[className] = [e.lower() for e in sect["modelNumber"].readStrings( "item" )]
		return modelDatas

	def __getPathXmls( self, xml ):
		"""
		获取指定光效路径下所有文件名列表
		"""
		xmlList = []
		paths = xml.split("/")
		dxml = paths[len( paths ) - 1]	# 最后个标志符
		path = xml.replace( dxml, "" )
		try:
			files = os.listdir( path )
		except:
			files = []
		for file in files:
			axml = path + file
			lxml = axml.lower()		# 大小写转换
			uxml = axml.upper()
			uxml = uxml.replace( "XML", "xml" )
			xmlList.append( axml )
			xmlList.append( lxml )
			xmlList.append( uxml )
		return xmlList

	def __getIcons( self ):
		"""
		获取所有物品图标路径数据
		@return {}  like as {itemID:iconPath...}
		"""
		iconDatas = {}
		for itemID, itemData in g_ItemsData.items():
			if itemID == "": continue
			iconName = itemData.get( "icon", "" )
			iconPath = "%s.dds" % iconName
			iconDatas[itemID] = iconPath
		return iconDatas

	def __loadSpaceResources( self ):
		"""
		地图配置加载
		"""
		files = []
		mapFiles = {}
		spawnFiles = {}
		sections = []
		filesPath = "config/server/gameObject/objPath.xml"
		sect = Language.openConfigSection( filesPath )
		if sect is None: raise SystemError, "can't load %s " % filesPath
		paths = [e for e in sect.readStrings( "path" )]
		Language.purgeConfig( filesPath )
		files = Language.searchConfigFile( paths, ".xml" )
		for fileName in files:
			section = Language.openConfigSection( fileName )
			if section.has_key( "dirMapping" ):
				mapFile = section.readString( "dirMapping" )
				mapFiles[fileName] = mapFile
			if section.has_key( "spawnFile" ):
				spawnFile = section.readString( "spawnFile" )
				spawnFiles[fileName] = spawnFile
		for space, file in spawnFiles.items():
			section = Language.openConfigSection( file )
			if section is None: continue
			sections.append( section )
		return mapFiles, sections

	def __getSpaceModelDatas( self, modelString ):
		"""
		获取地图配置模型路径/模型编号
		"""
		modelDatas = []
		mapFiles, sections = self.__loadSpaceResources()
		for section in sections:
			for sect in section.values():
				if sect.has_key( "properties" ):
					modelData = sect["properties"].readString( modelString )
					if modelData == "": continue
					modelDatas.append( modelData )
		return modelDatas

	def __loadItemModelResources( self, returnString ):
		"""
		物品模型资源加载
		"""
		itemModelDatas = {}
		notExistItemModelIDs = {}
		for itemID in g_ItemsData.keys():
			itemModelID = items.instance().id2model( itemID )
			if itemModelID == 0: continue
			if not itemModelID in ItemModel.Datas.keys():
				notExistItemModelIDs[itemID] = itemModelID
				continue
			itemModelDatas[itemID] = itemModelID
		if returnString == "itemModels":
			return notExistItemModelIDs		# 打印ItemModel中不存在的物品模型ID
		elif returnString == "loseItemModels":
			return itemModelDatas

	def __getItemModelPaths( self, modelString ):
		"""
		获取物品配置模型路径数据（掉落模型/主模型/次模型）
		@return {} like as {itemID:modelPath....}
		"""
		itemModelPaths = {}
		itemModelDatas = self.__loadItemModelResources( "loseItemModels" )
		if modelString == "model_drop":
			for itemID, itemModelID in itemModelDatas.items():
				modelPath = rds.itemModel.getDropModelByID( itemModelID, False )
				if modelPath == "": continue
				itemModelPaths[itemID] = [modelPath]
		elif modelString == "model_source1":
			for itemID, itemModelID in itemModelDatas.items():
				modelPath = rds.itemModel.getMSource( itemModelID )
				if modelPath == []: continue
				itemModelPaths[itemID] = modelPath
		elif modelString == "model_source2":
			for itemID, itemModelID in itemModelDatas.items():
				modelPath = rds.itemModel.getFSource( itemModelID )
				if modelPath == []: continue
				itemModelPaths[itemID] = modelPath
		return itemModelPaths

	def __loadBigMapResources( self ):
		"""
		大地图贴图资源加载
		"""
		sections_1 = {}
		sections_2 = {}
		filesPath_1 = "config/client/bigmap/bigmaps.xml"
		filesPath_2 = "config/client/bigmap/bigmapsky.xml"
		sect_1 = Language.openConfigSection( filesPath_1 )
		sect_2 = Language.openConfigSection( filesPath_2 )
		for spaceName, section in sect_1.items():
			tgas = []
			if section.has_key( "texture" ):
				tga = section.readString( "texture" )
				if tga == "": continue
				tgas.append( tga )
			sections_1[spaceName] = tgas
		for spaceName, section in sect_2.items():
			tgas = []
			if section.has_key( "texture" ):
				tga = section.readString( "texture" )
				if tga == "": continue
				tgas.append( tga )
			sections_2[spaceName] = tgas
		return sections_1, sections_2

	def __getPathTgas( self, tga ):
		"""
		获取指定贴图路径下所有文件名列表
		"""
		tgaList = []
		paths = tga.split("/")
		dtga = paths[len( paths ) - 1]	# 最后个标志符
		path = tga.replace( dtga, "" )
		try:
			files = os.listdir( path )
		except:
			files = []
		for file in files:
			atga = path + file
			ltga = atga.lower()		# 大小写转换
			utga = atga.upper()
			utga = utga.replace( "DDS", "dds" )
			tgaList.append( atga )
			tgaList.append( ltga )
			tgaList.append( utga )
		return tgaList

	def __loadHeadTgaResources( self ):
		"""
		模型头像贴图配置加载
		"""
		headTgas = {}
		for modelNumber in NPCModelConfig.Datas.keys():
			headTga = rds.npcModel.getHeadTexture( modelNumber )
			if headTga == "": continue
			headTgas[modelNumber] = headTga
		return headTgas

	def __loadSkillTgaResources( self, returnString ):
		"""
		技能贴图配置加载
		"""
		loseTgas = []
		skillTgas = {}
		for skillID, spellEffect in SpellEffect.Datas.items():
			tga = spellEffect.get( "spell_icon", "" )
			if skillID in Define.TRIGGER_SKILL_IDS:
				skillTgas[skillID] = "icons/skill_physics_037.dds"
				continue
			if tga == "":
				loseTgas.append( skillID )
				continue
			tgaPath = "icons/%s.dds" % tga
			skillTgas[skillID] = tgaPath
		if returnString == "skillTgas":
			return loseTgas
		elif returnString == "loseSkillTgas":
			return skillTgas

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def checkResources( self ):
		"""
		资源检测总的入口，会遍历所有的检测子方法
		# datas/...|config/...表示该方法所检测的资源路径
		# 私有方法中输出的ERROR_MSG也是错误问题
		"""
		loseResources = {}
		loseResources["loseObjModels"] = self.checkObjModelResources( "loseObjModels" )			# datas/avatar | datas/monster | datas/monster1 | datas/npc | datas/space | datas/creature | datas/mount
		loseResources["ObjModels"] = self.checkObjModelResources( "ObjModels" )					# config/client/NPCModelConfig.py
		loseResources["loseEffectXmls"] = self.checkParticleResources()							# datas/particles
		loseResources["loseItemIcons"] = self.checkItemIconResources()							# datas/icons
		loseResources["loseItemModels"] = self.checkItemModelResources( "loseItemModels" )		# datas/avatar | datas/dlwp | datas/weapon
		loseResources["itemModels"] = self.checkItemModelResources( "itemModels" )				# config/client/ItemModel.py
		loseResources["loseSpaceModels"] = self.checkSpaceModelResources( "loseSpaceModels" )	# datas/space
		loseResources["spaceModels"] = self.checkSpaceModelResources( "spaceModels" )			# config/client/NPCModelConfig.py
		loseResources["loseSpaceMaps"] = self.checkSpaceMapResources()							# datas/universes
		loseResources["loseBigMaps"] = self.checkBigMapResources()								# datas/space | datas/maps
		loseResources["loseModelHeadTgs"] = self.checkModelHeadTgaResources()   				# datas/maps
		loseResources["skillTgas"] = self.checkSkillTgaResources( "skillTgas" )					# config/client/SkillEffect/SpellEffct.py
		loseResources["loseSkillTgas"] = self.checkSkillTgaResources( "loseSkillTgas" )			# datas/icons
		return loseResources

	def checkObjModelResources( self, returnString ):
		"""
		Obj配置检测，返回与Obj的className对应的无法创建的模型路径
		"""
		loseObjModels = {}
		notExistModelNumbers = {}
		modelDatas = self.__getObjModelDatas()
		for className, modelNumbers in modelDatas.items():
			Paths = []
			modelPaths = []
			for modelNumber in modelNumbers:
				paths = rds.npcModel.getModelSources( modelNumber )
				if paths == []:		# 没有模型路径显示有问题的模型编号
					modelPaths.append( modelNumber )
				model = rds.effectMgr.createModel( paths )
				if model is None:		# 模型创建失败表示模型资源有问题
					Paths.extend( paths )
			if modelPaths != []:
				notExistModelNumbers[className] = modelPaths
			if Paths == []: continue
			loseObjModels[className] = Paths
		if returnString == "ObjModels":
			return notExistModelNumbers		# 打印NPCModelConfig中不存在的模型编号
		elif returnString == "loseObjModels":
			return loseObjModels

	def checkParticleResources( self ):
		"""
		光效配置检测，返回与光效ID对应的不存在的光效文件路径
		"""
		loseEffectXmls = {}
		effectDatas = rds.spellEffect.getEffectXml()	# 获取所有光效配置用到的光效xml文件
		for particleID, xml in effectDatas.items():
			if not xml.endswith( ".xml" ): continue
			xmlList = self.__getPathXmls( xml )
			if not xml in xmlList:	# 没有光效文件存在
				loseEffectXmls[particleID] = xml
		return loseEffectXmls

	def checkItemIconResources( self ):
		"""
		物品配置检测，返回与物品ID对应的不存在的图标文件路径
		"""
		loseItemIcons = {}
		iconDatas = self.__getIcons()
		files = os.listdir( "icons/" )	# 获取所有的图标文件
		icons = []
		for file in files:
			lfile = file.lower()	# 大小写转换
			ufile = file .upper()
			ufile = ufile.replace( "DDS", "dds" )
			icons.append( lfile )
			icons.append( ufile )
		icons.extend( files )
		for itemID, icon in iconDatas.items():
			if not icon in icons:	# 没有图标文件存在
				iconPath = "icons/" + icon
				loseItemIcons[itemID] = iconPath
		return loseItemIcons

	def checkItemModelResources( self, returnString ):
		"""
		物品配置检测，返回与物品ID对应的无法创建的模型路径
		分为掉落模型路径、主模型路径以及次模型路径
		"""
		loseItemModels = {}
		loseItemModels["model_drop"] = {}
		loseItemModels["model_main"] = {}
		loseItemModels["model_fit"] = {}
		itemDModelPaths = self.__getItemModelPaths( "model_drop" )
		for itemID, modelPath in itemDModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# 模型创建失败表示模型资源有问题
				loseItemModels["model_drop"][itemID] = modelPath
		itemMModelPaths = self.__getItemModelPaths( "model_source1" )
		for itemID, modelPath in itemMModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# 模型创建失败表示模型资源有问题
				loseItemModels["model_main"][itemID] = modelPath
		itemFModelPaths = self.__getItemModelPaths( "model_source2" )
		for itemID, modelPath in itemFModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# 模型创建失败表示模型资源有问题
				loseItemModels["model_fit"][itemID] = modelPath
		if returnString == "itemModels":
			return self.__loadItemModelResources( "itemModels" )
		elif returnString == "loseItemModels":
			return loseItemModels

	def checkSpaceModelResources( self, returnString ):
		"""
		地图配置检测，返回地图中无法创建的模型路径
		"""
		loseSpaceModels = []
		notExistModelNumbers = []
		modelNumbers = self.__getSpaceModelDatas( "modelNumber" )
		for modelNumber in modelNumbers:
			paths = rds.npcModel.getModelSources( modelNumber )
			if paths == []:		# 没有模型路径显示有问题的模型编号
				notExistModelNumbers.append( modelNumber )
			model = rds.effectMgr.createModel( paths )
			if model is None:		# 模型创建失败表示模型资源有问题
				loseSpaceModels.extend( paths )
		modelFiles = self.__getSpaceModelDatas( "modelFile" )
		for modelFile in modelFiles:
			xModel = rds.effectMgr.createModel( [modelFile] )
			if xModel is None:	# 模型创建失败表示模型资源有问题
				loseSpaceModels.append( modelFile )
		loseSpaceModels = list( set( loseSpaceModels ) )	# 去掉可能一样的
		if returnString == "spaceModels":
			return notExistModelNumbers		# 打印space配置中不存在的模型编号
		elif returnString == "loseSpaceModels":
			return loseSpaceModels

	def checkSpaceMapResources( self ):
		"""
		地图配置检测，返回与地图路径对应的不存在的地图资源路径
		"""
		loseSpaceMaps = {}
		mapFiles, sections = self.__loadSpaceResources()
		for space, map in mapFiles.items():
			try:
				mapFiles = os.listdir( map )
			except:
				mapFiles = []
			if mapFiles == []:	# 不存在地图资源
				loseSpaceMaps[space] = map
		return loseSpaceMaps

	def checkBigMapResources( self ):
		"""
		大地图配置检测，返回与地图名对应的不存在的地图贴图资源路径
		"""
		loseBigMaps = {}
		loseBigMaps["bigmaps"] = {}
		loseBigMaps["bigmapsky"] = {}
		sections_1, sections_2 = self.__loadBigMapResources()
		for spaceName, tgas in sections_1.items():
			tgasList = []
			for tga in tgas:
				tga = tga.replace( ".tga", ".dds" )
				tgaList = self.__getPathTgas( tga )
				if not tga in tgaList:
					tgasList.append( tga )
			if tgasList == []: continue
			loseBigMaps["bigmaps"][spaceName] = tgasList
		for spaceName, tgas in sections_2.items():
			tgasList = []
			for tga in tgas:
				tga = tga.replace( ".tga", ".dds" )
				tgaList = self.__getPathTgas( tga )
				if not tga in tgaList:
					tgasList.append( tga )
			if tgasList == []: continue
			loseBigMaps["bigmapsky"][spaceName] = tgasList
		return loseBigMaps

	def checkModelHeadTgaResources( self ):
		"""
		模型头像贴图配置检测，返回与模型编号对应的不存在的头像贴图资源路径
		"""
		loseModelHeadTgas = {}
		headTgas = self.__loadHeadTgaResources()
		for modelNumber, headTga in headTgas.items():
			headTga = headTga.replace( ".tga", ".dds" )
			headTgaList = self.__getPathTgas( headTga )
			if not headTga in headTgaList:
				loseModelHeadTgas[modelNumber] = headTga
		return loseModelHeadTgas

	def checkSkillTgaResources( self, returnString ):
		"""
		技能贴图配置检测，返回与技能ID对应的不存在的贴图资源路径
		"""
		loseSkillTgas = {}
		skillTgas = self.__loadSkillTgaResources( "loseSkillTgas" )
		for skillID, tga in skillTgas.items():
			tga = tga.replace( ".tga", ".dds" )
			tgaList = self.__getPathTgas( tga )
			if not tga in tgaList:
				loseSkillTgas[skillID] = tga
		if returnString == "skillTgas":
			return self.__loadSkillTgaResources( "skillTgas" )
		elif returnString == "loseSkillTgas":
			return loseSkillTgas


check = CheckResources.instance()

def lose( a ):
	"""
	字典处理函数
	"""
	newA = {}
	newB = {}
	listK = []
	listV = []
	Vlist = []
	listS = []	# 特殊处理
	if type(a) == type({}):
		for key, value in a.items():
			listK.append( key )
			if type( value ) == type({}):
				listS.append( value )
			elif type( value ) == type([]):
				for v in value:
					Vlist.append( v )
			else:
				listV.append( value )
		listK = list( set(listK) )
		listV = list( set(listV) )
		Vlist = list( set(Vlist) )
		for value in listV:
			Klist = []
			for key in listK:
				if a.get(key) == value:
					Klist.append(key)
			if Klist == []: continue
			newA[value] = Klist
		for value in Vlist:
			Klist = []
			for key in listK:
				if value in a.get(key) and value != a.get(key):
					Klist.append(key)
			if Klist == []: continue
			newA[value] = Klist
	elif type(a) == type([]):
		newA["loseResources"] = a		# 此处"loseResources"只是标示符，无其他意义
	for d in listS:
		newB.update( d )
	return newA, newB

def checkResult():
	"""
	检测结果，输出在love3/res/loseResources.txt中
	"""
	m = []
	print "++++++++++ check start!"
	result = check.checkResources()
	for key, value in result.items():
		if key == "loseObjModels":
			m.append( "缺失的模型资源路径：对应的怪物className列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseEffectXmls":
			m.append( "缺失的光效资源路径：对应的光效ID列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseItemIcons":
			m.append( "缺失的物品贴图资源路径：对应的物品ID列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseItemModels":
			m.append( "缺失的物品模型资源路径：对应的物品ID列表\n" )
			newA, newB = lose(value)
			A, B = lose( newB )  # 特殊处理
			if A == {}:
				m.append( str( A ) + "\n" )
			else:
				for k, v in A.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseSpaceModels":
			m.append( "不存在的模型资源路径列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # 一行行的输出
		elif key == "loseSpaceMaps":
			m.append( "缺失的地图资源路径：对应的地图名称列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseBigMaps":
			m.append( "缺失的大地图贴图资源路径：对应的地图名称列表\n" )
			newA, newB = lose(value)
			A, B = lose( newB )  # 特殊处理
			if A == {}:
				m.append( str( A ) + "\n" )
			else:
				for k, v in A.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "loseModelHeadTgs":
			m.append( "缺失的模型头像贴图资源路径：对应的模型编号列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "itemModels":
			m.append( "config/client/ItemModel配置中不存在的模型编号：对应的物品ID列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "spaceModels":
			m.append( "config/client/NPCModelConfig配置中不存在的模型编号列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # 一行行的输出
		elif key == "ObjModels":
			m.append( "config/client/NPCModelConfig配置中不存在的模型编号：对应的怪物className列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		elif key == "skillTgas":
			m.append( "config/client/SkillEffect/SpellEffect.py配置中没有配置贴图的技能ID列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # 一行行的输出
		elif key == "loseSkillTgas":
			m.append( "缺失的技能贴图资源路径：对应的技能ID列表\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # 一行行的输出
		m.append( "\n" )
	print "++++++++++ check over!"
	f = open( "loseResources.txt", "w" )
	f.writelines(m)
	f.close()

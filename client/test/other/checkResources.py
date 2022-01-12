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
	��Դ���ģ�飨CSOL-1458��
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
		Obj���ü���
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
		��ȡObj����ģ�ͱ������
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
		��ȡָ����Ч·���������ļ����б�
		"""
		xmlList = []
		paths = xml.split("/")
		dxml = paths[len( paths ) - 1]	# ������־��
		path = xml.replace( dxml, "" )
		try:
			files = os.listdir( path )
		except:
			files = []
		for file in files:
			axml = path + file
			lxml = axml.lower()		# ��Сдת��
			uxml = axml.upper()
			uxml = uxml.replace( "XML", "xml" )
			xmlList.append( axml )
			xmlList.append( lxml )
			xmlList.append( uxml )
		return xmlList

	def __getIcons( self ):
		"""
		��ȡ������Ʒͼ��·������
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
		��ͼ���ü���
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
		��ȡ��ͼ����ģ��·��/ģ�ͱ��
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
		��Ʒģ����Դ����
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
			return notExistItemModelIDs		# ��ӡItemModel�в����ڵ���Ʒģ��ID
		elif returnString == "loseItemModels":
			return itemModelDatas

	def __getItemModelPaths( self, modelString ):
		"""
		��ȡ��Ʒ����ģ��·�����ݣ�����ģ��/��ģ��/��ģ�ͣ�
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
		���ͼ��ͼ��Դ����
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
		��ȡָ����ͼ·���������ļ����б�
		"""
		tgaList = []
		paths = tga.split("/")
		dtga = paths[len( paths ) - 1]	# ������־��
		path = tga.replace( dtga, "" )
		try:
			files = os.listdir( path )
		except:
			files = []
		for file in files:
			atga = path + file
			ltga = atga.lower()		# ��Сдת��
			utga = atga.upper()
			utga = utga.replace( "DDS", "dds" )
			tgaList.append( atga )
			tgaList.append( ltga )
			tgaList.append( utga )
		return tgaList

	def __loadHeadTgaResources( self ):
		"""
		ģ��ͷ����ͼ���ü���
		"""
		headTgas = {}
		for modelNumber in NPCModelConfig.Datas.keys():
			headTga = rds.npcModel.getHeadTexture( modelNumber )
			if headTga == "": continue
			headTgas[modelNumber] = headTga
		return headTgas

	def __loadSkillTgaResources( self, returnString ):
		"""
		������ͼ���ü���
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
		��Դ����ܵ���ڣ���������еļ���ӷ���
		# datas/...|config/...��ʾ�÷�����������Դ·��
		# ˽�з����������ERROR_MSGҲ�Ǵ�������
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
		Obj���ü�⣬������Obj��className��Ӧ���޷�������ģ��·��
		"""
		loseObjModels = {}
		notExistModelNumbers = {}
		modelDatas = self.__getObjModelDatas()
		for className, modelNumbers in modelDatas.items():
			Paths = []
			modelPaths = []
			for modelNumber in modelNumbers:
				paths = rds.npcModel.getModelSources( modelNumber )
				if paths == []:		# û��ģ��·����ʾ�������ģ�ͱ��
					modelPaths.append( modelNumber )
				model = rds.effectMgr.createModel( paths )
				if model is None:		# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
					Paths.extend( paths )
			if modelPaths != []:
				notExistModelNumbers[className] = modelPaths
			if Paths == []: continue
			loseObjModels[className] = Paths
		if returnString == "ObjModels":
			return notExistModelNumbers		# ��ӡNPCModelConfig�в����ڵ�ģ�ͱ��
		elif returnString == "loseObjModels":
			return loseObjModels

	def checkParticleResources( self ):
		"""
		��Ч���ü�⣬�������ЧID��Ӧ�Ĳ����ڵĹ�Ч�ļ�·��
		"""
		loseEffectXmls = {}
		effectDatas = rds.spellEffect.getEffectXml()	# ��ȡ���й�Ч�����õ��Ĺ�Чxml�ļ�
		for particleID, xml in effectDatas.items():
			if not xml.endswith( ".xml" ): continue
			xmlList = self.__getPathXmls( xml )
			if not xml in xmlList:	# û�й�Ч�ļ�����
				loseEffectXmls[particleID] = xml
		return loseEffectXmls

	def checkItemIconResources( self ):
		"""
		��Ʒ���ü�⣬��������ƷID��Ӧ�Ĳ����ڵ�ͼ���ļ�·��
		"""
		loseItemIcons = {}
		iconDatas = self.__getIcons()
		files = os.listdir( "icons/" )	# ��ȡ���е�ͼ���ļ�
		icons = []
		for file in files:
			lfile = file.lower()	# ��Сдת��
			ufile = file .upper()
			ufile = ufile.replace( "DDS", "dds" )
			icons.append( lfile )
			icons.append( ufile )
		icons.extend( files )
		for itemID, icon in iconDatas.items():
			if not icon in icons:	# û��ͼ���ļ�����
				iconPath = "icons/" + icon
				loseItemIcons[itemID] = iconPath
		return loseItemIcons

	def checkItemModelResources( self, returnString ):
		"""
		��Ʒ���ü�⣬��������ƷID��Ӧ���޷�������ģ��·��
		��Ϊ����ģ��·������ģ��·���Լ���ģ��·��
		"""
		loseItemModels = {}
		loseItemModels["model_drop"] = {}
		loseItemModels["model_main"] = {}
		loseItemModels["model_fit"] = {}
		itemDModelPaths = self.__getItemModelPaths( "model_drop" )
		for itemID, modelPath in itemDModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
				loseItemModels["model_drop"][itemID] = modelPath
		itemMModelPaths = self.__getItemModelPaths( "model_source1" )
		for itemID, modelPath in itemMModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
				loseItemModels["model_main"][itemID] = modelPath
		itemFModelPaths = self.__getItemModelPaths( "model_source2" )
		for itemID, modelPath in itemFModelPaths.items():
			model = rds.effectMgr.createModel( modelPath )
			if model is None:	# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
				loseItemModels["model_fit"][itemID] = modelPath
		if returnString == "itemModels":
			return self.__loadItemModelResources( "itemModels" )
		elif returnString == "loseItemModels":
			return loseItemModels

	def checkSpaceModelResources( self, returnString ):
		"""
		��ͼ���ü�⣬���ص�ͼ���޷�������ģ��·��
		"""
		loseSpaceModels = []
		notExistModelNumbers = []
		modelNumbers = self.__getSpaceModelDatas( "modelNumber" )
		for modelNumber in modelNumbers:
			paths = rds.npcModel.getModelSources( modelNumber )
			if paths == []:		# û��ģ��·����ʾ�������ģ�ͱ��
				notExistModelNumbers.append( modelNumber )
			model = rds.effectMgr.createModel( paths )
			if model is None:		# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
				loseSpaceModels.extend( paths )
		modelFiles = self.__getSpaceModelDatas( "modelFile" )
		for modelFile in modelFiles:
			xModel = rds.effectMgr.createModel( [modelFile] )
			if xModel is None:	# ģ�ʹ���ʧ�ܱ�ʾģ����Դ������
				loseSpaceModels.append( modelFile )
		loseSpaceModels = list( set( loseSpaceModels ) )	# ȥ������һ����
		if returnString == "spaceModels":
			return notExistModelNumbers		# ��ӡspace�����в����ڵ�ģ�ͱ��
		elif returnString == "loseSpaceModels":
			return loseSpaceModels

	def checkSpaceMapResources( self ):
		"""
		��ͼ���ü�⣬�������ͼ·����Ӧ�Ĳ����ڵĵ�ͼ��Դ·��
		"""
		loseSpaceMaps = {}
		mapFiles, sections = self.__loadSpaceResources()
		for space, map in mapFiles.items():
			try:
				mapFiles = os.listdir( map )
			except:
				mapFiles = []
			if mapFiles == []:	# �����ڵ�ͼ��Դ
				loseSpaceMaps[space] = map
		return loseSpaceMaps

	def checkBigMapResources( self ):
		"""
		���ͼ���ü�⣬�������ͼ����Ӧ�Ĳ����ڵĵ�ͼ��ͼ��Դ·��
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
		ģ��ͷ����ͼ���ü�⣬������ģ�ͱ�Ŷ�Ӧ�Ĳ����ڵ�ͷ����ͼ��Դ·��
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
		������ͼ���ü�⣬�����뼼��ID��Ӧ�Ĳ����ڵ���ͼ��Դ·��
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
	�ֵ䴦����
	"""
	newA = {}
	newB = {}
	listK = []
	listV = []
	Vlist = []
	listS = []	# ���⴦��
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
		newA["loseResources"] = a		# �˴�"loseResources"ֻ�Ǳ�ʾ��������������
	for d in listS:
		newB.update( d )
	return newA, newB

def checkResult():
	"""
	������������love3/res/loseResources.txt��
	"""
	m = []
	print "++++++++++ check start!"
	result = check.checkResources()
	for key, value in result.items():
		if key == "loseObjModels":
			m.append( "ȱʧ��ģ����Դ·������Ӧ�Ĺ���className�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseEffectXmls":
			m.append( "ȱʧ�Ĺ�Ч��Դ·������Ӧ�Ĺ�ЧID�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseItemIcons":
			m.append( "ȱʧ����Ʒ��ͼ��Դ·������Ӧ����ƷID�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseItemModels":
			m.append( "ȱʧ����Ʒģ����Դ·������Ӧ����ƷID�б�\n" )
			newA, newB = lose(value)
			A, B = lose( newB )  # ���⴦��
			if A == {}:
				m.append( str( A ) + "\n" )
			else:
				for k, v in A.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseSpaceModels":
			m.append( "�����ڵ�ģ����Դ·���б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # һ���е����
		elif key == "loseSpaceMaps":
			m.append( "ȱʧ�ĵ�ͼ��Դ·������Ӧ�ĵ�ͼ�����б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseBigMaps":
			m.append( "ȱʧ�Ĵ��ͼ��ͼ��Դ·������Ӧ�ĵ�ͼ�����б�\n" )
			newA, newB = lose(value)
			A, B = lose( newB )  # ���⴦��
			if A == {}:
				m.append( str( A ) + "\n" )
			else:
				for k, v in A.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "loseModelHeadTgs":
			m.append( "ȱʧ��ģ��ͷ����ͼ��Դ·������Ӧ��ģ�ͱ���б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "itemModels":
			m.append( "config/client/ItemModel�����в����ڵ�ģ�ͱ�ţ���Ӧ����ƷID�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "spaceModels":
			m.append( "config/client/NPCModelConfig�����в����ڵ�ģ�ͱ���б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # һ���е����
		elif key == "ObjModels":
			m.append( "config/client/NPCModelConfig�����в����ڵ�ģ�ͱ�ţ���Ӧ�Ĺ���className�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		elif key == "skillTgas":
			m.append( "config/client/SkillEffect/SpellEffect.py������û��������ͼ�ļ���ID�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(v) + "\n" )	 # һ���е����
		elif key == "loseSkillTgas":
			m.append( "ȱʧ�ļ�����ͼ��Դ·������Ӧ�ļ���ID�б�\n" )
			newA, newB = lose(value)
			if newA == {}:
				m.append( str( newA ) + "\n" )
			else:
				for k, v in newA.items():
					m.append( str(k) + ":" + str(v) + "\n" )	 # һ���е����
		m.append( "\n" )
	print "++++++++++ check over!"
	f = open( "loseResources.txt", "w" )
	f.writelines(m)
	f.close()

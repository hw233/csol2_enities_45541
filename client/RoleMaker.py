# -*- coding: gb18030 -*-

# $Id: RoleMaker.py,v 1.34 2008-09-01 03:24:36 wangshufeng Exp $


"""
for making role model
-- 2006/04/21 written by huangyongwei
"""

from bwdebug import *
import BigWorld
import Language
import csdefine
import csconst
import ItemTypeEnum
from gbref import rds
import Const
import Define

# --------------------------------------------------------------------
# get RoleInfo instance via profession
# --------------------------------------------------------------------
def getCommonRoleInfo( profession, gender = csdefine.GENDER_MALE ) :
	race = csconst.RACE_CLASS_MAP[profession]
	infoDict 					= {}
	infoDict["raceclass"] 		= race | profession | gender
	infoDict["roleID"] 			= 0
	infoDict["roleName"] 		= ""
	infoDict["level"] 			= 1
	infoDict["hairNumber"] 		= 0
	infoDict["faceNumber"] 		= 0
	infoDict["bodyFDict"] 		= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][0], "iLevel" : 4 }
	infoDict["volaFDict"] 		= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][1], "iLevel" : 4 }
	infoDict["breechFDict"] 	= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][2], "iLevel" : 4 }
	infoDict["feetFDict"] 		= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][3], "iLevel" : 4 }
	infoDict["righthandFDict"] 	= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][4], "iLevel" : 9, "stAmount" : 0 }
	infoDict["lefthandFDict"] 	= {"modelNum" : Const.ROLE_CREATE_EQUIP_MAP[profession][5], "iLevel" : 9, "stAmount" : 0 }
	infoDict["talismanNum"] 	= 0
	infoDict["fashionNum"] 		= 0
	infoDict["adornNum"]	 	= 0
	infoDict["headTextureID"]	= 0		# 自定义头像贴图 by姜毅
	roleInfo = RoleInfo( infoDict )
	return roleInfo

# 角色默认的模型信息，创建角色模型失败时会尝试用此信息来再次创建
MODEL_DEFAULT_INFO = { "hairNumber" : 0, \
								"faceNumber" : 0, \
								"bodyFDict" : {'modelNum': 0, 'iLevel': 0}, \
								"volaFDict" : {'modelNum': 0, 'iLevel': 0}, \
								"breechFDict" : {'modelNum': 0, 'iLevel': 0}, \
								"feetFDict" : {'modelNum': 0, 'iLevel': 0}, \
								"lefthandFDict" : {'stAmount': 0, 'modelNum': 0, 'iLevel': 0}, \
								"righthandFDict" : {'stAmount': 0, 'modelNum': 0, 'iLevel': 0}, \
								"headTextureID" : 10001, \
							}
def getDefaultRoleInfo( infoDict ):
	"""
	@param infoDict : python字典，创建RoleInfo所需信息
	"""
	infoDict.update( MODEL_DEFAULT_INFO )
	return RoleInfo( infoDict )


# --------------------------------------------------------------------
# implement role information class
# --------------------------------------------------------------------
class RoleInfo :
	def __init__( self, infoDict ) :
		"""
		Constructor.
		@type			infoDict : dict
		@param			infoDict : role info dictionary
		"""
		self.__info = infoDict
		self.__roleID = infoDict["roleID"]
		self.__roleName = infoDict["roleName"]
		self.__level = infoDict["level"]
		self.__raceclass = infoDict["raceclass"]
		self.__bodyFDict = infoDict["bodyFDict"]			# 自定义数据类型ARMOR_EFFECT
		self.__volaFDict = infoDict["volaFDict"]			# 自定义数据类型ARMOR_EFFECT
		self.__breechFDict = infoDict["breechFDict"]		# 自定义数据类型ARMOR_EFFECT
		self.__feetFDict = infoDict["feetFDict"]			# 自定义数据类型ARMOR_EFFECT
		self.__lefthandFDict = infoDict["lefthandFDict"]	# 自定义数据类型WEAPON_EFFECT
		self.__righthandFDict = infoDict["righthandFDict"]	# 自定义数据类型WEAPON_EFFECT
		self.__talismanNum = infoDict["talismanNum"]
		self.__fashionNum = infoDict["fashionNum"]
		self.__adornNum = infoDict["adornNum"]
		self.__headTextureID = infoDict["headTextureID"]	# 自定义头像贴图 by姜毅

	def getID( self ) :
		"""
		role ID
		"""
		return self.__roleID

	def getName( self ) :
		"""
		role name
		"""
		return self.__roleName

	def getLevel( self ) :
		"""
		level
		"""
		return self.__level

	def getRaceClass( self ) :
		"""
		race | calss | gender
		"""
		return self.__raceclass

	def getRace( self ) :
		"""
		race
		"""
		return self.__raceclass & csdefine.RCMASK_RACE

	def getClass( self ) :
		"""
		profession
		"""
		return self.__raceclass & csdefine.RCMASK_CLASS

	def getGender( self ) :
		"""
		gender
		"""
		return self.__raceclass & csdefine.RCMASK_GENDER

	def resetGender( self, gender ) :
		"""
		reset gender
		"""
		race = self.getRace()
		profession = self.getClass()
		self.__raceclass = race | profession | gender

	def getHairNumber( self ) :
		"""
		get hair Number
		"""
		return self.__info["hairNumber"]

	def getFaceNumber( self ) :
		"""
		get face Number
		"""
		return self.__info["faceNumber"]

	def getBodyFDict( self ) :
		"""
		获取上身的数据
		"""
		return self.__bodyFDict

	def getVolaFDict( self ) :
		"""
		获取手套的数据
		"""
		return self.__volaFDict

	def getBreechFDict( self ) :
		"""
		获取下身的数据
		"""
		return self.__breechFDict

	def getFeetFDict( self ) :
		"""
		获取鞋子的数据
		"""
		return self.__feetFDict

	def getLHFDict( self ) :
		"""
		获取左手武器数据
		"""
		return self.__lefthandFDict

	def getRHFDict( self ):
		"""
		获取右手武器数据
		"""
		return self.__righthandFDict

	def getTalismanNum( self ):
		"""
		获取法宝模型编号
		"""
		return self.__talismanNum

	def getFashionNum( self ):
		"""
		获取时装模型编号
		"""
		return self.__info["fashionNum"]

	def getAdornNum( self ):
		"""
		获取饰品模型编号
		"""
		return self.__adornNum

	def getLevelStr( self ) :
		"""
		get type string of level
		"""
		return str( self.__level )

	def getCHClass( self ) :
		"""
		获取角色职业的中文名
		"""
		return csconst.g_chs_class[self.getClass()]

	def getHeadTextureID( self ):
		"""
		获取角色的头像ID by姜毅
		"""
		if self.__headTextureID is None: return 0
		return self.__headTextureID
		
	def getRoleInfo( self ):
		"""
		获取角色信息字典
		"""
		return self.__info

	def update( self, dict ):
		"""
		更新数值
		"""
		self.__info.update( dict )

# --------------------------------------------------------------------
# implement role model maker
# --------------------------------------------------------------------
class RoleModelMaker :
	__instance = None

	def __init__( self ) :
		assert RoleModelMaker.__instance is None

	@classmethod
	def instance( SELF ):
		if SELF.__instance is None:
			SELF.__instance = RoleModelMaker()
		return SELF.__instance

	# --------------------------------------------------------------------
	# 角色模型最终显示路径
	# --------------------------------------------------------------------
	def getShowModelPath( self, roleInfo ):
		"""
		返回显示模型路径
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@return 				: list of string
		"""
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		fashionNum = roleInfo.getFashionNum()
		if fashionNum:
			subModels = self.getFashionModelPath( fashionNum, profession, gender )
			faceNum = roleInfo.getFaceNumber()
			facePaths = self.getFaceModelPath( faceNum, profession, gender )
			subModels.extend( facePaths )
		else:
			subModels = self.getPartModelPath( roleInfo )
		return subModels

	def getShowModelDyes( self, roleInfo ):
		"""
		返回显示模型路径和dyes
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@return                 : ( [], [] )
		"""
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		fashionNum = roleInfo.getFashionNum()
		if fashionNum:
			subDyes = self.getFashionModelDyes( fashionNum, gender, profession )
			faceNum = roleInfo.getFaceNumber()
			faceDyes = self.getFaceModelDyes( faceNum, profession, gender )
			subDyes.extend( faceDyes )
		else:
			subDyes = self.getPartModelDyes( roleInfo )
		return subDyes

	# --------------------------------------------------------------------
	# 整个身体模型
	# --------------------------------------------------------------------
	def getPartModelPath( self, roleInfo ):
		"""
		返回整体模型path
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@return 				: list of string
		"""
		subModels = []
		# 职业和性别
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		#脸部的模型路径和Dye
		faceNum = roleInfo.getFaceNumber()
		facePath = self.getFaceModelPath( faceNum, profession, gender )
		subModels.extend( facePath )
		# 上身的模型路径和Dye
		bodyFDict = roleInfo.getBodyFDict()
		bodyPath = self.getBodyModelPath( bodyFDict, profession, gender )
		subModels.extend( bodyPath )
		# 手套的模型路径和Dye
		volaFDict = roleInfo.getVolaFDict()
		volaPath = self.getVolaModelPath( volaFDict, profession, gender )
		subModels.extend( volaPath )
		# 下身的模型路径和Dye
		breechFDict = roleInfo.getBreechFDict()
		breechPath = self.getBreechModelPath( breechFDict, profession, gender )
		subModels.extend( breechPath )
		# 鞋子的模型路径和Dye
		feetFDict = roleInfo.getFeetFDict()
		feetPath = self.getFeetModelPath( feetFDict, profession, gender )
		subModels.extend( feetPath )

		return subModels

	def getPartModelDyes( self, roleInfo ):
		"""
		返回整体模型dyes
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@return                 : ( [], [] )
		"""
		subDyes = []
		# 职业和性别
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		#脸部的模型Dye
		faceNum = roleInfo.getFaceNumber()
		faceDyes = self.getFaceModelDyes( faceNum, profession, gender )
		subDyes.extend( faceDyes )
		# 上身的模型Dye
		bodyFDict = roleInfo.getBodyFDict()
		bodyDyes = self.getBodyModelDyes( bodyFDict, profession, gender )
		subDyes.extend( bodyDyes )
		# 手套的模型Dye
		volaFDict = roleInfo.getVolaFDict()
		volaDyes = self.getVolaModelDyes( volaFDict, profession, gender )
		subDyes.extend( volaDyes )
		# 下身的模型Dye
		breechFDict = roleInfo.getBreechFDict()
		breechDyes = self.getBreechModelDyes( breechFDict, profession, gender )
		subDyes.extend( breechDyes )
		# 鞋子的模型Dye
		feetFDict = roleInfo.getFeetFDict()
		feetDyes = self.getFeetModelDyes( feetFDict, profession, gender )
		subDyes.extend( feetDyes )

		return subDyes

	def createPartModel( self, roleInfo ):
		"""
		后线程创建整个身体模型
		因为这种模型是不单独存在的，需创建头，脸，身体，手套，下身，鞋子6部分模型
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@return				   	: PyModel
		"""
		subModels = self.getShowModelPath( roleInfo )
		subDyes = self.getShowModelDyes( roleInfo )
		return rds.effectMgr.createModel( subModels, subDyes )

	def createPartModelBG( self, entityID, roleInfo, callback = None ):
		"""
		后线程创建整个身体模型
		因为这种模型是不单独存在的，需创建头，脸，身体，手套，下身，鞋子6部分模型
		@type		roleInfo 	: dict
		@param		roleInfo 	: 角色的模型数据
		@type		callback 	: func
		@param		callback 	: 模型创建好的回调
		@return				   	: None
		"""
		def onModelLoad( modelDict ):
			model = modelDict.get( Define.MODEL_EQUIP_MAIN, None )
			self.partModelAttachEffect( model, roleInfo )
			if callable( callback ):
				callback( model )
		paths = {}
		subModels = self.getShowModelPath( roleInfo )
		paths[Define.MODEL_EQUIP_MAIN] = subModels
		rds.modelFetchMgr.fetchModels( entityID, onModelLoad, paths )

	def partModelAttachEffect( self, partModel, roleInfo ):
		"""
		整个身体模型附加效果
		"""
		# 模型Dyes
		subDyes = self.getShowModelDyes( roleInfo )
		rds.effectMgr.createModelDye( partModel, subDyes )

	# --------------------------------------------------------------------
	# 头发
	# --------------------------------------------------------------------
	def getHairModelPath( self, hairNumber, fashionNum, profession, gender ):
		"""
		返回角色发型路径(大爷的，头发跟时装扯上关系了)
		@type		hairNumber 	: Int32
		@param		hairNumber 	: 角色的发型编号
		@type		fashionNum 	: Int32
		@param		fashionNum 	: 角色的时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: list of string
		@return				   	: 返回所包含的模型路径
		"""
		# 有时装的情况下，将优先返回时装的模型编号
		if fashionNum != 0:
			return rds.itemModel.getSHeadSource( fashionNum, gender, profession )

		if hairNumber == 0 :
			hairNumber = Const.ROLE_EQUIP_HAIR_MAP.get( profession | gender )
			if hairNumber is None: return []
		return rds.itemModel.getMSource( hairNumber )

	def getHairModelDyes( self, hairNumber, fashionNum, profession, gender ):
		"""
		返回角色发型Dyes
		@type		hairNumber 	: Int32
		@param		hairNumber 	: 角色的发型编号
		@type		fashionNum 	: Int32
		@param		fashionNum 	: 角色的时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: String
		@return				   	: 返回发型Dyes
		"""
		# 有时装的情况下，将优先返回时装的模型Dyes
		if fashionNum != 0:
			return rds.itemModel.getSHeadDyes( fashionNum, gender, profession )

		if hairNumber == 0 :
			hairNumber = Const.ROLE_EQUIP_HAIR_MAP.get( profession | gender )
			if hairNumber is None: return []
		return rds.itemModel.getMDyes( hairNumber )

	def hairModelAttachEffect( self, hairModel, hairNumber, fashionNum, profession, gender ):
		"""
		头发附加效果
		@type		model		: PyModel
		@param		model		: 法宝模型
		@type		hairNumber	: INT32
		@param		hairNumber	: 头发模型编号
		@type		fashionNum 	: Int32
		@param		fashionNum 	: 角色的时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		"""
		# 模型Dyes
		hairDyes = self.getHairModelDyes( hairNumber, fashionNum, profession, gender )
		rds.effectMgr.createModelDye( hairModel, hairDyes )

	def createHairModel( self, hairNumber, fashionNum, profession, gender ):
		"""
		主线程创建发型模型
		@type		hairNumber 	: Int32
		@param		hairNumber 	: 角色的发型编号
		@type		fashionNum 	: Int32
		@param		fashionNum 	: 角色的时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@return 				: pyModel
		"""
		# 获取路径信息
		paths = self.getHairModelPath( hairNumber, fashionNum, profession, gender )
		# 创建模型
		hairModel = rds.effectMgr.createModel( paths )
		self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
		return hairModel

	def createHairModelBG( self, hairNumber, fashionNum, profession, gender, callback = None ):
		"""
		后线程创建发型模型
		@type		hairNumber 	: Int32
		@param		hairNumber 	: 角色的发型编号
		@type		fashionNum 	: Int32
		@param		fashionNum 	: 角色的时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@type		callback	: func
		@param		callback	: 创建模型后返回
		@return 				: None
		"""
		def onModelLoad( hairModels ):
			hairModel = hairModels.get( Define.MODEL_EQUIP_HEAD )
			self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
			if callable( callback ):
				callback( hairModel )

		hairPaths = self.getHairModelPath( hairNumber, fashionNum, profession, gender )			# 获取路径信息
		rds.modelFetchMgr.fetchModels( 0, onModelLoad, {Define.MODEL_EQUIP_HEAD:hairPaths} )	# 创建模型

	# --------------------------------------------------------------------
	# 脸
	# --------------------------------------------------------------------
	def getFaceModelPath( self, faceNumber, profession, gender ) :
		"""
		返回脸型路径
		@type		faceNumber 	: Int32
		@param		faceNumber 	: 角色的脸型编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: list of string
		@return				   	: 返回所包含的模型路径
		"""
		if faceNumber == 0 :
			faceNumber = Const.ROLE_EQUIP_FACE_MAP.get( profession | gender )
			if faceNumber is None: return []
		return rds.itemModel.getMSource( faceNumber )

	def getFaceModelDyes( self, faceNumber, profession, gender ) :
		"""
		返回脸型Dyes
		@type		faceNumber 	: Int32
		@param		faceNumber 	: 角色的脸型编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: String
		@return				   	: 返回脸型Dyes
		"""
		if faceNumber == 0 :
			faceNumber = Const.ROLE_EQUIP_FACE_MAP.get( profession | gender )
			if faceNumber is None: return []
		return rds.itemModel.getMDyes( faceNumber )

	# --------------------------------------------------------------------
	# 上身
	# --------------------------------------------------------------------
	def getBodyModelPath( self, bodyFDict, profession, gender ) :
		"""
		返回上身模型路径
		@type		bodyFDict 	: FDict
		@param		bodyFDict 	: 角色的上身模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: List of String
		@return				   	: 返回所包含的模型路径
		"""
		bodyNum = bodyFDict["modelNum"]
		if bodyNum == 0:
			bodyNum = Const.ROLE_EQUIP_BODY_MAP.get( profession )
			if bodyNum is None: return []
		return rds.itemModel.getGSource( bodyNum, gender )

	def getBodyModelDyes( self, bodyFDict, profession, gender ) :
		"""
		返回上身模型Dyes
		@type		bodyFDict 	: FDict
		@param		bodyFDict 	: 角色的上身模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: string
		@return				   	: 返回所上身Dyes
		"""
		bodyNum = bodyFDict["modelNum"]
		if bodyNum == 0:
			bodyNum = Const.ROLE_EQUIP_BODY_MAP.get( profession )
			if bodyNum is None: return []

		dyes = rds.itemModel.getGDyes( bodyNum, gender )
		iLevel = bodyFDict["iLevel"]
		if iLevel >= Const.EQUIP_ARMOR_FLOW_LEVEL:
			index = Const.ROLE_EQUIP_TINT_MAP.get( profession )
			if index:
				dyes = [ list( k ) for k in dyes ]
				for k in dyes:
					if len( k ) != 2: continue
					k[1] += "_%s" % index
		return dyes

	# --------------------------------------------------------------------
	# 手套
	# --------------------------------------------------------------------
	def getVolaModelPath( self, volaFDict, profession, gender ) :
		"""
		返回手部模型路径
		@type		volaFDict 	: FDict
		@param		volaFDict 	: 角色的手部模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				 	: list of string
		@return				  	: 返回所包含的模型路径
		"""
		volaNum = volaFDict["modelNum"]
		if volaNum == 0:
			volaNum = Const.ROLE_EQUIP_VOLA_MAP.get( profession )
			if volaNum is None: return []
		return rds.itemModel.getGSource( volaNum, gender )

	def getVolaModelDyes( self, volaFDict, profession, gender ) :
		"""
		返回手部模型Dyes
		@type		volaFDict 	: FDict
		@param		volaFDict 	: 角色的手部模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				 	: string
		@return				  	: 返回手部Dyes
		"""
		volaNum = volaFDict["modelNum"]
		if volaNum == 0:
			volaNum = Const.ROLE_EQUIP_VOLA_MAP.get( profession )
			if volaNum is None: return []

		dyes = rds.itemModel.getGDyes( volaNum, gender )
		iLevel = volaFDict["iLevel"]
		if iLevel >= Const.EQUIP_ARMOR_FLOW_LEVEL:
			index = Const.ROLE_EQUIP_TINT_MAP.get( profession )
			if index:
				dyes = [ list( k ) for k in dyes ]
				for k in dyes:
					if len( k ) != 2: continue
					k[1] += "_%s" % index
		return dyes

	# --------------------------------------------------------------------
	# 下身
	# --------------------------------------------------------------------
	def getBreechModelPath( self, breechFDict, profession, gender ) :
		"""
		返回裤子模型路径
		@type		breechFDict	: FDict
		@param		breechFDict	: 角色的裤子模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				 	: List of string
		@return				   	: 返回所包含的模型路径
		"""
		breechNum = breechFDict["modelNum"]
		if breechNum == 0:
			breechNum = Const.ROLE_EQUIP_BREE_MAP.get( profession )
			if breechNum is None: return []
		return rds.itemModel.getGSource( breechNum, gender )

	def getBreechModelDyes( self, breechFDict, profession, gender ) :
		"""
		返回裤子Dyes
		@type		breechFDict	: FDict
		@param		breechFDict	: 角色的裤子模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				 	: string
		@return				   	: 返回裤子Dyes
		"""
		breechNum = breechFDict["modelNum"]
		if breechNum == 0:
			breechNum = Const.ROLE_EQUIP_BREE_MAP.get( profession )
			if breechNum is None: return []

		dyes = rds.itemModel.getGDyes( breechNum, gender )
		iLevel = breechFDict["iLevel"]
		if iLevel >= Const.EQUIP_ARMOR_FLOW_LEVEL:
			index = Const.ROLE_EQUIP_TINT_MAP.get( profession )
			if index:
				dyes = [ list( k ) for k in dyes ]
				for k in dyes:
					if len( k ) != 2: continue
					k[1] += "_%s" % index
		return dyes

	# --------------------------------------------------------------------
	# 鞋子
	# --------------------------------------------------------------------
	def getFeetModelPath( self, feetFDict, profession, gender ) :
		"""
		返回鞋子模型路径
		@type		feetFDict 	: FDict
		@param		feetFDict 	: 角色的鞋子模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: list of string
		@return				   	: 返回所包含的模型路径
		"""
		feetNum = feetFDict["modelNum"]
		if feetNum== 0:
			feetNum = Const.ROLE_EQUIP_FEET_MAP.get( profession )
			if feetNum is None: return []
		return rds.itemModel.getGSource( feetNum, gender )

	def getFeetModelDyes( self, feetFDict, profession, gender ) :
		"""
		返回鞋子Dyes
		@type		feetFDict 	: FDict
		@param		feetFDict 	: 角色的鞋子模型数据
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: string
		@return				   	: 返回鞋子Dyes
		"""
		feetNum = feetFDict["modelNum"]
		if feetNum== 0:
			feetNum = Const.ROLE_EQUIP_FEET_MAP.get( profession )
			if feetNum is None: return []

		dyes = rds.itemModel.getGDyes( feetNum, gender )
		iLevel = feetFDict["iLevel"]
		if iLevel >= Const.EQUIP_ARMOR_FLOW_LEVEL:
			index = Const.ROLE_EQUIP_TINT_MAP.get( profession )
			if index:
				dyes = [ list( k ) for k in dyes ]
				for k in dyes:
					if len( k ) != 2: continue
					k[1] += "_%s" % index
		return dyes

	# --------------------------------------------------------------------
	# 时装
	# --------------------------------------------------------------------
	def getFashionModelPath( self, fashionNum, gender, profession ):
		"""
		返回时装模型路径
		@type		fashionNum 	: INT32
		@param		fashionNum 	: 时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: list of String
		@return				   	: 返回所包含的模型路径
		"""
		return rds.itemModel.getSSource( fashionNum, gender, profession )

	def getFashionModelDyes( self, fashionNum, gender, profession ):
		"""
		返回时装Dyes
		@type		fashionNum 	: INT32
		@param		fashionNum 	: 时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: String
		@return				   	: 返回时装Dyes
		"""
		return rds.itemModel.getSDyes( fashionNum, gender, profession )

	def getFashionHeadModelDyes( self, fashionNum, gender, profession ):
		"""
		返回时装Dyes
		@type		fashionNum 	: INT32
		@param		fashionNum 	: 时装编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@rtype				   	: String
		@return				   	: 返回时装Dyes
		"""
		return rds.itemModel.getSHeadDyes( fashionNum, gender, profession )

	def createFashionModel( self, fashionNum, gender, profession  ):
		"""
		主线程创建时装模型
		@type		fashionNum	: INT32
		@param		fashionNum	: 时装模型编号
		@type		profession 	: Int
		@param		profession 	: 角色的职业
		@type		gender 		: Int
		@param		gender	 	: 角色的性别
		@return					: PyModel
		"""
		# 获取路径信息
		paths = self.getFashionModelPath( fashionNum, gender, profession )
		# 创建模型
		model = rds.effectMgr.createModel( paths )
		return model

	def createFashionModelBG( self, entityID, roleInfo, callback = None ):
		"""
		后线程创建时装模型
		@type		roleInfo	: dict
		@param		roleInfo	: 角色模型信息
		@return					: None
		"""
		def loadCompleted( modelDict ):

			# 身体模型效果
			bodyModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if bodyModel:
				self.partModelAttachEffect( bodyModel, roleInfo )
			# 发型效果
			hairModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			if hairModel:
				self.fashionHeadModelAttachEffect( hairModel, fashionNum, profession, gender )
			else:
				modelDict[Define.MODEL_EQUIP_HEAD] = None

			if callable( callback ):
				callback( modelDict )

		# 主模型路径
		paths = {}
		bodyPaths = self.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# 发型路径
		gender = roleInfo.getGender()
		profession = roleInfo.getClass()
		fashionNum = roleInfo.getFashionNum()
		hairPaths = rds.itemModel.getSHeadSource( fashionNum, gender, profession )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths

		rds.modelFetchMgr.fetchModels( entityID, loadCompleted, paths )


	def fashionHeadModelAttachEffect( self, headModel, fashionNum, profession, gender ):
		"""
		整个身体模型附加效果
		"""
		# 模型Dyes
		dyes = self.getFashionHeadModelDyes( fashionNum, gender, profession )
		rds.effectMgr.createModelDye( headModel, dyes )

	# --------------------------------------------------------------------
	# 法宝
	# --------------------------------------------------------------------
	def getTalismanModelPath( self, talismanNum ):
		"""
		返回法宝模型路径
		@type		talismanNum 	: INT32
		@param		talismanNum 	: 法宝编号
		@rtype				   		: list of string
		@return				   		: 返回所包含的模型路径
		"""
		return rds.itemModel.getMSource( talismanNum )

	def getTalismanModelDyes( self, talismanNum ):
		"""
		返回法宝模型Dyes
		@type		talismanNum 	: INT32
		@param		talismanNum 	: 法宝编号
		@rtype				   		: string
		@return				   		: 返回所包含的tintName
		"""
		return rds.itemModel.getMDyes( talismanNum )

	def createTalismanModel( self, talismanNum ):
		"""
		@type		talismanNum		: INT32
		@param		talismanNum		: 法宝模型编号
		@return						: PyModel
		"""
		paths = self.getTalismanModelPath( talismanNum )
		talisModel = rds.effectMgr.createModel( paths )
		return talisModel

	def createTalismanModelBG( self, talismanNum, callback = None ):
		"""
		@type		talismanNum		: INT32
		@param		talismanNum		: 法宝模型编号
		@return						: PyModel
		"""
		def loadCompleted( model ):
			# 回调
			if callable( callback ):
				callback( model )

		# 获取路径信息
		paths = self.getTalismanModelPath( talismanNum )
		# 创建模型
		rds.effectMgr.createModelBG( paths, loadCompleted )

	# --------------------------------------------------------------------
	# 主要武器和附属武器共有部分
	# --------------------------------------------------------------------

	# --------------------------------------------------------------------
	# 武器( 所有武器类型都是这种类型，包括盾 ）
	# --------------------------------------------------------------------
	def getMWeaponModelPath( self, weaponDict ) :
		"""
		返回角色武器附加主要模型路径
		@type		RHFDict : FDict
		@param		RHFDict : 角色的附加模型数据
		@rtype				: list of string
		@return				: 返回所包含的模型路径
		"""
		weaponNum = weaponDict["modelNum"]
		return rds.itemModel.getMSource( weaponNum )

	def getMWeaponModelDyes( self, weaponDict ) :
		"""
		返回角色武器附加主要模型dyes
		@type		RHFDict : FDict
		@param		RHFDict : 角色的附加模型数据
		@rtype				: string
		@return				: 返回右手附加模型dyes
		"""
		weaponNum = weaponDict["modelNum"]
		return rds.itemModel.getMDyes( weaponNum )

	def createMWeaponModel( self, weaponDict ):
		"""
		主线程创建主要附加模型
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 角色的附加模型数据
		@return					: PyModel
		"""
		weaponNum = weaponDict["modelNum"]
		# 获取路径信息
		paths = self.getMWeaponModelPath( weaponDict )
		# 创建模型
		model = rds.effectMgr.createModel( paths )
		return model

	def createMWeaponModelBG( self, weaponDict, callback = None ):
		"""
		后线程创建主要附加模型
		"""
		def loadCompleted( model ):
			# 回调
			if callable( callback ):
				callback( model )

		# 获取路径信息
		paths = self.getMWeaponModelPath( weaponDict )
		# 创建模型
		rds.effectMgr.createModelBG( paths, loadCompleted )

	# --------------------------------------------------------------------
	# 附属武器(指双持类武器的左手表现)
	# --------------------------------------------------------------------
	def getFWeaponModelPath( self, weaponDict ) :
		"""
		返回角色武器附加次要模型路径
		@type		RHFDict : FDict
		@param		RHFDict : 角色的附加模型数据
		@rtype				: list of string
		@return				: 返回所包含的模型路径
		"""
		leftHandNum = weaponDict["modelNum"]
		return rds.itemModel.getFSource( leftHandNum )

	def getFWeaponModelDyes( self, weaponDict ) :
		"""
		返回角色武器附加次要模型dyes
		@type		RHFDict : FDict
		@param		RHFDict : 角色的附加模型数据
		@rtype				: string
		@return				: 返回右手附加模型dyes
		"""
		leftHandNum = weaponDict["modelNum"]
		dyes = rds.itemModel.getFDyes( leftHandNum )
		intensifyLevel = weaponDict["iLevel"]
		if intensifyLevel >= Const.EQUIP_WEAPON_FLOW_LEVEL:
			dyes.append( ("intensify1", "intensify" ) )
		return dyes

	def createFWeaponModel( self, weaponDict ):
		"""
		主线程创建次要附加模型(暂时代码中没有使用，测试用)
		@type		weaponDict 	: FDict
		@param		weaponDict 	: 角色的附加模型数据
		@return					: PyModel
		"""
		# 获取路径信息
		paths = self.getFWeaponModelPath( weaponDict )
		# 创建模型
		model = rds.effectMgr.createModel( paths )
		return model

	def createFWeaponModelBG( self, weaponDict, callback = None ):
		"""
		后线程创建主要附加模型(暂时代码中没有使用，测试用)
		"""
		def loadCompleted( model ):
			# 回调
			if callable( callback ):
				callback( model )

		# 获取路径信息
		paths = self.getFWeaponModelPath( weaponDict )
		# 创建模型
		rds.effectMgr.createModelBG( paths, loadCompleted )

	def createModel( self, roleInfo ) :
		"""
		build candidate model
		@type			roleInfo : RoleInfo
		@param			roleInfo : RoleInfo csdefined in top of this module
		@rtype					 : BigWorld.Model
		@return					 : return a new model if create successfully, otherwise return None
		"""

		# 创建身体各部位模型
		model = self.createPartModel( roleInfo )

		# 添加左手武器
		#self.equipLWeapon( model, roleInfo.getLHFDict() )
		# 添加右手武器
		#self.equipRWeapon( model, roleInfo.getRHFDict() )

		return model

	def createEquipModelBG( self, entityID, paths, roleInfo, callback = None ) :
		"""
		根据角色信息创建角色整体模型(暂时代码中没有使用，测试用)
		"""
		def onEquipModelLoad( modelDict ):
			# 身体模型效果
			bodyModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if bodyModel:
				self.partModelAttachEffect( bodyModel, roleInfo )
			# 发型效果
			hairModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			if hairModel:
				profession = roleInfo.getClass()
				gender = roleInfo.getGender()
				hairNumber = roleInfo.getHairNumber()
				fashionNum = roleInfo.getFashionNum()
				self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
			# 右手武器效果
			righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
			if righthandModel:
				rightHandDict = roleInfo.getRHFDict()
			# 左手武器效果
			lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
			if lefthandModel:
				leftHandDict = roleInfo.getLHFDict()
			# 法宝效果
			talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
			if talismanModel:
				talismanNum = roleInfo.getTalismanNum()

			if callable( callback ):
				callback( modelDict )

		rds.modelFetchMgr.fetchModels( entityID, onEquipModelLoad, paths )
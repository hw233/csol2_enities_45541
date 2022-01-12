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
	infoDict["headTextureID"]	= 0		# �Զ���ͷ����ͼ by����
	roleInfo = RoleInfo( infoDict )
	return roleInfo

# ��ɫĬ�ϵ�ģ����Ϣ��������ɫģ��ʧ��ʱ�᳢���ô���Ϣ���ٴδ���
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
	@param infoDict : python�ֵ䣬����RoleInfo������Ϣ
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
		self.__bodyFDict = infoDict["bodyFDict"]			# �Զ�����������ARMOR_EFFECT
		self.__volaFDict = infoDict["volaFDict"]			# �Զ�����������ARMOR_EFFECT
		self.__breechFDict = infoDict["breechFDict"]		# �Զ�����������ARMOR_EFFECT
		self.__feetFDict = infoDict["feetFDict"]			# �Զ�����������ARMOR_EFFECT
		self.__lefthandFDict = infoDict["lefthandFDict"]	# �Զ�����������WEAPON_EFFECT
		self.__righthandFDict = infoDict["righthandFDict"]	# �Զ�����������WEAPON_EFFECT
		self.__talismanNum = infoDict["talismanNum"]
		self.__fashionNum = infoDict["fashionNum"]
		self.__adornNum = infoDict["adornNum"]
		self.__headTextureID = infoDict["headTextureID"]	# �Զ���ͷ����ͼ by����

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
		��ȡ���������
		"""
		return self.__bodyFDict

	def getVolaFDict( self ) :
		"""
		��ȡ���׵�����
		"""
		return self.__volaFDict

	def getBreechFDict( self ) :
		"""
		��ȡ���������
		"""
		return self.__breechFDict

	def getFeetFDict( self ) :
		"""
		��ȡЬ�ӵ�����
		"""
		return self.__feetFDict

	def getLHFDict( self ) :
		"""
		��ȡ������������
		"""
		return self.__lefthandFDict

	def getRHFDict( self ):
		"""
		��ȡ������������
		"""
		return self.__righthandFDict

	def getTalismanNum( self ):
		"""
		��ȡ����ģ�ͱ��
		"""
		return self.__talismanNum

	def getFashionNum( self ):
		"""
		��ȡʱװģ�ͱ��
		"""
		return self.__info["fashionNum"]

	def getAdornNum( self ):
		"""
		��ȡ��Ʒģ�ͱ��
		"""
		return self.__adornNum

	def getLevelStr( self ) :
		"""
		get type string of level
		"""
		return str( self.__level )

	def getCHClass( self ) :
		"""
		��ȡ��ɫְҵ��������
		"""
		return csconst.g_chs_class[self.getClass()]

	def getHeadTextureID( self ):
		"""
		��ȡ��ɫ��ͷ��ID by����
		"""
		if self.__headTextureID is None: return 0
		return self.__headTextureID
		
	def getRoleInfo( self ):
		"""
		��ȡ��ɫ��Ϣ�ֵ�
		"""
		return self.__info

	def update( self, dict ):
		"""
		������ֵ
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
	# ��ɫģ��������ʾ·��
	# --------------------------------------------------------------------
	def getShowModelPath( self, roleInfo ):
		"""
		������ʾģ��·��
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
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
		������ʾģ��·����dyes
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
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
	# ��������ģ��
	# --------------------------------------------------------------------
	def getPartModelPath( self, roleInfo ):
		"""
		��������ģ��path
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
		@return 				: list of string
		"""
		subModels = []
		# ְҵ���Ա�
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		#������ģ��·����Dye
		faceNum = roleInfo.getFaceNumber()
		facePath = self.getFaceModelPath( faceNum, profession, gender )
		subModels.extend( facePath )
		# �����ģ��·����Dye
		bodyFDict = roleInfo.getBodyFDict()
		bodyPath = self.getBodyModelPath( bodyFDict, profession, gender )
		subModels.extend( bodyPath )
		# ���׵�ģ��·����Dye
		volaFDict = roleInfo.getVolaFDict()
		volaPath = self.getVolaModelPath( volaFDict, profession, gender )
		subModels.extend( volaPath )
		# �����ģ��·����Dye
		breechFDict = roleInfo.getBreechFDict()
		breechPath = self.getBreechModelPath( breechFDict, profession, gender )
		subModels.extend( breechPath )
		# Ь�ӵ�ģ��·����Dye
		feetFDict = roleInfo.getFeetFDict()
		feetPath = self.getFeetModelPath( feetFDict, profession, gender )
		subModels.extend( feetPath )

		return subModels

	def getPartModelDyes( self, roleInfo ):
		"""
		��������ģ��dyes
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
		@return                 : ( [], [] )
		"""
		subDyes = []
		# ְҵ���Ա�
		profession = roleInfo.getClass()
		gender = roleInfo.getGender()
		#������ģ��Dye
		faceNum = roleInfo.getFaceNumber()
		faceDyes = self.getFaceModelDyes( faceNum, profession, gender )
		subDyes.extend( faceDyes )
		# �����ģ��Dye
		bodyFDict = roleInfo.getBodyFDict()
		bodyDyes = self.getBodyModelDyes( bodyFDict, profession, gender )
		subDyes.extend( bodyDyes )
		# ���׵�ģ��Dye
		volaFDict = roleInfo.getVolaFDict()
		volaDyes = self.getVolaModelDyes( volaFDict, profession, gender )
		subDyes.extend( volaDyes )
		# �����ģ��Dye
		breechFDict = roleInfo.getBreechFDict()
		breechDyes = self.getBreechModelDyes( breechFDict, profession, gender )
		subDyes.extend( breechDyes )
		# Ь�ӵ�ģ��Dye
		feetFDict = roleInfo.getFeetFDict()
		feetDyes = self.getFeetModelDyes( feetFDict, profession, gender )
		subDyes.extend( feetDyes )

		return subDyes

	def createPartModel( self, roleInfo ):
		"""
		���̴߳�����������ģ��
		��Ϊ����ģ���ǲ��������ڵģ��贴��ͷ���������壬���ף�����Ь��6����ģ��
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
		@return				   	: PyModel
		"""
		subModels = self.getShowModelPath( roleInfo )
		subDyes = self.getShowModelDyes( roleInfo )
		return rds.effectMgr.createModel( subModels, subDyes )

	def createPartModelBG( self, entityID, roleInfo, callback = None ):
		"""
		���̴߳�����������ģ��
		��Ϊ����ģ���ǲ��������ڵģ��贴��ͷ���������壬���ף�����Ь��6����ģ��
		@type		roleInfo 	: dict
		@param		roleInfo 	: ��ɫ��ģ������
		@type		callback 	: func
		@param		callback 	: ģ�ʹ����õĻص�
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
		��������ģ�͸���Ч��
		"""
		# ģ��Dyes
		subDyes = self.getShowModelDyes( roleInfo )
		rds.effectMgr.createModelDye( partModel, subDyes )

	# --------------------------------------------------------------------
	# ͷ��
	# --------------------------------------------------------------------
	def getHairModelPath( self, hairNumber, fashionNum, profession, gender ):
		"""
		���ؽ�ɫ����·��(��ү�ģ�ͷ����ʱװ���Ϲ�ϵ��)
		@type		hairNumber 	: Int32
		@param		hairNumber 	: ��ɫ�ķ��ͱ��
		@type		fashionNum 	: Int32
		@param		fashionNum 	: ��ɫ��ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: list of string
		@return				   	: ������������ģ��·��
		"""
		# ��ʱװ������£������ȷ���ʱװ��ģ�ͱ��
		if fashionNum != 0:
			return rds.itemModel.getSHeadSource( fashionNum, gender, profession )

		if hairNumber == 0 :
			hairNumber = Const.ROLE_EQUIP_HAIR_MAP.get( profession | gender )
			if hairNumber is None: return []
		return rds.itemModel.getMSource( hairNumber )

	def getHairModelDyes( self, hairNumber, fashionNum, profession, gender ):
		"""
		���ؽ�ɫ����Dyes
		@type		hairNumber 	: Int32
		@param		hairNumber 	: ��ɫ�ķ��ͱ��
		@type		fashionNum 	: Int32
		@param		fashionNum 	: ��ɫ��ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: String
		@return				   	: ���ط���Dyes
		"""
		# ��ʱװ������£������ȷ���ʱװ��ģ��Dyes
		if fashionNum != 0:
			return rds.itemModel.getSHeadDyes( fashionNum, gender, profession )

		if hairNumber == 0 :
			hairNumber = Const.ROLE_EQUIP_HAIR_MAP.get( profession | gender )
			if hairNumber is None: return []
		return rds.itemModel.getMDyes( hairNumber )

	def hairModelAttachEffect( self, hairModel, hairNumber, fashionNum, profession, gender ):
		"""
		ͷ������Ч��
		@type		model		: PyModel
		@param		model		: ����ģ��
		@type		hairNumber	: INT32
		@param		hairNumber	: ͷ��ģ�ͱ��
		@type		fashionNum 	: Int32
		@param		fashionNum 	: ��ɫ��ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		"""
		# ģ��Dyes
		hairDyes = self.getHairModelDyes( hairNumber, fashionNum, profession, gender )
		rds.effectMgr.createModelDye( hairModel, hairDyes )

	def createHairModel( self, hairNumber, fashionNum, profession, gender ):
		"""
		���̴߳�������ģ��
		@type		hairNumber 	: Int32
		@param		hairNumber 	: ��ɫ�ķ��ͱ��
		@type		fashionNum 	: Int32
		@param		fashionNum 	: ��ɫ��ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@return 				: pyModel
		"""
		# ��ȡ·����Ϣ
		paths = self.getHairModelPath( hairNumber, fashionNum, profession, gender )
		# ����ģ��
		hairModel = rds.effectMgr.createModel( paths )
		self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
		return hairModel

	def createHairModelBG( self, hairNumber, fashionNum, profession, gender, callback = None ):
		"""
		���̴߳�������ģ��
		@type		hairNumber 	: Int32
		@param		hairNumber 	: ��ɫ�ķ��ͱ��
		@type		fashionNum 	: Int32
		@param		fashionNum 	: ��ɫ��ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@type		callback	: func
		@param		callback	: ����ģ�ͺ󷵻�
		@return 				: None
		"""
		def onModelLoad( hairModels ):
			hairModel = hairModels.get( Define.MODEL_EQUIP_HEAD )
			self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
			if callable( callback ):
				callback( hairModel )

		hairPaths = self.getHairModelPath( hairNumber, fashionNum, profession, gender )			# ��ȡ·����Ϣ
		rds.modelFetchMgr.fetchModels( 0, onModelLoad, {Define.MODEL_EQUIP_HEAD:hairPaths} )	# ����ģ��

	# --------------------------------------------------------------------
	# ��
	# --------------------------------------------------------------------
	def getFaceModelPath( self, faceNumber, profession, gender ) :
		"""
		��������·��
		@type		faceNumber 	: Int32
		@param		faceNumber 	: ��ɫ�����ͱ��
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: list of string
		@return				   	: ������������ģ��·��
		"""
		if faceNumber == 0 :
			faceNumber = Const.ROLE_EQUIP_FACE_MAP.get( profession | gender )
			if faceNumber is None: return []
		return rds.itemModel.getMSource( faceNumber )

	def getFaceModelDyes( self, faceNumber, profession, gender ) :
		"""
		��������Dyes
		@type		faceNumber 	: Int32
		@param		faceNumber 	: ��ɫ�����ͱ��
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: String
		@return				   	: ��������Dyes
		"""
		if faceNumber == 0 :
			faceNumber = Const.ROLE_EQUIP_FACE_MAP.get( profession | gender )
			if faceNumber is None: return []
		return rds.itemModel.getMDyes( faceNumber )

	# --------------------------------------------------------------------
	# ����
	# --------------------------------------------------------------------
	def getBodyModelPath( self, bodyFDict, profession, gender ) :
		"""
		��������ģ��·��
		@type		bodyFDict 	: FDict
		@param		bodyFDict 	: ��ɫ������ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: List of String
		@return				   	: ������������ģ��·��
		"""
		bodyNum = bodyFDict["modelNum"]
		if bodyNum == 0:
			bodyNum = Const.ROLE_EQUIP_BODY_MAP.get( profession )
			if bodyNum is None: return []
		return rds.itemModel.getGSource( bodyNum, gender )

	def getBodyModelDyes( self, bodyFDict, profession, gender ) :
		"""
		��������ģ��Dyes
		@type		bodyFDict 	: FDict
		@param		bodyFDict 	: ��ɫ������ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: string
		@return				   	: ����������Dyes
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
	# ����
	# --------------------------------------------------------------------
	def getVolaModelPath( self, volaFDict, profession, gender ) :
		"""
		�����ֲ�ģ��·��
		@type		volaFDict 	: FDict
		@param		volaFDict 	: ��ɫ���ֲ�ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				 	: list of string
		@return				  	: ������������ģ��·��
		"""
		volaNum = volaFDict["modelNum"]
		if volaNum == 0:
			volaNum = Const.ROLE_EQUIP_VOLA_MAP.get( profession )
			if volaNum is None: return []
		return rds.itemModel.getGSource( volaNum, gender )

	def getVolaModelDyes( self, volaFDict, profession, gender ) :
		"""
		�����ֲ�ģ��Dyes
		@type		volaFDict 	: FDict
		@param		volaFDict 	: ��ɫ���ֲ�ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				 	: string
		@return				  	: �����ֲ�Dyes
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
	# ����
	# --------------------------------------------------------------------
	def getBreechModelPath( self, breechFDict, profession, gender ) :
		"""
		���ؿ���ģ��·��
		@type		breechFDict	: FDict
		@param		breechFDict	: ��ɫ�Ŀ���ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				 	: List of string
		@return				   	: ������������ģ��·��
		"""
		breechNum = breechFDict["modelNum"]
		if breechNum == 0:
			breechNum = Const.ROLE_EQUIP_BREE_MAP.get( profession )
			if breechNum is None: return []
		return rds.itemModel.getGSource( breechNum, gender )

	def getBreechModelDyes( self, breechFDict, profession, gender ) :
		"""
		���ؿ���Dyes
		@type		breechFDict	: FDict
		@param		breechFDict	: ��ɫ�Ŀ���ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				 	: string
		@return				   	: ���ؿ���Dyes
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
	# Ь��
	# --------------------------------------------------------------------
	def getFeetModelPath( self, feetFDict, profession, gender ) :
		"""
		����Ь��ģ��·��
		@type		feetFDict 	: FDict
		@param		feetFDict 	: ��ɫ��Ь��ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: list of string
		@return				   	: ������������ģ��·��
		"""
		feetNum = feetFDict["modelNum"]
		if feetNum== 0:
			feetNum = Const.ROLE_EQUIP_FEET_MAP.get( profession )
			if feetNum is None: return []
		return rds.itemModel.getGSource( feetNum, gender )

	def getFeetModelDyes( self, feetFDict, profession, gender ) :
		"""
		����Ь��Dyes
		@type		feetFDict 	: FDict
		@param		feetFDict 	: ��ɫ��Ь��ģ������
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: string
		@return				   	: ����Ь��Dyes
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
	# ʱװ
	# --------------------------------------------------------------------
	def getFashionModelPath( self, fashionNum, gender, profession ):
		"""
		����ʱװģ��·��
		@type		fashionNum 	: INT32
		@param		fashionNum 	: ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: list of String
		@return				   	: ������������ģ��·��
		"""
		return rds.itemModel.getSSource( fashionNum, gender, profession )

	def getFashionModelDyes( self, fashionNum, gender, profession ):
		"""
		����ʱװDyes
		@type		fashionNum 	: INT32
		@param		fashionNum 	: ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: String
		@return				   	: ����ʱװDyes
		"""
		return rds.itemModel.getSDyes( fashionNum, gender, profession )

	def getFashionHeadModelDyes( self, fashionNum, gender, profession ):
		"""
		����ʱװDyes
		@type		fashionNum 	: INT32
		@param		fashionNum 	: ʱװ���
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@rtype				   	: String
		@return				   	: ����ʱװDyes
		"""
		return rds.itemModel.getSHeadDyes( fashionNum, gender, profession )

	def createFashionModel( self, fashionNum, gender, profession  ):
		"""
		���̴߳���ʱװģ��
		@type		fashionNum	: INT32
		@param		fashionNum	: ʱװģ�ͱ��
		@type		profession 	: Int
		@param		profession 	: ��ɫ��ְҵ
		@type		gender 		: Int
		@param		gender	 	: ��ɫ���Ա�
		@return					: PyModel
		"""
		# ��ȡ·����Ϣ
		paths = self.getFashionModelPath( fashionNum, gender, profession )
		# ����ģ��
		model = rds.effectMgr.createModel( paths )
		return model

	def createFashionModelBG( self, entityID, roleInfo, callback = None ):
		"""
		���̴߳���ʱװģ��
		@type		roleInfo	: dict
		@param		roleInfo	: ��ɫģ����Ϣ
		@return					: None
		"""
		def loadCompleted( modelDict ):

			# ����ģ��Ч��
			bodyModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if bodyModel:
				self.partModelAttachEffect( bodyModel, roleInfo )
			# ����Ч��
			hairModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			if hairModel:
				self.fashionHeadModelAttachEffect( hairModel, fashionNum, profession, gender )
			else:
				modelDict[Define.MODEL_EQUIP_HEAD] = None

			if callable( callback ):
				callback( modelDict )

		# ��ģ��·��
		paths = {}
		bodyPaths = self.getShowModelPath( roleInfo )
		if len( bodyPaths ): paths[Define.MODEL_EQUIP_MAIN] = bodyPaths
		# ����·��
		gender = roleInfo.getGender()
		profession = roleInfo.getClass()
		fashionNum = roleInfo.getFashionNum()
		hairPaths = rds.itemModel.getSHeadSource( fashionNum, gender, profession )
		if len( hairPaths ): paths[Define.MODEL_EQUIP_HEAD] = hairPaths

		rds.modelFetchMgr.fetchModels( entityID, loadCompleted, paths )


	def fashionHeadModelAttachEffect( self, headModel, fashionNum, profession, gender ):
		"""
		��������ģ�͸���Ч��
		"""
		# ģ��Dyes
		dyes = self.getFashionHeadModelDyes( fashionNum, gender, profession )
		rds.effectMgr.createModelDye( headModel, dyes )

	# --------------------------------------------------------------------
	# ����
	# --------------------------------------------------------------------
	def getTalismanModelPath( self, talismanNum ):
		"""
		���ط���ģ��·��
		@type		talismanNum 	: INT32
		@param		talismanNum 	: �������
		@rtype				   		: list of string
		@return				   		: ������������ģ��·��
		"""
		return rds.itemModel.getMSource( talismanNum )

	def getTalismanModelDyes( self, talismanNum ):
		"""
		���ط���ģ��Dyes
		@type		talismanNum 	: INT32
		@param		talismanNum 	: �������
		@rtype				   		: string
		@return				   		: ������������tintName
		"""
		return rds.itemModel.getMDyes( talismanNum )

	def createTalismanModel( self, talismanNum ):
		"""
		@type		talismanNum		: INT32
		@param		talismanNum		: ����ģ�ͱ��
		@return						: PyModel
		"""
		paths = self.getTalismanModelPath( talismanNum )
		talisModel = rds.effectMgr.createModel( paths )
		return talisModel

	def createTalismanModelBG( self, talismanNum, callback = None ):
		"""
		@type		talismanNum		: INT32
		@param		talismanNum		: ����ģ�ͱ��
		@return						: PyModel
		"""
		def loadCompleted( model ):
			# �ص�
			if callable( callback ):
				callback( model )

		# ��ȡ·����Ϣ
		paths = self.getTalismanModelPath( talismanNum )
		# ����ģ��
		rds.effectMgr.createModelBG( paths, loadCompleted )

	# --------------------------------------------------------------------
	# ��Ҫ�����͸����������в���
	# --------------------------------------------------------------------

	# --------------------------------------------------------------------
	# ����( �����������Ͷ����������ͣ������� ��
	# --------------------------------------------------------------------
	def getMWeaponModelPath( self, weaponDict ) :
		"""
		���ؽ�ɫ����������Ҫģ��·��
		@type		RHFDict : FDict
		@param		RHFDict : ��ɫ�ĸ���ģ������
		@rtype				: list of string
		@return				: ������������ģ��·��
		"""
		weaponNum = weaponDict["modelNum"]
		return rds.itemModel.getMSource( weaponNum )

	def getMWeaponModelDyes( self, weaponDict ) :
		"""
		���ؽ�ɫ����������Ҫģ��dyes
		@type		RHFDict : FDict
		@param		RHFDict : ��ɫ�ĸ���ģ������
		@rtype				: string
		@return				: �������ָ���ģ��dyes
		"""
		weaponNum = weaponDict["modelNum"]
		return rds.itemModel.getMDyes( weaponNum )

	def createMWeaponModel( self, weaponDict ):
		"""
		���̴߳�����Ҫ����ģ��
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��ɫ�ĸ���ģ������
		@return					: PyModel
		"""
		weaponNum = weaponDict["modelNum"]
		# ��ȡ·����Ϣ
		paths = self.getMWeaponModelPath( weaponDict )
		# ����ģ��
		model = rds.effectMgr.createModel( paths )
		return model

	def createMWeaponModelBG( self, weaponDict, callback = None ):
		"""
		���̴߳�����Ҫ����ģ��
		"""
		def loadCompleted( model ):
			# �ص�
			if callable( callback ):
				callback( model )

		# ��ȡ·����Ϣ
		paths = self.getMWeaponModelPath( weaponDict )
		# ����ģ��
		rds.effectMgr.createModelBG( paths, loadCompleted )

	# --------------------------------------------------------------------
	# ��������(ָ˫�������������ֱ���)
	# --------------------------------------------------------------------
	def getFWeaponModelPath( self, weaponDict ) :
		"""
		���ؽ�ɫ�������Ӵ�Ҫģ��·��
		@type		RHFDict : FDict
		@param		RHFDict : ��ɫ�ĸ���ģ������
		@rtype				: list of string
		@return				: ������������ģ��·��
		"""
		leftHandNum = weaponDict["modelNum"]
		return rds.itemModel.getFSource( leftHandNum )

	def getFWeaponModelDyes( self, weaponDict ) :
		"""
		���ؽ�ɫ�������Ӵ�Ҫģ��dyes
		@type		RHFDict : FDict
		@param		RHFDict : ��ɫ�ĸ���ģ������
		@rtype				: string
		@return				: �������ָ���ģ��dyes
		"""
		leftHandNum = weaponDict["modelNum"]
		dyes = rds.itemModel.getFDyes( leftHandNum )
		intensifyLevel = weaponDict["iLevel"]
		if intensifyLevel >= Const.EQUIP_WEAPON_FLOW_LEVEL:
			dyes.append( ("intensify1", "intensify" ) )
		return dyes

	def createFWeaponModel( self, weaponDict ):
		"""
		���̴߳�����Ҫ����ģ��(��ʱ������û��ʹ�ã�������)
		@type		weaponDict 	: FDict
		@param		weaponDict 	: ��ɫ�ĸ���ģ������
		@return					: PyModel
		"""
		# ��ȡ·����Ϣ
		paths = self.getFWeaponModelPath( weaponDict )
		# ����ģ��
		model = rds.effectMgr.createModel( paths )
		return model

	def createFWeaponModelBG( self, weaponDict, callback = None ):
		"""
		���̴߳�����Ҫ����ģ��(��ʱ������û��ʹ�ã�������)
		"""
		def loadCompleted( model ):
			# �ص�
			if callable( callback ):
				callback( model )

		# ��ȡ·����Ϣ
		paths = self.getFWeaponModelPath( weaponDict )
		# ����ģ��
		rds.effectMgr.createModelBG( paths, loadCompleted )

	def createModel( self, roleInfo ) :
		"""
		build candidate model
		@type			roleInfo : RoleInfo
		@param			roleInfo : RoleInfo csdefined in top of this module
		@rtype					 : BigWorld.Model
		@return					 : return a new model if create successfully, otherwise return None
		"""

		# �����������λģ��
		model = self.createPartModel( roleInfo )

		# �����������
		#self.equipLWeapon( model, roleInfo.getLHFDict() )
		# �����������
		#self.equipRWeapon( model, roleInfo.getRHFDict() )

		return model

	def createEquipModelBG( self, entityID, paths, roleInfo, callback = None ) :
		"""
		���ݽ�ɫ��Ϣ������ɫ����ģ��(��ʱ������û��ʹ�ã�������)
		"""
		def onEquipModelLoad( modelDict ):
			# ����ģ��Ч��
			bodyModel = modelDict.get( Define.MODEL_EQUIP_MAIN )
			if bodyModel:
				self.partModelAttachEffect( bodyModel, roleInfo )
			# ����Ч��
			hairModel = modelDict.get( Define.MODEL_EQUIP_HEAD )
			if hairModel:
				profession = roleInfo.getClass()
				gender = roleInfo.getGender()
				hairNumber = roleInfo.getHairNumber()
				fashionNum = roleInfo.getFashionNum()
				self.hairModelAttachEffect( hairModel, hairNumber, fashionNum, profession, gender )
			# ��������Ч��
			righthandModel = modelDict.get( Define.MODEL_EQUIP_RHAND )
			if righthandModel:
				rightHandDict = roleInfo.getRHFDict()
			# ��������Ч��
			lefthandModel = modelDict.get( Define.MODEL_EQUIP_LHAND )
			if lefthandModel:
				leftHandDict = roleInfo.getLHFDict()
			# ����Ч��
			talismanModel = modelDict.get( Define.MODEL_EQUIP_TALIS )
			if talismanModel:
				talismanNum = roleInfo.getTalismanNum()

			if callable( callback ):
				callback( modelDict )

		rds.modelFetchMgr.fetchModels( entityID, onEquipModelLoad, paths )
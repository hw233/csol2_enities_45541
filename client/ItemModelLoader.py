# -*- coding: gb18030 -*-

#$Id: ItemModelLoader.py,v 1.6 2008-08-20 09:04:14 yangkai Exp $

from bwdebug import *
import Language
from gbref import rds
import Const
import csdefine
from config.client import ItemModel
import Define


# ----------------------------------------------------------------------------------------------------
# 物品模型加载
# ----------------------------------------------------------------------------------------------------
class ItemModelLoader:
	"""
	物品模型加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert ItemModelLoader._instance is None, "instance already exist in"
		self._datas = ItemModel.Datas # {modelID : {"model_drop": ..., "model_rweapon": ...}...}

		self.fashionMapIndex = {	csdefine.CLASS_FIGHTER 	| csdefine.GENDER_MALE 		:	1,
									csdefine.CLASS_FIGHTER 	| csdefine.GENDER_FEMALE	:	2,
									csdefine.CLASS_SWORDMAN | csdefine.GENDER_MALE 		:	3,
									csdefine.CLASS_SWORDMAN | csdefine.GENDER_FEMALE	:	4,
									csdefine.CLASS_ARCHER 	| csdefine.GENDER_MALE 		:	5,
									csdefine.CLASS_ARCHER 	| csdefine.GENDER_FEMALE	:	6,
									csdefine.CLASS_MAGE 	| csdefine.GENDER_MALE 		:	7,
									csdefine.CLASS_MAGE 	| csdefine.GENDER_FEMALE	:	8,
									}

		self.armorMapIndex = {		csdefine.GENDER_MALE 	:	1,
									csdefine.GENDER_FEMALE	:	2,
									}

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = ItemModelLoader()
		return self._instance

	def __getSData( self, itemModelID, key ):
		"""
		"""
		data = self._datas.get( itemModelID )
		if data is None: return []
		source = data.get( key )
		if source is None: return []
		return list( source )

	def getDropModelByID( self, itemModelID, isReturnDeFault = True ):
		"""
		根据模型编号ID获取掉落模型路径
		如果找不到则返回默认模型

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		dropModelPath = ""
		if isReturnDeFault:
			dropModelPath = "dlwp/dm_fj_tb_00001.model"
		dropModelPaths = self.__getSData( itemModelID, "model_drop" )
		if len( dropModelPaths ): return dropModelPaths[0]
		return dropModelPath

	def getGSource( self, itemModelID, gender ):
		"""
		根据模型编号和性别获取防具类资源
		"""
		if gender is None: return []
		index = self.armorMapIndex.get( gender )
		if index is None: return []
		return self.__getSData( itemModelID, "model_source%s" % index )

	def getGDyes( self, itemModelID, gender ):
		"""
		根据模型编号和性别获取防具类Dyes

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		if gender is None: return []
		index = self.armorMapIndex.get( gender )
		if index is None: return []
		return self.__getSData( itemModelID, "model_tint%s" % index )

	def getSHeadSource( self, itemModelID, gender, profession ):
		"""
		根据物品模型编号，职业性别，获取时装资源附加头发路径

		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@type  gender		: Uint8
		@param gender		: 性别
		@type  profession	: Uint8
		@param profession	: 职业
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_headSource%s" % index
		return self.__getSData( itemModelID, key )

	def getSHeadDyes( self, itemModelID, gender, profession ):
		"""
		根据模型编号ID获取时装资源附加头发Dyes

		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@type  gender		: Uint8
		@param gender		: 性别
		@type  profession	: Uint8
		@param profession	: 职业
		@return list of (tint, dye)
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_tint%s" % index
		return self.__getSData( itemModelID, key )

	def getSSource( self, itemModelID, gender, profession ):
		"""
		根据物品模型编号，职业性别，获取时装资源路径

		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@type  gender		: Uint8
		@param gender		: 性别
		@type  profession	: Uint8
		@param profession	: 职业
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_source%s" % index
		return self.__getSData( itemModelID, key )

	def getSDyes( self, itemModelID, gender, profession ):
		"""
		根据模型编号ID获取主模型Tint名

		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@type  gender		: Uint8
		@param gender		: 性别
		@type  profession	: Uint8
		@param profession	: 职业
		@return list of (tint, dye)
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_tint%s" % index
		return self.__getSData( itemModelID, key )

	def getSEffects( self, itemModelID, gender, profession ):
		"""
		根据物品模型编号，职业性别，获取时装绑定点
		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@type  gender		: Uint8
		@param gender		: 性别
		@type  profession	: Uint8
		@param profession	: 职业
		@return list of string
		"""
		if gender is None: return []
		if profession is None: return []
		key = gender | profession
		index = self.fashionMapIndex.get( key )
		if index is None: return []
		key = "model_effect%s" % index
		return self.__getSData( itemModelID, key )

	def getMSource( self, itemModelID ):
		"""
		获取主要的表现模型
		如果是防具类，则获取的是男性防具模型
		如果是武器类，则获取的是右手武器模型
		"""
		return self.__getSData( itemModelID, "model_source1" )

	def getMDyes( self, itemModelID ):
		"""
		根据模型编号ID获取主模型Dyes

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		return self.__getSData( itemModelID, "model_tint1" )

	def getMEffects( self, itemModelID ):
		"""
		获取主要的表现模型效果
		"""
		return self.__getSData( itemModelID, "model_effect1" )

	def getFSource( self, itemModelID ):
		"""
		获取次要的表现模型
		如果是防具类，则获取的是女性防具模型
		如果是武器类，则获取的是左手武器模型
		"""
		return self.__getSData( itemModelID, "model_source2" )

	def getFDyes( self, itemModelID ):
		"""
		根据模型编号ID获取次模型Dyes

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		return self.__getSData( itemModelID, "model_tint1" )
		
	def getActionsName( self, itemModelID ):
		"""
		根据模型编号ID获取次模型动作

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		actionsList = self.__getSData( itemModelID, "model_action" )
		if len( actionsList ):return actionsList[0]
		
	def getTimetick( self, itemModelID ):
		"""
		根据模型编号ID获取次模型动作间隔

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		timeList = self.__getSData( itemModelID, "model_timetick" )
		if len( timeList ):return timeList[0]

	def isShine( self, itemModelID ):
		"""
		根据模型编号ID判断是否自发光

		@type  itemModelID: string
		@param itemModelID: 物品模型编号
		"""
		try:
			return self._datas[itemModelID]["model_isShine"]
		except:
			return False

	def reset( self ):
		"""
		重新加载 itemModel 配置
		"""
		reload( ItemModel )
		self._datas = ItemModel.Datas

	def createModel( self, itemModelID, callback = None ):
		"""
		在主线程根据itemModelID 创建主体模型
		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@return				：PyModel
		"""
		# 获取路径信息
		paths = self.getMSource( itemModelID )
		dyes = self.getMDyes( itemModelID )
		# 创建模型
		model = rds.effectMgr.createModel( paths, dyes )
		
		# 自发光
		isShine = self.isShine( itemModelID )
		if isShine:
			weaponKey = paths[0]
			type = rds.equipParticle.getWType( weaponKey )
			texture = rds.equipParticle.getWTexture( weaponKey )
			colour = rds.equipParticle.getWColour( weaponKey )
			scale = rds.equipParticle.getWScale( weaponKey, Const.NPC_SHINE_INTENSIFY )
			offset = rds.equipParticle.getWOffset( weaponKey )
			rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
		if callable( callback ):
			callback( model )
		return model

	def createModelBG( self, itemModelID, onLoadCompleted ):
		"""
		在后线程根据itemModelID 创建主体模型
		@type  itemModelID	: string
		@param itemModelID	: 物品模型编号
		@return				：None
		"""
		def loadCompleted( model ):
			# 自发光
			isShine = self.isShine( itemModelID )
			if isShine:
				weaponKey = paths[0]
				type = rds.equipParticle.getWType( weaponKey )
				texture = rds.equipParticle.getWTexture( weaponKey )
				colour = rds.equipParticle.getWColour( weaponKey )
				scale = rds.equipParticle.getWScale( weaponKey, Const.NPC_SHINE_INTENSIFY )
				offset = rds.equipParticle.getWOffset( weaponKey )
				rds.effectMgr.modelShine( model, type, texture, colour, scale, offset )
			if callable( onLoadCompleted ):
				onLoadCompleted( model )

		# 获取路径信息
		paths = self.getMSource( itemModelID )
		dyes = self.getMDyes( itemModelID )
		# 创建模型
		rds.effectMgr.createModelBG( paths, loadCompleted, dyes )

#$Log: not supported by cvs2svn $
#Revision 1.5  2008/07/08 09:36:33  yangkai
#修正初始化方式，
#
#Revision 1.4  2008/03/20 03:31:35  yangkai
#no message
#
#Revision 1.3  2007/12/14 07:55:21  yangkai
#修正搜索模型Dye贴图的小bug
#
#Revision 1.2  2007/11/27 01:52:30  phw
#所有职业变量加上前缀'CLASS_'，所有性别变量加上前缀'GENDER_'，如原来的战士'FIGHTER'变为'CLASS_FIGHTER'，其余类同
#
#Revision 1.1  2007/11/23 07:40:46  yangkai
#根据新的物品掉落模型表现修改掉落物品模型加载方式
#
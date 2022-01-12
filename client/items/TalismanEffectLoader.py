# -*- coding: gb18030 -*-
#
from bwdebug import *
import Language
import random
from config.item import TalismanSkill
from config.item import TalismanPotential
from config.item import TalismanGrade
from config.item import TalismanExtraParam

class TalismanEffectLoader:
	"""
	法宝属性配置加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert TalismanEffectLoader._instance is None, "instance already exist in"
		self._aDatas = TalismanGrade.Datas		# like as { grade : { "tm_upItem" : itemID, ... }, ... }
		self._gDatas = TalismanExtraParam.Datas		# like as { id : { "effectID" : effectID,...},... }
		self._sDatas = TalismanSkill.Datas		# like as { level : odds, ... }
		self._pDatas = TalismanPotential.Datas		# like as { skill_level, potential, ... }

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = TalismanEffectLoader()
		return self._instance

	def getPotential( self, skillLevel ):
		"""
		获取法宝技能升级所需的潜能点
		@type	skillLevel	:	INT8
		@param	skillLevel	:	法宝技能等级
		@return				：	INT32
		"""
		try:
			return self._pDatas[skillLevel+1]
		except KeyError:
			ERROR_MSG( "Can't find PotentialConfig by SkillLevel(%s)" % skillLevel )
			return 0

	def getMaxExp( self, explevel ):
		"""
		获取法宝升级所需的经验
		@type	explevel	:	INT8
		@param	explevel	:	所升等级
		@return				：	INT32
		"""
		try:
			return self._sDatas[explevel+1]
		except KeyError:
			ERROR_MSG( "Can't find TalisExpConfig by explevel(%s)" % explevel )
			return 0

	def getEffectID( self, tmID ):
		"""
		根据法宝自定义属性ID获取对应的装备ID
		@type	tmID	:	INT8
		@param	tmID	:	法宝自定义属性ID
		@return			:	int16
		"""
		try:
			return self._gDatas[tmID]["tm_effectID"]
		except KeyError:
			ERROR_MSG( "Can't find tm_EffectID config by tmID(%s)" % tmID )
			return 0

	def getInitValue( self, tmID ):
		"""
		根据法宝自定义属性ID获取对应的装备ID出现时的初值
		@type	tmID	:	INT8
		@param	tmID	:	法宝自定义属性ID
		@return			:	Float
		"""
		try:
			return self._gDatas[tmID]["tm_initValue"]
		except KeyError:
			ERROR_MSG( "Can't find tm_initValue config by tmID(%s)" % tmID )
			return 0.0

	def getUpParam( self, tmID ):
		"""
		根据法宝自定义属性ID获取对应的装备ID升级时候的控制参数
		@type	tmID	:	INT8
		@param	tmID	:	法宝自定义属性ID
		@return			:	Float
		"""
		try:
			return self._gDatas[tmID]["tm_upParam"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upParam config by tmID(%s)" % tmID )
			return 0.0

	def getUpItem( self, grade ):
		"""
		获取法宝品级提升需求物品
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_upItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upItem config by grade(%s)" % grade )
			return 0

	def getUpItemAmount( self, grade ):
		"""
		获取法宝品级提升需求物品数量
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_upItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_upItemAmount config by grade(%s)" % grade )
			return 0

	def getActivatItem( self, grade ):
		"""
		获取法宝品级激活属性所需物品
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_activatItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_activatItem config by grade(%s)" % grade )
			return 0

	def getActivatItemAmount( self, grade ):
		"""
		获取法宝品级激活属性所需物品数量
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_activatItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_activatItemAmount config by grade(%s)" % grade )
			return 0

	def getRebuildItem( self, grade ):
		"""
		根据法宝品级获取改造属性需求原料
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_rebuildItem"]
		except KeyError:
			ERROR_MSG( "Can't find tm_rebuildItem config by grade(%s)" % grade )
			return 0

	def getRebuildItemAmount( self, grade ):
		"""
		根据法宝品级获取改造属性需求原料数量
		@type	grade	:	INT8
		@param	grade	:	法宝品级
		@return			:	INT
		"""
		try:
			return self._aDatas[grade]["tm_rebuildItemAmount"]
		except KeyError:
			ERROR_MSG( "Can't find tm_rebuildItemAmount config by grade(%s)" % grade )
			return 0

	def getAcGradeByItemID( self, itemID ):
		"""
		根据物品ID获取激活的品级
		"""
		for grade, data in self._aDatas.iteritems():
			tmItemIDs = data.get( "tm_activatItem", [] )
			if itemID in tmItemIDs: return grade
		return None

	def reset( self ):
		"""
		重新加载法宝数据配置
		@return None
		"""
		reload( TalismanGrade )
		reload( TalismanExtraParam )
		reload( TalismanSkill )
		reload( TalismanPotential )
		self._aDatas = TalismanGrade.Datas		# like as { grade : { "tm_upItem" : itemID, ... }, ... }
		self._gDatas = TalismanExtraParam.Datas		# like as { id : { "effectID" : effectID,...},... }
		self._sDatas = TalismanSkill.Datas		# like as { level : odds, ... }
		self._pDatas = TalismanPotential.Datas		# like as { skill_level, potential, ... }

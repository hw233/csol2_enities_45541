# -*- coding: gb18030 -*-

#$Id: EquipEffectLoader.py,v 1.12 2008-08-09 09:31:24 wangshufeng Exp $

from bwdebug import *
import Language
from SmartImport import smartImport
import Function
import random
import copy
from config.item.EquipEffects import serverDatas as g_serverDatas
import ItemTypeEnum


# ----------------------------------------------------------------------------------------------------
# 装备属性加载
# ----------------------------------------------------------------------------------------------------

class EquipEffectLoader:
	"""
	装备属性加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：[...], ...}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipEffectLoader._instance is None, "instance already exist in"
		self._datas = g_serverDatas
		for key, value in self._datas.iteritems():
			self._datas[key]["dynClass"] = smartImport( value["dynClass"] )

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipEffectLoader()
		return self._instance

	def getEffect( self, effectID ):
		"""
		根据效果ID获取效果对应脚本类
		"""
		try:
			return self._datas[effectID]["dynClass"]
		except:
			ERROR_MSG( "Can't find equipEffect config by %s" % effectID )
			return None

	def getEffectIDsByQuality( self, quality ):
		"""
		通过装备品质确定可出现的效果ID列表
		"""
		EffectIDs = set([])
		for key, value in self._datas.iteritems():
			if value["needEquipQuality"] <= quality:
				EffectIDs.add( key )
		return list( EffectIDs )

	def getEffectIDsByLevel( self, level, canSystemCreate = False ):
		"""
		通过装备等级确定可出现的效果ID列表

		canSystemCreate为False时过滤掉系统随机属性，否则返回所有随机属性id列表
		"""
		EffectIDs = set([])
		for key, value in self._datas.iteritems():
			if value["needEquipLevel"] <= level:
				if not canSystemCreate and value[ "canSystemCreate" ] == 0:
					continue
				EffectIDs.add( key )
		return list( EffectIDs )

	def getLevel( self, effectID ):
		"""
		根据效果ID获取该效果所出现的装备最低等级
		"""
		try:
			return self._datas[effectID]["needEquipLevel"]
		except:
			return 0

	def getReqClass( self, effectID ):
		"""
		根据效果ID获取该效果所出现的装备职业限制
		"""
		try:
			return self._datas[effectID]["needEquipClass"]
		except:
			return 0

	def getPerGene( self, effectID ):
		"""
		根据效果ID获取每单位该效果所需价值因子数
		"""
		try:
			gene =  self._datas[effectID]["needPerProceGene"]
		except:
			gene = 0
		return gene

	def getType( self, effectID ):
		"""
		根据效果ID获取属性类型
		"""
		data = self._datas.get( effectID, None )
		if data is None: return ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD
		return data.get( "type", ItemTypeEnum.EQUIP_EFFECT_TYPE_ADD )

	def canSystemCreate( self, effectID ):
		"""
		判断该条属性是否允许系统随机生成
		@param effectID: 效果编号
		@type  effectID: Int
		@return 1 or 0
		"""
		try:
			return self._datas[effectID]["canSystemCreate"]
		except KeyError:
			ERROR_MSG( "Can't find CanSystemCreate config by %s" % effectID )
			return 0

	def getNoCoexist( self, effectID ):
		"""
		获取效果ID共存表
		"""
		try:
			return list( self._datas[effectID]["noCoexist"] )
		except KeyError:
			ERROR_MSG( "Can't find noCoexist config by %s" % effectID )
			return []

	def canSmelt( self, effectID ):
		"""
		判断该条属性是否允许炼化
		@param effectID: 效果编号
		@type  effectID: Int
		@return 1 or 0
		"""
		try:
			return self._datas[effectID]["canSmelt"]
		except KeyError:
			ERROR_MSG( "Can't find canSmelt config by %s" % effectID )
			return 0
			
# -*- coding: gb18030 -*-

from bwdebug import *
import Language
import csdefine
import Math
from config.client import IntensifyEffect
from config.client import StuddedEffect
from config.client import WeaponGlow


class EquipParticleLoader:
	"""
	装备强化、镶嵌效果加载
	@ivar _data: 全局数据字典; key is id, value is dict like as {key：{...}}
	@type _data: dict
	"""
	_instance = None

	def __init__( self ):
		assert EquipParticleLoader._instance is None, "instance already exist in"
		self._datas = IntensifyEffect.Datas
		self._sdatas = StuddedEffect.Datas
		self._wdatas = WeaponGlow.Datas

	@classmethod
	def instance( self ):
		if self._instance is None:
			self._instance = EquipParticleLoader()
		return self._instance

	def getFsHp( self, intensify ):
		"""
		根据强化等级获取发射效果绑定点
		return string
		"""
		try:
			return self._datas[intensify]["fs_hp"]
		except:
			return ""

	def getFsGx( self, intensify, profession, gender ):
		"""
		根据职业和性别和强化等级获取发射粒子
		return list of string
		"""
		try:
			return self._datas[intensify]["fs_gx"][profession | gender]
		except:
			return []

	def getSsHp( self, intensify ):
		"""
		根据强化等级获取上升效果绑定点
		return string
		"""
		try:
			return self._datas[intensify]["ss_hp"]
		except:
			return ""

	def getSsGx( self, intensify, profession ):
		"""
		根据职业获取上升效果粒子
		return list of string
		"""
		try:
			return self._datas[intensify]["ss_gx"][profession]
		except:
			return []

	def getPxHp( self, intensify ):
		"""
		根据强化等级获取盘旋上升光带效果绑定点
		return string
		"""
		try:
			return self._datas[intensify]["px_hp"]
		except:
			return ""

	def getPxGx( self, intensify ):
		"""
		根据职业获取盘旋上升光带效果粒子
		return list of string
		"""
		try:
			return self._datas[intensify]["px_gx"]
		except:
			return []

	def getLongHp( self, intensify ):
		"""
		根据强化等级获取龙型旋转光环效果绑定点
		return string
		"""
		try:
			return self._datas[intensify]["long_hp"]
		except:
			return ""

	def getLongGx( self, intensify ):
		"""
		根据职业获取龙型旋转光环效果粒子
		return list of string
		"""
		try:
			return self._datas[intensify]["long_gx"]
		except:
			return []

	def getDianHp( self, intensify ):
		"""
		根据强化等级获取龙型旋转光环效果绑定点
		return string
		"""
		try:
			return self._datas[intensify]["dian_hp"]
		except:
			return ""

	def getDianGx( self, intensify ):
		"""
		根据职业获取龙型旋转光环效果粒子
		return list of string
		"""
		try:
			return self._datas[intensify]["dian_gx"]
		except:
			return []

	def getXqHp( self, studdedAmount ):
		"""
		根据镶嵌数量获取镶嵌绑定点
		"""
		try:
			return self._sdatas[studdedAmount]["hp"]
		except:
			return []

	def getXqGx( self, studdedAmount ):
		"""
		根据镶嵌数量获取镶嵌粒子
		return list of string
		"""
		try:
			return self._sdatas[studdedAmount]["particle"]
		except:
			return []

	def getWTexture( self, weaponKey ):
		"""
		根据关键字获取武器贴图路径
		return string
		"""
		try:
			return self._wdatas[weaponKey]["texture"]
		except:
			WARNING_MSG( "Can't find textureConfig by (%s)" % weaponKey )
			return ""

	def getWType( self, weaponKey ):
		"""
		根据关键字获取武器渲染类型
		return Int
		"""
		try:
			return self._wdatas[weaponKey]["type"]
		except:
			WARNING_MSG( "Can't find typeConfig by (%s)" % weaponKey )
			return 0

	def getWScale( self, weaponKey, intensifyLevel ):
		"""
		根据关键字和强化等级获取武器缩放值
		return Vector4
		"""
		key = ""
		if intensifyLevel in [4,5]:
			key = "scale1"
		elif intensifyLevel in [6,7]:
			key = "scale2"
		elif intensifyLevel in [8,9]:
			key = "scale3"

		try:
			return self._wdatas[weaponKey][key]
		except:
			WARNING_MSG( "Can't find scaleConfig by (%s)" % weaponKey )
			return Math.Vector4()

	def getWColour( self, weaponKey ):
		"""
		根据关键字获取武器颜色Vector4
		return Vector4
		"""
		try:
			return self._wdatas[weaponKey]["colour"]
		except:
			WARNING_MSG( "Can't find colourConfig by (%s)" % weaponKey )
			return Math.Vector4()

	def getWOffset( self, weaponKey ):
		"""
		根据关键字获取武器贴图偏移量Vector3
		return Vector3
		"""
		try:
			return self._wdatas[weaponKey]["offset"]
		except:
			WARNING_MSG( "Can't find offsetConfig by (%s)" % weaponKey )
			return Math.Vector3()

	def reset( self ):
		"""
		重新加载数据
		"""
		reload( IntensifyEffect )
		reload( StuddedEffect )
		reload( WeaponGlow )
		self._datas = IntensifyEffect.Datas
		self._sdatas = StuddedEffect.Datas
		self._wdatas = WeaponGlow.Datas
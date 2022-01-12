# -*- coding: gb18030 -*-
#
# 实现模型的缩放edit by wuxo 2012-3-10

"""
BUFF技能类。
"""


from SpellBase import Buff
from gbref import rds

class Buff_299035( Buff ):
	"""
	模型缩放
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self._scale = 1.0
		self._lastTime = 1.0
		self._endLastTime = 1.0
		self._modelScale =(1,1,1)
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		self._scale = float( dict[ "Param1" ] )
		self._lastTime = float( dict[ "Param2" ] )
		self._endLastTime = float( dict[ "Param3" ] )
		
	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		model = target.getModel()
		self._modelScale = model.scale
		if model:
			rds.effectMgr.scaleModel( model, (self._scale, self._scale,self._scale), self._lastTime )
		
	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		model = target.getModel()
		if model:
			rds.effectMgr.scaleModel( model, self._modelScale, self._endLastTime )
		
		
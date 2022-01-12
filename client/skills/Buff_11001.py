# -*- coding: gb18030 -*-
#霸体 buff客户端脚本

from bwdebug import *
from SpellBase import *
import Math

class Buff_11001( Buff ):
	"""
	霸体 buff客户端脚本
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )
		self.color = Math.Vector4( 1.0, 1.0, 1.0, 1.0 )
		self.lastTime = 0.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )
		param2 = dict[ "Param2" ].split(";")
		if len( param2 ) >= 2:
			self.color = eval( param2[0] )
			self.lastTime = eval( param2[1] )

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		target.addModelColorBG( self.getID(), self.color, self.lastTime )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		target.removeModelColorBG( self.getID() )


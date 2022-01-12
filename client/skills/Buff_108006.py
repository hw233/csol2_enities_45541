# -*- coding: gb18030 -*-
#
# $Id: Buff_108006.py,v 1.8 2010-07-17 04:08:27 pengju Exp $

"""
BUFF技能类。
"""
from bwdebug import *
from SpellBase import *
import BigWorld
import skills as Skill
import math
import Math

class Buff_108006( Buff ):
	"""
	example:井底之蛙 BUFF	角色在此期间不会被攻击， 不会被玩家控制， 变成青蛙模型
	"""
	def __init__( self ):
		"""
		从sect构造SkillBase
		@param sect:			技能配置文件的XML Root Section
		@type sect:				DataSection
		"""
		Buff.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff.init( self, dict )

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		yaw = 0
		if target.id == BigWorld.player().id:
			yaw = target.yaw
			direction = Math.Vector3( math.sin(yaw), 0.0, math.cos(yaw) )
			pos = target.position + direction
			ma = Math.Matrix()
			ma.setTranslate( pos ) 
			target.turnaround( ma, None)

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_108006()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

#
# $Log: not supported by cvs2svn $
#
#
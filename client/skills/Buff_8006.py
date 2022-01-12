# -*- coding: gb18030 -*-

"""
飞行buff
"""

import math
import items
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
from Buff_Vehicle import Buff_Vehicle

class Buff_8006( Buff_Vehicle ):
	"""
	飞行buff
	"""
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Buff_Vehicle.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置字典数据
		@type dict:				Python dict
		"""
		Buff_Vehicle.init( self, dict )
		self._des = dict["Description"]
		self._speedInc = int( dict[ "Param1" ] )

	def getDescription( self ):
		"""
		获取此buff的描述
		"""
		# 现在没有相应的骑宠装备，所以只显示基本加速，等以后配置出了飞行骑宠的状态，可以根据装备来计算加速，参考buff 6005
		return self._des
	
	
	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_Vehicle.cast( self, caster, target )
		if target == BigWorld.player():
			target.onEnterFlyState()
	
	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff_Vehicle.end( self, caster,target )

		if target == BigWorld.player():
			# 下飞行骑宠停止自动寻路
			target.endAutoRun( False )
			target.onLeaveFlyState()

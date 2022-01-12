# -*- coding: gb18030 -*-
"""
Spell技能类。
"""
import math
from bwdebug import *
from SpellBase import *
from Function import Functor
import BigWorld
import skills as Skill
import csdefine
import csstatus
import csconst
import csstatus_msgs as StatusMsgs
import Define

class Buff_99027( Buff ):
	"""
	example:骑宠传送	BUFF	角色在此期间不会被攻击， 不会被玩家控制， 坐上骑宠模型
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
		if len( dict["Param2"] ) == 0:
			self.teleportVehicleSeat = 0
		else:
			self.teleportVehicleSeat = int( dict["Param2"] )

	def cast( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.cast( self, caster, target )
		if target.id == BigWorld.player().id:
			target.addControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_99027 )
			target.filter = BigWorld.AvatarFilter()

	def end( self, caster, target ):
		"""
		@param caster	:	施放者Entity
		@type caster	:	Entity
		@param target	: 	施展对象
		@type  target	: 	对象Entity
		"""
		Buff.end( self, caster, target )
		if target.id == BigWorld.player().id: #让镜头回归 add by wuxo 2012-10-20
			BigWorld.player().resetCamera()
			target.removeControlForbid( Define.CONTROL_FORBID_ROLE_MOVE,Define.CONTROL_FORBID_ROLE_MOVE_BUFF_99027  )
			target.filter = target.filterCreator()

	def createFromDict( self, data ):
		"""
		virtual method.
		根据给定的字典数据创建一个与自身相同id号的技能。详细字典数据格式请参数SkillTypeImpl。
		此函数默认返回实例自身，这样在一些不需要保存动态数据的技能中就能以更高的效率进行数据还原，
		如果哪些技能需要保存动态数据，则只要重载此接口即可。

		@type data: dict
		"""
		obj = Buff_99027()
		obj.__dict__.update( self.__dict__ )
		obj.param = data["param"]
		return obj

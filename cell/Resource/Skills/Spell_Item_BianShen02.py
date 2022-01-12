# -*- coding: gb18030 -*-
#
# 变身技能基类 2009-04-02 SPF
#

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csconst
from VehicleHelper import getCurrVehicleID


class Spell_Item_BianShen02( Spell_ItemBuffNormal ):
	"""
	变身技能基类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""

		# 骑乘状态下不允许变身
		if target.getObject().vehicle or getCurrVehicleID( target.getObject() ):
			return csstatus.SKILL_CAST_CHANGE_NO_VEHICLE

		# 判断角色是否在舞厅中
		if target.getObject().actionSign( csdefine.ACTION_ALLOW_DANCE ):
			return csstatus.SKILL_CAST_CHANGE_NO_DANCE

		# 判断角色是否在武道中
		if target.getObject().getState() == csdefine.ENTITY_STATE_DANCE or target.getObject().getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return csstatus.SKILL_IN_FIGHT
		
		# 判断角色是否普通状态
		if target.getObject().getState() != csdefine.ENTITY_STATE_FREE:
			return csstatus.SKILL_IN_FREE

		return Spell_ItemBuffNormal.useableCheck( self, caster, target)
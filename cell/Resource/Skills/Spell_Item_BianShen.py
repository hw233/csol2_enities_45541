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

class Spell_Item_BianShen( Spell_ItemBuffNormal ):
	"""
	变身技能基类
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.spaceLimited = "fengming"

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		"""
		这里先暂时不删掉，策划有可能又改为在指定坐标附近使用
		self.param1 = dict[ "param1" ]
		positionStr = dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else '0, 0, 0'
		posArr = positionStr.replace( " ", "" ).split( "," )
		self.param2 = ( float( posArr[0] ), float( posArr[1] ), float( posArr[2] ) )
		self.param3 = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 )
		"""

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		Spell_ItemBuffNormal.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		# 如果不在对应的坐标位置附近则不能使用变身纸牌
		if self.spaceLimited != "" and caster.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) != self.spaceLimited:
			return csstatus.CIB_MSG_ITEM_NOT_USED_IN_HERE

		# 骑乘状态下不允许变身
		if caster.vehicle or getCurrVehicleID( caster ):
			return csstatus.SKILL_CAST_CHANGE_NO_VEHICLE

		# 判断角色是否在舞厅中
		if caster.actionSign( csdefine.ACTION_ALLOW_DANCE ):
			return csstatus.SKILL_CAST_CHANGE_NO_DANCE

		# 判断角色是否在武道中
		if caster.getState() == csdefine.ENTITY_STATE_DANCE or caster.getState() == csdefine.ENTITY_STATE_DOUBLE_DANCE:
			return csstatus.SKILL_IN_FIGHT
		
		# 判断角色是否在舞厅中
		if caster.getState() == csdefine.ENTITY_STATE_FIGHT:
			return csstatus.SKILL_IN_FIGHT

		return Spell_ItemBuffNormal.useableCheck( self, caster, target)
# -*- coding: gb18030 -*-
#
# $Id: Spell_Item.py,v 1.1 12:10 2010-9-4 jianyi Exp $

import BigWorld
import csdefine
import csstatus
from bwdebug import *
from Spell_Item import Spell_Item

class Spell_Item_NPC_Visible( Spell_Item ):
	"""
	使用物品让一个NPC可见/不可见
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.targetNpcClassName = dict["param1"] if len( dict["param1"] ) > 0 else None	# str or None
		self.checkDistance = int( dict["param2"] if len( dict["param2"] ) > 0 else 0 )
		self.visible = bool( int( dict["param3"] if len( dict["param3"] ) > 0 else 0 ) )
		self.lasted = float( dict["param4"] if len( dict["param4"] ) > 0 else 0 )
		
	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		主要是屏蔽信息，避免不能使用物品时提示使用技能
		"""
		# 防止其他原因导致的不可施法
		if self.targetNpcClassName is None:
			ERROR_MSG( "config error, target npc className is None." )
			return csstatus.CIB_ITEM_CONFIG_ERROR
		if self.checkDistance <= 0:
			ERROR_MSG( "config error, check distance is 0 or less." )
			return csstatus.CIB_ITEM_CONFIG_ERROR
		
		t = None
		entities = caster.entitiesInRangeExt( self.checkDistance )
		for e in entities:
			if e.className == self.targetNpcClassName:
				t = e
		if t is None:
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
				
		return Spell_Item.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		法术到达时
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		entities = caster.entitiesInRangeExt( self.checkDistance )
		for e in entities:
			if e.className == self.targetNpcClassName:
				if e.isReal():
					e.setVisibleByRole( caster, self.visible, self.lasted )
				else:
					e.remoteCall( "setVisibleByRole", ( caster, self.visible, self.lasted ) )
		Spell_Item.receive( self, caster, receiver )
# -*- coding: gb18030 -*-
#
# 2009-04-06 SongPeifang

from SpellBase import *
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csarithmetic

class Spell_Item_Dart_ExpandLife( Spell_ItemBuffNormal ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )	

			
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.param1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 		# 距离镖车的距离
				
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		dartId = caster.queryTemp( 'dart_id', 0 )
		receiver = BigWorld.entities[dartId]
		Spell_ItemBuffNormal.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		for id in caster.questsTable._quests:
			if caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_DART or caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				dartId = caster.queryTemp( 'dart_id', 0 )
				if BigWorld.entities.has_key( dartId ) and csarithmetic.distancePP3( caster.position, BigWorld.entities[dartId].position ) <= self.param1:
					return Spell_ItemBuffNormal.useableCheck( self, caster, target)
		return csstatus.SKILL_USE_ITEM_DO_NOT_FIND_DART
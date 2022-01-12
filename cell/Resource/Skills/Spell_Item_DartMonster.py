# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_DartMonster.py,v 1.1 2008-09-05 03:42:03 zhangyuxing Exp $

from SpellBase import *
import cschannel_msgs
import ShareTexts as ST
from Spell_Item import Spell_Item
import csstatus
import BigWorld
import csconst
import csdefine
import csarithmetic
import random
from FactionMgr import factionMgr

class Spell_Item_DartMonster( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = ( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else "" ) 		#招保镖的ID列表
		self.param2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 			#允许召唤几个
		self.param3 = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) 		# 距离镖车的距离
		self._idRate = {}

		if self.param1 == "":
			self.param1 = "20111004:100"
		if self.param2 == 0:
			self.param2 = 1

		idList = self.param1.split('|')
		b = 0
		for i in idList:
			l = i.split(':')
			self._idRate[l[0]] = ( b, b+int(l[1]) )
			b += int(l[1])

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		dartId = caster.queryTemp( 'dart_id', 0 )
		dart = BigWorld.entities[dartId]
		a = random.randint(0, 99)
		boyGuardID = -1
		for i in self._idRate:
			if self._idRate[i][0] <= a and self._idRate[i][1] >= a:
				boyGuardID = i	#召唤的保镖的className
				break
		if boyGuardID == -1:
			boyGuardID = self._idRate.keys()[0]
		entity = dart.createObjectNearPlanes( str( boyGuardID ), dart.position, dart.direction, {'level':caster.level} )
		
		entity.setOwner( dart )
		entity.uname = factionMgr.getName( dart.factionID ) + cschannel_msgs.SKILL_INFO_8
		entity.setTemp( "factionID", dart.factionID )
		tempList = BigWorld.entities[dartId].queryTemp( "DartMonsterIdList", [])
		tempList.append( entity.id )
		dart.setTemp( "DartMonsterIdList", tempList )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		for id in caster.questsTable._quests:
			if caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_DART or caster.getQuest( id ).getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				dartId = caster.queryTemp( 'dart_id', 0 )
				if BigWorld.entities.has_key( dartId ) and csarithmetic.distancePP3( caster.position, BigWorld.entities[dartId].position ) <= self.param3:
					if len(BigWorld.entities[dartId].queryTemp( "DartMonsterIdList", [])) >= self.param2:
						return 	csstatus.SKILL_USE_ITEM_DART_HAS_MONSTER
					return Spell_Item.useableCheck( self, caster, target)
		return csstatus.SKILL_USE_ITEM_DO_NOT_FIND_DART


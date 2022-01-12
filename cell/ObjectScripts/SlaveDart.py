# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster
import csdefine
import BigWorld
import csstatus
import csconst

class SlaveDart( Monster ):
	"""
	镖车
	"""
	def __init__(self):
		Monster.__init__( self )

	def onMonsterDie( self, selfEntity, killerID ):
		"""
		为了增加全局广播 重写加入一个广播类 by姜毅
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.setTemp('beKilled',True)

		if selfEntity.ownerName == "":
			return

		if not BigWorld.entities.has_key( killerID ):
			return

		killer = BigWorld.entities[killerID]
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" :
				return
			killer = owner.entity

		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return

		BigWorld.globalData['DartManager'].addDartMessage( selfEntity.ownerName, csstatus.ROLE_QUEST_DART_NPC_DIE, True )
		factionID = selfEntity.factionID
		if killer.isRobbingOppose( factionID ) and killer.level - selfEntity.queryTemp( "level", selfEntity.level ) < csconst.DART_ROB_MIN_LEVEL:
			selfEntity.dartMissionBrocad( killer, factionID )
			questID = selfEntity.queryTemp( 'questID', 0 )
			killer.questDartKilled( questID, factionID )
			return
		selfEntity.calcKillerPkValue( killer )	#增加狙杀镖车车者的pk值
		if killer.level - selfEntity.level <= csconst.DART_ROB_MIN_LEVEL:
			self.dropItemBox( selfEntity, selfEntity.getBootyOwner() )
			
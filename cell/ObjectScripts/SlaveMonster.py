# -*- coding: gb18030 -*-

from bwdebug import *
from Monster import Monster
import csdefine
import BigWorld
import csconst

class SlaveMonster( Monster ):
	"""
	怪物类，续承于NPC和可战斗单位
	"""
	def __init__(self):
		Monster.__init__( self )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		"""
		self.dieNotify( selfEntity, killerID )
		selfEntity.setTemp('beKilled',True)

		if selfEntity.ownerName == "":
			return

		if not BigWorld.entities.has_key( killerID ):
			return

		killer = BigWorld.entities[killerID]
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			earg, killer = killer.getOwner()
			if earg == "MAILBOX" :
				return

		if not killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return

		factionID = selfEntity.queryTemp( "factionID", -1 )
		if killer.isRobbingOppose( factionID ) and killer.level - selfEntity.queryTemp( "level", selfEntity.level ) < csconst.DART_ROB_MIN_LEVEL:
			return

		selfEntity.calcKillerPkValue( killer )	# 增加狙杀保镖的pk值


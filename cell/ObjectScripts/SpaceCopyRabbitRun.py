# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
import BigWorld
import csconst
import csdefine

WAIT_FOR_RABBIT_RUN	= 344021001	# 等待小兔快跑BUFF

FORBID_ACTION = csdefine.ACTION_FORBID_PK|csdefine.ACTION_FORBID_CALL_PET|csdefine.ACTION_FORBID_VEHICLE|csdefine.ACTION_FORBID_FIGHT|csdefine.ACTION_FORBID_CHAT|csdefine.ACTION_FORBID_USE_ITEM

class SpaceCopyRabbitRun( SpaceCopy ):
	"""
	小兔快跑
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )

	def initContent( self ):
		"""
		"""
		self.contents.append( None )
		pass

	def onLoadEntityProperties_( self, section ):
		"""
		"""
		SpaceCopy.onLoadEntityProperties_( self, section )
		self.wolfSkillIDs = [ int( skillID ) for skillID in section.readString( "wolfSkills" ).split( ";" ) ]
		self.rabbitSkillIDs = [ int( skillID ) for skillID in section.readString( "rabbitSkills" ).split( ";" ) ]

	def packedDomainData( self, player ):
		"""
		"""
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = 0
		data = {"copyLevel"			: 	level,
				"dbID" 				: 	0,
				"spaceLabel"		:	BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY ),
				"position"			:	player.position,
				"spaceKey"			:	0,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, player )
		packDict[ "dbID" ] = 0
		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		baseMailbox.cell.remoteCall( "addFlag", ( csdefine.ROLE_FLAG_HIDE_INFO, ) )
		baseMailbox.cell.remoteCall( "addFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )
		baseMailbox.cell.remoteCall( "actCounterInc",( FORBID_ACTION, ) )

		

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, selfEntity, id, userArg )


	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.remoteCall( "removeFlag", ( csdefine.ROLE_FLAG_HIDE_INFO, ) )
		baseMailbox.cell.remoteCall( "removeFlag", ( csdefine.ROLE_FLAG_AREA_SKILL_ONLY, ) )
		baseMailbox.cell.remoteCall( "actCounterDec",( FORBID_ACTION, ) )
		
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )


	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		SpaceCopy.onTeleportReady( self, selfEntity, baseMailbox )
		baseMailbox.cell.spellTarget( WAIT_FOR_RABBIT_RUN, baseMailbox.id )


	def canUseSkill( self, playerEntity, skillID ):
		"""
		"""
		if playerEntity.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_WOLF_BUFF_ID ) is not None:
			return skillID in self.wolfSkillIDs
		
		if playerEntity.findBuffByID( csconst.RABBIT_RUN_CATCH_RABBIT_RABBIT_BUFF_ID ) is not None:
			return skillID in self.rabbitSkillIDs
		return False
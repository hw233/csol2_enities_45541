# -*- coding: gb18030 -*-
#


import BigWorld
from SpaceCopyTeam import SpaceCopyTeam
import random
import csstatus
import Const


CLOSE_GUMIGONG		= 2

class SpaceCopyGumigong(SpaceCopyTeam):
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True

	def packedDomainData( self, entity ):
		"""
		"""
		data = {  'dbID' : entity.databaseID, "teamID" : entity.teamMailbox.id,"captainDBID"	: entity.id, "spaceKey": entity.teamMailbox.id }
		return data
	
	
	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		"""
		selfEntity.addTimer( 7200.0, 0.0, CLOSE_GUMIGONG )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		��������ˮ������ά������
		"""
		if userArg == CLOSE_GUMIGONG:
			for e in selfEntity._players:
				if BigWorld.entities.has_key( e.id ):
					BigWorld.entities[ e.id ].gotoForetime()
					BigWorld.entities[ e.id ].client.onStatusMessage( csstatus.SPACE_WILL_CLOSE_IN_10_SECOND, "" )
				else:
					e.cell.gotoForetime()
			selfEntity.addTimer( 10.0, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )
			
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		pass
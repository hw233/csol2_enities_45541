# -*- coding: gb18030 -*-
#
# $Id: SpaceCopy.py,v 1.3 2008-01-28 06:08:59 kebiao Exp $

"""
"""
import BigWorld
import csdefine
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy
import Const

class SpaceCopyPotential( SpaceCopy ):
	"""
	����
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )

	def onDisableQuest( self ):
		"""
		define method.
		ĳ����������� ���� ʧЧ��(����ȡ����)
		"""
		DEBUG_MSG( "Ǳ����������������NPC." )
		if self.queryTemp( "NPC_Dead", 0 ) == 0:
			self.params[ "NPCObjMailbox" ].cell.remoteScriptCall( "onDestroySelf", () )

	def addSpawnPoint( self, spawnPointBaseMB ):
		"""
		"""
		key = "spawnPointPotentialBaseMB"
		spawnPointBaseMBList = self.queryTemp( key, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( key, spawnPointBaseMBList )
		
	def addDarkSpawnPoint( self, spawnPointBaseMB ):
		"""
		"""
		key = "spawnPointPotentialDarkBaseMB"
		spawnPointBaseMBList = self.queryTemp( key, [] )
		spawnPointBaseMBList.append( spawnPointBaseMB )
		self.setTemp( key, spawnPointBaseMBList )
	
	def spawnPotentialMonster( self ):
		self.setTemp( "timer_castMon", self.addTimer( 1.0, 0, 0x01 ) )
#
#
#
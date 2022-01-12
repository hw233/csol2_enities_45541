# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy
import csstatus
import Const

class SpaceCopyMaps( SpaceCopy ):
	"""
	���ͼ����
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
	
	def onCloseMapsCopy( self ):
		"""
		define method.
		�رո���
		"""
		if not self.waitDestroy:
			self.waitDestroy = True
			self.getScript().onCloseMapsCopy( self )
	
	def setCopyKillBoss( self, bossNum ):
		"""
		define method
		���ø���BOSS����
		"""
		self.copyStatBoss = bossNum
		self.getScript().setCopyKillBoss( self, bossNum )
	
	def setCopyKillMonster( self, monsterNum ):
		"""
		define method
		���ø���С������
		"""
		self.copyStatMonster = monsterNum
		self.getScript().setCopyKillMonster( self, monsterNum )
	
	def getSpaceGlobalKey( self ):
		"""
		��ȡ�������global key
		"""
		spaceType = self.getScript().getSpaceType()
		teamId = self.params['teamID'] if self.params.has_key( "teamID" ) else 0
		if Const.SPACE_COPY_GLOBAL_KEY.has_key( spaceType ):
			return Const.GET_SPACE_COPY_GLOBAL_KEY( spaceType, teamId, self.getScript().difficulty )
		else:
			return ""

	def onAllCopyMonsterkilled( self, spaceName ):
		"""
		define method
		������С��ȫ������ɱ
		"""
		self.getScript().onAllCopyMonsterkilled( self, spaceName )

	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		�����������븱��
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			copyNo = self.getScript().getCopyNo()
			spaceMapsInfos = self.getScript().getSpaceBirth( copyNo )
			pos, direction = spaceMapsInfos[1], spaceMapsInfos[2]
			playerMB.cell.onSpaceCopyTeleport( actType, self.className, pos, direction, not( playerDBID in self._enterRecord ) )
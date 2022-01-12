# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus
import Const
from Love3 import g_copyPotentialMeleeLoader as g_config

COMMAN_PASS_MAX_REMAIN = 2

class SpaceCopyPotentialMelee( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.batchs = g_config.getBatchTotal()
		self.liveMonsterNum = g_config.getMonsterCount()
		self.liveBossNum = g_config.getBossCount()
		
	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			if BigWorld.globalData.has_key( self.queryTemp('globalkey') ):
				del BigWorld.globalData[self.queryTemp('globalkey')]

	def setLeaveTeamPlayerMB( self, baseMailbox ):
		"""
		define method
		"""
		self.setTemp( 'leavePMB', baseMailbox )
	
	def onNotifySpaceMonsterDie( self, className, killerID ):
		"""
		define method.
		�����������
		"""
		if self.queryTemp( "spaceIsComplete", False ):
			return 
			
		self.setTemp( "spaceIsComplete", True )
		
		for e in self._players:
			if BigWorld.entities.has_key( e.id ):
				e.client.onStatusMessage( csstatus.POTENTIAL_MELEE_FLAG_DIE, "" )
		
		self.getScript().onFlagDie( self )
	
	def onNotifySpaceMonsterHP( self, className, hp, hp_max ):
		"""
		define method.
		�������Ѫ�������仯
		"""
		precent = int( hp*1.0/ hp_max * 100 )
		if  int( BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP ) )== precent:
			return
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_POTENTIAL_FLAG_HP, precent )
	
	def onAINotifySpaceDied( self, className, entity ):
		"""
		define method.
		AI֪ͨNPC����
		"""
		SpaceCopy.onAINotifySpaceDied( self, className, entity )
		self.checkDoPass()
	
	def checkDoPass( self ):
		# ��������������Ƿ���ִ��ͨ��
		if self.curBatch in g_config.mustKillAllBath:
			if g_config.isKillAllBefMonster( self.curBatch, self.liveMonsterNum, self.liveBossNum ):
				if self.isCallAllDie():
					self.getScript().passBatch( self )
		else:
			aiRecordMonsterNum = len( self.aiRecordMonster )
			if aiRecordMonsterNum <= COMMAN_PASS_MAX_REMAIN:
				n = COMMAN_PASS_MAX_REMAIN - aiRecordMonsterNum
				if g_config.isKillAllBefMonster( self.curBatch, self.liveMonsterNum - n, self.liveBossNum ):
					self.getScript().passBatch( self )
	
	def startNextBatch( self ):
		"""
		�����µ�һ��
		"""
		self.curBatch += 1
		BigWorld.setSpaceData( self.spaceID, csconst.SPACE_SPACEDATA_LEVEL, g_config.getBatchTotal() - self.curBatch )
		self.base.spawnMonster( self.curBatch, { "level": self.teamLevel } )

	def isCallAllDie( self ):
		return len( self.aiRecordMonster ) == 0
	
	def isLastBatch( self ):
		return self.batchs == self.curBatch
		
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
		]
		"""
		# ��ʾʣ�����Σ�ʣ��BOSS��ʣ��ʱ�䡣
		return [ 0, 1, 2, 3, 10 ]
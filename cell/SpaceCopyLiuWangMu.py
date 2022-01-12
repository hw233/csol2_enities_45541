# -*- coding: gb18030 -*-
from bwdebug import *
import BigWorld
import Math
from SpaceCopy import SpaceCopy
import random
from TimeString import TimeString


class SpaceCopyLiuWangMu( SpaceCopy ):
	# ����Ĺ
	def __init__( self ):
		SpaceCopy.__init__( self )
	#	self.base.spawnMonster()
			

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		if self.getScript().isViewer( params ):
			self.onEnterViewer( baseMailbox, params)
		else:
			self.onEnterCommon( baseMailbox, params )
 		DEBUG_MSG("player %d enter liuwangmu"%baseMailbox.id)
		baseMailbox.cell.lockPkMode()
		baseMailbox.cell.setTemp( "copy_space_lock_pkmode", 4 ) #���pkģʽ
		
		#	baseMailbox.gotoSpace( baseMailbox.reviveSpace, baseMailbox.revivePosition, baseMailbox.reviveDirection )

	def rankList(self, msg):
		"""
		define method
		"""
		for player in self._players:
			#msg = [self.getMaxDamagePlayers(10), self.getMaxDamageTongs(3), self.playerNameTotongName]
			player.client.showRankList(msg)
			INFO_MSG("LIU_WANG_MU_ACTIVITY_RESULT is %s",msg)		
		
	def activityClosed(self):
		"""
		define method
		boss���������Ͳ����ߵ�����
		ֻ�л������bossû�����Ż��ɸ����ռ��base����
		"""
		INFO_MSG("liuwangmu space get notice activity is over!")
		bossID = self.queryTemp( "liuwangmuBossEntityID", -1 )					# �������Ĺ��bossID��¼��������Ĺ��bossAI�����ģ��ڽű����Ҳ�����
		if bossID == -1:
			ERROR_MSG( "----->>> liuwangmuBossEntityID hasn't recorded to space when creating normal monster!" )
			return
		if BigWorld.entities.get(bossID, None):  #���boss�����򲻻��������
			DEBUG_MSG("liuwangmu boss: %d not dead, but activity is over!"%bossID)
			BigWorld.entities[bossID].onActivityClosed()
			
	def readyToClosed(self):
		"""
		defined method
		"""
		INFO_MSG("liuwangmu space ready to close!")
		for player in self._players:
			area = random.random() * 10 * 2 - 10
			player.gotoSpace("zly_bi_shi_jian", Math.Vector3(-457.0 + area, 60.0, -841.0 + area), Math.Vector3(0, 0, 0))
		

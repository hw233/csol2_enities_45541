# -*- coding: gb18030 -*-

from MiniMonster_Mini import MiniMonster_Mini
import BigWorld
import csdefine
from bwdebug import *
import time
from YXLMBoss import YXLMBoss
from Resource.LolMiniMonsterData import LolMiniMonsterData

g_lolMiniMonsterData = LolMiniMonsterData.instance()


class MiniMonster_Lol( MiniMonster_Mini ):
	"""
	Ӣ������С��
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		MiniMonster_Mini.__init__( self )
		self.patrolList = ""
		self.enemyClasses = []		# �жԹ���ID
	
	def loadLolData( self, selfEntity ):
		"""
		����С������
		"""
		data = g_lolMiniMonsterData.getLolMiniMonsterData( selfEntity.className )
		self.patrolList = data["patrolList"]
		self.enemyIDs = data["enemyIDs"].split( "|" )
		
	def onFightAIHeartbeat( self, selfEntity ):
		"""
		ս��״̬��AI �� ����
		"""
		MiniMonster_Mini.onFightAIHeartbeat( self, selfEntity )
		
		# ÿ��3������ѡ�������С����Ϊ����Ŀ��
		if selfEntity.fightStartTime > 0 and int( ( time.time() - selfEntity.fightStartTime ) ) % 3 == 0:
			target = BigWorld.entities.get( selfEntity.targetID )
			if target:
				if target.utype == csdefine.ENTITY_TYPE_ROLE or isinstance( target, YXLMBoss ):
					selfEntity.getNearByEnemy( float( selfEntity.viewRange ) )	# ���׷����һ�Boss��ǿ���л�Ŀ��
	
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		yxlm�������еĲ�������
		"""
		self.dieNotify( selfEntity, killerID )
		bootyOwner = selfEntity.getBootyOwner()					# ����ӵ����
		if bootyOwner[0] != 0:							# ��õ���ɱ������
			killers = selfEntity.gainSingleReward( bootyOwner[0] )
			for entity in killers:
				entity.client.onShowAccumPoint( selfEntity.id, selfEntity.accumPoint )
		else:
			INFO_MSG( "%s(%i): I died, but no booty owner." % ( selfEntity.className, selfEntity.id ) )


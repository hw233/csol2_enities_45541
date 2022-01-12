# -*- coding: gb18030 -*-
import time
import random
import BigWorld

from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csconst
import csstatus
import Const

INIT_INTEGRAL = 5	  #��ʼ����

TIMER_START_ACT		 = 1	# ��ʼս��
TIMER_CLOSE_ACT 	 = 2 	# �رջ
TIMER_BOSS_REVIVE 	 = 3	# BOSS����
TIMER_CLOSE_CD		 = 4	# ֪ͨ�ͻ��˵ĵ���ʱ

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# ҹս������
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.minLevel = 0
		self.maxLevel = 0
		self.isSpaceDesideDrop = True
		self.enterInfos = []
		self.gainSkillID = 0
		self.integralClassName = ""
		self.closeTime = 5
		self.reviveTime = 0
		self.prepareTime = 0
		self.spaceLife = 0
		self.bossRevive = 0
	
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )
		self.minLevel = section[ "Space" ][ "minLevel" ].asInt
		self.maxLevel = section[ "Space" ][ "maxLevel" ].asInt
		
		for idx, item in enumerate( section[ "Space" ][ "enterInfos" ].values() ):
			pos = tuple( [ float(x) for x in item["position"].asString.split() ] )
			direction = tuple( [ float(x) for x in item["direction"].asString.split() ] )
			self.enterInfos.append( ( pos, direction ) )
		
		roleDieCreate = []
		for item in section[ "Space" ][ "roleDieCreate" ].values():
			roleDieCreate.append( item.asString )
		
		gainSkill, self.integralClassName = roleDieCreate
		self.gainSkillID = int( gainSkill )
		
		self.closeTime = section[ "Space" ][ "closeTime" ].asInt
		self.reviveTime = section[ "Space" ][ "reviveTime" ].asInt
		self.prepareTime = section[ "Space" ][ "prepareTime" ].asInt # ׼��ʱ��
		self.spaceLife = section[ "Space" ][ "spaceLife" ].asInt # ����ʱ��
		self.bossRevive = section[ "Space" ][ "bossRevive" ].asInt # Boss����ʱ��
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		SpaceCopy.initEntity( self, selfEntity )
		
		prepareTime = self.prepareTime * 60 - ( time.time() - selfEntity.actStartTime )
		selfEntity.addTimer( prepareTime, 0, TIMER_START_ACT )
		
		spaceTime = self.spaceLife * 60 - ( time.time() - selfEntity.actStartTime )
		selfEntity.addTimer( spaceTime - 60, 0, TIMER_CLOSE_CD )
		
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.actStartTime )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_PREPARE_TIME, self.prepareTime * 60 )
	
	def getRandomEnterPos( self ):
		"""
		���ȡ��һ�������λ��
		"""
		return random.choice( self.enterInfos )
	
	def packedDomainData( self, entity ):
		"""
		����SpaceDomainShenGuiMiJingʱ�����ݲ���
		"""
		d = {}
		d[ "dbID" ] = entity.databaseID
		d[ "level" ] = entity.level
		return d
	
	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		d = {}
		d[ "roleName" ] = entity.getName()
		d.update( SpaceCopy.packedSpaceDataOnEnter( self, entity ) )
		return d
		
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		����
		"""
		selfEntity.battlefieldIntegral.add( baseMailbox, params[ "roleName" ] )
		baseMailbox.cell.fengQiOnEnter( selfEntity.warIsAction )
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		�뿪
		"""
		selfEntity.playerExit( baseMailbox )
		selfEntity.battlefieldIntegral.onAcitivyEnd( baseMailbox )
		SpaceCopy.onLeaveCommon( self, selfEntity, baseMailbox, params )
	
	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		ĳrole�ڸø���������
		"""
		killerType = 0
		killerBase = None
		if killer:
			killerType = killer.getEntityType()
			killerBase  = killer.base
			
		role.getCurrentSpaceBase().cell.onRoleBeKill( tuple( role.position ), role.base, killerBase, killerType )
	
	def activityAction( self, selfEntity ):
		"""
		׼��ʱ���������ʼս��
		"""
		selfEntity.warIsAction = True
		for e in selfEntity._players:
			e.cell.fengQiAction()
		
		selfEntity.base.createSpawnEntities( { "level": selfEntity.spaceLevel } )
	
	def closeActivity( self, selfEntity ):
		for e in selfEntity._players:
			e.cell.fengQiCloseActivity()
			
		selfEntity.addTimer( self.closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( self.closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
	
	def notifyCountDown( self, selfEntity ):
		# ��������ʱ
		for e in selfEntity._players:
			e.client.fengQiCountDown()
	
	def bossAllDie( self, selfEntity ):
		# ���е�BOSSȫ����
		selfEntity.addTimer( self.bossRevive, 0.0, TIMER_BOSS_REVIVE )
	
	def reviveBoss( self, selfEntity ):
		# ����BOSS
		if len( selfEntity.aiRecordMonster ) == 0:
			selfEntity.base.createSpawnEntities( { "level": selfEntity.spaceLevel } )
	
	def onTimer( self, selfEntity, id, userArg ):
		"""
		ʱ�������
		"""
		if userArg == TIMER_START_ACT:
			self.activityAction( selfEntity )
		
		if userArg == TIMER_CLOSE_CD:
			self.notifyCountDown( selfEntity )
		
		elif userArg == TIMER_CLOSE_ACT:
			self.closeActivity( selfEntity )
		
		elif userArg == TIMER_BOSS_REVIVE:
			self.reviveBoss( selfEntity )
			
		else:
			SpaceCopy.onTimer( self, selfEntity, id, userArg )
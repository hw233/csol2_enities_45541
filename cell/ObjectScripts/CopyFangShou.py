# -*- coding: gb18030 -*-

# ------------------------------------------------
# from python
import time
# ------------------------------------------------
# from engine
import BigWorld
# ------------------------------------------------
# from common
import csdefine
import csstatus
import csconst
# ------------------------------------------------
# from locale_default
import cschannel_msgs
# ------------------------------------------------
# from cell
import Const
# ------------------------------------------------
# from current directory
from CopyTeamTemplate import CopyTeamTemplate

# ------------------------------------------------



class CopyFangShou( CopyTeamTemplate ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		CopyTeamTemplate.__init__( self )

	def onFangShouGearStarting( self, selfEntity, areaName ) :
		"""
		���ظ������ؿ����ص�
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["areaName"] = areaName
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_GEAR_STARTING, params )
	
	def onFangShouTowerCreate( self, selfEntity, currentArea, towerID ) :
		"""
		���ظ��������������ص�
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["currentArea"] = currentArea
		params["towerID"] = towerID
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_TOWER_CREATE, params )
	
	def onFangShouNpcHPChanged( self, selfEntity, hp, hp_max ) :
		"""
		����NPCѪ���ı�ص�
		"""
		currentStage = self.getCurrentStage( selfEntity )
		params = {}
		params["hp"] = hp
		params["hp_max"] = hp_max
		currentStage.doAllEvent( selfEntity, csdefine.COPY_EVENT_FANG_SHOU_ON_NPC_HP_CHANGED, params )
	
	def onTimer( self, selfEntity, timerID, userArg, params ) :
		"""
		"""
		if userArg == Const.SPACE_TIMER_ARG_FANG_SHOU_DELAY_SPAWN_MONSTER :		# ���ظ����ӳ� 1 ��ˢ��timer
			selfEntity.base.spawnMonsters( { "monsterType" : 3, "level": selfEntity.params["copyLevel"] } )
		CopyTeamTemplate.onTimer( self, selfEntity, timerID, userArg, params )
	
	def packedDomainData( self, player ):
		"""
		"""
		data = CopyTeamTemplate.packedDomainData( self, player )
		copyLevel = player.level
		if player.getTeamCaptain() :
			copyLevel = player.getTeamCaptain().level
		data["copyLevel"] = copyLevel

		return data

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
		# ��ʾʣ��С�֣�ʣ��BOSS�� 
		return [ 0, 1, 3, 21, 12, 22 ]
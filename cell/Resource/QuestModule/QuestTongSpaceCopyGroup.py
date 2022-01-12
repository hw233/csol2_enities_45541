# -*- coding: gb18030 -*-
#
# $Id $

"""
��ḱ������ģ�飺 by mushuang
�μ� CSOL-9753
��ʾ��
	��ḱ������������ȼ����ֲ�ͬ�ȼ�����ҿɽ��ܵ����񣬱��磺
	�ȼ�			���ܳ�������					����ȼ�
	45-54	"��ɱ30�Ű�ɫˮ����ˮ����������
			��ɱ30ֻ�����ʹӣ�����ؾ�����
			��ɱ30ֻħ�ƻ�������ǰ�ڣ���"			50
	55-64	"��ɱ30�Ű�ɫˮ����ˮ����������
			��ɱ30ֻ�����ʹӣ�����ؾ�����
			��ɱ30ֻħ�ƻ�������ǰ�ڣ���
			��ɱ������֮Ӱ��ʧ�䱦�أ���"			60
	65-74	"��ɱ30�Ű�ɫˮ����ˮ����������
			��ɱ30ֻ�����ʹӣ�����ؾ�����
			��ɱ30ֻħ�ƻ�������ǰ�ڣ���
			��ɱ������֮Ӱ��ʧ�䱦�أ���
			��ɱ�����5��СBOSS����أ���
			��ɱ5ֻӲ����ħ�����Ȫm؅����"			70
	75-84	"��ɱ30�Ű�ɫˮ����ˮ����������
			��ɱ30ֻ�����ʹӣ�����ؾ�����
			��ɱ30ֻħ�ƻ�������ǰ�ڣ���
			��ɱ������֮Ӱ��ʧ�䱦�أ���
			��ɱ�����5��СBOSS����أ���
			��ɱ5ֻӲ����ħ�����Ȫm؅����
			����10ֻа�����飨а����Ѩ����"			80
			
��ƣ�
	��ḱ��������������������飬��Ӧ�أ��С���ḱ�������顱�͡���ḱ�������񡱡�
��ḱ����������ָ��Щ��ͬ�ȼ��ε���ҿ��Խ��ܵ�����ͬ��������ͬһ�죬ͬһ�ȼ���
����ҽ��ܵ��İ�ḱ����������ͬ����ÿ����㣨��ʹ�����������������£����Ҳ���Կ�
����1���ڣ�ˢ�½���İ�ḱ��������

"��ḱ��������"����Ҳ��һ�����񣬵����ڽ������ʱ�����Ὣ����ת��������ḱ����
���񡱡�����֮�������Զ�����ܽӵ�"��ḱ��������"���񡣵�����"��ḱ��������"�Ľ�
������������������ò����Ͻ��ܰ�ḱ��������������ҿ�������ḱ������

�μ����ģʽ�����
"""

from Quest import *
import QuestTongNormal
from QuestDataType import QuestDataType
from QuestRandomRecordType import QuestRandomRecordType
from ActivityRecordMgr import g_activityRecordMgr
from string import Template
from QTScript import QTSGiveItems
from bwdebug import *
import csdefine
import csstatus
import QTReward
import QTTask
import random
import time
from config.server.PlayerLevelToQuestLevelMap import Datas as mapPlayerLevelToQuestLevel # ����ҵȼ�ӳ��Ϊ����ȼ�

# �߻��涨��ḱ���������Ч����24Сʱ
QUEST_LIFE_TIME = 24 * 3600
PLAYER_REQUIRED_LEVEL = 45

class QuestTongSpaceCopyGroup( Quest ):
	def __init__( self ):
		Quest.__init__( self )
		self._style = csdefine.QUEST_STYLE_TONG_SPACE_COPY	# ������ʽ
		# ������ȼ�ӳ��Ϊ��Ҳ�ͬ�ȼ��εĿ�ѡ����
		self._mapQuestLevelToQuests = {} #{ ����ȼ�1:[ 21,��ѡ����2, ... ], ����ȼ�2:[ ��ѡ����1, ��ѡ����2, ... ], ... }
		# �������ɵĲ�ͬ����ȼ���������Ч��Ϊһ�죬��Ч�ڹ����Ӳ�ͬ�ȼ��εĿ�ѡ���������ѡȡ�µ������������б�
		self._todayQuest = {} #{ ����ȼ�1:����ʵ��, ����ȼ�2:����ʵ�� ... }
		# �Ƿ��Ѿ���ʼ���ı�־
		self._initialized = False
		# ˢ��ʱ��( ��ʱ�� )
		self._refreshTime = 0
		# ������Ч��
		self._lifeTime = QUEST_LIFE_TIME
		
		# ǿ��ˢ�������־
		self._forceRefresh = False
		
		self.__initTodayQuest()
		
	def __initTodayQuest( self ):
		"""
		����ˢ�¾��������ʵ������������ʱ���趨Ϊָ����ʱ��
		"""
		# ����ĳ�ʼˢ��ʱ�䣬Ŀǰ�߻��涨Ϊÿ��00:00:00ˢ��,�����Ҫ����ʱ�����������������
		hour = 0
		minute = 0
		second = 0
		
		
		# �趨��ʼˢ��ʱ�䣨 ע�⣺�Ժ�ÿ��ˢ��ʱ��Ϊ�˴�ˢ��ʱ�� + ��Ч�� ��
		year,month,day = time.localtime()[:3]
		timeString = "%s %s %s %s %s %s" %( year, month, day, hour, minute, second )
		refreshTime = time.mktime( time.strptime( timeString , "%Y %m %d %H %M %S" ) )
		
		self.__doRefresh( refreshTime )
		
	
	def __getDateString( self ):
		"""
		�õ���ǰ�����ַ���������20101111
		"""
		return time.strftime("(%Y, %m, %d)", time.localtime() )
		#year,month,day = time.localtime()[:3]
		#return "%s%s%s"%( year, month, day )
	
	def __canPlayerAcceptQuest( self, player ):
		"""
		��������Ƿ���Խ��ܰ�ḱ������
		"""
		# ��ȡ������ϱ�����ϴβμӰ�ḱ��������ַ�����ʽ������
		# �������磺20101111
		
		#start ����־�Ƿ�Ҫ���£����ڴ˱�־����ҵ�½��ʱ��Ÿ���,����������Ҫ�ֶ����һ�£�
		flagValue = player.queryRoleRecord("tongfuben_record")
		if flagValue == "":
			return True
			
		timeString = flagValue.split("_")[0]
		lastDateHash = hash( timeString )
		currDateHash = hash( self.__getDateString() )
		
		if currDateHash != lastDateHash:
			# ���� false
			self.forceRefresh(player)
			return True
		#end ����־�Ƿ�Ҫ����
		
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_TONG_FUBEN ) :
			return False
		
		return True
		
	def __getFitQuest( self, player ):
		"""
		�������ʵ������õ�������ҵ�����
		"""
		questLevel = mapPlayerLevelToQuestLevel.get( player.level, None )
		if questLevel == None:
			ERROR_MSG( "Config file is inconsistent with code!" )
			return None
		
		quest = self._todayQuest.get( questLevel, None )
		if quest == None:
			ERROR_MSG( "Can't find quest of specified questLevel! Quest config maybe wrong!" )
			return None
		
		return quest
		
	def __isRefreshNeeded( self ):
		"""
		��鵱ǰʱ�䣬��ȷ���Ƿ���Ҫˢ������
		"""
		currentTimeInSec = time.time()
		refreshTimeInSec = self._refreshTime # �ϴ�ˢ��ʱ��
				
		# if ����������Ѿ����� ���� ǿ��ˢ��
		if currentTimeInSec - refreshTimeInSec >= self._lifeTime or self._forceRefresh :
			self._forceRefresh = False
			# ���� True
			return True
		
		# ���� False
		return False
		
	def __doRefresh( self, refreshTime ):
		"""
		ˢ�����в�ͬ�ȼ��ε�����
		@refreshTime: ִ��ˢ�µ�ʱ��( ��ʱ�� )
		"""
		self._todayQuest = {}
		self._refreshTime = refreshTime
		
		for questLevel in self._mapQuestLevelToQuests:
			quest = random.choice( self._mapQuestLevelToQuests[ questLevel ] )
			self._todayQuest[ questLevel ] = quest
			

	def addChild( self, quest ):
		"""
		��һ������ʵ�����뵽���ʵĵȼ������񼯺�
		"""
		if not self._mapQuestLevelToQuests.has_key( quest._level ):
			self._mapQuestLevelToQuests[ quest._level ] = []

		self._mapQuestLevelToQuests[ quest._level ].append( quest )
		
	def accept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		# if ��Ҳ��߱����������������
		if not self.__canPlayerAcceptQuest( player ):
			# ��ʾ���
			player.statusMessage( csstatus.TONG_SPACE_COPY_ONLY_ONE_CHANCE )
			# ����
			return
			
		# if û�г�ʼ����
		if not self._initialized:
			# ��ʼ��
			self.__initTodayQuest()
			# ���Ϊ�Ѿ���ʼ��
			self._initialized = True
		
		# if ��Ҫˢ������
		if self.__isRefreshNeeded():
			# ˢ������
			self.__doRefresh( time.time() )
		
		
		quest = self.__getFitQuest( player )
		if quest == None:
			ERROR_MSG( "Can't find fit quest for player!" )
			return False
			
		return quest.accept( player )
	
	def baseAccept( self, player ):
		"""
		virtual method.
		���������������ʧ�����򷵻�False��������ұ������˷Ų���������ߣ���

		@param     player: instance of Role Entity
		@type      player: Entity
		@return: BOOL
		@rtype:  BOOL
		"""
		# �˽ӿ������ʵ���в���Ҫ������
		pass
	
	def __hasLoggedQuest( self, player ):
		"""
		�ж�����Ƿ���Ȼ���а�ḱ������
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )
		if 0 == len(questIDs):
			return False
		
		return True
		
	def __removeCurQuest( self, player ):
		"""
		�Ƴ���ḱ������
		"""
		questIDs = player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )
		if 0 == len(questIDs):
			return False
			
		for qid in questIDs:
			player.abandonQuest( player.id, qid )
	
	def query( self, player ):
		"""
		��ѯ��Ҷ�ĳһ������Ľ���״̬��

		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		
		if self.__canPlayerAcceptQuest( player ) and self.checkRequirement( player ):
			# ����о�����û�н�����ô�Զ�����������
			#if self.__hasLoggedQuest( player ) or self._forceRefresh:
				#self.__removeCurQuest( player )

			return csdefine.QUEST_STATE_NOT_HAVE # ���Խӵ���δ�Ӹ�����
		"""	
		isCanAceept = csdefine.QUEST_STATE_NOT_ALLOW
		while(True):
			if not self.__canPlayerAcceptQuest( player ):
				break
			
			if not self.checkRequirement( player ):
				break
			
			if len(player.findQuestByType( csdefine.QUEST_STYLE_TONG_FUBEN )) != 0:
				break
			
			isCanAceept = csdefine.QUEST_STATE_NOT_HAVE
			break
			
		return isCanAceept

	def forceRefresh( self , player ):
		"""
		ǿ��ˢ������
		"""
		player.setRoleRecord("tongfuben_record", "00000000_0")
		g_activityRecordMgr.initAllActivitysJoinState(player)
		self._forceRefresh = True
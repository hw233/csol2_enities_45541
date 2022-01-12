# -*- coding: gb18030 -*-

from bwdebug import *
import csdefine
import csconst
import csstatus
import time
import BigWorld

class FuncRequestTongFete:
	"""
	���������
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		pass
		
		
	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if talkEntity is None:
			player.endGossip( talkEntity )
			return
			
		if not player.checkDutyRights( csdefine.TONG_RIGHT_ACTIVITY ):
			player.statusMessage( csstatus.TONG_FETE_GRADE_INVALID )
			player.endGossip( talkEntity )
			return
		#����CSOL-9750������ȡ��������ĵȼ�����
		#elif player.tong_level < 3:
		#	player.statusMessage( csstatus.TONG_FETE_LEVEL_INVALID )
		#	player.endGossip( talkEntity )
		#	return
		
		tm = time.localtime()
		# ��������Ϊÿ����12:00-22:00֮��ſ������룬by mushuang
		weekDay = tm[6] # 0 ��ʾ��һ
		hour = tm[3]
		minute = tm[4]
		sec = tm[5]		
		curTimeInSec = hour * 3600 + minute * 60 + sec
		# ��ʼʱ�� 12��00
		startTimeInSec = 12 * 3600 
		# ����ʱ�� 22:00
		endTimeInSec = 22 * 3600
		
		if not ( weekDay == 6 and curTimeInSec >= startTimeInSec and curTimeInSec <= endTimeInSec ) :
			player.statusMessage( csstatus.TONG_FETE_DATE_INVALID )
			player.endGossip( talkEntity )
			return
		BigWorld.globalData[ "TongManager" ].requestFete( player.tong_dbID, player.tong_grade, player.base )
		player.endGossip( talkEntity )
		
		
	def valid( self, player, talkEntity = None ):
		"""
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True
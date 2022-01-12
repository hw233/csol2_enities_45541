# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
ռ��
"""
import time
import random
from Function import Function
import csstatus
import csdefine

class FuncAugury( Function ):
	"""
	ռ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# һ��ռ������
		self._param2 = section.readInt( "param2" )	# ÿ��������ɹ�೤ʱ��
		self._param3 = section.readInt( "param3" )	# ռ����Ǯ����
		self._param4 = section.readInt( "param4" )  # ռ�����ʱ��
		self._param5 = section.readString( "param5" )	# ��ɫʩ��ռ������
		self.allSkills = self._param5.split("|")

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		if player.money < self._param3:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_MONEY_LOW )
			return

		# �ж��Ƿ��ںϷ��չ�ԡʱ��
		if not player.isSunBathing() and player.sunBathDailyRecord.sunBathCount < self._param2:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_FORBID_TIME )
			return

		date = time.localtime()[2]
		# �ж��Ƿ�Ϊͬһ��
		if player.sunBathDailyRecord.auguryDate != date:
			player.sunBathDailyRecord.auguryDate = date
			player.sunBathDailyRecord.auguryCount = 0

		# �ж��Ƿ񳬹�ռ������
		if not player.sunBathDailyRecord.auguryCount < self._param1:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_COUNT_LOW )
			return

		# �ж�ռ���Ƿ���5����
		nowTime = int( time.time() )
		if nowTime - player.sunBathDailyRecord.auguryTime < self._param4:
			player.statusMessage( csstatus.SUN_BATHING_AUGURY_INTERVAL_TIME )
			return

		player.sunBathDailyRecord.auguryCount += 1
		player.sunBathDailyRecord.auguryTime = nowTime
		player.payMoney( self._param3, csdefine.CHANGE_MONEY_AUGURY )	# ��ҿ۳���Ǯ

		skillID = int( random.choice( self.allSkills ) )
		player.spellTarget( skillID, player.id )		# ���ѡ��ʩ��һ��ռ������


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
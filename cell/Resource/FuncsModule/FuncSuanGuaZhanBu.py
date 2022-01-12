# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
����ռ��
"""
import time
import cschannel_msgs
import ShareTexts as ST
import random
from Function import Function
import csstatus
import csdefine
from csarithmetic import getRandomElement
from Resource.SuanGuaZhanBuLoader import SuanGuaZhanBuLoader
g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()

class FuncSuanGuaZhanBu( Function ):
	"""
	����ռ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )		# ռ�����Ե���͵ȼ�
		self._param2 = section.readInt( "param2" )		# һ��ռ������
		
		"""
		self._param3 = section.readString( "param3" )	# ռ����Ǯ���ģ����ã�"30-59,60-89,90-119,120-150;1,2,5,15"
		self._param4 = section.readString( "param4" )	# ռ�����ܺͻ��ʣ����ã�"ID1:����1;ID2:����2"

		self._expendKey = []	# [[30, 59], [60, 89], [90, 119], [120, 150]]
		self._expendValue = []	# [1,2,5,15]
		keyStr = self._param3.split( ";" )[0]
		valStr = self._param3.split( ";" )[1]
		for e in keyStr.split(","):
			self._expendKey.append( [ int(e.split( "-" )[0]), int(e.split( "-" )[1]) ] )
		for e in valStr.split(","):
			self._expendValue.append( int(e) )

		self._skillIDList = []				# ��ż��ܵ�ID
		self._skillOddsList = []			# ��ż���ID��Ӧ�Ļ�������
		for e in self._param4.split( ";" ):
			self._skillIDList.append( str( e.split( ":" )[0] ) )
			self._skillOddsList.append( float( e.split( ":" )[1] ) )
		"""

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
		if player.level < self._param2:		# �Ƿ�������͵ȼ�Ҫ��
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_NEED_LEVEL, self._param1 )
			return

		# ��������ж�������Role.selectSuanGuaZhanBu()�����������ڷ�������������³��ֶ����������
		# �μ�CSOL-9799 updated by mushuang
		if not player.suanGuaZhanBuDailyRecord.checklastTime():				# �ж��Ƿ�ͬһ��
			player.suanGuaZhanBuDailyRecord.reset()
		if player.suanGuaZhanBuDailyRecord.getDegree() >= self._param2:		# �жϴ���
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_NUM )
			return

		cost = g_SuanGuaZhanBuLoader.getNeedMoney( player.level )
		if player.money < cost:
			gold = cost / 10000
			silver = cost / 100 - gold * 100
			coin = cost - gold * 10000 - silver * 100
			costText = ""
			if gold : costText += cschannel_msgs.SHI_TU_GIFT_INFO_1%gold
			if silver : costText += cschannel_msgs.SHI_TU_GIFT_INFO_2%silver
			if coin : costText += cschannel_msgs.SHI_TU_GIFT_INFO_3%coin
			player.statusMessage( csstatus.SUAN_GUA_ZHAN_BU_LIMIT_MONEY, costText )
			return

		player.client.askSuanGuaZhanBu( cost )	# ѯ���Ƿ����
		
#		player.suanGuaZhanBuDailyRecord.incrDegree()	# ����ռ��������1
#		player.payMoney( self._expendValue[index], csdefine.CHANGE_MONEY_SUANGUAZHANBU )		# ��ҿ۳���Ǯ

#		skillID = int( getRandomElement( self._skillIDList, self._skillOddsList ) )		# ���ݸ��ʣ�ѡȡ����ID
#		player.spellTarget( skillID, player.id )

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
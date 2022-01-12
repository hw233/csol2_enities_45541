# -*- coding: gb18030 -*-
#
# $Id:  $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csconst
import csdefine
import csstatus


def switchMoney( money ):
	"""
	ת��������ʾ��ʽ ���ڸú������÷�Χ�ȽϹ� ���ݿ´����Ľ��� ���������ӹ����ӿ� by����
	"""
	if money <= 0: return "0"
	gold = int( money / 10000 )
	silver = int( ( money % 10000 ) / 100 )
	coin = int( ( money % 10000 ) % 100 )
	moneyText = ""
	if gold > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_1 % gold
	if silver > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_2 % silver
	if coin > 0: moneyText += cschannel_msgs.ON_LINE_GIFT_INFO_3 % coin
	return moneyText

class FuncPrisonContribute( Function ):
	"""
	��������
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

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
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return

		money = 0
		lv = player.level

		for item in csconst.PRISON_CONTRIBUTE_DATAS:
			if lv <= item[ 1 ]:
				money = item[ 2 ]
				break

		if player.money < money:
			player.statusMessage( csstatus.PRISON_CONTRIBUTE_VALID, switchMoney( money ) )
			return

		player.client.onPrisonContributeSure( money )

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
		return player.pkValue > 0

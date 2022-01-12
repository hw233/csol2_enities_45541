# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import cschannel_msgs
import ShareTexts as ST
import csdefine
import BigWorld
import csstatus
import csconst
import time

datamap = {
	100 : cschannel_msgs.ON_LINE_GIFT_INFO_4,
	200 : cschannel_msgs.KE_JU_SHUANG,
	300 : cschannel_msgs.KE_JU_SAN,
	400 : cschannel_msgs.KE_JU_SI,
	500 : cschannel_msgs.KE_JU_WU,
	600 : cschannel_msgs.KE_JU_LIU,
	700 : cschannel_msgs.KE_JU_QI,
	800 : cschannel_msgs.KE_JU_BA,
	900 : cschannel_msgs.KE_JU_JIU,
	1000 : cschannel_msgs.KE_JU_SHI,
}

class FuncQueryDoubleExpRemainTime( Function ):
	"""
	��ѯ˫������ʣ��ʱ��
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		week = player.takeExpRecord[ "week" ]
		lastTime = player.takeExpRecord[ "lastTime" ]
		remainTime = player.takeExpRecord[ "remainTime" ]
		t = time.localtime()
		week1 = t[6]
		"""
		���㷽ʽ�� �ó���һ�μ�¼��ʱ���� ��ݼ�Ȼ��ó�����������ʱ�䣬
		Ȼ���ý����ʱ���ȥ�ϴμ�¼��ʱ�� �ó���ʱ��������ھ���������ʱ�������
		һ�������Ѿ���ȥ wrriten by kebiao.
		"""
		# �õ���һ�μ�¼ʱ�䵽����24��֮��ļ��
		lastClock = time.ctime( lastTime ).split()[3].split(":")
		lastDayRemainTime = 24 * 60 * 60 - int( lastClock[0] ) * 60 * 60 - int( lastClock[1] ) * 60 - int( lastClock[2] )

		# �ó���һ��ʱ����������������ʱ��
		remainWeekTime = ( 6 - week ) * 60 * 60 * 24
		# �����ʱ��-�ϴ���ȡʱ��Ĳ�ֵ < ��һ����ȡ�����Ǵ��������ʱ��+��һ����ȡ��������24���ʱ�� ��һ������û�й�ȥ
		if ( time.time() - lastTime ) >= remainWeekTime + lastDayRemainTime:
			# һ�����ڹ��� ����ʱ��
			player.takeExpRecord[ "remainTime" ] = 7
		if player.takeExpRecord[ "remainTime" ] > 0:
			s = datamap[ player.takeExpRecord[ "remainTime" ] * 100 ]
			if player.takeExpRecord[ "remainTime" ] == 2:
				s = cschannel_msgs.KE_JU_ER
			player.statusMessage( csstatus.TAKE_EXP_REMAIN_QUERY,  s )
		else:
			if player.takeExpRecord[ "lastTime" ] > 0:
				player.statusMessage( csstatus.TAKE_EXP_REMAIN_OVER )
			else:
				player.statusMessage( csstatus.TAKE_EXP_REMAIN_QUERY,  cschannel_msgs.KE_JU_QI )
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


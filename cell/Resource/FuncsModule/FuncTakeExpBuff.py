# -*- coding: gb18030 -*-
#
# $Id: FuncLevel.py,v 1.1 2008-01-31 05:18:39 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
from csdefine import *		# just for "eval" expediently
import time
import csconst
import csstatus

class FuncTakeExpBuff( Function ):
	"""
	��ȡ����BUFF 10111224
	"""
	def __init__( self, section ):
		"""
		param1: CLASS_*

		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.skillID = section.readInt( "param1" )  			#����ID
		self.hour = section.readInt( "param2" )					#��������Сʱ

	def do( self, player, talkEntity = None ):
		"""
		ִ��һ������

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: None
		"""
		if player.takeExpRecord[ "freezeTime" ] > 0:
			# ��¼��󶳽��ʱ��
			t = time.time() - player.takeExpRecord[ "freezeTime" ]
			lostTime = 0
			if t > 24 * 60 * 60:
				lostTime = t - 24 * 60 * 60

			buff = player.takeExpRecord[ "freezeBuff" ]
			# ����BUFF��ʣ��ʱ��
			buff[ "persistent" ] -= lostTime
			# BUFF�Ƿ�ʱ
			if buff[ "persistent" ] <= 0:
				player.endGossip( talkEntity )
				player.takeExpRecord[ "freezeBuff" ] = { "skill" : None, "persistent" : 0, "currTick" : 0, "state" : 0, "caster" : 0, "index" : 0 ,"sourceType":0 }
				player.takeExpRecord[ "freezeTime" ] = 0
			else:
				player.statusMessage( csstatus.TAKE_EXP_NOT_RESUME_FAIL )
				player.endGossip( talkEntity )
				return

		week = player.takeExpRecord[ "week" ]
		lastTime = player.takeExpRecord[ "lastTime" ]
		remainTime = player.takeExpRecord[ "remainTime" ]
		t = time.localtime()
		week1 = t[6]
		m_hour = self.hour

		if lastTime <= 0: # ��һ��ʹ��
			player.takeExpRecord[ "week" ] = week1
			player.takeExpRecord[ "remainTime" ] = 7
			player.takeExpRecord[ "lastTime" ] = time.time()
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
			player.endGossip( talkEntity )
			return;

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
		if ( time.time() - lastTime ) < remainWeekTime + lastDayRemainTime:
			# һ�����ڻ�û��ȥ
			if remainTime < m_hour : # ʣ��ʱ�䲻��
				player.statusMessage( csstatus.TAKE_EXP_HOUR_LESS )
				player.endGossip( talkEntity )
				return
		else:
			player.takeExpRecord[ "remainTime" ] = 7

		buffs = player.findBuffsByBuffID( 22117 )

		if len( buffs ) <= 0:
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
		else:
			buff = player.getBuff( buffs[ 0 ] )
			if ( buff["persistent"] - time.time() + self.hour * 60 * 60 ) > 5 * 60 * 60: # ������ӵ����Ͻ��ᳬ��5Сʱ ��˲�����
				player.statusMessage( csstatus.TAKE_EXP_HOUR_MAX )
				player.endGossip( talkEntity )
				return
			player.setTemp( "rewardExpHour", m_hour )
			talkEntity.spellTarget( self.skillID, player.id )
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



#
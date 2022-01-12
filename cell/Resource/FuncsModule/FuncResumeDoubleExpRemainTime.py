# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import csdefine
import BigWorld
import csstatus
import csconst
import time

def calculateOnLoad( timeVal ):
	"""
	�ڼ����������ݵ�ʱ�����¼����ӳ�ֵ��
	1.��ȡʣ��ʱ��(��Ҫ�������ߺ��Ƿ��ʱ)
	2.�������ڵķ���������ʱ��

	@type  timeVal: INT32
	@return: �������µ�cooldownʱ��
	@rtype:  INT32
	"""
	if timeVal == 0: return timeVal		# �޳���ʱ�䣬������
	return int( timeVal + time.time() )		# int( (ʣ��ʱ�� + ��ǰ����ʱ��) * ����ֵ )

class FuncResumeDoubleExpRemainTime( Function ):
	"""
	�ָ�˫������ʱ��
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
		player.endGossip( talkEntity )
		buff = player.takeExpRecord[ "freezeBuff" ]
		if player.takeExpRecord[ "freezeTime" ] > 0:
			# ��¼��󶳽��ʱ��
			t = time.time() - player.takeExpRecord[ "freezeTime" ]
			lostTime = 0
			if t > 24 * 60 * 60:
				lostTime = t - 24 * 60 * 60
			
			# BUFF�Ƿ�ʱ
			if buff[ "persistent" ] <= lostTime:
				player.endGossip( talkEntity )
				player.takeExpRecord[ "freezeBuff" ] = { "skill" : None , "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 ,"sourceType" : 0, "isNotIcon": 0 }
				player.takeExpRecord[ "freezeTime" ] = 0
				return
			
			# ����BUFF��ʣ��ʱ��
			buff[ "persistent" ] -= lostTime
			buff[ "persistent" ] = calculateOnLoad( buff[ "persistent" ] )
			player.takeExpRecord[ "freezeBuff" ] = { "skill" :  None , "persistent" : 0, "currTick" : 0, "caster" : 0, "state" : 0, "index" : 0 ,"sourceType" : 0, "isNotIcon": 0 }
			player.takeExpRecord[ "freezeTime" ] = 0


			buffs = player.findBuffsByBuffID( 22117 )

			if len( buffs ) > 0:
				buff1 = player.getBuff( buffs[0] )
				if ( buff1[ "persistent" ] + buff[ "persistent" ] ) > 5 * 60 * 60:
					player.statusMessage( csstatus.TAKE_EXP_HOUR_HUIFU_FAIL )
					player.endGossip( talkEntity )
					return
					
			player.addSavedBuff( buff )
			
			player.statusMessage( csstatus.TAKE_EXP_HOUR_HUIFU, "%i%%" % buff["skill"].getPercent() )

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


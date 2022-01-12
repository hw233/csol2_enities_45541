# -*- coding: gb18030 -*-
#
# $Id: Buff_108003.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

class Buff_13011( Buff_Normal ):
	"""
	example:����ͬʱ���������ħ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #�����˺�����ٷֱ�
		self._p2 = 0 #�����˺�����ٷֱ�
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		receiver.damage_derate_ratio_value += self._p1
		receiver.calcDamageDerateRatio()
		
		receiver.magic_damage_derate_ratio_value += self._p2
		receiver.calcMagicDamageDerateRatio()
		
		receiver.elem_huo_derate_ratio_value += self._p3
		receiver.calcElemHuoDerateRatio()
		receiver.elem_xuan_derate_ratio_value  += self._p3
		receiver.calcElemXuanDerateRatio()
		receiver.elem_lei_derate_ratio_value  += self._p3
		receiver.calcElemLeiDerateRatio()
		receiver.elem_bing_derate_ratio_value  += self._p3
		receiver.calcElemBingDerateRatio()

		skill = buffData["skill"]
		if skill.isMalignant():
			buffData["caster"] = 0
		Buff_Normal.doBegin( self, receiver, buffData )
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()


	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		receiver.damage_derate_ratio_value += self._p1
		receiver.calcDamageDerateRatio()
		
		receiver.magic_damage_derate_ratio_value += self._p2
		receiver.elem_huo_derate_ratio_value += self._p3
		receiver.elem_xuan_derate_ratio_value  += self._p3
		receiver.elem_lei_derate_ratio_value  += self._p3
		receiver.elem_bing_derate_ratio_value  += self._p3
		
		Buff_Normal.doReload( self, receiver, buffData )
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.damage_derate_ratio_value -= self._p1
		receiver.calcDamageDerateRatio()
		receiver.magic_damage_derate_ratio_value -= self._p2
		receiver.calcMagicDamageDerateRatio()
		
		receiver.elem_huo_derate_ratio_value -= self._p3
		receiver.calcElemHuoDerateRatio()
		receiver.elem_xuan_derate_ratio_value  -= self._p3
		receiver.calcElemXuanDerateRatio()
		receiver.elem_lei_derate_ratio_value  -= self._p3
		receiver.calcElemLeiDerateRatio()
		receiver.elem_bing_derate_ratio_value  -= self._p3
		receiver.calcElemBingDerateRatio()
		
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )

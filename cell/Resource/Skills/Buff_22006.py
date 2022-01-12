# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import csdefine
import time
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22006( Buff_Normal ):
	"""
	�չ�ԡbuff���������Ӿ��飨��Ȼ��ָ������Чʱ���ڣ�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) 					# ���Ӿ���Ĺ�ʽ
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 ) 					# ÿ��������ɹ�೤ʱ�䣨 ��λ���� ��
		self._p3 = int( dict[ "LoopSpeed" ] if dict[ "LoopSpeed" ] > 0 else 0 ) 					# ���Ӿ��������ʱ��
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )	# ���ӵľ���ֵ
		self._hpOpt = self._p1[ 2:3 ]						# ������

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
		actPet = receiver.pcg_getActPet()
		if actPet :													# ������Я���г�������
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )	# ���ջ�֮
		Buff_Normal.doBegin( self, receiver, buffData )
		date = time.localtime()[2]
		if receiver.sunBathDailyRecord.date != date:
			receiver.sunBathDailyRecord.date = date
			receiver.sunBathDailyRecord.sunBathCount = 0
			receiver.sunBathDailyRecord.prayCount = 0

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
		Buff_Normal.doReload( self, receiver, buffData )
		actPet = receiver.pcg_getActPet()
		if actPet :													# ������Я���г�������
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )	# ���ջ�֮
		date = time.localtime()[2]
		if receiver.sunBathDailyRecord.date != date:
			receiver.sunBathDailyRecord.date = date
			receiver.sunBathDailyRecord.sunBathCount = 0

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		increaseEXP = self.getIncreaseEXP( receiver.level, self._hpOpt, self._hpVal )
		if receiver.queryTemp( "clean_sun_bath_exp", 0 ) != increaseEXP:
			# ��¼��ҵĴ����չ�ԡ���飬һ����ͼ��ʱ�������һ���ˣ����ﻹҪ����һ�Σ��Է�ֹ��Ҽ���ı�
			receiver.setTemp( "clean_sun_bath_exp", increaseEXP )

		# �жϽ�ɫ�Ƿ��ںϷ��չ�ԡʱ��
		if receiver.isSunBathing() and receiver.sunBathDailyRecord.sunBathCount < self._p2:

			if receiver.queryTemp("btxy_exp_percent", 0.0) > 0:	# �����ɫ�в�����ӿbuff
				increaseEXP = int( increaseEXP * (1 - ( receiver.queryTemp("btxy_exp_percent", 0.0) )/100) )

			gainedExp = 0
			#receiver.updateSunBathCount( self._p3 )	# ѭ���೤ʱ���һ�Σ��ͼӶ���ʱ��

			if receiver.queryTemp( "has_cleanlily_drink", 0 ) == 1:	# �������ˬ����
				expRate = receiver.queryTemp( "drink_exp_rate", 0.0 )
				gainedExp = int( increaseEXP * expRate )			# ���˫�����飨����������������Ҫ������ˬ���ϵ������˶��ٱ���

			if receiver.queryTemp( "sxym_exp_rate", 0.0 ) > 0:	# �����������Ŀbuff
				gainedExp += int( increaseEXP * receiver.queryTemp( "sxym_exp_rate", 0.0 ) )

			if receiver.queryTemp( "lwxl_exp_rate", 0.0 ) > 0:	# �������������buff
				gainedExp += int( increaseEXP * receiver.queryTemp( "lwxl_exp_rate", 0.0 ) )

			if receiver.queryTemp( "scyy_exp_rate", 0.0 ) > 0:	# ������������buff
				gainedExp += int( increaseEXP * receiver.queryTemp( "scyy_exp_rate", 0.0 ) )

			if receiver.queryTemp( "has_sun_bath_vip", 0 ) == 1:	# ����Ǻ���VIP
				expRate = receiver.queryTemp( "vip_exp_rate", 0.0 )
				gainedExp += int( increaseEXP * expRate )			# ����vip���µľ��鷭�������屶��ͬ��Ҫ����VIP���������˶��ٱ���

			if gainedExp == 0:										# ˵��ʲô���鷭���ĵ��߶�û����
				gainedExp = increaseEXP

			if receiver.queryTemp( "hssl_exp_stop", 0 ) != 1:	# �����ɫ�к�����¥buff�򲻻�þ���
				receiver.addExp ( gainedExp, csdefine.CHANGE_EXP_SUN_BATH )

			if receiver.queryTemp( "hsch_gain_potential", 0 ) == 1:	# �����ɫ�к���͸�buff�����ú;���ֵ��ͬ��Ǳ��
				receiver.addPotential( gainedExp )
		else:
			receiver.statusMessage( csstatus.SKILL_NO_SUN_BATH_TIME_EXP )

		return Buff_Normal.doLoop( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "sun_bath_area_count" )	# �������¼��������м�������ı��

	def getIncreaseEXP( self, level, opration, value ):
		"""
		���ݹ�ʽ������ӵ�Exp
		"""
		return level + value
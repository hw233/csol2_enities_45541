# -*- coding: utf_8 -*-
#
# $Id: Buff_62004.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99019( Buff_Normal ):
	"""
	example:�����������40 * ��������%,�������������40 * ��������%��
				<Param1>	40	</Param1>
				<Param2>	����className	</Param3>
				<Param3>	Ѱ�ҷ�Χ	</Param4>
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100
		self._p2 = str( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )

	def addEffect( self, receiver ):
		"""
		"""
		num = 0
		monsterList = receiver.entitiesInRangeExt( self._p3, "Monster", receiver.position )
		for e in monsterList:
			if e.className == self._p2:
				num += 1
		
		receiver.damage_min_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.damage_max_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.magic_damage_percent += self._p1 * ( num - receiver.queryTemp( "99019Num", 0 ) )
		receiver.calcDamageMin()
		receiver.calcDamageMax()
		receiver.calcMagicDamage()
		receiver.setTemp( "99019Num", num )		# ��¼Ŀǰ���������

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
		Buff_Normal.doBegin( self, receiver, buffData )
		self.addEffect( receiver )
		
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
		self.addEffect( receiver )
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		self.addEffect( receiver )

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
		self.addEffect( receiver )
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/07/14 04:05:32  kebiao
# no message
#
# 
#
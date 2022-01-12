# -*- coding: gb18030 -*-
#
# $Id: Buff_1015.py,v 1.2 2007-12-13 04:59:55 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_1016( Buff_Normal ):
	"""
	example:�Ƹ�����	�����������10%��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p2 = 0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100
		self.spaceNames = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) .split("|")
		self._loopSpeed = 3 # ǿ��3����һ��

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
		receiver.strength_percent += self._p2
		receiver.dexterity_percent += self._p2
		receiver.intellect_percent += self._p2
		receiver.corporeity_percent += self._p2
		receiver.calcDynamicProperties()

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
		receiver.strength_percent += self._p2
		receiver.dexterity_percent += self._p2
		receiver.intellect_percent += self._p2
		receiver.corporeity_percent += self._p2

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
		receiver.strength_percent -= self._p2
		receiver.dexterity_percent -= self._p2
		receiver.intellect_percent -= self._p2
		receiver.corporeity_percent -= self._p2
		receiver.calcDynamicProperties()

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
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not spaceType in self.spaceNames:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
#
#
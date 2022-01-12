# -*- coding: gb18030 -*-
#
# $Id: Buff_101015.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_101015( Buff_Normal ):
	"""
	�������������Խ���x�㡣����������½�%�������������½�%��
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0.0
		self._p3 = 0.0

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) 			# �������Խ���x�㡣
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100		# ����������½�%��
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100		# �����������½�%��


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
		receiver.strength_value -= self._p1
		receiver.intellect_value -= self._p1
		receiver.dexterity_value -= self._p1
		receiver.corporeity_value -= self._p1
		receiver.armor_percent -= self._p2
		receiver.magic_armor_percent -= self._p3
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
		receiver.strength_value -= self._p1
		receiver.intellect_value -= self._p1
		receiver.dexterity_value -= self._p1
		receiver.corporeity_value -= self._p1
		receiver.armor_percent -= self._p2
		receiver.magic_armor_percent -= self._p3


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
		receiver.strength_value += self._p1
		receiver.intellect_value += self._p1
		receiver.dexterity_value += self._p1
		receiver.corporeity_value += self._p1
		receiver.armor_percent += self._p2
		receiver.magic_armor_percent += self._p3
		receiver.calcDynamicProperties()

#$Log: not supported by cvs2svn $
#Revision 1.1  2008/08/30 10:01:12  wangshufeng
#npc��ؼ��ܡ�buff
#
#
#
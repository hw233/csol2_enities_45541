# -*- coding: gb18030 -*-
#
# $Id: Buff_103002.py,v 1.2 2008-09-04 07:46:27 kebiao Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_103002( Buff_Normal ):
	"""
	���磺������������������������%i
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0		# �ӳɲ���
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		
		
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
		receiver.magic_damage_percent -= self._p1
		receiver.calcMagicDamage()
		
		
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
		receiver.magic_damage_percent -= self._p1
		
		
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.magic_damage_percent += self._p1
		receiver.calcMagicDamage()
		
		
#$Log: not supported by cvs2svn $
#Revision 1.1  2008/08/30 10:01:12  wangshufeng
#npc��ؼ��ܡ�buff
#
#
#
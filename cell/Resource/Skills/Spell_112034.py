# -*- coding: gb18030 -*-
#
# $Id: Spell_HP.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $

from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus
import random
from SpellBase import *
from Spell_Magic import Spell_Magic


class Spell_112034( Spell_Magic ):
	"""
	��ս ���ڼ��ܣ�ֻ�ܹ�����¥,��ɹ̶��˺�,������޹�.
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._p1 = 0
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		self._p2 = int( dict[ "param2" ] if len( dict[ "param2" ] ) > 0 else 0 ) 	
		
	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		���㱻�����������˺�����
		�˺�=�����˺�x (1 �C �������������˺�������) 
		�C �������������˺�����ֵ
		�˺�����Ϊ0��
		ע���˺�ΪDOT�ͳ����˺�������˺���ֵ�������ٷִ����á�
		���У������˺������ʼ������˺�����ֵ�ο���ʽ�ĵ�����ʽ���£�
		��ɫ���������˺�����������ܹ�ʽ�еĻ���ֵ��=0
		��ɫ���������˺�����ֵ���ܹ�ʽ�еĻ���ֵ��=0
		@param target: ��������
		@type  target: entity
		@param  damage: �����м��жϺ���˺�
		@type   damage: INT
		@return: INT32
		"""
		return damage
		
#$Log: not supported by cvs2svn $
#
#
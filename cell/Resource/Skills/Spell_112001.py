# -*- coding: gb18030 -*-
#
# $Id: Spell_112001.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Spell_Magic import Spell_Magic


class Spell_112001( Spell_Magic ):
	"""
	����
	
	ʧȥ��ǰ����ֵ��50%��ֱ������Ч��Ŀ��ʧȥ����ֵ���������κη����ͻ��⣬��Ϊֱ�ӵı仯ϵ�����˺�
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ֱ���˺�
		��ͨ�����˺����ܹ�ʽ�еĻ���ֵ��=��������*��1-������������������ˣ�
		���������˺����ܹ�ʽ�еĻ���ֵ��=���ܹ�����*��1-������������������ˣ�
		
		@param source: ������
		@type  source: entity
		@param target: ��������
		@type  target: entity
		@param skillDamage: ���ܹ�����
		@return: INT32
		"""
		receiver.HP = int( receiver.HP * 0.5 )	# HP��ǰ����Ϊint
		
#$Log: not supported by cvs2svn $
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_MultAttack.py,v 1.5 2007-12-26 08:19:50 kebiao Exp $

"""
��ι����˺��ͼ��ܻ���
"""

from SpellBase import *
import random
import csdefine
from Spell_PhysSkill import *
from Spell_Magic import *
		
class Spell_MultAttackPhy( Spell_PhysSkill ):
	"""
	��ι����˺��ͼ��� ����1 ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		for count in xrange( self._attackCount ): #�߻�Ҫ���ÿ��ENTITY��һ���˺����� ��ɶ�ε�Ѫ ����ι��������ɿͻ������
			Spell_PhysSkill.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackVolleyPhy( Spell_PhyVolley ):
	"""
	��ι����˺��ͼ��� ����1 Ⱥ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhyVolley.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhyVolley.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		for count in xrange( self._attackCount ): #�߻�Ҫ���ÿ��ENTITY��һ���˺����� ��ɶ�ε�Ѫ ����ι��������ɿͻ������
			Spell_PhyVolley.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackMagic( Spell_Magic ):
	"""
	��ι����˺��ͼ��� ���� ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		for count in xrange( self._attackCount ): #�߻�Ҫ���ÿ��ENTITY��һ���˺����� ��ɶ�ε�Ѫ ����ι��������ɿͻ������
			Spell_Magic.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackVolleyMagic( Spell_MagicVolley ):
	"""
	��ι����˺��ͼ��� ���� Ⱥ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_MagicVolley.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		for count in xrange( self._attackCount ): #�߻�Ҫ���ÿ��ENTITY��һ���˺����� ��ɶ�ε�Ѫ ����ι��������ɿͻ������
			Spell_MagicVolley.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )

# $Log: not supported by cvs2svn $
# Revision 1.4  2007/12/17 01:36:36  kebiao
# ����PARAM0Ϊparam1
#
# Revision 1.3  2007/12/03 08:26:22  kebiao
# ȥ���˻�����
#
# Revision 1.2  2007/11/26 08:44:18  kebiao
# �޸�BUG
#
# Revision 1.1  2007/11/26 08:25:31  kebiao
# һ�ι������̲�������˺�
#
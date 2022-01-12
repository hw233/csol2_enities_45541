# -*- coding: gb18030 -*-
#
# $Id: ChildSpell.py,v 1.1 2007-12-11 08:04:36 kebiao Exp $

"""
"""

import Language
from bwdebug import *
from CombatSpell import CombatSpell
import csstatus

class ChildSpell( CombatSpell ):
	"""
	һ���������Ӽ��ܡ� ͨ��ʹ����(ɢ����)Ⱥ�巨����.
	���Ӽ���ӵ�и����ܵĹ������ԺͲ�����  ������������ȴ���ж�, 
	��������Ⱥ�����ҵ�Ҫ�˺�������ENTITY����ÿһ��entity���ͷ�һ�����Ӽ���
	"""
	def __init__( self, parent ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self.parent = parent
		
	def init( self, dictDat ):
		"""
		��ȡ��������
		"""
		self.__dict__.update( self.parent.__dict__ )

	def doRequire_( self, caster ):
		"""
		virtual method.
		��������

		@param caster	:	�ͷ���ʵ��
		@type caster	:	Entity
		"""
		pass

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		��ʩ�������÷��������cooldownʱ��

		@return: None
		"""
		pass
		

	def getReceivers( self, caster, target ):
		"""
		virtual method
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��
		@return: array of Entity

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]

	def receive( self, caster, receiver ):
		"""
		virtual method = 0.
		���ÿһ�������߽�����������������˺����ı����Եȵȡ�ͨ������´˽ӿ�����onArrive()���ã�
		�������п�����SpellUnit::receiveOnreal()�������ã����ڴ���һЩ��Ҫ�������ߵ�real entity�����������顣
		�������Ƿ���Ҫ��real entity���Ͻ��գ��ɼ����������receive()�������жϣ������ṩ��ػ��ơ�
		ע���˽ӿ�Ϊ�ɰ��е�onReceive()
		
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		#�Ӽ����޷����������ܵļ��㷽ʽ(���������������),���ת��������ȥ��������
		self.parent.receive( caster, receiver )
		
#
# $Log: not supported by cvs2svn $
#
#
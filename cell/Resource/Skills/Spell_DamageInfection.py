# -*- coding: gb18030 -*-
#
# $Id: Spell_DamageInfection.py,v 1.3 2007-12-20 01:18:32 kebiao Exp $

"""
�˺���Ⱦ�ͼ��ܻ���
"""

from SpellBase import *
import random
import csdefine
from Spell_PhysSkill import *
from Spell_Magic import *
import SkillTargetObjImpl

def getNearEntity( caster, receivers ):
	"""
	��ȡ��caster�����һ��������
	"""
	x = 0.0
	e = 0
	for i, receiver in enumerate( receivers ):
		xx = caster.position.flatDistTo( receiver.position )
		if xx < x:
			x = xx
			e = i
	return e
	
class Spell_DamageInfectionPhy( Spell_PhysSkill ):
	"""
	�˺���Ⱦ�ͼ��ܻ��� ���� ����
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
		self._rmax = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  	#��Ⱦ����
		
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
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		rmax = self._rmax
		rlist = [ receiver ] #���������(ͨ��һ���ǵ�һ��ʩչĿ��)���Ѿ�ȷ���Ľ��ܵ��˺�������
		# ����receiver �������Χ�ķ�Χ������ENTITY Ȼ���ҳ������
		receivers = self._receiverObject.getReceivers( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		
		while( 1 ):
			if len( receivers ) <= 0 or rmax <= 0: break
			entity = receivers.pop( getNearEntity( caster, receivers ) )
			if entity.id != receiver.id:
				rlist.append( entity )
				rmax -= 1

		for receiver in rlist:
			if not receiver.isDestroyed and not receiver.state == csdefine.ENTITY_STATE_DEAD:
				Spell_PhysSkill.persentDamage( self, caster, receiver, damageType, damage )

class Spell_DamageInfectionMagic( Spell_Magic ):
	"""
	�˺���Ⱦ�ͼ��ܻ��� ���� ����
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
		self._rmax = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  	#��Ⱦ����
		
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
		return [target.getObject()]
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		rmax = self._rmax
		rlist = [ receiver ] #���������(ͨ��һ���ǵ�һ��ʩչĿ��)���Ѿ�ȷ���Ľ��ܵ��˺�������
		# ����receiver �������Χ�ķ�Χ������ENTITY Ȼ���ҳ������
		receivers = self._receiverObject.getReceivers( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		
		while( 1 ):
			if len( receivers ) <= 0 or rmax <= 0: break
			entity = receivers.pop( getNearEntity( caster, receivers ) )
			if entity.id != receiver.id:
				rlist.append( entity )
				rmax -= 1

		for receiver in rlist:
			if not receiver.isDestroyed and not receiver.state == csdefine.ENTITY_STATE_DEAD:			
				Spell_Magic.persentDamage( self, caster, receiver, damageType, damage )
			
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/17 01:36:36  kebiao
# ����PARAM0Ϊparam1
#
# Revision 1.1  2007/11/26 08:22:42  kebiao
# no message
#
# -*- coding: gb18030 -*-
#


from SpellBase import *
from Skill_Normal import Skill_Normal
import csdefine
import random

class Skill_400027( Skill_Normal ):
	"""
	������������������ֵ�൱�ڣ�����+���ݣ�*1%��

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Skill_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Normal.init( self, dict )

	def springOnHit( self, caster, receiver, damageType ):
		"""
		��������ʱ����Ϣ�ص�
		@param   caster: ʩ����
		@type    caster: Entity
		@param   receiver: ������
		@type    receiver: Entity
		"""
		for buff in self._buffLink:
			# �в����������жϻ���
			if random.randint( 1, 100 ) > buff.getLinkRate():
				continue
			buff.getBuff().receive( caster, receiver )				# ����buff��receive()���Զ��ж�receiver�Ƿ�ΪrealEntity
			
	def attach( self, ownerEntity ):
		"""
		virtual method = 0;
		ΪĿ�긽��һ��Ч����ͨ�������ϵ�Ч����ʵ������������ͨ��detach()ȥ�����Ч��������Ч���ɸ����������о�����
		
		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.appendAttackerHit( self.getNewObj() )
		
	def detach( self, ownerEntity ):
		"""
		virtual method
		ִ����attach()�ķ������

		@param ownerEntity:	ӵ����ʵ��
		@type ownerEntity:	BigWorld.Entity
		"""
		ownerEntity.removeAttackerHit( self.getUID() )
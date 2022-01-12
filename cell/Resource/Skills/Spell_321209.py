# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_PhysSkill import Spell_PhysSkill
import csstatus
import csconst
import csdefine
import BigWorld
import random

class Spell_321209( Spell_PhysSkill ):
	"""
	�����������﹥������������Լ��Ͷ��ѵı������ʣ�����10��
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhysSkill.__init__( self )
		self._range = 0.0
		self._rate = 0.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._range = float( dict[ "param1" ] )
		self._rate = int( dict[ "param2" ] )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		if random.randint( 0, 100 ) <= self._rate:
			elist = caster.getAllMemberInRange( self._range )
			if len( elist ) <= 0:
				elist = [ caster ]
				
			for e in elist:
				self._buffLink[0].getBuff().receive( caster, e )	

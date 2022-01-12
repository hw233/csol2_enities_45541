# -*- coding: gb18030 -*-

from bwdebug import *
from Spell_Magic import Spell_Magic
import csstatus
import csconst
import csdefine
import BigWorld
import random

class Spell_322471( Spell_Magic ):
	"""
	�����
	
	30%������������Ŀ�����һ���ķ����˺���ͬʱ�����Χ10����������ҵ�����������
	����10�롣10����ȴ���ȼ�Խ�ߣ��˺�Խ��ͬʱ�����������Խ�ࡣ
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		self._range = 0.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._range = float( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 )
		
	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		elist = caster.getAllMemberInRange( self._range )
		if len( elist ) <= 0:
			elist = [ caster ]
			
		for e in elist:
			self._buffLink[0].getBuff().receive( caster, e )
			
# -*- coding: gb18030 -*-

# ϵͳ���ܣ�����һ��AreaRestrictTransducer��entity(���幦��entity)���ڽ�����λ��

import BigWorld
import csdefine
import csstatus
from SpellBase import *
from ObjectScripts.GameObjectFactory import g_objFactory

class Spell_trapReceive( Spell ):
	"""
	ϵͳ����
	����һ��AreaRestrictTransducer��entity(���幦��entity)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self.trapEntityClass = ""				# ����className


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self.trapEntityClass = dict[ "param1" ]

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		receiver.createObjectNearPlanes( self.trapEntityClass, caster.position, caster.direction, {} )

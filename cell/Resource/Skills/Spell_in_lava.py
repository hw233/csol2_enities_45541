# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase import *
import Love3

class Spell_in_lava( SystemSpell ):
	"""
	�����������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )
		self.param1 = 0			#skill ID

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		SystemSpell.init( self, dict )
		self.param1 = int( dict[ "param1" ] )				#����ID
		self.param2 = int( str( self.param1 ) + "01" )		#���ܶ�Ӧ�ĵ�һ��BUFF ID

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) ):		# ֻ�����ʩ�ţ����������
			return

		if receiver.isReal():
			if receiver.findBuffByID( self.param2 ) is None:
				receiver.removeTemp( "In_lava_List" )
			ids = receiver.queryTemp( "In_lava_List", [] )
			if caster.id in ids:
				return
			ids.append( caster.id )
			receiver.setTemp( "In_lava_List", ids )
			if len( ids ) == 1:
				Love3.g_skills[self.param1].receiveLinkBuff( None, receiver )

		else:
			receiver.receiveOnReal( -1, self )								# ʩ����ID����-1����ʾûʩ����
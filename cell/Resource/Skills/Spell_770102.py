# -*- coding: gb18030 -*-

#�µĽ��밲ȫ���ݽ���������
#���Ӱ�ȫ������ĸ߶��ж�
# wuxo  2012-6-5

import csdefine
from SpellBase import *

class Spell_770102( SystemSpell ):
	"""
	ϵͳ����
	����PK������ʱʩ�Ŵ˼���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		SystemSpell.__init__( self )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����ʵ�ֵ�Ŀ��
		"""
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ֻ�����ʩ�ţ����������
			return
		if not receiver.isReal():
			receiver.receiveOnReal( -1, self )						# ʩ����ID����-1����ʾûʩ����
			return
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )
		self.receiveLinkBuff( caster, receiver )# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)
# -*- coding: gb18030 -*-

# 2009-1-6 gjx

import csdefine
import csstatus
from SpellBase import *

class Spell_770100( SystemSpell ):
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

		receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# ������ϼ�һ����ȫ����ı�־������һЩ�������ж�
		receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ��ֹPK
		receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
		# ����������������Ϊ���뿪ʱ�ܸ��ݱ��״̬�����Ƿ����뿪��ȫ������Ϣ
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )

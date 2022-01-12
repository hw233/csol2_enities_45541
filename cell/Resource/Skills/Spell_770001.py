# -*- coding: gb18030 -*-

# 2008-11-26 gjx&lq

import csdefine
import csstatus
from SpellBase import *

class Spell_770001( SystemSpell ):
	"""
	ϵͳ����
	�����̯��������ʱʩ�Ŵ˼���
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
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):		# ֻ�����ʩ�ţ����������
			return

		if receiver.isReal():
			receiver.actCounterInc( csdefine.ACTION_ALLOW_VEND )			# �����̯
			receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )		# ��ֹPK
			#receiver.statusMessage( csstatus.VEND_ENTER_VEND_ALLOWED_AREA )
			# ����������������Ϊ���뿪ʱ�ܸ��ݱ��״̬�����Ƿ����뿪��ȫ������Ϣ
			receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) + 1 )
		else:	# �����ghost��֧�֡�17:31 2009-1-16��wsf
			receiver.receiveOnReal( -1, self )								# ʩ����ID����-1����ʾûʩ����
# -*- coding: gb18030 -*-

# 2009-1-6 gjx

import csdefine
import csstatus
from SpellBase import *

class Spell_770101( SystemSpell ):
	"""
	ϵͳ����
	�뿪PK������ʱʩ�Ŵ˼���
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
		if not receiver.isReal() :
			receiver.receiveOnReal( -1, self )							# ʩ����ID����-1����ʾûʩ����
			return

		receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# �Ƴ�������ϵİ�ȫ����ı�־
		receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )		# ����PK
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) - 1 )
		tempFlag = receiver.queryTemp( "RestrictAreaFlag" )
		if tempFlag < 1 :
			receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )
			receiver.removeTemp( "RestrictAreaFlag" )

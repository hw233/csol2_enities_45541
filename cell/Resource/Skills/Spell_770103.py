# -*- coding: gb18030 -*-

#�µ��뿪��ȫ���ݽ���������
#���Ӱ�ȫ������ĸ߶��ж�
# wuxo  2012-6-5

import csdefine
import csstatus
from SpellBase import *
SAFE_AREA_BUFF_ID = 22020 #��ȫ���ݽ�Buff

class Spell_770103( SystemSpell ):
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
			receiver.receiveOnReal( -1, self )	# ʩ����ID����-1����ʾûʩ����
			return
		receiver.setTemp( "RestrictAreaFlag", receiver.queryTempInt( "RestrictAreaFlag" ) - 1 )
		tempFlag = receiver.queryTemp( "RestrictAreaFlag" )
		if tempFlag < 1 :
			#�жϰ�ȫ������buff
			if receiver.findBuffByBuffID( SAFE_AREA_BUFF_ID ) :
				receiver.removeBuffByBuffID( SAFE_AREA_BUFF_ID, ( csdefine.BUFF_INTERRUPT_NONE, ) )
				receiver.removeTemp( "RestrictAreaFlag" )
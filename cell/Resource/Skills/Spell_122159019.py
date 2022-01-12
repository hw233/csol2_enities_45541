# -*- coding: gb18030 -*-
#

import csdefine
from SpellBase import *
import csstatus
import csconst
from Spell_BuffNormal import Spell_BuffNormal

class Spell_122159019( Spell_BuffNormal ):
	"""
	����������ʩ�ż���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_BuffNormal.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		return csstatus.SKILL_GO_ON

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		# ������������ͻ��߳������ͻ����ڳ������ڣ����͵�ʵ����д���
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) ):
			return

		receiver.actCounterInc( csdefine.ACTION_FORBID_PK )						# ������������ֹ���PK�ı��
		actPet = receiver.pcg_getActPet()
		if actPet :																# ������Я���г�������
			actPet.entity.withdraw( csdefine.PET_WITHDRAW_COMMON )				# ���ջ�֮
		receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )			# �ջ�����

		self.receiveLinkBuff( receiver, receiver )

		receiver.statusMessage( csstatus.JING_WU_SHI_KE_ENTER )

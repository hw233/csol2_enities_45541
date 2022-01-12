# -*- coding: gb18030 -*-
#
#

import csdefine
import csstatus
from SpellBase import Spell
import Const

class Spell_122159020( Spell ):
	"""
	�뿪����ʩ�ż���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
	
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
		����ʵ�ֵ�Ŀ��
		"""
		# ������������ͻ��߳������ͻ����ڳ������ڣ����͵�ʵ����д���
		if not ( receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_PET ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_SLAVE_MONSTER ) or \
		receiver.isEntityType( csdefine.ENTITY_TYPE_VEHICLE_DART ) ):
			return
		
		receiver.actCounterDec( csdefine.ACTION_FORBID_PK )		# �������PK�ı��
		#receiver.removeAllBuffByBuffID( Const.JING_WU_SHI_KE_BUFF, [csdefine.BUFF_INTERRUPT_NONE] )
		
		receiver.statusMessage( csstatus.JING_WU_SHI_KE_LEAVE )

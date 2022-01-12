# -*- coding:gb18030 -*-

from Spell_BuffNormal import Spell_BuffNormal
import csstatus
import csdefine
from bwdebug import *

class Spell_PushDrag( Spell_BuffNormal ):
	"""
	������Ҽ以�������ֵ���
	"""
	def __init__( self ):
		"""
		"""
		Spell_BuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ����
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
		targetObject = target.getObject()
		if caster == targetObject:								# �����߲������Լ�
			return csstatus.SKILL_NOT_ROLE_ENTITY
		if targetObject.hasFlag( csdefine.ROLE_FLAG_FLY ):  	# �����߷���״̬���
			return csstatus.SKILL_TARGET_FLYING
		if targetObject.state == csdefine.ENTITY_STATE_DEAD:    # ����������״̬���
			return csstatus.SKILL_TARGET_DEAD
		return Spell_BuffNormal.useableCheck( self, caster, target )

	def cast( self, caster, target ):
		"""
		virtual method.
		��ʽ��һ��Ŀ���λ��ʩ�ţ���з��䣩�������˽ӿ�ͨ��ֱ�ӣ����ӣ���intonate()�������á�

		ע���˽ӿڼ�ԭ���ɰ��е�castSpell()�ӿ�

		@param     caster: ʹ�ü��ܵ�ʵ��
		@type      caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_BuffNormal.cast( self, caster, target )
		self.updateItem( caster )

	def updateItem( self, caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			printStackTrace()
			ERROR_MSG( "cannot find the item form uid[%s]." % uid )
			return
		item.onSpellOver( caster )
		caster.removeTemp( "item_using" )
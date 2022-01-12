# -*- coding: gb18030 -*-
#
# $Id: Spell_Item.py,v 1.22 2008-08-13 07:55:41 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
import random
import csdefine
import csstatus
from bwdebug import *

class Spell_Item( Spell ):
	"""
	ʹ����Ʒ���ܻ���
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

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_ITEM

	def onSpellInterrupted( self, caster ):
		"""
		��ʩ�������ʱ��֪ͨ��
		��Ϻ���Ҫ��һЩ����
		"""
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.unfreeze()
		caster.removeTemp( "item_using" )
		Spell.onSpellInterrupted( self, caster )

	def setCooldownInUsed( self, caster ):
		"""
		virtual method.
		��ʩ�������÷��������cooldownʱ�� (����ʹ�ú� ������ʼʱ)

		@return: None
		"""
		Spell.setCooldownInUsed( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSetCooldownInUsed( caster )

	def setCooldownInIntonateOver( self, caster ):
		"""
		virtual method.
		��ʩ�������÷��������cooldownʱ��(������������ʱ)

		@return: None
		"""
		Spell.setCooldownInIntonateOver( self, caster )
		uid = caster.queryTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSetCooldownInIntonateOver( caster )

	def use( self, caster, target ):
		"""
		virtual method.
		����� target/position ʩչһ���������κη�����ʩ������ɴ˽���
		dstEntity��position�ǿ�ѡ�ģ����õĲ�����None���棬���忴���������Ƕ�Ŀ�껹��λ�ã�һ��˷���������client����ͳһ�ӿں���ת������
		Ĭ��ɶ��������ֱ�ӷ��ء�
		ע���˽ӿڼ�ԭ���ɰ��е�cast()�ӿ�
		@param   caster: ʩ����
		@type    caster: Entity

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		caster.doOnUseSkill( self )	# ��������ʹ��ʱ���б� ������������ ����ʱ�� �� XX ���ĵĸı�
		Spell.use( self, caster, target )

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
		# �������ܼ��
		#���ݲ߻����� ��ҩ���������modify by wuxo2012-5-7
		#caster.delHomingOnCast( self )
		self.setCooldownInIntonateOver( caster )
		# ��������
		self.doRequire_( caster )
		#֪ͨ���пͻ��˲��Ŷ���/����������
		caster.planesAllClients( "castSpell", ( self.getID(), target ) )
		
		# ����ʩ�����֪ͨ����һ���ܴ�����Ŷ(�Ƿ��ܴ����Ѿ���ʩ��û�κι�ϵ��)��
		# �����channel����(δʵ��)��ֻ�еȷ�����������ܵ���
		self.onSkillCastOver_( caster, target )
		
		self.onArrive( caster, target )
		#������Ʒ ֻ����Ʒ�ɹ�ʹ��֮��ſ��Զ���Ʒ���������в���
		self.updateItem( caster ) #������д�����������Ϊ��ʱ���Ա�֤casterΪreal,��Ϊʹ����Ʒ���ܻ�Գ����ʹ�ã���˲���ʹ��receiver

	def updateItem( self , caster ):
		"""
		������Ʒʹ��
		"""
		uid = caster.popTemp( "item_using" )
		item = caster.getByUid( uid )
		if item is None:
			ERROR_MSG( "Player(%s) cannot find the item form uid[%s]." %(caster.playerName, uid ) )
			return
		item.onSpellOver( caster )
		caster.removeTemp( "item_using" )

	def useableCheck( self, caster, target ):
		"""
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		��Ҫ��������Ϣ�����ⲻ��ʹ����Ʒʱ��ʾʹ�ü���
		"""
		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_USE_ITEM ):
			if caster.getState() == csdefine.ENTITY_STATE_PENDING:
				return csstatus.CIB_MSG_PENDING_CANT_USE_ITEM
			return csstatus.CIB_MSG_TEMP_CANT_USE_ITEM
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		# ��鼼��cooldown
		if not self.isCooldown( caster ):
			return csstatus.SKILL_ITEM_NOT_READY

		# ʩ��������
		state = self.checkRequire_( caster )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ʩ���߼��
		state = self.castValidityCheck( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ���Ŀ���Ƿ���Ϸ���ʩչ
		state = self.getCastObject().valid( caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		return csstatus.SKILL_GO_ON

# $Log: not supported by cvs2svn $
# Revision 1.21  2008/05/31 03:01:19  yangkai
# ��Ʒ��ȡ�ӿڸı�
#
# Revision 1.20  2008/03/26 08:28:45  kebiao
# �޸Ĵ�����ʾ��Ϣ
#
# Revision 1.19  2008/03/01 06:24:00  yangkai
# ��Ʒϵͳ��ʹ�ô������˴������ýӿ�onSpellOver
#
# Revision 1.18  2008/01/18 06:35:05  zhangyuxing
# �޸ģ��Ƴ���Ʒ��ʽ�ı�
#
# Revision 1.17  2008/01/03 03:34:11  kebiao
# add:from bwdebug import *
#
# Revision 1.16  2007/12/18 09:32:43  kebiao
# ����ж�֪ͨ�ӿ�
#
# Revision 1.15  2007/12/18 09:23:33  kebiao
# �޸���Ʒ�������жϷ�ʽ
#
# Revision 1.14  2007/12/18 09:05:23  kebiao
# �����жϽӿ�
#
# Revision 1.13  2007/12/18 08:33:16  kebiao
# ��������ж� ��Ʒʹ��ʧ�ܺ����
#
# Revision 1.12  2007/12/18 07:49:45  kebiao
# �޸�ʹ����ƷBUG ����ע��
#
# Revision 1.11  2007/12/11 08:36:48  kebiao
# ������Ʒ�����ж�
#
# Revision 1.10  2007/12/11 08:22:36  kebiao
# ����һ��BUG
#
# Revision 1.9  2007/12/11 06:35:13  kebiao
# ��Ӽ���֪ͨ��Ʒȥ��ȴ����
#
# Revision 1.8  2007/12/04 08:31:07  kebiao
# �޸����ķ�ʽ
#
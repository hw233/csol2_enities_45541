# -*- coding: gb18030 -*-
#
# $Id: Spell_121014.py,v 1.5 2008-07-15 04:06:26 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from bwdebug import *
from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill2
import utils
import csstatus
import csdefine

class Spell_121014( Spell_PhysSkill2 ):
	"""
	������	���	����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill2.__init__( self )
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF

	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )

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
		d  = caster.distanceBB( target.getObject() )
		if d < 8.0:
			return csstatus.SKILL_INVALID_DISTANCE_CHONGFENG1
		if d > 20.0:
			return csstatus.SKILL_INVALID_DISTANCE_CHONGFENG2
		return Spell_PhysSkill2.useableCheck( self, caster, target )

	def receiveLinkBuff( self, caster, receiver ):
		"""
		��entity����buff��Ч��
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: ʩչ����
		@type  receiver: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.receiveLinkBuff( self, caster, caster ) #ʩ���߻�ø�buff��

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
		caster.clearBuff( self._triggerBuffInterruptCode ) #ɾ�������������п���ɾ����BUFF
		caster.changeAttackTarget( target.getObject().id )
		Spell_PhysSkill2.cast( self, caster, target )
		caster.move_speed = 50.0
		if caster.actionSign( csdefine.ACTION_FORBID_MOVE ):
			DEBUG_MSG( "im cannot the move!" )
			caster.stopMoving()
			return
		caster.gotoPosition( target.getObject().position )

	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		����ʩ�����֪ͨ
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		Spell_PhysSkill2.onSkillCastOver_( self, caster, target )
		caster.calcMoveSpeed()

# $Log: not supported by cvs2svn $
# Revision 1.4  2008/05/28 05:59:47  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.3  2008/03/29 08:58:43  phw
# ����distanceBB()�ĵ��÷�ʽ��ԭ����utilsģ���е��ã���Ϊֱ���� entity ���ϵ���
#
# Revision 1.2  2007/12/29 09:13:42  kebiao
# no message
#
# Revision 1.1  2007/12/20 05:43:42  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_CatchPet.py,v 1.20 2008-07-04 03:50:57 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
import csdefine
import csconst
from Spell_Item import Spell_Item

class Spell_CatchPet( Spell_Item ):
	"""
	ʹ�ã�ץ�����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.isResetLevel = dict.get( "param2", 1 )	# Ĭ�ϻ����ó���ȼ�

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_MAGIC

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
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0 or caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
			
		if caster.pcg_isFull():
			return csstatus.SKILL_MISSING_FULL_PET

		monsterScript = target.getObject().getScript()			# ������ͳ����ӳ����Ϊ�ù���������������ӳ��ĳ���( hyw -- 2008.10.28 )
		if monsterScript.mapPetID == "" :								# �������û��ӳ��ĳ���򷵻ز��ܲ�׽( hyw -- 2008.10.28 )
			return csstatus.SKILL_MISSING_NOT_CATCH_PET

		if caster.level < monsterScript.takeLevel:
			return csstatus.PET_CATCH_FAIL_LESS_TAKE_LEVEL

		if t.level - csconst.PET_CATCH_OVER_LEVEL > caster.level:
			return csstatus.SKILL_MISSING_NOT_CATCH_PET_LEVEL

		return Spell_Item.useableCheck( self, caster, target )

	def getCatchType( self ):
		"""
		��ò������͡�19:22 2009-2-27��wsf
		"""
		return csdefine.PET_GET_CATCH

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		level = receiver.level
		if self.isResetLevel:
			needResetLevel = True
		else:
			needResetLevel = False
		caster.pcg_catchPet( receiver.className, level, receiver.modelNumber, self.getCatchType(), True, needResetLevel )
		receiver.destroy()

# $Log: not supported by cvs2svn $
# Revision 1.19  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.18  2008/05/26 08:02:39  huangyongwei
# �޸��˵ȼ��ж�
#
# Revision 1.17  2008/05/26 05:54:21  huangyongwei
# ����˲�׽�ȼ��ж�
#
# Revision 1.16  2008/04/01 05:22:59  zhangyuxing
# �г���ȼ�����Ϊ�����к��Լ��ȼ�һ���ĳ���
#
# Revision 1.15  2008/02/29 04:03:56  kebiao
# ���޸�Ϊ��Ʒ����
#
# Revision 1.14  2008/02/01 02:46:11  kebiao
# �������﹥���Ĺ��ﲻ�ܲ�׽����
#
# Revision 1.13  2008/01/09 06:40:49  kebiao
# ��ӹ�������Ȩ�ж�
#
# Revision 1.12  2008/01/09 04:11:50  kebiao
# ��Ӷ����ж�
#
# Revision 1.11  2007/12/25 03:09:16  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.10  2007/12/25 01:45:50  kebiao
# �޸ĳ�û����
#
# Revision 1.9  2007/12/18 10:42:06  huangyongwei
# no message
#
# Revision 1.8  2007/12/12 07:32:43  kebiao
# �����ж���Ϣ
#
# Revision 1.7  2007/12/12 04:20:30  kebiao
# �޸�ѣ�ε�״̬�ж�
#
# Revision 1.6  2007/12/06 02:51:48  kebiao
# ����жϵ�ǰ�Ƿ�����ʩ�����ж�
#
# Revision 1.5  2007/12/05 02:11:41  kebiao
# �޸�BUG
#
# Revision 1.4  2007/12/04 10:17:52  kebiao
# no message
#
# Revision 1.3  2007/12/04 09:24:33  kebiao
# no message
#
# Revision 1.2  2007/12/04 08:31:46  kebiao
# �޸Ĵ���
#
# Revision 1.1  2007/12/03 07:45:38  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHPMP.py,v 1.8 2008-08-14 06:11:18 songpeifang Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus

class Spell_ItemHPMP( Spell_ItemCure ):
	"""
	ʹ�ã����ָ̻�����HP,MP1960�㡣
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemCure.__init__( self )
		#self._p1 = 0 #HP
		#self._p2 = 0 #MP

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemCure.init( self, dict )
		#self._p1 = dict.readInt( "param0" )
		#self._p2 = dict.readInt( "param1" )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		#�����������ǰ�� ��ο��ײ�
		if caster.isReal():
			Spell_ItemCure.receive( self, caster, receiver )

		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		self.receiveLinkBuff( caster, receiver )		# ���ն����CombatSpellЧ����ͨ����buff(������ڵĻ�)

		self.cureHP( caster, receiver, self._effect_max )
		self.cureMP( caster, receiver, self._effect_max )

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
		if target.getObject().HP == target.getObject().HP_Max and target.getObject().MP == target.getObject().MP_Max:
			return csstatus.SKILL_CURE_NONEED
		return Spell_ItemCure.useableCheck( self, caster, target)

# $Log: not supported by cvs2svn $
# Revision 1.7  2008/08/13 09:18:46  songpeifang
# ������ҩƷ����Ϊ�˼��ܣ�����buff��ʹ֮������ʱҲ��ʾ����ʹ��
#
# Revision 1.6  2008/07/29 06:36:20  songpeifang
# �޸������Ѫ/����ʱ����Ҳ���ܳԺ�/����bug
#
# Revision 1.5  2008/07/16 06:25:34  huangdong
# ��������Ѫ�������ܺȼ�ҩ������
#
# Revision 1.4  2008/01/31 08:13:48  kebiao
# �޸��˿��ܳ��ֵ�BUG
#
# Revision 1.3  2008/01/31 07:06:45  kebiao
# ����������Ϣ
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# ʹ�ü���Ч��ֵ
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
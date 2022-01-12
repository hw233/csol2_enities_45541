# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemMP.py,v 1.7 2008-08-14 06:11:27 songpeifang Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
#from Spell_Item import Spell_Item
from Spell_ItemCure import Spell_ItemCure
import csstatus

class Spell_ItemMP( Spell_ItemCure ):
	"""
	ʹ�ã����ָ̻�����MP1960�㡣
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemCure.__init__( self )
		#self._p1 = 0 #���ָ̻�����MP1960�㡣
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemCure.init( self, dict )
		#self._p1 = dict.readInt( "param0" )
		
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
		if target.getObject().MP == target.getObject().MP_Max:
			return csstatus.SKILL_CURE_NONEED
		return Spell_ItemCure.useableCheck( self, caster, target)


# $Log: not supported by cvs2svn $
# Revision 1.6  2008/08/13 09:18:50  songpeifang
# ������ҩƷ����Ϊ�˼��ܣ�����buff��ʹ֮������ʱҲ��ʾ����ʹ��
#
# Revision 1.5  2008/07/29 06:36:25  songpeifang
# �޸������Ѫ/����ʱ����Ҳ���ܳԺ�/����bug
#
# Revision 1.4  2008/07/16 04:08:38  huangdong
# �޸����������ܺ�ҩ����ʾ��Ϣ
#
# Revision 1.3  2008/07/16 03:33:30  huangdong
# �������������ܺ�ҩ������
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# ʹ�ü���Ч��ֵ
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
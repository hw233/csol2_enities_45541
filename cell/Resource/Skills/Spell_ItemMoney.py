# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_Item import Spell_Item
import csstatus
import random

class Spell_ItemMoney( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Item.__init__( self )
		self._p0 = 0 #���ӽ�Ǯ��Сֵ
		self._p1 = 0 #���ӽ�Ǯ���ֵ
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._p0 = int( dict[ "param0" ] if len( dict[ "param0" ] ) > 0 else 0 ) 	
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		#�����������ǰ�� ��ο��ײ�
		Spell_Item.receive( self, caster, receiver )
		money = random.randint( self._p0, self._p1 )
		caster.addMonery( money )
				

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
		return Spell_Item.useableCheck( self, caster, target)


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
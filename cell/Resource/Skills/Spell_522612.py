# -*- coding: gb18030 -*-
#
# $Id: Spell_522612.py,v 1.7 2008-06-26 00:54:56 zhangyuxing Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
from Spell_Magic import Spell_Magic
import random
import csdefine

class Spell_522612( Spell_Magic ):
	"""
	��������
	����Ŀ�꣬���Ŀ�귨��ֵ�ļ��٣����ٵ���ֵ��Ϊ����ķ���ֵ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		�������߳��������˺�
		ͨ��������Щ�����Ҫ���� ��Ҫ���ݶ�ĳentity���������˺� �������������Ӱ��
		"""
		SkillMessage.spell_ConsumeMP( self, caster, receiver, damage )
		#damage = caster.calcShieldSuck( receiver, damage, self._damageType )
		receiver.addMP( -damage )
		caster.addMP( damage )
			
			
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/02/25 09:29:18  kebiao
# �޸� ���ܼ������
#
# Revision 1.5  2008/02/13 08:46:53  kebiao
# �޸��˵ײ�ṹ
#
# Revision 1.4  2008/01/30 06:06:16  kebiao
# no message
#
# Revision 1.3  2007/12/26 09:03:57  kebiao
# no message
#
# Revision 1.2  2007/12/26 08:19:50  kebiao
# no message
#
# Revision 1.1  2007/12/26 03:54:24  kebiao
# no message
#
#
# -*- coding: gb18030 -*-
#
# $Id: Spell_312602.py,v 1.7 2008-08-13 02:24:55 kebiao Exp $

"""
���ܶ���Ʒʩչ����������
"""

from SpellBase import *
import random
import csdefine

class Spell_312602( Spell ):
	"""
	��ȥ���� ��������ѣ�κͶ���״̬����ѣ��״̬�¿���ʹ�á�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell.__init__( self )
		self._p1 = 150
		
	def init( self, dict ):
		"""
		��ȡ����
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		self._triggerBuffInterruptCode = []							# �ü��ܴ�����Щ��־���ж�ĳЩBUFF
		self._p1 = int( dict.get( "param1" , 0 ) )		# �ܹ����BUFF����ߵȼ�
		for val in dict[ "triggerBuffInterruptCode" ]:
			self._triggerBuffInterruptCode.append( val )
			
	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		for index, buff in enumerate( receiver.getBuffs() ):
			skill = buff["skill"]
			if skill.getLevel() <= self._p1:# ֻ����ɢ���Լ�����׵�BUFF
				receiver.removeBuff( index, self._triggerBuffInterruptCode )
				break
						

# $Log: not supported by cvs2svn $
# Revision 1.6  2008/05/28 05:59:47  kebiao
# �޸�BUFF�������ʽ
#
# Revision 1.5  2007/12/17 01:36:36  kebiao
# ����PARAM0Ϊparam1
#
# Revision 1.4  2007/12/06 01:24:22  kebiao
# �޸���һ�����ܵ��µ�BUG
#
# Revision 1.3  2007/11/30 08:45:13  kebiao
# csstatus.BUFF_INTERRUPT
# TO��
# csdefine.BUFF_INTERRUPT
#
# Revision 1.2  2007/11/29 09:04:14  kebiao
# �޸�BUG
#
# Revision 1.1  2007/11/24 08:35:30  kebiao
# no message
#
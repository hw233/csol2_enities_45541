# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffNormal.py,v 1.10 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
from Spell_BuffNormal import Spell_ItemBuffNormal

class Spell_BuffSunBlock( Spell_ItemBuffNormal ):
	"""
	��Ҫ������Ʒ������صļ���ֱ��ʩ��һ��BUFF��   ������Ҫ������Ʒ�������Ե�
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_ItemBuffNormal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		�����Ʒ�Ƿ����
		"""
		#�����ã��ǵ�ɾ��
		return csstatus.SKILL_GO_ON
		if not target.getObject().isSunBathing():
			return csstatus.SKILL_CAST_NOT_SUN_BATHING
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.8  2008/05/20 01:32:01  kebiao
# modify a bug.
#
# Revision 1.7  2008/05/19 08:52:53  kebiao
# �޸�spell_buffnormal �̳�
#
# Revision 1.6  2007/12/25 03:09:29  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.5  2007/12/13 00:48:08  kebiao
# ����������״̬�ı䲿�֣���Ϊ�ײ�����س�ͻ���� �������Ͳ��ٹ��ĳ�ͻ����
#
# Revision 1.4  2007/12/12 07:33:04  kebiao
# ��ӳ�ûһ���жϷ�ʽ
#
# Revision 1.3  2007/12/06 02:51:48  kebiao
# ����жϵ�ǰ�Ƿ�����ʩ�����ж�
#
# Revision 1.2  2007/12/03 03:59:46  kebiao
# ������Ʒ�ͷ�BUFF
#
# Revision 1.1  2007/10/26 07:07:52  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.8  2007/08/15 03:28:57  kebiao
# �¼���ϵͳ
#
#
#
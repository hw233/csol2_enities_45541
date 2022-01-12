# -*- coding: gb18030 -*-
#
# $Id: QuestMonster.py,v 1.4 2007-12-15 11:25:30 huangyongwei Exp $

import BigWorld
import Monster
from bwdebug import *
from ECBExtend import *
import time
import Role

class QuestMonster( Monster.Monster ):
	"""An QuestMonster class for cell.
	�������ĳ��������˺��Ĺ���
	"""

	def __init__( self ):
		"""
		"""
		Monster.Monster.__init__( self )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.

		�����˺���

		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		try:
			player = BigWorld.entities[ casterID ]
		except KeyError:
			ERROR_MSG("can not found(%i)" % casterID )
			return

		# ����ɽű������������Ϊ
		if not self.getScript().checkDamageValid( player ):
			return

		Monster.Monster.receiveDamage( self, casterID, skillID, damageType, damage )
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/28 02:14:10  yangkai
# �Ƴ������õ� from ItemTypeEnum import *
#
# Revision 1.2  2007/06/14 09:55:30  huangyongwei
# �ᶯ�˺궨��
#
# Revision 1.1  2007/03/23 05:45:02  kebiao
# �������
#
#
#
#
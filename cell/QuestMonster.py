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
	需求完成某任务才能伤害的怪物
	"""

	def __init__( self ):
		"""
		"""
		Monster.Monster.__init__( self )

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.

		接受伤害。

		@param   casterID: 施法者ID
		@type    casterID: OBJECT_ID
		@param    skillID: 技能ID
		@type     skillID: INT
		@param damageType: 伤害类型；see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: 伤害数值
		@type      damage: INT
		"""
		try:
			player = BigWorld.entities[ casterID ]
		except KeyError:
			ERROR_MSG("can not found(%i)" % casterID )
			return

		# 如果由脚本来定义相关行为
		if not self.getScript().checkDamageValid( player ):
			return

		Monster.Monster.receiveDamage( self, casterID, skillID, damageType, damage )
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/11/28 02:14:10  yangkai
# 移除了无用的 from ItemTypeEnum import *
#
# Revision 1.2  2007/06/14 09:55:30  huangyongwei
# 搬动了宏定义
#
# Revision 1.1  2007/03/23 05:45:02  kebiao
# 任务怪物
#
#
#
#
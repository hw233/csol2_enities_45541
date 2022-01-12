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
	主要用于物品道具相关的技能直接施放一个BUFF用   他是需要进行物品消损特性的
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		检查物品是否可用
		"""
		#测试用，记得删除
		return csstatus.SKILL_GO_ON
		if not target.getObject().isSunBathing():
			return csstatus.SKILL_CAST_NOT_SUN_BATHING
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.8  2008/05/20 01:32:01  kebiao
# modify a bug.
#
# Revision 1.7  2008/05/19 08:52:53  kebiao
# 修改spell_buffnormal 继承
#
# Revision 1.6  2007/12/25 03:09:29  kebiao
# 调整效果记录属性为effectLog
#
# Revision 1.5  2007/12/13 00:48:08  kebiao
# 重新修正了状态改变部分，因为底层有相关冲突机制 因此这里就不再关心冲突问题
#
# Revision 1.4  2007/12/12 07:33:04  kebiao
# 添加沉没一类判断方式
#
# Revision 1.3  2007/12/06 02:51:48  kebiao
# 填加判断当前是否允许施法的判定
#
# Revision 1.2  2007/12/03 03:59:46  kebiao
# 加入物品释放BUFF
#
# Revision 1.1  2007/10/26 07:07:52  kebiao
# 根据全新的策划战斗系统做调整
#
# Revision 1.8  2007/08/15 03:28:57  kebiao
# 新技能系统
#
#
#
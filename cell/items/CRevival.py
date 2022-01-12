# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.7 2008-05-17 11:42:42 huangyongwei Exp $

"""

"""
import csstatus
import SkillTargetObjImpl
from CItemBase import CItemBase
from Resource.SkillLoader import g_skills

class CRevival( CItemBase ):
	"""
	复活类物品基础类 by姜毅 2009-7-28
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
		
	def use( self, owner, target ):
		"""
		简化归命符的使用流程，因为这是个特例化物品
		"""
		target = SkillTargetObjImpl.createTargetObjEntity( target )
		spell = g_skills[self.getSpellID()]		# 不用父类接口try的做法，因为这个技能非常古老，要是出问题干脆让暴露算了
		spell.use( owner, target )
		return csstatus.SKILL_GO_ON

#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/03/24 02:30:55  yangkai
# 添加套装属性相关描述
#
# Revision 1.5  2008/02/22 01:40:25  yangkai
# 添加防具附加属性描述
#
# Revision 1.4  2008/01/29 02:37:26  yangkai
# 修正物品描述信息
#
# Revision 1.3  2008/01/24 10:10:41  yangkai
# 添加物品相关描述
#
# Revision 1.2  2006/08/11 02:47:12  phw
# 删除了接口wield()和unwield()里属于cellApp的废代码
#
# Revision 1.1  2006/08/09 08:21:30  phw
# no message
#

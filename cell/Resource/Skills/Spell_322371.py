# -*- coding: gb18030 -*-
#
# $Id: Spell_322371.py,v 1.4 2008-02-21 02:31:16 kebiao Exp $

"""
"""

from SpellBase import *
import csstatus
from Spell_Item import Spell_Item
from Resource.SkillLoader import g_skills
from Resource.SkillTeachLoader import g_skillTeachDatas
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine

class Spell_322371( Spell_Item ):
	"""
	使用：宠物遗忘自己所有的技能。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def useableCheck( self, caster, target ) :
		if not target.getObject().pcg_hasActPet() :
			return csstatus.PET_EVOLVE_FAIL_NOT_CONJURED
		return Spell_Item.useableCheck( self, caster, target )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		for skillID in list( receiver.getSkills() ): # 必需复制列表，因为循环里面有操作该列表的行为 -pj
			if g_skills[skillID].getType() == csdefine.BASE_SKILL_TYPE_PASSIVE:
				continue
			receiver.removeSkill( skillID )
			
# $Log: not supported by cvs2svn $
# Revision 1.3  2007/12/18 02:51:17  kebiao
# 修改继承关系
#
# Revision 1.2  2007/12/05 01:35:48  kebiao
# no message
#
# Revision 1.1  2007/12/04 03:52:15  kebiao
# no message
#
# Revision 1.1  2007/12/03 08:23:30  kebiao
# no message
#
#
#
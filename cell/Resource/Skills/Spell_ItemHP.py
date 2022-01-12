# -*- coding: gb18030 -*-
#
# $Id: Spell_ItemHP.py,v 1.10 2008-08-14 06:11:09 songpeifang Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_ItemCure import Spell_ItemCure
import csstatus

class Spell_ItemHP( Spell_ItemCure ):
	"""
	使用：立刻恢复自身生命值1960点。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemCure.__init__( self )
		#self._p1 = 0 #立刻恢复自身生命值1960点。
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemCure.init( self, dict )
		#self._p1 = dict.readInt( "param0" )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		#这句必须放在最前面 请参考底层
		if caster.isReal():
			Spell_ItemCure.receive( self, caster, receiver )
		
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return
		
		self.receiveLinkBuff( caster, receiver )		# 接收额外的CombatSpell效果，通常是buff(如果存在的话)

		self.cureHP( caster, receiver, self._effect_max )
		
	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if target.getObject().HP == target.getObject().HP_Max:
			return csstatus.SKILL_CURE_NONEED
		return Spell_ItemCure.useableCheck( self, caster, target)

# $Log: not supported by cvs2svn $
# Revision 1.9  2008/08/13 09:18:37  songpeifang
# 将缓慢药品配置为此技能，加上buff，使之在满血时也提示无需使用
#
# Revision 1.8  2008/07/29 06:39:02  songpeifang
# 向自己宠物释放技能的对象改为宠物本身而不是玩家本身
#
# Revision 1.6  2008/07/29 03:47:06  kebiao
# 修改判断方式
#
# Revision 1.5  2008/07/16 06:25:20  huangdong
# 增加了满血不能喝加血药的限制
#
# Revision 1.4  2008/01/31 08:13:48  kebiao
# 修改了可能出现的BUG
#
# Revision 1.3  2008/01/31 07:06:45  kebiao
# 加入治疗信息
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# 使用技能效果值
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
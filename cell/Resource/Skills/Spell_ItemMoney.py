# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
技能对物品施展法术基础。
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
		构造函数。
		"""
		Spell_Item.__init__( self )
		self._p0 = 0 #增加金钱最小值
		self._p1 = 0 #增加金钱最大值
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self._p0 = int( dict[ "param0" ] if len( dict[ "param0" ] ) > 0 else 0 ) 	
		self._p1 = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		#这句必须放在最前面 请参考底层
		Spell_Item.receive( self, caster, receiver )
		money = random.randint( self._p0, self._p1 )
		caster.addMonery( money )
				

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
		return Spell_Item.useableCheck( self, caster, target)


# $Log: not supported by cvs2svn $
# Revision 1.6  2008/08/13 09:18:50  songpeifang
# 将缓慢药品配置为此技能，加上buff，使之在满蓝时也提示无需使用
#
# Revision 1.5  2008/07/29 06:36:25  songpeifang
# 修改了玩家血/蓝满时宠物也不能吃红/蓝的bug
#
# Revision 1.4  2008/07/16 04:08:38  huangdong
# 修改了满蓝不能喝药的提示消息
#
# Revision 1.3  2008/07/16 03:33:30  huangdong
# 加入了满蓝不能喝药的限制
#
# Revision 1.2  2007/12/04 08:31:21  kebiao
# 使用技能效果值
#
# Revision 1.1  2007/12/03 07:45:20  kebiao
# no message
#
#
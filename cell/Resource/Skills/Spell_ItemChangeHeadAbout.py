# -*- coding: gb18030 -*-
#
# $Id: Spell_Item_Change_Body.py,v 1.2 2008-08-14 02:32:06 zhangyuxing Exp $

"""
在规定位置使用物品
"""

from SpellBase import *
import cschannel_msgs
import ShareTexts as ST
from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus
import BigWorld
import csdefine
import csconst
from Spell_Item import Spell_Item

# 根据角色的性别、职业，从物品的param参数中得到适当的模型组合ID
param_map = {
	0:{
	16:"param1",		# 战士
	32:"param2",		# 剑客
	48:"param3",		# 射手
	64:"param4",		# 法师
	},
	1:{
	16:"param5",
	32:"param6",
	48:"param7",
	64:"param8",
	},
}

class Spell_ItemChangeHeadAbout( Spell_Item ):
	"""
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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		# self.drawChangeBody( caster, receiver )
		uid = caster.queryTemp( "item_using" )
		item = caster.getItemByUid_( uid )
		if item:
			param = param_map[receiver.getGender()][receiver.getClass()]
			modnum = int(item.query( param ))
			receiver.setTemp( "headAboutModNum", modnum )
		Spell_Item.receive( self, caster, caster )
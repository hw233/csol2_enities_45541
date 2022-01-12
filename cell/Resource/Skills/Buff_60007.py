# -*- coding: gb18030 -*-
#
# $Id: Buff_1004.py,v 1.4 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


#血量增加 %
#物理伤害减免 %
#法术伤害减免 %
#血量每秒增加 %

EFFECT_DATA = { 6: { "HP_Max" : 60, "damage_derate": 60, "damage" : 60 },
	   	5: { "HP_Max" : 50, "damage_derate": 50, "damage" : 50 },
		4: { "HP_Max" : 40, "damage_derate": 40, "damage" : 40 },
		3: { "HP_Max" : 30, "damage_derate": 30, "damage" : 30 },
		2: { "HP_Max" : 20, "damage_derate": 20, "damage" : 20 },
		1: { "HP_Max" : 10, "damage_derate": 10, "damage" : 10 },
		}


class Buff_60007( Buff_Normal ):
	"""
	夸父神殿，树的BUFF
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.param1 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.param1 = int( dict["Param1"] )
		self.param2 = dict["Param2"]

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		monsters = receiver.entitiesInRangeExt( self.param1, "Monster", receiver.position )
		for i in monsters:
			if i.className == self.param2:
				receiver.setTemp( "kua_fu_remain_tree_id", i.id )
				break

		id = receiver.queryTemp( "kua_fu_remain_tree_id", 0 )
		
		tree = BigWorld.entities.get( id )
		lastHPRange = 0
		newHPRange = int ( tree.HP * 1.0 / tree.HP_Max * 100 ) / 20 + 1		#树的 HP 区域。（1～19， 20～39， ...， 80～99， 100）
		self.doNewEffect( receiver, lastHPRange, newHPRange )



	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )


	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		lastHPRange = receiver.queryTemp( "kua_fu_remain_tree_HP_range", 0 )
		receiver.removeTemp( "kua_fu_remain_tree_HP_range" )
		self.doNewEffect( receiver, lastHPRange, 0 )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		id = receiver.queryTemp( "kua_fu_remain_tree_id", 0 )
		
		tree = BigWorld.entities.get( id )
		lastHPRange = receiver.queryTemp( "kua_fu_remain_tree_HP_range", 0 )
		if tree and tree.position.flatDistTo( receiver.position ) <= tree.initiativeRange + 1:
			newHPRange = int ( tree.HP * 1.0 / tree.HP_Max * 100 ) / 20 + 1		#树的 HP 区域。（1～19， 20～39， ...， 80～99， 100）
			self.doNewEffect( receiver, lastHPRange, newHPRange )
		else:
			self.doNewEffect( receiver, lastHPRange, 0 )
			receiver.removeTemp( "kua_fu_remain_tree_HP_range" )
			return False
		
		return Buff_Normal.doLoop( self, receiver, buffData )
	
	
	def doNewEffect( self, receiver, lastHPRange, newHPRange ):
		"""
		"""
		if newHPRange != 0:
			addHPValue = int( receiver.HP * 0.1 * newHPRange )
			if receiver.HP + addHPValue > receiver.HP_Max:
				addHPValue = receiver.HP_Max - receiver.HP
			receiver.addHP( addHPValue )
		
		if lastHPRange != newHPRange:
			if lastHPRange != 0:
				receiver.HP_Max_percent -= EFFECT_DATA[lastHPRange]["HP_Max"] * 100
				receiver.damage_derate_ratio_value -= EFFECT_DATA[lastHPRange]["damage_derate"] * 100
				receiver.damage_derate_ratio_value -= EFFECT_DATA[lastHPRange]["damage_derate"] * 100
				receiver.magic_damage_percent -= EFFECT_DATA[lastHPRange]["damage"]
				receiver.damage_min_value -= EFFECT_DATA[lastHPRange]["damage"]
				receiver.damage_max_value -= EFFECT_DATA[lastHPRange]["damage"]
				
			
			if newHPRange != 0:
				receiver.HP_Max_percent += EFFECT_DATA[newHPRange]["HP_Max"] * 100
				receiver.damage_derate_ratio_value += EFFECT_DATA[newHPRange]["damage_derate"] * 100
				receiver.damage_derate_ratio_value += EFFECT_DATA[newHPRange]["damage_derate"] * 100
				receiver.magic_damage_percent += EFFECT_DATA[newHPRange]["damage"]
				receiver.damage_min_value += EFFECT_DATA[newHPRange]["damage"]
				receiver.damage_max_value += EFFECT_DATA[newHPRange]["damage"]
			receiver.setTemp( "kua_fu_remain_tree_HP_range", newHPRange )
			receiver.calcMagicDamageDerateRatio()
			receiver.calcDamageDerateRatio()
			receiver.calcHPMax()
			receiver.calcMagicDamage()
			receiver.calcDamageMin()
			receiver.calcDamageMax()
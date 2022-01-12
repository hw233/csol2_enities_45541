# -*- coding: gb18030 -*-
"""
钓鱼技能 2009-01-09 SongPeifang & LinQing
"""
import csstatus
import csdefine
import random
import sys
from Spell_Item import Spell_Item
from bwdebug import *
from Love3 import g_rewards
from VehicleHelper import getCurrVehicleID
import SkillTargetObjImpl

class Spell_322399001( Spell_Item ):
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
		self._validSunTime = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 			# 每天的合法日光浴时间
		self._fishingRange = int( dict[ "param3" ] if len( dict[ "param3" ] ) > 0 else 0 ) 			# 距离海边多远可以钓鱼
		self._escapeRate = float( dict[ "param4" ] if len( dict[ "param4" ] ) > 0 else 0.0 ) 		# 钓鱼脱钩的几率

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver = caster
		a = random.random()
		if a <= 1 - self._escapeRate:
			# 钓到鱼的情况
			awarder = g_rewards.fetch( csdefine.RCG_FISH, caster )
			kitbagState = receiver.checkItemsPlaceIntoNK_( awarder.items )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# 背包空间不够装下这条鱼
				receiver.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
				return
			awarder.award( caster, csdefine.ADD_ITEM_FISHING )
		else:
			# 脱钩的情况，提示玩家鱼脱钩
			receiver.statusMessage( csstatus.SKILL_FISH_RUN_AWAY )

		# 钓鱼经验奖励
		gainExp = int( 31.42 + 6.28 * pow( receiver.level, 1.2 ) )
		receiver.addExp ( gainExp, csdefine.CHANGE_EXP_FISHING )

		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		if caster.getState() == csdefine.ENTITY_STATE_FIGHT:
			caster.end_body_changing( caster.id, "" )	# 取消钓鱼
			return csstatus.SKILL_USE_TELEPORT_ON_FIGHTING
		uid = caster.queryTemp( "item_using" )
		caster.setTemp( "current_yugan_index", uid )
		receiver = caster

		# 骑乘状态下不允许钓鱼
		if receiver.vehicle or getCurrVehicleID( receiver ):
			return csstatus.SKILL_CAST_FISH_NO_VEHICLE

		# 判断是否在钓鱼的区域
		if len( receiver.entitiesInRangeExt( self._fishingRange, "SpecialHideEntity", receiver.position ) ) < 1:
			receiver.end_body_changing( receiver.id, "" )	# 取消钓鱼
			return csstatus.SKILL_CAST_NOT_SUN_FISH_PLACE

		# 判断玩家是否还剩有钓鱼时间
		if not receiver.queryTemp( "has_fishing_time", False ):
			if receiver.getState() == csdefine.ENTITY_STATE_CHANGING:
				receiver.changeState( csdefine.ENTITY_STATE_FREE )	# 设置为普通状态
				receiver.currentModelNumber == ""
			return csstatus.SKILL_CAST_NOT_SUN_FISH_TIME

		state = Spell_Item.useableCheck( self, caster, target)

		if caster.getState() == csdefine.ENTITY_STATE_CHANGING and \
			caster.currentModelNumber != 'fishing' and caster.currentModelNumber != '':
				return csstatus.SKILL_CAST_CANT_FISH_IN_BC

		if state == csstatus.SKILL_GO_ON:
			# 通知更换变身模型，这里是钓鱼模型
			if caster.getState() != csdefine.ENTITY_STATE_CHANGING:
				caster.begin_body_changing( 'fishing', 1.0 )
		return state

	def updateItem( self , caster ):
		"""
		更新物品使用
		"""
		Spell_Item.updateItem( self , caster )
		uid = caster.queryTemp( "current_yugan_index" )
		item = caster.getByUid( uid )
		# 更新完该物品，继续自动使用该物品
		if item is None:
			caster.statusMessage( csstatus.CIB_MSG_FISHING_ROD_BROKEN ) # 鱼竿磨损严重，已经不能使用了，钓鱼停止！
			caster.end_body_changing( caster.id, "" )					# 取消钓鱼
		else:
			casterObj = SkillTargetObjImpl.createTargetObjEntity( caster )
			caster.useItem( caster.id, item.uid, casterObj )			# 继续使用该鱼竿钓鱼，产生连续钓鱼的效果

	def onSpellInterrupted( self, caster ):
		"""
		当施法被打断时的时候，改变钓鱼状态为自由状态
		"""
		caster.removeTemp( "current_yugan_index" )
		Spell_Item.onSpellInterrupted( self, caster )
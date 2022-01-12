# -*- coding: gb18030 -*-
#
# 钓鱼的客户端技能 2009-01-10 SongPeifang & LinQing
#
from Spell_Item import Spell_Item
import GUIFacade
import BigWorld
import random
import csdefine
import csstatus

class Spell_322399001( Spell_Item ):
	"""
	钓鱼的客户端技能
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell_Item.init( self, dict )
		self._fishingRange = int( dict[ "param3" ] )		# 距离海边多远可以钓鱼

	def rotate( self, caster ):
		"""
		转动方向面对大海（实际上就是面对海边布置的隐藏Entity）
		"""
		# 获取象征海边的一些特殊隐藏Entity
		entities = caster.entitiesInRange( self._fishingRange, cnd = lambda ent : ent.__class__.__name__ == "SpecialHideEntity" )
		if len( entities ) < 1:
			return
		index = random.randint( 0, len( entities ) - 1 )
		# 从这些Entity里随机出一个供玩家转向
		specialHideEntity = entities[index]
		new_yaw = ( specialHideEntity.position - caster.position ).yaw
		# yaw差距大于10度时才转向
		if abs( caster.yaw - new_yaw ) > 0.0:
			caster.turnaround( specialHideEntity.matrix, None )

	def useableCheck( self, caster, target ):
		"""
		校验技能是否可以使用。
		"""
		entities = caster.entitiesInRange( self._fishingRange, cnd = lambda ent : ent.__class__.__name__ == "SpecialHideEntity" )
		if len( entities ) < 1:
			# 判断玩家是否满足在可钓鱼的区域内
			return csstatus.SKILL_CAST_NOT_SUN_FISH_PLACE
		return Spell_Item.useableCheck( self, caster, target)

	def interrupt( self, caster, reason ):
		"""
		中断钓鱼
		@type	speller 	: entity
		@param	speller 	: 动作施放者
		"""
		player = BigWorld.player()
		if player.id != caster.id:
			return
		Spell_Item.interrupt( self, caster, reason )
		if reason != csstatus.SKILL_PLAYER_REQUIRE_INTERRUPT_1 or caster.getState() == csdefine.ENTITY_STATE_DEAD:
			# 结束钓鱼要关闭钓鱼界面，但是如果中断原因还是钓鱼就不需要了
			GUIFacade.onFishingEnd( caster )
			caster.end_body_changing( "" )

	def intonate( self, caster, intonateTime, targetObject ):
		"""
		播放技能吟唱动作和效果。
		"""
		player = BigWorld.player()
		if player.id == caster.id:
			self.rotate( caster )	# 转向海边
		Spell_Item.intonate( self, caster, intonateTime, targetObject )
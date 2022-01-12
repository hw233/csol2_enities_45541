# -*- coding: gb18030 -*-

"""
延迟传送技能
"""
import BigWorld
import Math
import csconst
from gbref import rds
from bwdebug import *
from SpellBase import *


class Spell_DelayTeleport( Spell ):
	"""
	延迟传送
	"""
	def __init__( self ):
		"""
		"""
		Spell.__init__( self )
		# 传送数据
		self._spaceName = ""         # 空间名称
		self._pos = Math.Vector3()	 # 坐标
		self._npcName = ""			 # NPC名字
		self._delayTime = 0			 # 延迟时间

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )

		self._spaceName = dict["param1"] if len( dict["param1"] ) > 0 else ""
		pos = dict["param2"] if len( dict["param2"] ) > 0 else ""
		if pos:
			self._pos = Math.Vector3( eval( pos ) )
		self._npcName = dict["param3"] if len( dict["param3"] ) > 0 else ""
		self._delayTime = int( dict["param4"] if len( dict["param4"] ) > 0 else 0 )

	def receiveSpell( self, target, casterID, damageType, damage ):
		"""
		接受技能处理

		@type   casterID: OBJECT_ID
		@type	  param1: INT32
		@type	  param2: INT32
		@type	  param3: INT32
		"""
		player = BigWorld.player()
		caster = None
		if casterID:
			try:
				caster = BigWorld.entities[casterID]
			except KeyError:
				return

		# 动作光效部分
		self._skillAE( player, target, caster, damageType, damage )

	def _skillAE( self, player, target, caster, damageType, damage ):
		"""
		受击效果，动作光效等
		"""
		if caster is None: return
		if target != player: return # 不是玩家自己
		if caster.position.distTo( target.position ) >= csconst.PLAYER_TO_NPC_DISTANCE: return
		id = self.getID()
		self.pose.hit( id, target )
		rds.skillEffect.playHitEffects( caster, target, id )
		rds.skillEffect.playCameraEffects( caster, target, id )

		target.delayTeleport( self, caster, self._spaceName, self._pos, self._npcName, self._delayTime )  # 延迟传送接口
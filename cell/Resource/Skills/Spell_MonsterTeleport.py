# -*- coding: gb18030 -*-

"""
怪物瞬移
"""
import csdefine
from bwdebug import *
from SpellBase import *
from utils import vector3TypeConvert

class Spell_MonsterTeleport( Spell ):
	"""
	怪物瞬移到指定地点（仅限当前地图）
	param1（位置）：x,y,z
	param2（方向）：x,y,z，逗号隔开
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Spell.__init__( self )
		self._position = ( 0.0, 0.0, 0.0 )	# 位置
		self._direction = ( 0.0, 0.0, 0.0 )	# 方向

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell.init( self, dict )
		position = dict["param1"] if dict["param1"] else ""
		direction = dict["param2"] if dict["param2"] else ""
		if position:
			pos = vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error: skillID(%s), param1(%s)" % ( self.getID(), position ) )
			else:
				self._position = pos

		if direction:
			dir = vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error: skillID(%s), param2(%s)" % ( self.getID(), direction ) )
			else:
				self._direction = dir

	def __allowTeleport( self, entity ):
		"""
		entity当前状态是否可以瞬移
		@return bool
		"""
		if entity.effect_state & csdefine.EFFECT_STATE_VERTIGO: #眩晕
			return False	
		if entity.effect_state & csdefine.EFFECT_STATE_SLEEP: #昏睡
			return False
		if entity.effect_state & csdefine.EFFECT_STATE_FIX:	#定身
			return False
		if entity.actionSign( csdefine.ACTION_FORBID_MOVE ): #不允许移动标志
			return False
		return True

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( caster.id, self )
			return

		if not self.__allowTeleport( receiver ):
			return

		receiver.position = self._position
		receiver.spawnPos = self._position
		receiver.direction = self._direction
		receiver.closeVolatileInfo()
		receiver.openVolatileInfo()
		receiver.planesAllClients( "setFilterLatency", () ) #瞬间移动，不会有缓冲过程
		receiver.stopMoving()
		self.receiveLinkBuff( caster, receiver ) #支持buff
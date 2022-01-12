# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22007( Buff_Normal ):
	"""
	日光浴buff，不断不断减少玩家血值（当然，遵循一定规律）
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = "lv*2"
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ) .replace(" ","")			# 获得每次要掉多少血的计算公式
		self._hpVal = int( self._p1[ 3:len( self._p1 ) ] )
		self._hpOpt = self._p1[ 2:3 ]
	
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
		receiver.setTemp( "forbid_revert_hp", False )	# 给玩家身上增加禁止回血的标记
	
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
		receiver.setTemp( "forbid_revert_hp", False )	# 给玩家身上增加禁止回血的标记
	
	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.removeTemp( "forbid_revert_hp" )	# 清除掉玩家身上禁止回血的标记
	
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
		decreaseHP = 0
		
		if receiver.queryTemp( "has_suntan_oil", 0 ) != 1:	# 如果玩家没有涂防晒霜
			decreaseHP = self.getDecHP( receiver.level, self._hpOpt, self._hpVal )
			
			if receiver.queryTemp( "jthl_hp_rate", 0.0 ) > 0:	# 如果角色有惊涛骇浪buff
				# 惊涛骇浪扣除的血量为正常值的jthl_hp_rate倍
				decreaseHP += decreaseHP * receiver.queryTemp( "jthl_hp_rate", 0.0 )
		
		if decreaseHP > 0:	# 如果角色掉血了
			receiver.addHP ( 0 - decreaseHP )
			self.onPlayerAddHP( receiver, decreaseHP )
			
		return Buff_Normal.doLoop( self, receiver, buffData )
		
	def onPlayerAddHP( self, player, decreaseHP ):
		"""
		客户端表现减血，及判断玩家是否死亡
		"""
		player.receiveSpell( 0, self.getID(), csdefine.DAMAGE_TYPE_VOID, decreaseHP, 0 )
		if player.HP <= 0:
			player.onInSunBathingDead()
	
	def getDecHP( self, level, opration, value ):
		"""
		根据公式获得减少的血量
		"""
		return level * value
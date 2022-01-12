# -*- coding: gb18030 -*-
#安全区高度判断buff

from Buff_Normal import Buff_Normal
import csstatus
import csdefine

class Buff_22020( Buff_Normal ):
	"""
	安全区高度判断buff
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] ) #安全区陷进的Y坐标
		self._p2 = float( dict[ "Param2" ] ) #陷阱高度
		self._loopSpeed = 3
		

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
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #大于高度则不进入安全区
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#如果没有安全区标志
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # 玩家身上加一个安全区域的标志，用于一些其他的判定
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# 禁止PK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )

	def doLoop( self, receiver, buffData ):
		"""
		@add by wuxo 2011-11-11
		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #大于高度则不进入安全区
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#如果没有安全区标志
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # 玩家身上加一个安全区域的标志，用于一些其他的判定
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# 禁止PK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
		else:
			if receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#如果有安全区标志
				receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# 移除玩家身上的安全区域的标志
				receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )	
				receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )
				
		return  Buff_Normal.doLoop( self, receiver, buffData )
	
	
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
		pos = receiver.position
		if pos[1] - self._p1 <= self._p2: #大于高度则不进入安全区
			if not receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#如果没有安全区标志
				receiver.addFlag( csdefine.ROLE_FLAG_SAFE_AREA ) # 玩家身上加一个安全区域的标志，用于一些其他的判定
				receiver.effectStateInc( csdefine.EFFECT_STATE_NO_FIGHT )# 禁止PK
				receiver.statusMessage( csstatus.ROLE_ENTER_PK_FORBIDEN_AREA )
			

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
		if receiver.hasFlag( csdefine.ROLE_FLAG_SAFE_AREA ):#如果有安全区标志
			receiver.removeFlag( csdefine.ROLE_FLAG_SAFE_AREA )				# 移除玩家身上的安全区域的标志
			receiver.effectStateDec( csdefine.EFFECT_STATE_NO_FIGHT )	
			receiver.statusMessage( csstatus.ROLE_LEAVE_PK_FORBIDEN_AREA )

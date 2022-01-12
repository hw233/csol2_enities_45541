# -*- coding: gb18030 -*-
#
"""
防沉迷系统模块
2010.06.09: rewriten by huangyongwei
"""

import time
import BigWorld
import csdefine

class AntiWallow :
	"""
	未成年人防沉迷系统
	"""
	def __init__( self ):
		"""
		初始化
		"""
		self.bWallow_isAdult = False				# 是否是成年人（defined）


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onGetCell( self ) :
		eAccount = getattr( self, "accountEntity", None )
		if eAccount :
			isAdult = eAccount.customData.query( "adult" )
			if isAdult == "" or not isAdult :						# 配置为空或未配置，将被认为是未成年
				isAdult = False
			else:
				isAdult = int( isAdult )
		else:
			ERROR_MSG( "%s(%i:%i): I has no account entity." % ( self.getName(), self.databaseID, self.id ) )
			return	# 找不到所属帐号则不验证是否未成年，使用默认值就好
		
		if not isAdult:												# 如果是未成年人
			gwp = BigWorld.globalBases["AntiWallowBridge"]
			gwp.onAccountLogin( eAccount.playerName )				# 则向防沉迷后台发送登录信息
		
		self.bWallow_isAdult = isAdult
		self.cell.wallow_setAgeState( isAdult )

	def onLoseCell( self ) :
		eAccount = getattr( self, "accountEntity", None )
		if eAccount and not self.bWallow_isAdult :						# 如果是非成年人
			gwp = BigWorld.globalBases["AntiWallowBridge"]
			gwp.onAccountLogout( eAccount.playerName )					# 则向防沉迷后台发送登出信息

	# -------------------------------------------------
	def wallow_onWallowNotify( self, state, olTime ) :
		"""
		defined.
		沉迷提醒
		@type			state  : MACRO DEFINATION
		@param			state  : 收益状态，在 csdefine 中定义：WALLOW_XXX
		@type			olTime : INT64
		@param			olTime : 在线时间
		"""
		self.cell.wallow_onWallowNotify( state, olTime )


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def wallow_setAgeState( self, isAdult ) :
		"""
		defined.
		设置年龄状态
		@type			isAdult : BOOL
		@param			isAdult : 是否是成年
		"""
		eAccount = getattr( self, "accountEntity", None )
		if eAccount :
			eAccount.customData.set( "adult", str( int( isAdult ) ) )	# 将 BOOL 型的 isAdult 转换为字符'0','1'。还原数据避免其他对方使用的时候不知道该只会被修改而出错。
			self.bWallow_isAdult = isAdult
			self.cell.wallow_setAgeState( isAdult )

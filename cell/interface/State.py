# -*- coding: gb18030 -*-
#
# $Id: State.py,v 1.21 2008-07-04 03:49:47 kebiao Exp $

"""
状态模块
"""

from bwdebug import *
import csdefine
import csconst

class State:
	"""
	"""
	def __init__( self ):
		"""
		初始化状态。要在Fight初始化之前
		"""
		self.actCounter = [0] * len( csconst.ACTFBLIST )
		self.effectCounter = [0] * len( csconst.EFFECT_STATE_LIST )
		"""
		self.actCounter = []
		for tmp in csconst.ACTFBLIST:
			self.actCounter.append( 0 )
		#self.actCounter = [0, 0, 0, 0, 0, 0, 0]		# 不能在显示未初始化属性的时候使用append，会有问题
		"""
		self.actWord = 0
		self.effect_state = 0
		self.lastState = 0 # 保存上一次的状态
		
		if self.state < 0 or self.state >= csdefine.ENTITY_STATE_MAX:
			self.state = csdefine.ENTITY_STATE_FREE

		self.actCounterInc( csconst.ACTFBMASK[self.state] )		# 恢复存盘过的状态计数

	def changeState( self, newState ):
		"""
		改变状态。
			@param newState	:	新的状态
			@type newState	:	integer
		"""
		#if newState == csdefine.ENTITY_STATE_FREE:
		#	print "++++++ restoring to pending state... "
		#	import msdebug
		#	msdebug.printStackTrace()
			
		
		
		if self.state == newState:
			return

		old = self.state
		
		# phw 2009-12-22: 在没有什么特殊情况下，状态切换不再写日志，这种日志数量太大了，什么时候需要测试的时候再打开吧
		#TRACE_MSG( self.id, " State ", self.state, " => ", newState )
		
		# 减少原状态的行为限制记数
		self.actCounterDec( csconst.ACTFBMASK[self.state] )
		self.state = newState
		# 增加新状态的行为限制记数
		self.actCounterInc( csconst.ACTFBMASK[newState] )
		
		# phw 2009-12-22: 在没有什么特殊情况下，状态切换不再写日志，这种日志数量太大了，什么时候需要测试的时候再打开吧
		#TRACE_MSG( self.id, " actCounter = ", self.actCounter )

		self.onStateChanged( old, self.state )

	def actCounterInc( self, stateWord ):
		"""
		动作计数器加一，并维护动作限制。
			@param stateWord	:	动作状态字
			@type stateWord		:	integer
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if stateWord & act:
				if self.actCounter[i] == 0:
					self.actWord |= act
					self.onActWordChanged( act, True )
				self.actCounter[i] += 1		# Counter不得大于255

	def actCounterDec( self, stateWord ):
		"""
		动作计数器减一，并维护动作限制。
			@param stateWord	:	动作状态字
			@type stateWord		:	integer
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if stateWord & act:
				if self.actCounter[i] - 1 >= 0:
					self.actCounter[i] -= 1
					if self.actCounter[i] == 0:
						self.actWord &= ~act
						self.onActWordChanged( act, False )
				else:
					ERROR_MSG( "Asymmetric call of actCounterInc/actCounterDec!" )
	
	def getActCounter( self, actBit ):
		"""
		获取行为计数器的值
		"""
		for i, act in enumerate( csconst.ACTFBLIST ):
			if actBit == act:
				return self.actCounter[ i ]
		
		ERROR_MSG( "No such act bit!" )
		return 0

	def getState( self ):
		"""
		获取状态。
			@return :	当前状态
			@rtype	:	integer
		"""
		return self.state
		
	def getLastState( self ):
		"""
		获取当前状态之前的状态
		"""
		return self.lastState
		

	def isState( self, state ) :
		"""
		判断是否在某种状态下( hyw )
		@param			state : MACRO DEFINATION
		@type			state : states defined in csdefine.py
		@rtype				  : bool
		@return				  : 在指定状态下则返回 True
		"""
		return state == self.state

	def getActWord( self ):
		"""
		获取动作限制。应该很少用，一般会使用actionSign()来测试是否动作可用
			@return	:	当前动作限制
			@rtype	:	integer
		"""
		return self.actWord

	def actionSign( self, signWord ):
		"""
		是否存在标记。
			@return	:	标记字
			@rtype	:	bool
		"""
		return self.actWord & signWord != 0

	def onStateChanged( self, old, new ):
		"""
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		self.lastState = old

	def onActWordChanged( self, act, disabled ):
		"""
		动作限制改变.
			@param act		:	动作标识(非组合)
			@type act		:	integer
			@param disabled	:	动作是否被禁止
			@param disabled	:	bool
		"""
		pass

	# ----------------------------------------------------------------------------------------------------
	# 效果状态
	# EFFECT_STATE_SLEEP						= 0x00000001		# 昏睡效果
	# EFFECT_STATE_VERTIGO						= 0x00000002		# 眩晕效果
	# EFFECT_STATE_FIX							= 0x00000004		# 定身效果
	# EFFECT_STATE_HUSH_PHY						= 0x00000008		# 物理沉默效果
	# EFFECT_STATE_HUSH_MAGIC					= 0x00000010		# 法术沉默效果
	# EFFECT_STATE_INVINCIBILITY				= 0x00000020		# 无敌效果
	# EFFECT_STATE_NO_FIGHT					= 0x00000040			# 免战效果
	# EFFECT_STATE_PROWL						= 0x00000080			# 潜行效果
	# EFFECT_STATE_FOLLOW					= 0x00000100			# 跟随（玩家处于组队跟随中）
	# EFFECT_STATE_LEADER						= 0x00000200			# 引导（玩家处于组队引导中）
	# ----------------------------------------------------------------------------------------------------
	
	def effectStateChanged( self, estate, disabled ):
		"""
		效果改变.
			@param estate		:	效果标识(非组合)
			@type estate		:	integer
			@param disabled		:	效果是否生效
			@param disabled		:	bool
		"""
		pass
		
	def effectStateInc( self, estate ):
		"""
		添加一个效果状态到记数器
		"""
		for i, es in enumerate( csconst.EFFECT_STATE_LIST ):
			if estate & es:
				if self.effectCounter[i] == 0:
					self.effect_state |=  estate
					self.effectStateChanged( estate, True )
				self.effectCounter[i] += 1		# Counter不得大于255
				
	def effectStateDec( self, estate ):
		"""
		删除一个效果状态到记数器
		"""
		for i, es in enumerate( csconst.EFFECT_STATE_LIST ):
			if estate & es:
				self.effectCounter[i] -= 1
				if self.effectCounter[i] == 0:
					self.effect_state &= ~estate
					self.effectStateChanged( estate, False )
					
	
	# ---------------------------------------------------------------------------------
	# posture
	# ---------------------------------------------------------------------------------
	def changePosture( self, posture ):
		"""
		改变姿态
		
		@param posture : 目标姿态
		@type posture : UINT16
		"""
		self.beforePostureChange( posture )
		oldPosture = self.posture
		self.posture = posture
		self.afterPostureChange( oldPosture )
		
	def isPosture( self, posture ):
		"""
		是否处于某种姿态
		
		@param posture : 姿态
		@type posture : UINT16
		"""
		return self.posture == posture
		
	def getPosture( self ):
		return self.posture
		
	def beforePostureChange( self, newPosture ):
		"""
		姿态改变了
		
		@param oldPosture : 改变前的姿态
		@param newPosture : 改变后的姿态
		"""
		pass
		
	def afterPostureChange( self, oldPosture ):
		"""
		姿态改变了
		
		@param oldPosture : 改变前的姿态
		@param newPosture : 改变后的姿态
		"""
		pass
#
# $Log: not supported by cvs2svn $
# Revision 1.20  2007/12/14 08:20:06  huangyongwei
# 添加了 isState 函数
#
# Revision 1.19  2007/06/14 09:46:25  huangyongwei
# 删除了 validAction 方法
#
# Revision 1.18  2006/09/13 02:51:03  phw
# modify method: changeState(); 状态改变日志的输出加入了状态改变者的ID号
#
# Revision 1.17  2006/05/29 10:53:28  phw
# 调整状态，把ACTION_CANFIGHT改为ACTION_FORBID_FIGHT，统一所有定义都是默认为可以，修改相关代码
#
# Revision 1.16  2005/12/28 11:28:23  wanhaipeng
# Fix skill bugs.
#
# Revision 1.15  2005/12/09 03:37:22  xuning
# no message
#
# Revision 1.14  2005/12/01 06:38:22  xuning
# 工会
#
# Revision 1.13  2005/09/02 03:58:05  xuning
# 增加了Buff
# 增加了属性控制
# 调整了经验,升级,属性计算,状态控制等等,重新划分了模块关系.
#
# Revision 1.12  2005/07/04 12:28:00  xuning
# 去掉了状态存盘
#
# Revision 1.11  2005/07/04 08:18:56  xuning
# 将常量定义搬到L3Define.py
#
# Revision 1.10  2005/06/29 08:37:11  xuning
# no message
#
# Revision 1.9  2005/06/29 02:46:03  xuning
# no message
#
# Revision 1.8  2005/06/20 07:35:13  xuning
# 修改了物理攻击和状态切换的BUG
#
# Revision 1.7  2005/06/17 05:08:04  xuning
# 攻击和技能基础,修改
#
# Revision 1.6  2005/06/17 04:20:42  xuning
# 攻击和技能基础
#
# Revision 1.5  2005/05/09 04:42:49  panguankong
# 修改了持续状态的访问
#
# Revision 1.4  2005/03/29 10:02:29  panguankong
# 添加了代码注释，修改了变量大小写
#

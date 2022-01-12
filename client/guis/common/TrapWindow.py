# -*- coding: gb18030 -*-

# 把需要添加对话陷阱的窗口抽象出来，并定义了添加和移除对话陷阱
# 的保护方法
# by gjx 2010-08-18

from Window import Window
import BigWorld
import csconst

class TrapWindowBase( Window ) :

	def __init__( self, wnd = None ) :
		Window.__init__( self, wnd )

		self.__trappedEntityID = 0						# id of the trapped entity
		self.trapID_ = 0								# id of the added trap


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		添加陷阱
		"""
		pass

	def delTrap_( self ) :
		"""
		移除陷阱
		"""
		pass

	def onTrapTriggered_( self, *args ) :
		"""
		陷阱触发
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTrappedEntID( self, id ) :
		"""
		提供该接口给外部设置entity的ID
		应该在窗口显示之前设置entityID
		"""
		self.__trappedEntityID = id

	def show( self ) :
		"""
		默认窗口显示时添加陷阱
		"""
		Window.show( self )
		self.addTrap_()

	def hide( self ) :
		"""
		默认窗口关闭时移除陷阱
		"""
		Window.hide( self )
		self.delTrap_()

	def dispose( self ) :
		"""
		窗口销毁时调用
		"""
		self.delTrap_()
		Window.dispose( self )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def trappedEntity( self ) :
		return BigWorld.entities.get( self.__trappedEntityID )


class FixedTrapWindow( TrapWindowBase ) :
	"""陷阱的位置是固定的，玩家进出陷阱时会有回调，
	适用于创建之后就不会销毁的Entity"""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		默认是添加一个静态的陷阱
		"""
		self.delTrap_()
		trapEnt = self.trappedEntity
		if trapEnt :
			distance = csconst.COMMUNICATE_DISTANCE
			if hasattr( trapEnt, "getRoleAndNpcSpeakDistance" ) :
				distance = trapEnt.getRoleAndNpcSpeakDistance()
			self.trapID_ = BigWorld.addPot( trapEnt.matrix, distance, self.onTrapTriggered_ )
		else :
			self.hide()

	def delTrap_( self ) :
		"""
		移除陷阱
		"""
		if self.trapID_ > 0 :
			BigWorld.delPot( self.trapID_ )
			self.trapID_ = 0

	def onTrapTriggered_( self, enteredTrap, handle ) :
		"""
		陷阱触发
		@param	enteredTrap		: 是否进入了陷阱
		@type	enteredTrap		: int( 在陷阱里是1, 否则是0 )
		@param	handle			: 陷阱ID
		@type	handle			: int
		"""
		if not enteredTrap :
			self.hide()


class UnfixedTrapWindow( TrapWindowBase ) :
	"""陷阱添加在玩家身上，有Entity进出陷阱时会有回调，
	适用于创建之后会销毁的Entity"""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addTrap_( self ) :
		"""
		默认是添加一个静态的陷阱
		"""
		self.delTrap_()
		trapEnt = self.trappedEntity
		if trapEnt :
			distance = csconst.COMMUNICATE_DISTANCE
			if hasattr( trapEnt, "getRoleAndNpcSpeakDistance" ) :
				distance = trapEnt.getRoleAndNpcSpeakDistance()
			self.trapID_ = BigWorld.player().addTrapExt( distance, self.onTrapTriggered_ )
		else :
			self.hide()

	def delTrap_( self ) :
		"""
		移除陷阱
		"""
		if self.trapID_ > 0 :
			BigWorld.player().delTrap( self.trapID_ )
			self.trapID_ = 0

	def onTrapTriggered_( self, entitiesInTrap ) :
		"""
		陷阱触发
		@param	enteredTrap		: 是否进入了陷阱
		@type	enteredTrap		: int( 在陷阱里是1, 否则是0 )
		@param	handle			: 陷阱ID
		@type	handle			: int
		"""
		if self.trappedEntity not in entitiesInTrap :
			self.hide()

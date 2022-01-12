# -*- coding: gb18030 -*-
#
# $Id: SelectorGroup.py,v 1.3 2008-08-25 07:06:18 huangyongwei Exp $

"""
implement control arry, controls in the array must can be selected

2007/3/17 : writen by huangyongwei
"""

from guis import *

class SelectorGroup( object ) :
	def __init__( self, *pySelectors ) :
		self.__pySelectors = []						# 可选中控件列表
		self.__events = []
		self.generateEvents_()

		self.addSelectors( *pySelectors )

	def __del__( self ) :
		self.clearSelectors()
		self.__events = []
		if Debug.output_del_SelectorGroup :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def createEvent_( self, ename ) :
		"""
		创建事件
		"""
		event = ControlEvent( ename, self )
		self.__events.append( event )
		return event

	def generateEvents_( self ) :
		"""
		生成事件
		"""
		self.__onSelectChanged = self.createEvent_( "onSelectChanged" )		# 当选中的控件改变时被触发

	@property
	def onSelectChanged( self ) :
		"""
		当选中的控件改变时被触发。带一个参数，表示当前选中的控件，如果当前没有选中的控件，则该参数为 None
		"""
		return self.__onSelectChanged


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSelectChanged_( self, pySelector, selected ) :
		"""
		当某个 selector 选中状态改变时被调用
		"""
		if selected :
			for pyTmp in self.__pySelectors :								# 找出之前被选中的控件
				if not pyTmp.selected : continue
				if pyTmp == pySelector : continue							# 如果是当前正要选中的控件，则继续
				pyTmp.onSelectChanged.unbind( self.onSelectChanged_ )		# 清除之前选中控件的绑定事件，以防死循环
				pyTmp.selected = False										# 将之前选中的控件设置为未选中
				pyTmp.onSelectChanged.bind( self.onSelectChanged_ )			# 重新绑定
				break
			self.onSelectChanged( pySelector )								# 修改选中的控件触发事件
		else :
			self.onSelectChanged( None )									# 修改选中的控件触发事件


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addSelector( self, pySelector ) :
		"""
		添加一个可选控件
		@type				pySelector : checkable Control
		@param				pySelector : 可选中的控件（有 selected 属性）
		@rtype						   : bool
		@return					  	   : 添加成功则返回 True
		"""
		if pySelector in self.__pySelectors :
			DEBUG_MSG( "the button has been set!" )
			return False
		if hasattr( pySelector, "selectable" ) :
			pySelector.selectable = True
		self.__pySelectors.append( pySelector )
		pySelector.onSelectChanged.bind( self.onSelectChanged_ )
		return True

	def addSelectors( self, *pySelectors ) :
		"""
		添加一组可选中控件
		@type				pySelectors : list
		@param				pySelectors : 一组可被选中的控件
		@return							: None
		"""
		for pySelector in pySelectors :
			self.addSelector( pySelector )

	def removeSelector( self, pySelector ) :
		"""
		删除一个可选中控件
		@type				pySelector : checkable Control
		@param				pySelector : 可选中的控件（有 selected 属性）
		@rtype						   : bool
		@return					  	   : 删除成功则返回 True
		"""
		if pySelector not in self.__pySelectors :							# 要删除的控件不在列表中
			DEBUG_MSG( "the selector has not in the selector array!" )
			return False													# 返回删除失败
		isRemoveChecked = pySelector == self.pyCurrSelector					# 删除的控件是否是当前被选中的控件
		pySelector.onSelectChanged.unbind( self.onSelectChanged_ )			# 绑定选中事件
		self.__pySelectors.remove( pySelector )								# 从列表中删除
		if isRemoveChecked : self.onSelectChanged( None )					# 如果删除的控件，恰好是被选中的控件，则以 None 触发选中改变
		return True															# 返回删除成功

	def clearSelectors( self ) :
		"""
		清除所有可选中控件
		@return					  : None
		"""
		hasSelected = False													# 记录是否有选中的控件
		for pySelector in self.__pySelectors :								# 循环检查控件
			if pySelector.selected : hasSelected = True						# 如果有正被选中的控件，则置 hasSelected 为 True
			pySelector.onSelectChanged.unbind( self.onSelectChanged_ )		# 取消控件的选中绑定事件
		self.__pySelectors = []												# 清空控件列表
		if hasSelected :													# 如果之前有选中的控件
			self.onSelectChanged( None )									# 则，以 None 触发选中改变事件


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelectors( self ) :
		return self.__pySelectors[:]

	def _getCount( self ) :
		return len( self.__pySelectors )

	# -------------------------------------------------
	def _getCurrSelector( self ) :
		for pySelector in self.__pySelectors :
			if pySelector.selected :
				return pySelector
		return None

	def _setCurrSelector( self, pySelector ) :
		if isDebuged :
			assert pySelector in self.__pySelectors, "%s is not my member!" % str( pySelector )
		pySelector.selected = True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pySelectors = property( _getSelectors )								# 获取所有可选中的控件
	count = property( _getCount )										# 获取可选中控件的数量
	pyCurrSelector = property( _getCurrSelector, _setCurrSelector )		# 获取当前选中的控件

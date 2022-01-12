# -*- coding: gb18030 -*-
#
# $Id: CheckerGroup.py,v 1.2 2008-06-21 01:39:48 huangyongwei Exp $

"""
implement radio button array
-- 2007/06/26: writen by huangyongwei( the model's old name: RadioButtonArray )
-- 2008/03/29: renamed to 'CheckGroup' by huangyongwei
-- 2008/06/18: rename to 'CheckerGroup' by huangyongwei
"""

from guis import *

class CheckerGroup( object ) :
	def __init__( self, *pyCheckers ) :
		self.__pyCheckers = []				# 可选中控件列表
		self.__events = []
		self.generateEvents_()

		self.addCheckers( *pyCheckers )

	def __del__( self ) :
		self.clearCheckers()
		self.__events = []
		if Debug.output_del_CheckerGroup :
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
		产生事件
		"""
		self.__onCheckChanged = self.createEvent_( "onCheckChanged" )		# 当选中的控件改变时被触发

	@property
	def onCheckChanged( self ) :
		"""
		当选中的控件改变时被触发。带一个参数，表示当前选中的控件，如果当前没有选中的控件，则该参数为 None
		"""
		return self.__onCheckChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onChackerChackChanged( self, pyChecker, checked ) :
		if checked :															# 如果另一个控件被选中
			for pyTmp in self.__pyCheckers :									# 找出之前被选中的控件
				if not pyTmp.checked : continue
				if pyTmp == pyChecker : continue								# 如果是当前正要选中的控件，则继续
				pyTmp.onCheckChanged.unbind( self.__onChackerChackChanged )		# 清除之前选中控件的绑定事件，以防死循环
				pyTmp.checked = False											# 将之前选中的控件设置为未选中
				pyTmp.onCheckChanged.bind( self.__onChackerChackChanged )		# 重新绑定
				break
			self.onCheckChanged( pyChecker )									# 修改选中的控件触发事件
		else :																	# 如果某个控件的选中被取消
			self.onCheckChanged( None )											# 则，以 None 触发事件


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addChecker( self, pyChecker ) :
		"""
		添加一个可选控件
		@type				pyChecker : checkable Control
		@param				pyChecker : 可选中的控件（有 checked 属性）
		@rtype						  : bool
		@return					  	  : 添加成功则返回 True
		"""
		if pyChecker in self.__pyCheckers :
			DEBUG_MSG( "the button has been set!" )
			return False
		self.__pyCheckers.append( pyChecker )
		pyChecker.onCheckChanged.bind( self.__onChackerChackChanged )
		return True

	def addCheckers( self, *pyCheckers ) :
		"""
		添加一组可选中控件
		@type				pyCheckers : list
		@param				pyCheckers : 一组可被选中的控件
		@return						   : None
		"""
		for pyChecker in pyCheckers :
			self.addChecker( pyChecker )

	def removeChecker( self, pyChecker ) :
		"""
		删除一个可选中控件
		@type				pyChecker : checkable Control
		@param				pyChecker : 可选中的控件（有 checked 属性）
		@rtype						  : bool
		@return					  	  : 删除成功则返回 True
		"""
		if pyChecker not in self.__pyCheckers :
			DEBUG_MSG( "the button has not in the button array!" )
			return False
		isRemoveChecked = pyChecker == self.pyCurrChecker
		pyChecker.onCheckChanged.unbind( self.__onChackerChackChanged )
		self.__pyCheckers.remove( pyChecker )
		if isRemoveChecked :
			self.onCheckChanged( None )
		return True

	def clearCheckers( self ) :
		"""
		清除所有可选中控件
		@return					  : None
		"""
		hasChecked = False
		for pyChecker in self.__pyCheckers :
			if pyChecker.checked : hasChecked = True
			pyChecker.onCheckChanged.unbind( self.__onChackerChackChanged )
		self.__pyCheckers = []
		if hasChecked :
			self.onCheckChanged( None )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCheckers( self ) :
		return self.__pyCheckers[:]

	def _getCount( self ) :
		return len( self.__pyCheckers )

	# -------------------------------------------------
	def _getCurrChecker( self ) :
		for pyChecker in self.__pyCheckers :
			if pyChecker.checked :
				return pyChecker
		return None

	def _setCurrChecker( self, pyChecker ) :
		if isDebuged :
			assert pyChecker in self.__pyCheckers, "%s is not my member!" % str( pyChecker )
		pyChecker.checked = True


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyCheckers = property( _getCheckers )								# 获取所有可选中的控件
	count = property( _getCount )										# 获取可选中控件的数量
	pyCurrChecker = property( _getCurrChecker, _setCurrChecker )		# 获取当前选中的控件

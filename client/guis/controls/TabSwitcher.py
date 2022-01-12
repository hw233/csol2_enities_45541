# -*- coding: gb18030 -*-
#
# $Id: TabSwitcher.py,v 1.7 2008-06-21 01:53:33 huangyongwei Exp $

"""
implement tab switcher class
2006/07/21: writen by huangyongwei
2009/04/09: rewriten byw huangyongwei
		    取消 RootGUI 继承于 TabSwitcher
		    修改为需要在多个控件之间转换焦点时再创建
		    每个控件必须包含 onKeyDown 事件时，焦点转换才能生效
"""

from guis import *

class TabSwitcher( object ) :
	"""
	焦点转移器
	"""
	def __init__( self, pyCons = None ) :
		self.__pyCons = WeakList()						# 要获取焦点的子控件
		if pyCons :
			self.addTabInControls( pyCons )

	def dispose( self ) :
		self.clearTabInControls()

	def __del__( self ) :
		if Debug.output_del_TabSwitcher :
			INFO_MSG( str( self ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addTabInControls( self, pyCons ) :
		"""
		添加一组要获取焦点的控件
		"""
		for pyCon in pyCons :
			self.addTabInControl( pyCon )

	def addTabInControl( self, pyCon ) :
		"""
		添加一个要获取焦点的控件
		"""
		if pyCon not in self.__pyCons :
			self.__pyCons.append( pyCon )
			pyCon.onKeyDown.bind( self.onKeyDown_ )

	def removeTabInControl( self, pyCon ) :
		"""
		删除一个要获取焦点的控件
		"""
		if pyCon not in self.__pyCons :
			ERROR_MSG( "pyCon is not in %s" % str( self ) )
		else :
			self.__pyCons.remove( pyCon )
			pyCon.onKeyDown.unbind( self.onKeyDown_ )

	def clearTabInControls( self ) :
		"""
		清除所有要获取焦点的控件
		"""
		for pyCon in self.__pyCons :
			pyCon.onKeyDown.unbind( self.onKeyDown_ )
		self.__pyCons.clear()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __cancelCurrTabStop( self ) :
		"""
		取消当前控件的输入焦点
		"""
		pyCon = self.pyTabInControl
		if not pyCon : return False
		pyCon.tabStop = False
		return True

	def __getCanBeTabInControls( self ) :
		"""
		获取所有可以获得焦点的控件
		"""
		pyCons = []
		for pyCon in self.__pyCons :
			if not pyCon.rvisible : continue
			if not pyCon.enable : continue
			if not pyCon.canTabIn : continue
			pyCons.append( pyCon )
		return pyCons


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		"""
		按键按下时被调用（必须保证激活窗口首先截获按键消息）
		"""
		if mods == 0 and key == KEY_TAB :					# 如果按下 TAB 键
			self.tabForward()								# 则前移焦点
			return True
		elif mods == MODIFIER_SHIFT and key == KEY_TAB :	# 如果按下 SHIFT 和 TAB 键
			self.tabBackward()								# 则后移焦点
			return True
		return False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def tabForward( self ) :
		"""
		前移焦点
		"""
		pyCons = self.__getCanBeTabInControls()				# 获取所有可以获得焦点的控件
		if not len( pyCons ) : return False					# 如果数量为 0，则返回 False
		pyCon = self.pyTabInControl
		if pyCon is None :									# 如果当前没有获得焦点的控件
			pyCons[0].tabStop = True						# 则，让第一个控件获得焦点
			return True										# 返回设置成功
		if len( pyCons ) == 1 :								# 如果只有一个可获取焦点控件
			return True										# 则不作处理
		index = pyCons.index( pyCon )						# 获得当前焦点控件的索引
		nextIndex = ( index + 1 ) % len( pyCons )			# 获得下一个控件的索引
		pyCons[nextIndex].tabStop = True					# 设置下一个控件获得焦点
		return True

	def tabBackward( self ) :
		"""
		后移焦点
		"""
		pyCons = self.__getCanBeTabInControls()				# 获取所有可以获得焦点的控件
		if not len( pyCons ) : return False					# 如果数量为 0，则返回 False
		pyCon = self.pyTabInControl
		if pyCon is None :									# 如果当前没有获得焦点的控件
			pyCons[0].tabStop = True						# 则，让第一个控件获得焦点
			return True										# 返回设置成功
		if len( pyCons ) == 1 :								# 如果只有一个可获取焦点控件
			return True										# 则不作处理
		index = pyCons.index( pyCon )						# 获得当前焦点控件的索引
		foreIndex = ( index - 1 ) % len( pyCons )			# 获得上一个控件的索引
		pyCons[foreIndex].tabStop = True					# 设置上一个控件获得焦点
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTabInControls( self ) :
		return self.__pyCons.list()

	def _getTabInControlCount( self ) :
		return self.__pyCons.count()

	# -------------------------------------------------
	def _getTabInControl( self ) :
		for pyCon in self.__pyCons :
			if pyCon.tabStop : return pyCon
		return None


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	pyTabInControls = property( _getTabInControls )								# 获取所有可以获得焦点的控件
	tabInControlCount = property( _getTabInControlCount )						# 获取可以获得焦点控件的数量
	pyTabInControl = property( _getTabInControl )								# 获取当前获得焦点的控件，没有则返回 None

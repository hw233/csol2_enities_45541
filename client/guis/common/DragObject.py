# -*- coding: gb18030 -*-
#
# $Id: DragObject.py,v 1.6 2008-08-26 02:12:34 huangyongwei Exp $

"""
implement dragitem class
2005/08/10: wirten by huangyongwei( DragItem )
2008/01/24: renamed by huangyongwei( DragObject )
"""
"""
composing :
	the same as the source dragged
"""

import weakref
from guis import *
from AbstractTemplates import Singleton
from RootGUI import RootGUI

class DragObject( Singleton, RootGUI ) :
	def __init__( self ) :
		item = GUI.Simple( "" )							# 创建一个默认的 UI
		RootGUI.__init__( self, item )					# 回调父类构造函数
		self.posZSegment = ZSegs.L2						# 设置为管理器中第二层
		self.activable_ = False							# 不可以被激活
		self.hitable_ = False							# 不挡住鼠标
		self.escHide_ = False							# 不可以按 ESC 键隐藏

		self.__attach = None							# 拖放附加对象，可以在起拖的时候设置一个附加对象，然后在放下的时候获取该对象
		self.__mouseInPos = ( 0, 0 )					# 临时变量：保存鼠标按下时的坐标


	def dispose( self ) :
		self.release()
		RootGUI.dispose( self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onLastKeyUp( self, key, mods ) :
		"""
		当鼠标提起时被调用
		"""
		if key == KEY_LEFTMOUSE :
			LastKeyUpEvent.detach( self.__onLastKeyUp )			# 释放最好提起事件
			LastMouseEvent.detach( self.__onLastMouseEvent )	# 绑定鼠标最后移动事件
			self.release()										# 释放拖放 UI 的复制品

	def __onLastMouseEvent( self, dx, dy, dz ) :
		"""
		鼠标最后移动事件
		"""
		self.left += dx
		self.top += dy


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyDragged, dragMark ) :
		"""
		显示拖放对象
		"""
		def handle( newGui ) :									# 设置拖放对象复制品的属性
			newGui.focus = False								# 不可以接收按键事件
			newGui.dragFocus = False							# 不可以接收拖放事件
			newGui.dropFocus = False							# 不可以接收拖放事件
			newGui.moveFocus = False							# 不可以接收鼠标移动事件
			newGui.crossFocus = False							# 不可以接收鼠标进入事件

		cpy = util.copyGuiTree( pyDragged.getGui(), handle )	# 复制拖放对象
		self.resetBindingUI_( cpy )								# 重新绑定 UI 对象
		self.r_pos = pyDragged.r_posToScreen					# 设置复制品的位置
		self.dragMark = dragMark								# 设置拖放标记
		LastKeyUpEvent.attach( self.__onLastKeyUp )				# 绑定鼠标提起事件
		LastMouseEvent.attach( self.__onLastMouseEvent )		# 绑定鼠标最后移动事件
		RootGUI.show( self )									# 显示拖放对象的复制品

	def release( self ) :
		"""
		取消拖放
		"""
		self.attach = None										# 清空附加对象
		self.dragMark = DragMark.NONE							# 清空拖放标记
		self.hide()												# 隐藏拖放 UI 对象


	# ----------------------------------------------------------------
	# property methonds
	# ----------------------------------------------------------------
	def _setVisible( self, isVisible ) :
		if not isVisible : self.release()

	# -------------------------------------------------
	def _getMouseInPos( self ) :
		return self.__mouseInPos

	def _setMouseInPos( self, pos ) :
		self.__mouseInPos = pos

	# -------------------------------------------------
	def _getAttach( self ) :
		if self.__attach is None :
			return None
		if type( self.__attach ) is weakref.ReferenceType :	# 是弱引用对象
			return self.__attach()
		return self.__attach								# 是强引用对象

	def _setAttach( self, attach ) :
		try :
			self.__attach = RefEx( attach )					# 可以采取弱引用的则使用弱引用
		except TypeError :
			self.__attach = attach							# 否则使用强引用


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	visible = property( RootGUI._getVisible, _setVisible )			# 获取/设置拖放复制品的可见性
	dragging = property( RootGUI._getVisible )						# 获取是否处于拖放状态
	mouseInPos = property( _getMouseInPos, _setMouseInPos )			# 获取/设置鼠标拖放时它在拖放对象上的坐标
	attach = property( _getAttach, _setAttach )						# 拖放附加对象，可以在起拖的时候设置一个附加对象，然后在放下的时候获取该对象

# -*- coding: gb18030 -*-
#
"""
implement the polygon button
2009.05.11: written by gjx
2009.05.12: rewrote "mouseEnter" and "mouseLeave" events ( huangyongwei )
"""

from guis import *
from cscustom import Polygon
from Button import Button

class PolygonButton( Button ) :
	"""
	实现不规则的多边形按钮
	"""
	def __init__( self, button, points = [], pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.bound_ = Polygon( points )
		self.__isMouseHit = False								# 鼠标是否在按钮上


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLastMouseEvent_( self, dx, dy, dz ) :
		"""
		鼠标在按钮上并移动时调用
		"""
		outHit = Button.isMouseHit( self )
		inHit = self.bound_.isPointIn( self.mousePos )
		isMouseHit = outHit and inHit
		if not isMouseHit and self.__isMouseHit :				# 鼠标刚好不在按钮有效区域内
			self.__isMouseHit = False
			self.onMouseLeave_()
		elif isMouseHit and not self.__isMouseHit :				# 按钮刚好进入有效区域内
			self.__isMouseHit = True
			self.onMouseEnter_()
		if not outHit :											# 如果鼠标不在整个按钮上
			LastMouseEvent.detach( self.onLastMouseEvent_ )		# 则，取消鼠标移动事件


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleMouseEnterEvent( self, comp, pos ) :
		"""
		当鼠标进入时被调用
		"""
		LastMouseEvent.attach( self.onLastMouseEvent_ )		# 添加鼠标移动事件，以侦测鼠标的位置
		return False

	def handleMouseLeaveEvent( self, comp, pos ) :
		"""
		当鼠标离开时被调用
		"""
		return True

	# -------------------------------------------------
	def updateVertexes( self, points ) :
		"""
		更新按钮顶点
		"""
		self.bound_.update( points )


	# -------------------------------------------------
	# rewrite method
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		重写isMouseHit方法，判断鼠标是否落在多边形内
		"""
		return Button.isMouseHit( self ) and self.bound_.isPointIn( self.mousePos )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	vertexes = property( lambda self : self.bound_.points )							# 获取所有顶点

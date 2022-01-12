# -*- coding: gb18030 -*-

# by gjx 2010-09-20
# 由于未找到更好的办法，暂时取巧使用设置crossFocus的方式
# 达到无效区域不影响被覆盖的控件的鼠标消息的接收的目的

from guis import scale_util
from guis.controls.PolygonButton import PolygonButton


class NavigationButton( PolygonButton ) :

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleMouseEnterEvent( self, comp, pos ) :
		self.crossFocus = False
		return PolygonButton.handleMouseEnterEvent( self, comp, pos )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLastMouseEvent_( self, dx, dy, dz ) :
		PolygonButton.onLastMouseEvent_( self, dx, dy, dz )
		if not scale_util.isMouseHit( self.gui ) :
			self.crossFocus = True
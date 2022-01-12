# -*- coding: gb18030 -*-

# by gjx 2010-09-20
# ����δ�ҵ����õİ취����ʱȡ��ʹ������crossFocus�ķ�ʽ
# �ﵽ��Ч����Ӱ�챻���ǵĿؼ��������Ϣ�Ľ��յ�Ŀ��

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
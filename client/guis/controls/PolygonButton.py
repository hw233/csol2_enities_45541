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
	ʵ�ֲ�����Ķ���ΰ�ť
	"""
	def __init__( self, button, points = [], pyBinder = None ) :
		Button.__init__( self, button, pyBinder )
		self.bound_ = Polygon( points )
		self.__isMouseHit = False								# ����Ƿ��ڰ�ť��


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLastMouseEvent_( self, dx, dy, dz ) :
		"""
		����ڰ�ť�ϲ��ƶ�ʱ����
		"""
		outHit = Button.isMouseHit( self )
		inHit = self.bound_.isPointIn( self.mousePos )
		isMouseHit = outHit and inHit
		if not isMouseHit and self.__isMouseHit :				# ���պò��ڰ�ť��Ч������
			self.__isMouseHit = False
			self.onMouseLeave_()
		elif isMouseHit and not self.__isMouseHit :				# ��ť�պý�����Ч������
			self.__isMouseHit = True
			self.onMouseEnter_()
		if not outHit :											# �����겻��������ť��
			LastMouseEvent.detach( self.onLastMouseEvent_ )		# ��ȡ������ƶ��¼�


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def handleMouseEnterEvent( self, comp, pos ) :
		"""
		��������ʱ������
		"""
		LastMouseEvent.attach( self.onLastMouseEvent_ )		# �������ƶ��¼������������λ��
		return False

	def handleMouseLeaveEvent( self, comp, pos ) :
		"""
		������뿪ʱ������
		"""
		return True

	# -------------------------------------------------
	def updateVertexes( self, points ) :
		"""
		���°�ť����
		"""
		self.bound_.update( points )


	# -------------------------------------------------
	# rewrite method
	# -------------------------------------------------
	def isMouseHit( self ) :
		"""
		��дisMouseHit�������ж�����Ƿ����ڶ������
		"""
		return Button.isMouseHit( self ) and self.bound_.isPointIn( self.mousePos )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	vertexes = property( lambda self : self.bound_.points )							# ��ȡ���ж���

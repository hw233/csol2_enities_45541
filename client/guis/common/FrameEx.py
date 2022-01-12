# -*- coding: gb18030 -*-
#
# $Id: Frame.py,v 1.8 2008-06-21 01:51:28 huangyongwei Exp $

"""
��Է������ṩ�� TextureFrame ��������Ŀ������������
ע�⣺Ŀǰֻ֧�� widthRelative = False �� heightRelative = False
2009/10/19: writen by huangyongwei
"""

from guis import *
from GUIBaseObject import GUIBaseObject

# --------------------------------------------------------------------
# ����ˮƽ����� Frame
# --------------------------------------------------------------------
"""
GUI.TextureFrame :
	frm_l( GUI.Texture )	frm_bg( GUI.Texture)	frm_r( GUI.Texture )
"""
class HFrameEx( GUIBaseObject ) :
	def __init__( self, f ) :
		GUIBaseObject.__init__( self, f )
		elements = f.elements
		l = elements["frm_l"]
		r = elements["frm_r"]
		bg = elements["frm_bg"]
		self.minWidth_ = l.size.x + r.size.x
		self.__rRightSpace = f.width - r.position.x		# �ұ����������ұߵľ���
		self.__bgInFrameSpace = f.width - bg.size.x		# ������ȿ��С����


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		width = max( self.minWidth_, width )
		GUIBaseObject._setWidth( self, width )
		elements = self.getGui().elements
		r = elements["frm_r"]
		bg = elements["frm_bg"]
		r.position.x = width - self.__rRightSpace
		bg.size.x = width - self.__bgInFrameSpace

	def _setRWidth( self, width ) :
		pwidth = s_util.toFElemPXMeasure( width, self.getGui() )
		self._setWidth( pwidth )

	def _setSize( self, size ) :
		self._setWidth( size[0] )

	def _setRSize( self, size ) :
		self._setRWidth( size[0] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	minWidth = property( lambda self : self.minWidth_ )

	width = property( GUIBaseObject._getWidth, _setWidth )
	height = property( GUIBaseObject._getHeight )
	r_width = property( GUIBaseObject._getRWidth, _setRWidth )
	r_height = property( GUIBaseObject._getRHeight )
	size = property( GUIBaseObject._getSize, _setSize )
	r_size = property( GUIBaseObject._getRSize, _setRSize )


# --------------------------------------------------------------------
# ���Դ�ֱ����� Frame
# --------------------------------------------------------------------
"""
GUI.TextureFrame :
	frm_t( GUI.Texture )
	frm_b( GUI.Texture )
	frm_bg( GUI.Texture )
"""

class VFrameEx( GUIBaseObject ) :
	def __init__( self, f ) :
		GUIBaseObject.__init__( self, f )
		elements = f.elements
		t = elements["frm_t"]
		b = elements["frm_b"]
		bg = elements["frm_bg"]
		self.minHeight_ = t.size.y + b.size.y				# ��С�߶�
		self.__bBottomSpace = f.height - b.position.y		# �ױ��������ܵײ��ľ���
		self.__bgInFrameSpace = f.height - bg.size.y		# �������ܵײ��ľ���


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setHeight( self, height ) :
		height = max( self.minHeight_, height )
		GUIBaseObject._setHeight( self, height )
		elements = self.getGui().elements
		b = elements["frm_b"]
		bg = elements["frm_bg"]
		b.position.y = height - self.__bBottomSpace
		bg.size.y = height - self.__bgInFrameSpace

	def _setRHeight( self, height ) :
		pheight = s_util.toFElemPYMeasure( height )
		self._setHeight( pheight )

	def _setSize( self, size ) :
		self._setHeight( size[1] )

	def _setRSize( self, size ) :
		self._setRHeight( size[1] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	minHeight = property( lambda self : self.minHeight_ )

	width = property( GUIBaseObject._getWidth )
	height = property( GUIBaseObject._getHeight, _setHeight )
	r_width = property( GUIBaseObject._getRWidth )
	r_height = property( GUIBaseObject._getRHeight, _setRHeight )
	size = property( GUIBaseObject._getSize, _setSize )
	r_size = property( GUIBaseObject._getRSize, _setRSize )



# --------------------------------------------------------------------
# ����ˮƽ�ʹ�ֱͬʱ����� Frame
# --------------------------------------------------------------------
"""
GUI.TextureFrame :
	frm_lr( GUI.Texture )		frm_t( GUI.Texture )		frm_rt( GUI.Texture )
	frm_l( GUI.Texture )		frm_bg( GUI.Texture )		frm_r( GUI.Texture )
	frm_lb( GUI.Texture )		frm_b( GUI.Texture )		frm_rb( GUI.Texture )

"""

class HVFrameEx( GUIBaseObject ) :
	def __init__( self, f ) :
		GUIBaseObject.__init__( self, f )
		elements = f.elements
		lt = elements["frm_lt"]
		rt = elements["frm_rt"]
		lb = elements["frm_lb"]
		rb = elements["frm_rb"]

		l = elements["frm_l"]
		r = elements["frm_r"]
		t = elements["frm_t"]
		b = elements["frm_b"]
		bg = elements["frm_bg"]
		minWidth = lt.size.x + rt.size.x
		minWidth = min( minWidth, lb.size.x + rb.size.x )
		self.minWidth_ = minWidth							# ��С���
		minHeight = lt.size.y + lb.size.y
		minHeight = min( minHeight, rt.size.y + rb.size.y )
		self.minHeight_ = minHeight							# ��С�߶�

		self.__rtRightSpace = f.width - rt.position.x		# ���Ͻ������ұߵľ���
		self.__lbBottomSpace = f.height - lb.position.y		# ���½����ܵױߵľ���
		self.__rbRightSpace = f.width - rb.position.x		# ���½������ұߵľ���
		self.__rbBottomSpace = f.height - rb.position.y		# ���½����ܵײ��ľ���

		self.__lInFrameSpace = f.height - l.size.y			# ��ܸ߶�����߸߶Ȳ�
		self.__rInFrameSpace = f.height - r.size.y			# ��ܸ߶����ұ߸߶Ȳ�
		self.__tInFrameSpace = f.width - t.size.x			# ��ܿ���붥�߿�Ȳ�
		self.__bInFrameSpace = f.width - b.size.x			# ��ܿ����ױ߿�Ȳ�

		self.__rRightSpace = f.width - r.position.x			# �ұߵ��������Ҳ��ľ���
		self.__bBottomSpace = f.height - b.position.y		# �ұ����������ұߵľ���

		self.__bgInFrameHSpace = f.width - bg.size.x		# �������ƿ�Ȳ�
		self.__bgInFrameVSpace = f.height - bg.size.y		# �������Ƹ߶Ȳ�


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		width = max( self.minWidth_, width )
		GUIBaseObject._setWidth( self, width )
		elements = self.getGui().elements
		rt = elements["frm_rt"]
		rb = elements["frm_rb"]

		r = elements["frm_r"]
		t = elements["frm_t"]
		b = elements["frm_b"]
		bg = elements["frm_bg"]

		rt.position.x = width - self.__rtRightSpace
		rb.position.x = width - self.__rbRightSpace
		r.position.x = width - self.__rRightSpace

		t.size.x = width - self.__tInFrameSpace
		b.size.x = width - self.__bInFrameSpace
		bg.size.x = width - self.__bgInFrameHSpace

	def _setRWidth( self, width ) :
		pwidth = s_util.toFElemPXMeasure( width, self.getGui() )
		self._setWidth( pwidth )

	# ---------------------------------------
	def _setHeight( self, height ) :
		height = max( self.minHeight_, height )
		GUIBaseObject._setHeight( self, height )
		elements = self.getGui().elements
		lb = elements["frm_lb"]
		rb = elements["frm_rb"]

		l = elements["frm_l"]
		r = elements["frm_r"]
		b = elements["frm_b"]
		bg = elements["frm_bg"]

		lb.position.y = height - self.__lbBottomSpace
		rb.position.y = height - self.__rbBottomSpace
		b.position.y = height - self.__bBottomSpace

		l.size.y = height - self.__lInFrameSpace
		r.size.y = height - self.__rInFrameSpace
		bg.size.y = height - self.__bgInFrameVSpace

	def _setRHeight( self, height ) :
		pheight = s_util.toFElemPYMeasure( height )
		self._setHeight( pheight )

	# ---------------------------------------
	def _setSize( self, size ) :
		self._setWidth( size[0] )
		self._setHeight( size[1] )

	def _setRSize( self, size ) :
		self._setRWidth( size[0] )
		self._setRHeight( size[1] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	minWidth = property( lambda self : self.minWidth_ )
	minHeight = property( lambda self : self.minHeight_ )

	width = property( GUIBaseObject._getWidth, _setWidth )
	height = property( GUIBaseObject._getHeight, _setHeight )
	r_width = property( GUIBaseObject._getRWidth, _setRWidth )
	r_height = property( GUIBaseObject._getRHeight, _setRHeight )
	size = property( GUIBaseObject._getSize, _setSize )
	r_size = property( GUIBaseObject._getRSize, _setRSize )


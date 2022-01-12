# -*- coding: gb18030 -*-
#
# $Id: TipWindow.py,v 1.3 2008-08-26 02:21:39 huangyongwei Exp $

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HVFrame
from guis.tooluis.CSRichText import CSRichText

class BubbleTip( HVFrame ) :

	cc_fade_speed_			= 0.5		# ������ʱ
	cc_edge_width_			= 10.0		# ��������صľ���
#	__cc_max_width = 160.0				#�����
	__cc_min_width = 65.0				# ��С���

	texture_path = "guis/otheruis/floatnames/bubble/%s_%d.tga"

	def __init__( self ) :
		bubble = GUI.load( "guis/otheruis/floatnames/bubble/bubbletip.gui" )
		uiFixer.firstLoadFix( bubble )
		HVFrame.__init__( self, bubble )
		self.focus = False
		self.moveFocus = False
		self.style = 0

		self.pyBL_ = PyGUI( bubble.bl )
		self.pyBR_ = PyGUI( bubble.br )
		self.pyPointer_ = PyGUI( bubble.pointer )

		self.__pointerSitScale = float( self.pyPointer_.left )/ self.width #��ͷ�봰�ڿ�ȱ���

		self.__fader = bubble.fader
		self.__fader.value = 0.0
		self.__fader.speed = self.cc_fade_speed_

		self.pyRtMsg_ = CSRichText( bubble.rtMsg )
		self.pyRtMsg_.maxWidth = 180.0
		self.pyRtMsg_.align = "L"
		self.pyRtMsg_.left = self.cc_edge_width_
		self.pyRtMsg_.top = self.cc_edge_width_

		self.__fadeDelayCBID = 0						# ������ʱ�ص� ID
		self.__vsDetectCBID = 0							# �����󶨿ؼ��ɼ����ص� ID

	def __del__( self ) :
		if Debug.output_del_BubbleTip :
			INFO_MSG( str( self ) )

	def dispose( self ):
		self.pyBL_.dispose()
		self.pyBR_.dispose()
		self.pyRtMsg_.dispose()
		HVFrame.dispose( self )

	def __layout( self ) :
		"""
		���ô�����Ӧ�ı���С
		"""
		self.width = self.pyRtMsg_.right + self.cc_edge_width_ + 0.6 #��0.6������ȥ��������ߵĺ����ģ���ʱֻ��������
		self.height = self.pyRtMsg_.bottom + self.cc_edge_width_

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, msg, style, opGBLink ) :
		BigWorld.cancelCallback( self.__fadeDelayCBID )
		type = int( style )
		if self.style != type:
			self.style = type
			for name, child in self.getGui().children:
				if name in ["b", "rtMsg"]:continue
				child.textureName = self.texture_path%( name, self.style )
		self.__fader.value = 1.0
		# ������������ת���ַ�
		if opGBLink:
			self.pyRtMsg_.opGBLink = True
		self.pyRtMsg_.text = msg
		if len( msg ) <= 5: #�����Ϣ����С��5�ֽ�,�;�����ʾ��Ҫ�ŵ�text��ֵ�ĺ������Ч��
			self.pyRtMsg_.center = self.__cc_min_width / 2.0
		self.visible = True
		self.__layout()

	def hide( self ) :
		BigWorld.cancelCallback( self.__fadeDelayCBID )
#		BigWorld.cancelCallback( self.__vsDetectCBID )
		self.__fader.value = 0.0
		def delayHide() :
			self.clear()
		self.__fadeDelayCBID = BigWorld.callback( self.__fader.speed, delayHide )

	def clear( self ) :
		"""
		��������ı�
		"""
		self.visible = False

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _setWidth( self, width ) :
		width = max( self.__cc_min_width, width )
		HVFrame._setWidth( self, width )
		self.pyPointer_.left = max( self.pyLB_.right, width*self.__pointerSitScale )
		self.pyBL_.width = self.pyPointer_.left - self.pyLT_.right
		self.pyBR_.width = self.pyRB_.left - self.pyPointer_.right
		self.pyBR_.right = self.pyRB_.left
		size = self.pyR_.getGui().size
		self.pyR_.mapping = util.getGuiMapping( size, 0.0, 16.0, 0.0, 8.0 )

	def _setHeight( self, height ) :
		HVFrame._setHeight( self, height )
		top = self.pyB_.top
		self.pyBL_.top = top
		self.pyPointer_.top = top
		self.pyBR_.top = top
		size = self.pyBL_.getGui().size
		self.pyBL_.mapping = util.getGuiMapping( size, 0.0, 8.0, 0, 16 )

	def _getCenter( self ):
		offset = self.width*( 0.5 - self.__pointerSitScale )
		center = HVFrame._getCenter( self )
		return center - offset

	def _setCenter( self, center ):
		offset = self.width*( 0.5 - self.__pointerSitScale )
		HVFrame._setCenter( self, center + offset )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	width = property( HVFrame._getWidth, _setWidth )
	height = property( HVFrame._getHeight, _setHeight )
	center = property( _getCenter, _setCenter )

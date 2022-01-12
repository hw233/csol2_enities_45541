# -*- coding: gb18030 -*-
#
# $Id: TrackBar.py,v 1.14 2008-08-21 09:07:12 huangyongwei Exp $

"""
implement color board class
"""

from AbstractTemplates import Singleton
from LabelGather import labelGather
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TrackBar import HTrackBar
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText

class ColorBoard( Singleton, Window ) :
	def __init__( self ) :
		Singleton.__init__( self )
		wnd = GUI.load( "guis/tooluis/colorboard/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr()
		self.__initialzie( wnd )

		self.cbChanging_ = None				# ��ɫ�ı�����еĻص�
		self.__chcbid = 0
		self.cbResult_ = None				# ���ȷ����ȡ����ťʱ�Ļص�

	def __del__( self ) :
		if Debug.output_del_ColorBoard :
			INFO_MSG( str( self ) )

	# -------------------------------------------------
	def __initialzie( self, wnd ) :
		self.pyNewView_ = PyGUI( wnd.newView)
		self.pyCurView_ = Control( wnd.curView )
		self.pyCurView_.focus = True
		self.pyCurView_.onLClick.bind( self.onCurrDspClick_ )

		self.pyRBar_ = ColorBar( wnd.tbarT, self )					# ����
		self.pyGBar_ = ColorBar( wnd.tbarS, self )					# ����
		self.pyBBar_ = ColorBar( wnd.tbarL, self )					# ����
		self.pyABar_ = ColorBar( wnd.tbarA, self )					# ͸����

		self.pyBtnOk_ = HButtonEx( wnd.btnOk )							# ȷ����ť
		self.pyBtnOk_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnOk_.onLClick.bind( self.onOkClick_ )
		self.pyBtnCancel_ = HButtonEx( wnd.btnCancel )					# ȡ����ť
		self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.onCancelClick_ )

		self.pyStTone=StaticText(wnd.tText)
		self.pyStSature_=StaticText(wnd.sText)
		self.pyStLight_=StaticText(wnd.lText)
		self.pyStApha_=StaticText(wnd.aText)

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "ColorBoard:main", "title" )
		labelGather.setPyBgLabel( self.pyBtnOk_, "ColorBoard:main", "btnOk" )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "ColorBoard:main", "btnCancel" )
		labelGather.setPyLabel( self.pyStTone, "ColorBoard:main", "tText" )
		labelGather.setPyLabel( self.pyStSature_, "ColorBoard:main", "sText" )
		labelGather.setPyLabel( self.pyStLight_, "ColorBoard:main", "lText" )
		labelGather.setPyLabel( self.pyStApha_, "ColorBoard:main", "aText" )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self, res ) :
		"""
		�ص� callback
		"""
		color = self.pyCurView_.color
		if res == DialogResult.OK :
			color = self.pyNewView_.color
		if not self.pyABar_.enable :
			color = color[:-1]
		self.cbResult_( res, color )
		self.cbChanging_ = None
		self.cbResult_ = None

	# -------------------------------------------------
	def onCurrDspClick_( self, pyDsp ) :
		"""
		�����ǰ��ɫ��ʾ���棬�򽫽�Ҫ���õ���ɫ����Ϊ��ǰ��ɫ
		"""
		r, g, b, a = color = pyDsp.color
		self.pyNewView_.color = color
		self.pyRBar_.value = r
		self.pyGBar_.value = g
		self.pyBBar_.value = b
		if self.pyABar_.enable :
			self.pyABar_.value = a

	# ---------------------------------------
	def onOkClick_( self ) :
		"""
		���ȷ����ťʱ������
		"""
		self.notify_( DialogResult.OK )
		self.hide()

	def onCancelClick_( self ) :
		"""
		���ȡ����ťʱ������
		"""
		self.notify_( DialogResult.CANCEL )
		self.hide()

	# -------------------------------------------------
	def onColorBarValueChanged_( self, pyColorBar ) :
		"""
		��ɫ���ı�ʱ������
		"""
		r = self.pyRBar_.value
		g = self.pyGBar_.value
		b = self.pyBBar_.value
		a = self.pyABar_.value
		if self.pyABar_.enable :
			color = r, g, b, a
			self.pyNewView_.color = r, g, b, a
		else :
			color = r, g, b
			self.pyNewView_.color = r, g, b,
		if self.cbChanging_ :
			BigWorld.cancelCallback( self.__chcbid )
			func = Functor( self.cbChanging_, color )
			self.__chcbid = BigWorld.callback( 0.3, func )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyOwner, currColor, cbResult, cbChanging = None, pos = None ) :
		"""
		@type			pyOwner	   : GUIBaseObject
		@param			pyOwner	   : �����ĸ�����
		@type			currColor  : Color/tuple
		@param			currColor  : ��ǰ��ɫֵ��ע�⣺�������Χ��ɫ���� alpha ���ɵ��ڣ�
		@type			cbResult   : callable object
		@param			cbResult   : ���ȷ����ȡ����ťʱ�Ļص�����������������
									 �� DialogResult��ָ������ˡ�ȷ�������ǡ�ȡ������ť����
									 �� ���ú����ɫ
		@type			cbChanging : callable object
		@param			cbChanging : ��ɫ�ı�����еĻص�������һ����������ǰ���õ���ɫֵ
		@type			pos		   : Vector2
		@param			pos		   : ��ʾλ��
		"""
		if self.cbResult_ :									# û�رյ�ǰ���¾�ֱ�����¿���
			self.notify_( DialogResult.CANCEL )

		color = currColor
		if ( len( color ) == 4 ) :							# �� alpha ֵ
			self.pyABar_.enable = True
		else :												# û�� alpha ֵ
			r, g, b = currColor
			color = r, g, b, 255
			self.pyABar_.enable = False
		r, g, b, a = color
		self.pyCurView_.color = color
		self.pyNewView_.color = color
		self.pyRBar_.value = r
		self.pyGBar_.value = g
		self.pyBBar_.value = b
		self.pyABar_.value = a
		self.cbChanging_ = cbChanging
		self.cbResult_ = cbResult

		if pos :
			self.pos = pos
		else :
			scSize = BigWorld.screenSize()
			self.center = scSize[0] / 2
			self.middle = scSize[1] / 2 - 20
		Window.show( self, pyOwner )

	def hide( self ) :
		Window.hide( self )
		self.dispose()


# --------------------------------------------------------------------
# implement color bar
# --------------------------------------------------------------------
class ColorBar( Control ) :
	def __init__( self, bar, pyBinder ) :
		Control.__init__( self, bar, pyBinder )
		self.pyTBar_ = HTrackBar( bar.bar )
		self.pyTBar_.stepCount = 255
		self.pyTBar_.onSlide.bind( self.onSliderSlided_ )

		self.pyTBInput_ = TextBox( bar.tbInput.box )
		self.pyTBInput_.font = "stroke_tiny.font"
		self.pyTBInput_.inputMode = InputMode.NATURALNUM
		self.pyTBInput_.maxLength = 3
		self.pyTBInput_.onTextChanged.bind( self.onInputTextChanged_ )
		self.pyTBInput_.onTabOut.bind( self.__onInputTabOut )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInputTabOut( self, pyBox ) :
		"""
		���㳷�������ʱ������
		"""
		if pyBox.text == "" :
			pyBox.text = "0"


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onSliderSlided_( self, pySlider, value ) :
		"""
		��������ʱ������
		"""
		self.pyTBInput_.onTextChanged.shield()
		self.pyTBInput_.text = str( int( value * 255 ) )
		self.pyTBInput_.onTextChanged.unshield()
		self.pyBinder.onColorBarValueChanged_( self )

	def onInputTextChanged_( self, pyBox ) :
		"""
		�ı��ı�ʱ������
		"""
		text = pyBox.text
		value = 0
		if text.strip() != "" :
			value = min( 255, int( text ) )
		self.pyTBar_.onSlide.shield()
		self.pyTBar_.value = float( value ) / 255
		self.pyTBar_.onSlide.unshield()
		self.pyBinder.onColorBarValueChanged_( self )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getValue( self ) :
		if self.pyTBInput_.text == "" :
			return 0
		return int( self.pyTBInput_.text )

	def _setValue( self, value ) :
		value = max( 0, min( 255, int( value ) ) )
		self.pyTBInput_.text = str( value )
		self.pyBinder.onColorBarValueChanged_( self )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	value = property( _getValue, _setValue )

# -*- coding: gb18030 -*-
#
#$Id: ColorSetter.py,v 1.3 2008-08-19 09:27:21 huangyongwei Exp $
#

"""
implement color setter for channels

2009/09/01: writen by huangyongwei
"""

from AbstractTemplates import Singleton
from ChatFacade import chatFacade
from LabelGather import labelGather
from guis import *
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.colorboard.ColorBoard import ColorBoard

class ColorSetter( Singleton, Window ) :
	def __init__( self ) :
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/chatwindow/channelcolorsetter/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr()
		self.__initialize( wnd )
		self.__pyItems = {}						# ��������Ƶ��
		self.__initItems()
		self.__pressedOk = False 				# �Ƿ����� ok ��ť
		self.cbChanging_ = None					# Ƶ����ɫ�ı�����лص�
		self.cbResult_ = None					# Ƶ����ɫ�ı��ص�

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_ChatColorSetter :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()			# �ͷ�ʵ�����´���ʾʱ�ٴ���

	def __initialize( self, wnd ) :
		self.pyIPChannels_ = ItemsPanel( wnd.ipChannels.clipPanel, wnd.ipChannels.sbar )
		self.pyIPChannels_.viewCols = 2

		self.pyBtnOk_ = HButtonEx( wnd.btnOk )
		self.pyBtnOk_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnOk_.onLClick.bind( self.onOkClick_ )
		self.pyBtnCancel_ = HButtonEx( wnd.btnCancel )
		self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.onCancelClick_ )

		# ---------------------------------------------
		# �����ı���ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.pyLbTitle_, "ChatWindow:ColorSetter", "title" )
		labelGather.setPyBgLabel( self.pyBtnOk_, "ChatWindow:ColorSetter", "btnOk" )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "ChatWindow:ColorSetter", "btnCancel" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initItems( self ) :
		"""
		��ʼ������Ƶ��ѡ��
		"""
		for channel in chatFacade.setableChannels :
			pyItem = ChannelItem( channel, self )
			self.pyIPChannels_.addItem( pyItem )
			self.__pyItems[channel.id] = pyItem

	# -------------------------------------------------
	def notify_( self, res ) :
		chcolors = {}
		if res == DialogResult.OK :
			for pyItem in self.pyIPChannels_.pyItems :		# �ҳ����б��޸��˵�Ƶ��
				if pyItem.modifiered :
					channel = pyItem.channel
					color = pyItem.chColor
					channel.resetColor( color )
					chcolors[channel.id] = color
		else :
			for pyItem in self.pyIPChannels_.pyItems :		# �ҳ�����Ҫȡ���޸ĵ�Ƶ��
				if pyItem.modifiered :
					channel = pyItem.channel
					pyItem.reset()
					chcolors[channel.id] = channel.color
		self.cbResult_( res, chcolors )						# �ص����
		self.cbChanging_ = None
		self.cbResult_ = None


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onOkClick_( self ) :
		"""
		���ȷ����ťʱ������
		"""
		self.__pressedOk = True
		self.hide()

	def onCancelClick_( self ) :
		"""
		���ȡ����ťʱ������
		"""
		self.__pressedOk = False
		self.hide()

	# -------------------------------------------------
	def onChanelColorChanged_( self, pyItem, color ) :
		"""
		ĳ��Ƶ����ɫ�ı�ʱ������
		"""
		if self.cbChanging_ :
			self.cbChanging_( pyItem.channel.id, color )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyOwner, cbResult, cbChanging = None ) :
		"""
		@type				pyOwner	   : GUIBaseObject
		@param				pyOwner	   : ����������
		@type				cbResult   : callable object
		@param				cbResult   : ����ص������������������� DialogResult����{ Ƶ��ID : Ƶ����ɫ }
		@type				cbChanging : callable object
		@param				cbChanging : ��ɫ���������еĻص������������������� Ƶ��ID���� Ƶ����ɫ
		"""
		self.cbResult_ = cbResult
		self.cbChanging_ = cbChanging
		Window.show( self, pyOwner )

	def hide( self ) :
		Window.hide( self )
		if self.__pressedOk :
			self.notify_( DialogResult.OK )
		else :
			self.notify_( DialogResult.CANCEL )
		self.__pressedOk = False
		self.dispose()

	# -------------------------------------------------
	def getChannelColor( self, chid ) :
		"""
		��ȡƵ����ɫ
		"""
		return self.__pyItems[chid].chColor


# --------------------------------------------------------------------
# Ƶ��ѡ��
# --------------------------------------------------------------------
class ChannelItem( Control ) :
	def __init__( self, channel, pyBinder ) :
		item = GUI.load( "guis/general/chatwindow/channelcolorsetter/chitem.gui" )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.pyDsp_ = Control( item.dsp )
		self.pyDsp_.focus = True
		self.pyDsp_.crossFocus = True
		self.pyDsp_.onMouseEnter.bind( self.__onDspMouseEnter )
		self.pyDsp_.onMouseLeave.bind( self.__onDspMouseLeave )
		self.pyDsp_.onLClick.bind( self.__onDspClick )
		self.pyCHName_ = StaticText( item.stChannel )
		self.pyCHName_.text = channel.name

		self.channel_ = channel						# ��Ӧ��Ƶ��
		self.chColor = channel.color				# ����Ƶ����ɫ����ѡ����ɫ
		self.__modifiered = False					# �Ƿ��Ѿ��޸�


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onDspMouseEnter( self ) :
		"""
		��������ɫ��ʾ��ťʱ������
		"""
		rds.ccursor.set( "hand" )

	def __onDspMouseLeave( self ) :
		"""
		����뿪��ɫ��ʾ��ťʱ������
		"""
		rds.ccursor.normal()

	def __onDspClick( self ) :
		"""
		�������ɫ��ʾ��ťʱ������
		"""
		rds.ccursor.normal()

		def cbChanging( color ) :
			"""
			��ɫ�ı�����б�����
			"""
			self.chColor = color
			self.pyBinder.onChanelColorChanged_( self, color )

		def cbResult( res, color ) :
			"""
			ȷ��/ȡ����ɫʱ������
			"""
			if res == DialogResult.OK :
				self.__modifiered = True
			else :
				self.__modifiered = False

		colorBoard = ColorBoard()
		cbHeight = colorBoard.height
		left = self.rightToScreen
		top = self.middleToScreen - cbHeight * 0.5
		colorBoard.show( self, self.channel_.color, cbResult, cbChanging, ( left, top ) )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def reset( self ) :
		"""
		�ָ�Ƶ����ɫ
		"""
		self.__modifiered = False
		self.chColor = self.channel_.color


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCHName( self ) :
		return self.pyCHName_.text

	def _setCHName( self, name ) :
		self.pyCHName_.text = name

	# -------------------------------------------------
	def _getCHColor( self ) :
		return self.pyDsp_.color[:-1]

	def _setCHColor( self, color ) :
		color = tuple( color )
		self.pyDsp_.color = color
		self.pyCHName_.color = color


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	channel = property( lambda self : self.channel_ )					# ��Ӧ��Ƶ��
	chName = property( _getCHName, _setCHName )							# Ƶ������
	chColor = property( _getCHColor, _setCHColor )						# Ƶ����ɫ
	modifiered = property( lambda self : self.__modifiered )			# �Ƿ��Ѿ��޸�

# -*- coding: gb18030 -*-
#
# $Id: ChannelFilter.py,v 1.10 2008-08-30 09:05:30 huangyongwei Exp $

"""
implement ChannelFilter for message page

2009/08/29: writen by huangyongwei
"""

from ChatFacade import chatFacade
from AbstractTemplates import Singleton
from LabelGather import labelGather
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText

class ChannelFilter( Singleton, Window ) :
	__cc_cols				= 3					# ѡ������
	__cc_row_space			= 4					# �о�
	__cc_col_space			= 20					# �о�

	def __init__( self ) :
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/chatwindow/channelfilter/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr()
		self.__initialize( wnd )
		self.__initCHItems()

		self.__ok = False
		self.__callback = None

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_ChatChanneFilter :
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__callback = None
		self.__class__.releaseInst()

	def __initialize( self, wnd ) :
		self.__pySTTips = StaticText( wnd.stTips )					# ����
		self.pyPanel_ = ItemsPanel( wnd.ipChannels.clipPanel, wnd.ipChannels.sbar )		# Ƶ��ѡ�����
		self.pyPanel_.viewCols = self.__cc_cols
		self.pyPanel_.rowSpace = self.__cc_row_space
		self.pyPanel_.colSpace = self.__cc_col_space
		self.pyBtnOk_ = HButtonEx( wnd.btnOk )							# ȷ����ť
		self.pyBtnOk_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnOk_.onLClick.bind( self.__onOK )
		self.pyBtnCancel_ = HButtonEx( wnd.btnCancel )					# ȡ����ť
		self.pyBtnCancel_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.__onCancel )

		# ---------------------------------------------
		# �����ı���ǩ
		# ---------------------------------------------
		self.__tips = labelGather.getText( "ChatWindow:ChannelFilter", "tips" )
		labelGather.setPyLabel( self.pyLbTitle_, "ChatWindow:ChannelFilter", "title" )
		labelGather.setPyLabel( self.__pySTTips, "ChatWindow:ChannelFilter", "tips" )
		labelGather.setPyBgLabel( self.pyBtnOk_, "ChatWindow:ChannelFilter", "btnOk" )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "ChatWindow:ChannelFilter", "btnCancel" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initCHItems( self ) :
		"""
		��ʼ������Ƶ������ѡ��
		"""
		channels = chatFacade.setableChannels
		item = GUI.load( "guis/general/chatwindow/channelfilter/chitem.gui" )
		uiFixer.firstLoadFix( item )
		for index, channel in enumerate( channels ) :
			item = util.copyGuiTree( item )
			pyItem = CheckBoxEx( item )
			pyItem.chid = channel.id
			pyItem.text = channel.name
			self.pyPanel_.addItem( pyItem )

	# -------------------------------------------------
	def __onOK( self ) :
		self.__ok = True
		self.hide()

	def __onCancel( self ) :
		self.__ok = False
		self.hide()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onClose_( self ) :
		checkedChannels = set( [pyItem.chid for pyItem in self.pyPanel_.pyItems if pyItem.checked ] )
		if self.__ok :
			self.__callback( True, checkedChannels )
		else :
			self.__callback( False, checkedChannels )
		self.__callback = None
		self.__ok = False
		return True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, chName, checkedChannels, callback, pyOwner = None ) :
		"""
		��ʾƵ��ѡ�����
		@type			checkedChannels : set
		@param			checkedChannels : ��ǰѡ�е�Ƶ��
		@type			callback		: callable object
		@param			callback		: �ɵ��÷���/����
										  �ص������������������
										  	��һ������Ϊ bool����ʾ���淵��ȷ������ȡ��
										  	�ڶ�������Ϊ set����ʾƵ��ѡ�������ѡ������ЩƵ��
		@type			pyOwner			: PyObject
		@param			pyOwner			: �����ĸ�����
		"""
		if self.__callback :
			self.__ok = False
		self.__pySTTips.text = self.__tips % chName
		self.__callback = callback
		for pyItem in self.pyPanel_.pyItems :
			pyItem.checked = ( pyItem.chid in checkedChannels )
		Window.show( self, pyOwner )

	def hide( self ) :
		Window.hide( self )
		self.dispose()

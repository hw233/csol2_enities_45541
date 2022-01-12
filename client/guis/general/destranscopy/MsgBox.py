# -*- coding: gb18030 -*-

"""
implement animation dice class

"""
from guis import *
import Font
import BigWorld
from guis.common.RootGUI import RootGUI
from guis.common.FrameEx import HFrameEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText

class MsgBox( RootGUI, HFrameEx ):
	"""
	��Ϣ��
	"""
	def __init__( self ) :
		box = GUI.load( "guis/general/destranscopy/msgbox.gui" )
		uiFixer.firstLoadFix( box )
		RootGUI.__init__( self, box )
		HFrameEx.__init__( self, box )
		self.posZSegment = ZSegs.L1
		self.h_dockStyle = "CENTER"							# ˮƽ������ʾ
		self.v_dockStyle = "TOP"							# ��ֱ������ʾ
		self.escHide_ = False
		self.__pyRtMsg = CSRichText( box.rtMsg )
		self.__pyRtMsg.text = ""
		self.__pyRtMsg.align = "C"				# ��ǰ���ı���ˮƽͣ����ʽ
		self.__pyRtMsg.lineFlat = "M"
		self.__pyRtMsg.font = "STXINWEI.TTF"
		self.__pyRtMsg.limning = Font.LIMN_OUT
		self.__pyRtMsg.foreColor = 250, 218, 181
		self.__pyRtMsg.fontSize = 40
		
		self.__fader = box.fader
		self.__fader.speed = 0.5
		self.__fader.value = 0.0
		
		self.__fadecbid = 0
		self.addToMgr( "destMsgBox" )
	
	def showMsg( self, msg, color = (250, 218, 181), delay = 3.0  ):
		self.__pyRtMsg.text = msg
		self.__pyRtMsg.foreColor = color
		self.__fader.value = 1.0
		self.__fader.reset()
		self.__fadecbid = BigWorld.callback( delay, self.__delayHide )
		self.show()
	
	def __delayHide( self ):
		self.__fader.value = 0
		BigWorld.cancelCallback( self.__fadecbid )
		self.hide()
	
	def show( self ):
		RootGUI.show( self )
	
	def hide( self ):
		RootGUI.hide( self )
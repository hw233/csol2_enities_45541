# -*- coding: gb18030 -*-
# $Id: SendWindow.py, fangpengjun Exp $
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.TrackBar import HTrackBar
from guis.controls.TextBox import TextBox
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from DamageStatisticMgr import Broadcast
import config.client.labels.DmgStatMgr as lbDatas

import csdefine

class SendWindow( Window ):
	__instance = None
	def __init__( self ):
		assert SendWindow.__instance is None,"SendWindow instance has been created"
		SendWindow.__instance = self
		wnd = GUI.load( "guis/general/damagestatis/sendwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "sendStatic" )
		self.msgNum = 0
	
	def __del__( self ):
		Window.__del__( self )
		if Debug.output_del_SendDamageMsgs :
			INFO_MSG( str( self ) )
	
	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "Damagestatic:SendWindow", "lbTitle" )
		self.__pyNumTrackBar = ValueTrackBar( wnd.numTrackBar )
		self.__pyNumTrackBar.stepCount = 9
		self.__pyNumTrackBar.onSlide.bind( self.__onSlide )
		self.__pyChannelGroup = CheckerGroup()
		for name, item in wnd.children:
			if not name.startswith( "channel_" ):continue
			index = int( name.split( "_" )[1] )
			pyChaRadion = RadioButtonEx( item )
			pyChaRadion.checked = False
			pyChaRadion.channel = index
			pyChaRadion.text = labelGather.getText( "Damagestatic:SendWindow", name )
			self.__pyChannelGroup.addChecker( pyChaRadion )
			self.__pyChannelGroup.onCheckChanged.bind( self.__onCheckChange )
	
		self.__pyWhisperBox =  TextBox( wnd.whisperBox.box )
		self.__pyWhisperBox.text = ""
		self.__pyWhisperBox.onTextChanged.bind( self.__onWhisperChange )

		self.__pyBtnSend = Button( wnd.btnSend )
		self.__pyBtnSend.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSend.onLClick.bind( self.__onSend )
		labelGather.setPyBgLabel( self.__pyBtnSend, "Damagestatic:SendWindow", "btnSend" )
		labelGather.setLabel( wnd.numsText, "Damagestatic:SendWindow", "numsText" )
		labelGather.setLabel( wnd.sendTitle, "Damagestatic:SendWindow", "sendTarget" )
		labelGather.setLabel( wnd.minNum, "Damagestatic:SendWindow", "minNum" )
		labelGather.setLabel( wnd.maxNum, "Damagestatic:SendWindow", "maxNum" )
	
	def __onSlide( self, pySlider, value ):
		number = min( int( 10*value ) + 1, 10 )
		self.msgNum = number
		self.__pyNumTrackBar.stValue = str( number )
	
	def __onSend( self ):
		"""
		发送伤害数据
		"""
		dmgMsgs = []
		pyChaRadion = self.__pyChannelGroup.pyCurrChecker
		if pyChaRadion is None:return
		channel = pyChaRadion.channel
		receiver = ""
		if channel == csdefine.CHAT_CHANNEL_WHISPER:
			receiver = self.__pyWhisperBox.text.replace( ' ', '' )
		broadCaster = Broadcast( BigWorld.player() )
		damages = rds.damageStatistic.damages
		damageList = damages.values()
		damageList.sort( key = lambda item : item[-1], reverse = False )
		for damageData in damageList:
			dmgMsg = lbDatas.STATLINE % ( damageData[0], damageData[1], damageData[2], damageData[3]*100 )
			dmgMsgs.append( dmgMsg )
		if len( dmgMsgs ) >= self.msgNum:
			dmgMsgs = dmgMsgs[:self.msgNum]
		broadCaster.__call__( channel, dmgMsgs, receiver )
	
	def __onCheckChange( self, pyChecker ):
		if pyChecker is None:return
		if pyChecker.channel == csdefine.CHAT_CHANNEL_WHISPER:
			self.__pyWhisperBox.enable = True
			self.__pyBtnSend.enable = self.__pyWhisperBox.text != ""
		else:
			 self.__pyBtnSend.enable = pyChecker is not None
	
	def __onWhisperChange( self ):
		pyChaRadion = self.__pyChannelGroup.pyCurrChecker
		self.__pyBtnSend.enable = self.__pyWhisperBox.text != "" and \
		pyChaRadion.channel == csdefine.CHAT_CHANNEL_WHISPER

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if SendWindow.__instance is None:
			SendWindow.__instance = SendWindow()
		return SendWindow.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return SendWindow.__instance
	
	def show( self, pyOwner = None ):
		self.__pyChannelGroup.pyCurrChecker = self.__pyChannelGroup.pyCheckers[0]
		self.__pyNumTrackBar.value = 0.0
		Window.show( self, pyOwner )
	
	def hide( self ):
		Window.hide( self )
		SendWindow.__instance=None
		self.dispose()
		
		
# ---------------------------------------------------------------
from guis.controls.StaticText import StaticText
class ValueTrackBar( HTrackBar ):
	def __init__( self, trackBar ):
		HTrackBar.__init__( self, trackBar )
		self.__pyStValue = StaticText( trackBar.stValue )
		self.__pyStValue.text = ""
		self.__pyStValue.fontSize = 10
	
	def _getStValue( self ):
		return self.__pyStValue.text
	
	def _setStValue( self, value ):
		self.__pyStValue.text = str( value )
		self.__pyStValue.center = self.pySlider_.center
	
	stValue = property( _getStValue, _setStValue )
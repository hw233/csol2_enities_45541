# -*- coding: gb18030 -*-

# 好友聊天窗口
# written by gjx 2010-06-17

from guis import *
from guis.UIFixer import hfUILoader
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.common.Window import Window
from guis.common.GUIBaseObject import GUIBaseObject

from PLMTextBox import PLMTextBox
from PLMMsgPanel import PLMMsgPanel
from PLMLogBrowser import plmLogBrowser

import csstatus
import csconst
import Const
import csdefine
from ChatFacade import chatFacade, msgInserter
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs


class PLMChatWindow( Window ) :

	__CHID = csdefine.CHAT_CHANNEL_PLAYMATE

	def __init__( self ) :
		wnd = hfUILoader.load( "guis/general/chatwindow/playmatechat/chatwindow.gui" )
		Window.__init__( self, wnd )

		self.__pyMsgBox = None
		self.__flashCBID = 0

		self.__initialize( wnd )
		self.addToMgr()

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_PLMChatWindow :
			INFO_MSG( "[%s] delete!" % str( self ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if ( mods == MODIFIER_CTRL ) and \
			( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了CTRL+回车键
				self.__sendMsg()
				return True
		return Window.onKeyDown_( self, key, mods )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyBtnLog = Button( wnd.btn_log )
		self.__pyBtnLog.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLog.onLClick.bind( self.__browseLog )

		self.__pyBtnHide = Button( wnd.btn_hide )
		self.__pyBtnHide.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		self.__pyBtnSend = Button( wnd.btn_send )
		self.__pyBtnSend.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSend.onLClick.bind( self.__sendMsg )
		self.__pyBtnSend.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyBtnSend.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyBtnEmote = Button( wnd.btn_emote )
		self.__pyBtnEmote.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnEmote.onLClick.bind( self.__openEmotionBox )

		self.__pyObjHeader = Header( wnd.header_obj )
		self.__pyMyHeader = Header( wnd.header_me )

		rcvPnl = wnd.mlRTB_rcvPanel							# 消息接收框
		self.__pyRcvBox = PLMMsgPanel( rcvPnl.clipPanel, rcvPnl.sbar )

		sdePnl = wnd.mlRTB_sdePanel							# 消息输入框
		self.__pySendBox = PLMTextBox( sdePnl.clipPanel, sdePnl.sbar )
		self.__pySendBox.onTextChanged.bind( self.__onTextChanged )
		msgInserter.registerInputObj( self.__pySendBox )
		
		self.__pyStTextCount = StaticText( wnd.textCount )
		self.__pyStTextCount.text = "0/" +str( csconst.CHAT_MESSAGE_UPPER_LIMIT/2 )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnSend, "ChatWindow:PLMChatWnd", "btnSend" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "ChatWindow:PLMChatWnd", "btnHide" )
		labelGather.setPyBgLabel( self.__pyBtnLog, "ChatWindow:PLMChatWnd", "btnLog" )
		labelGather.setLabel( wnd.stEmote, "ChatWindow:PLMChatWnd", "stEmote" )

	def __flash( self ) :
		"""
		窗口闪烁
		"""
		BigWorld.cancelCallback( self.__flashCBID )
		preVisible = self.gui.hlFrame.visible
		self.gui.hlFrame.visible = not preVisible
		self.__flashCBID = BigWorld.callback( 0.4, self.__flash )

	def __stopFlash( self ) :
		"""
		停止闪烁
		"""
		if self.__flashCBID :
			BigWorld.cancelCallback( self.__flashCBID )
			self.__flashCBID = 0
		self.gui.hlFrame.visible = False

	# -------------------------------------------------
	def __onTextChanged( self ) :
		curLength = self.__pySendBox.wviewLength
		if curLength <= csconst.CHAT_MESSAGE_UPPER_LIMIT/2:
			self.__pyStTextCount.text = str( curLength ) + "/" + str( csconst.CHAT_MESSAGE_UPPER_LIMIT/2 )
		else:
			self.__pyStTextCount.text = str( csconst.CHAT_MESSAGE_UPPER_LIMIT/2 - curLength )
	
	def __browseLog( self ) :
		"""
		浏览聊天记录
		"""
		objName = self.__pyObjHeader.name
		plmLogBrowser.showChatLogs( objName )

	def __sendMsg( self ) :
		"""
		发送聊天消息
		"""
		sendText = self.__pySendBox.text
		if sendText.strip() == "" : return
		if len( self.__pySendBox.wviewText ) > csconst.CHAT_MESSAGE_UPPER_LIMIT/2:
			BigWorld.player().statusMessage( csstatus.CHAT_WORDS_TOO_LONG )
			return
		receiver = self.__pyObjHeader.name
		if not BigWorld.player().friends.has_key( receiver ) : # 不在好友列表中
			self.__showMessage( MB_OK, mbmsgs[0x0271] % receiver )
			return
		if chatFacade.sendChannelMessage( self.__CHID, sendText, receiver ) :
			self.__pySendBox.clear()

	def __updateTitle( self ) :
		"""
		更新标题
		"""
		objName = self.__pyObjHeader.name
		title = labelGather.getText( "ChatWindow:PLMChatWnd", "lbTitle", objName )
		self.pyLbTitle_.text = title

	# -------------------------------------------------
	def __openEmotionBox( self ) :
		"""
		打开表情选择界面
		"""
		emotionBox = rds.ruisMgr.emotionBox
		emotionBox.toggle( self.__insertEmotion, self.__pySendBox )
		emotionBox.bottom = self.__pyBtnEmote.topToScreen
		emotionBox.left = self.__pyBtnEmote.rightToScreen
		self.__pySendBox.tabStop = True

	def __insertEmotion( self, sign ) :
		if self.__pySendBox.tabStop :
			self.__pySendBox.notifyInput( sign )

	def __clearRcvText( self ) :
		"""
		清空消息接收框
		"""
		self.__pyRcvBox.reset()

	def __showMessage( self, style, msg, cb = None ) :
		"""
		用消息框提示消息
		"""
		def callback( res ) :
			if callable( cb ) :
				cb( res )
			self.__pyMsgBox = None
		if self.__pyMsgBox : self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", style, callback )

	# -------------------------------------------------
	def __onBtnMouseEnter( self, pyBtn ) :
		"""
		鼠标进入按钮时调用
		"""
		# "快捷键：\n－－ Ctrl + Enter"
		dsp = labelGather.getText( "ChatWindow:PLMChatWnd", "sendShortcut" )
		toolbox.infoTip.showToolTips( pyBtn, dsp )

	def __onBtnMouseLeave( self, pyBtn ) :
		"""
		鼠标离开按钮时调用
		"""
		toolbox.infoTip.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		Window.show( self )
		player = BigWorld.player()
		online = True
		name = player.getName()
		raceClass = player.raceclass
		headTexture = player.getHeadTexture()
		myInfo = ( name, online, raceClass, headTexture )
		self.__pyMyHeader.update( myInfo )
		self.__updateTitle()

	def dispose( self ) :
		self.__stopFlash()
		Window.dispose( self )

	def onActivated( self ) :
		"""
		窗口被激活
		"""
		Window.onActivated( self )
		self.__stopFlash()
		self.__pySendBox.tabStop = True

	# -------------------------------------------------
	def onReceiveMessages( self, msgs ) :
		"""
		接收多条消息记录
		"""
		self.__pyRcvBox.addMessages( msgs )
		if not rds.ruisMgr.isActRoot( self ) :
			self.__flash()

	def onReceiveMessage( self, channel, spkID, spkName, msg, date ) :
		"""
		接收到一条消息
		"""
		self.__pyRcvBox.addMessage( channel, spkID, spkName, msg, date )
		if not rds.ruisMgr.isActRoot( self ) :
			self.__flash()

	def insertMessage( self, msg ) :
		"""
		在输入框的光标处插入一段消息
		"""
		self.__pySendBox.notifyInput( msg )

	def updateChatObj( self, objInfo ) :
		"""
		更新聊天对象的信息
		"""
		self.__pyObjHeader.update( objInfo )
		self.__updateTitle()

	def updateObjOnlineState( self, online ) :
		"""
		更新聊天对象的在线状态
		"""
		self.__pyObjHeader.updateOLState( online )


class Header( GUIBaseObject ) :

	__METIER_MAPPING = {
		csdefine.CLASS_FIGHTER 	: ( 1, 1 ),
		csdefine.CLASS_SWORDMAN	: ( 1, 2 ),
		csdefine.CLASS_ARCHER	: ( 2, 1 ),
		csdefine.CLASS_MAGE		: ( 2, 2 ),
	}

	def __init__( self, header ) :
		GUIBaseObject.__init__( self, header )
		self.__pyName = StaticText( header.st_name )
		labelGather.setLabel( header.stOffline, "ChatWindow:PLMChatWnd", "stOffline" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setMetier( self, raceClass ) :
		"""
		设置职业图标
		"""
		metier = raceClass & csdefine.RCMASK_CLASS
		metierState = Header.__METIER_MAPPING.get( metier, (1,1) )
		mapping = util.getStateMapping( (48, 48), (2, 2), metierState )
		self.gui.metier.mapping = mapping

	def __setHeadTx( self, headTexture ) :
		"""
		设置头像
		"""
		self.gui.header.textureName = headTexture

	def __setOnline( self, online ) :
		"""
		设置在线状态
		"""
		matlFX = online and "BLEND" or "COLOUR_EFF"
		self.materialFX = matlFX
		self.gui.header.materialFX = matlFX
		self.gui.metier.materialFX = matlFX


	def __visibleOFLText( self ) :
		"""
		设置离线文字是否显示
		"""
		txHead = self.gui.header.textureName
		online = self.materialFX == "BLEND"
		showOFLText = txHead == "" and not online
		self.gui.stOffline.visible = showOFLText			# 显示离线文字


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, roleInfo ) :
		"""
		更新数据
		"""
		self.__pyName.text = roleInfo[0]
		self.__setOnline( roleInfo[1] )
		self.__setMetier( roleInfo[2] )
		self.__setHeadTx( roleInfo[3] )
		self.__visibleOFLText()

	def updateOLState( self, online ) :
		"""
		更新在线状态
		"""
		self.__setOnline( online )
		self.__visibleOFLText()


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def name( self ) :
		return self.__pyName.text

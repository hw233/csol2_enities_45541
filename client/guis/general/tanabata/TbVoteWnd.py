# -*- coding: gb18030 -*-

from guis import *
from guis.common.Window import Window
from AbstractTemplates import Singleton
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.CheckerGroup import CheckerGroup
from guis.tooluis.CSTextPanel import CSTextPanel
import Const
import csdefine
from LabelGather import labelGather
import GUIFacade

from AbstractTemplates import MultiLngFuncDecorator

class deco_InitVoteEmote( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyVoteBoxs ) :
		"""
		繁体版下重新設置投票表情
		"""
		voteEmotes = {
				csdefine.FCWR_VOTE_KAN_HAO: "maps/emote/emote_5.dds",
				csdefine.FCWR_VOTE_QING_DI: "maps/emote/emote_11.dds",
				csdefine.FCWR_VOTE_SHI_LIAN: "maps/emote/emote_21.dds",
				csdefine.FCWR_VOTE_KAN_QI: "maps/emote/emote_32.dds",
				csdefine.FCWR_VOTE_FAN_DUI: "maps/emote/emote_19.dds",
				csdefine.FCWR_VOTE_LU_GUO: "maps/emote/emote_22.dds",
			}
		for pyVoteBox in pyVoteBoxs.values():
			voteType = pyVoteBox.voteType
			pyVoteBox.getGui().elements["frm_emote"].texture = voteEmotes[voteType]

class TbVoteWnd( Singleton, Window ) :

	__instance=None

	__cc_voteCountText = labelGather.getText( "Tanabata:vote", "stVoteAmount" )
	__cc_anonymityText = labelGather.getText( "Tanabata:vote", "stCryptonym" )

	def __init__( self ) :
		assert TbVoteWnd.__instance is None ,"MsgBoard instance has been created"
		TbVoteWnd.__instance = self
		wnd = GUI.load( "guis/general/tanabata/votewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )

		self.__msgIndex = -1
		self.__pyVoteBoxs = {}

		self.__initialize( wnd )
		self.addToMgr( "tbVoteWnd" )
		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TANABATA1 )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		Window.__del__( self )
		if Debug.output_del_TbVoteWnd:
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __initialize( self, wnd ) :
		self.__pyBtnVote = Button( wnd.btn_vote )
		self.__pyBtnVote.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnVote.onLClick.bind( self.__onVote )

		self.__pyBtnHide = Button( wnd.btn_hide )
		self.__pyBtnHide.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHide.onLClick.bind( self.hide )

		txPnl = wnd.pnl_msg
		self.__pyTextPanel = CSTextPanel( txPnl.clipPanel, txPnl.sbar )

		self.__pySender = TbHeader( wnd.header_sender )
		self.__pySender.setLabel( "Tanabata:vote", "stSender" )
		self.__pyReceiver = TbHeader( wnd.header_receiver )
		self.__pyReceiver.setLabel( "Tanabata:vote", "stReceiver" )
		self.__pyVoteAmount = StaticText( wnd.stVoteAmount )
		self.__pyVoteAmount.text = self.__cc_voteCountText % 0
		self.__initVoteCheckers( wnd )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyBtnVote, "Tanabata:vote", "btnVote" )
		labelGather.setPyBgLabel( self.__pyBtnHide, "Tanabata:vote", "btnHide" )
		labelGather.setLabel( wnd.lbTitle, "Tanabata:vote", "lbTitle" )

	def __initVoteCheckers( self, wnd ) :
		"""
		初始化投票选择框
		"""
		voteMap = {
			"support"	: csdefine.FCWR_VOTE_KAN_HAO,
			"rival"		: csdefine.FCWR_VOTE_QING_DI,
			"lovelorn"	: csdefine.FCWR_VOTE_SHI_LIAN,
			"playgoing"	: csdefine.FCWR_VOTE_KAN_QI,
			"oppose"	: csdefine.FCWR_VOTE_FAN_DUI,
			"onlooker"	: csdefine.FCWR_VOTE_LU_GUO,
		}
		self.__checkerGroup = CheckerGroup()
		for name, box in wnd.children :
			if not "rdbox_" in name : continue
			opinion = name.split( "_" )[1]
			voteType = voteMap[ opinion ]
			pyBox = TbVoteBox( box )
			pyBox.voteType = voteType
			pyBox.setLabel( "Tanabata:vote", opinion )
			self.__checkerGroup.addChecker( pyBox )
			self.__pyVoteBoxs[ voteType ] = pyBox
	
		self.__initVoteEmote( self.__pyVoteBoxs )
	
	@deco_InitVoteEmote
	def __initVoteEmote( self, pyVoteBoxs ):
		voteEmotes = {
				csdefine.FCWR_VOTE_KAN_HAO: "maps/emote/emote_16/1.dds",
				csdefine.FCWR_VOTE_QING_DI: "maps/emote/emote_6/1.dds",
				csdefine.FCWR_VOTE_SHI_LIAN: "maps/emote/emote_20/1.dds",
				csdefine.FCWR_VOTE_KAN_QI: "maps/emote/emote_3/1.dds",
				csdefine.FCWR_VOTE_FAN_DUI: "maps/emote/emote_18/1.dds",
				csdefine.FCWR_VOTE_LU_GUO: "maps/emote/emote_3/1.dds",
			}
		for pyVoteBox in pyVoteBoxs.values():
			voteType = pyVoteBox.voteType
			pyVoteBox.getGui().elements["frm_emote"].texture = voteEmotes[voteType]

	# -------------------------------------------------
	def __onVote( self ) :
		"""
		投票
		"""
		pyVoteBox = self.__checkerGroup.pyCurrChecker
		if pyVoteBox is None :
			# "请先选择一项"
			self.__showMessage( MB_OK, 0x0e61 )
			return
		player = BigWorld.player()
		player.base.voteLoveMsg( self.__msgIndex, pyVoteBox.voteType )

	def __updateVoteInfo( self, voteInfo ) :
		"""
		更新选票信息
		"""
		sum = 0
		for voteType, value in voteInfo.iteritems() :
			self.__pyVoteBoxs[ voteType ].voteCount = value
			sum += value
		self.__pyVoteAmount.text = self.__cc_voteCountText % sum

	# -------------------------------------------------
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

	@staticmethod
	def instance():
		if TbVoteWnd.__instance is None:
			TbVoteWnd.__instance = TbVoteWnd()
		return TbVoteWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return TbVoteWnd.__instance
	
	def onVoteSucc( self, msgInst ):
		if msgInst.index == self.__msgIndex:
			votes = {
				csdefine.FCWR_VOTE_KAN_HAO	: msgInst.vote_1,
				csdefine.FCWR_VOTE_QING_DI	: msgInst.vote_2,
				csdefine.FCWR_VOTE_SHI_LIAN	: msgInst.vote_3,
				csdefine.FCWR_VOTE_KAN_QI	: msgInst.vote_4,
				csdefine.FCWR_VOTE_FAN_DUI	: msgInst.vote_5,
				csdefine.FCWR_VOTE_LU_GUO	: msgInst.vote_6,
			}
			self.__updateVoteInfo( votes )
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def readConfession( self, info, pyOwner = None ) :
		"""
		阅读表白的详细内容
		"""
		self.__msgIndex = info.index
		senderName = info.senderName
		if info.isAnonymity :						# 匿名发表
			senderName = self.__cc_anonymityText
		self.__pySender.updateInfo( ( senderName, info.senderRaceclass ) )
		self.__pyReceiver.updateInfo( ( info.receiverName, info.receiverRaceclass ) )
		votes = {
			csdefine.FCWR_VOTE_KAN_HAO	: info.vote_1,
			csdefine.FCWR_VOTE_QING_DI	: info.vote_2,
			csdefine.FCWR_VOTE_SHI_LIAN	: info.vote_3,
			csdefine.FCWR_VOTE_KAN_QI	: info.vote_4,
			csdefine.FCWR_VOTE_FAN_DUI	: info.vote_5,
			csdefine.FCWR_VOTE_LU_GUO	: info.vote_6,
		}
		self.__updateVoteInfo( votes )
		self.__pyTextPanel.text = info.msg
		pyCurrChecker = self.__checkerGroup.pyCurrChecker
		if pyCurrChecker : pyCurrChecker.checked = False
		self.show( pyOwner )

	# -------------------------------------------------
	def hide( self ):
		Window.hide( self )
		self.__msgIndex = -1
		self.removeFromMgr()
		TbVoteWnd.__instance = None
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		
	def onLeaveWorld( self ) :
		"""
		退出游戏
		"""
		self.hide()
# --------------------------------------------------------------------------
class TbHeader( GUIBaseObject ) :

	__METIER_MAPPING = {
		csdefine.CLASS_FIGHTER 	: ( 1, 1 ),
		csdefine.CLASS_SWORDMAN	: ( 1, 2 ),
		csdefine.CLASS_ARCHER	: ( 2, 1 ),
		csdefine.CLASS_MAGE		: ( 2, 2 ),
	}

	def __init__( self, header ) :
		GUIBaseObject.__init__( self, header )

		self.__pyName = StaticText( header.st_name )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __setMetier( self, raceClass ) :
		"""
		设置职业图标
		"""
		metier = raceClass & csdefine.RCMASK_CLASS
		metierState = TbHeader.__METIER_MAPPING.get( metier, (1,1) )
		mapping = util.getStateMapping( (48, 48), (2, 2), metierState )
		self.gui.metier.mapping = mapping

	def __setHeadTx( self, raceClass ) :
		"""
		设置头像
		"""
		metier = raceClass & csdefine.RCMASK_CLASS
		gender = raceClass & csdefine.RCMASK_GENDER
		txHead = ""
		txMetier = Const.ROLE_HEADERS.get( metier )			# 根据职业和性别设定头像
		if txMetier is not None :
			txHead = txMetier.get( gender, "" )
		self.gui.header.textureName = txHead


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setLabel( self, key, lbName ) :
		"""
		设置标签
		"""
		labelGather.setLabel( self.gui.stLabel.stText, key, lbName )

	def updateInfo( self, info ) :
		"""
		更新信息
		"""
		self.__pyName.text = info[0]
		self.__setMetier( info[1] )
		self.__setHeadTx( info[1] )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def name( self ) :
		return self.__pyName.text

class TbVoteBox( GUIBaseObject ) :

	def __init__( self, box ) :
		GUIBaseObject.__init__( self, box )

		self.__evtCheckChanged = ControlEvent( "onCheckChanged", self )

		self.__pyChecker = RadioButtonEx( box.radioBox )
		self.__pyChecker.onCheckChanged.bind( self.__onCheckChanged )
		self.__pyVoteCount = StaticText( box.stCount )

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	@property
	def onCheckChanged( self ) :
		return self.__evtCheckChanged


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onCheckChanged( self, checked ) :
		"""
		选择改变
		"""
		self.onCheckChanged( checked )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setLabel( self, key, lbName ) :
		"""
		设置标签
		"""
		labelGather.setPyLabel( self.__pyChecker.pyText_, key, lbName )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getChecked( self ) :
		return self.__pyChecker.checked

	def _setChecked( self, checked ) :
		self.__pyChecker.checked = checked

	def _getVoteCount( self ) :
		return int( self.__pyVoteCount.text )

	def _setVoteCount( self, count ) :
		self.__pyVoteCount.text = count

	checked = property( _getChecked, _setChecked )
	voteCount = property( _getVoteCount, _setVoteCount )
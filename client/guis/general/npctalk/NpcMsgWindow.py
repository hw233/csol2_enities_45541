# -*- coding: gb18030 -*-
#
# $Id: QuestTalkWindow.py,v 1.53 2008-08-25 09:26:25 huangyongwei Exp $

"""
implement quest talking window。
"""

import Language
import csdefine
import csconst
import GUIFacade
from guis import *
from LabelGather import labelGather
from ChatFacade import chatFacade
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from ContentPanel import ContentPanel


# --------------------------------------------------------------------
# implement npc message window
# --------------------------------------------------------------------
class NpcMsgWindow( Window ) :
	__cc_content_spacing	= 4.0		# text spacing of talking content text

	def __init__( self ) :
		wnd = GUI.load( "guis/general/npctalk/commtalk.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.__initialize( wnd )
		self.__trapID = None
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_NPC_TALK, self.__showNpcMessage )

	def __initialize( self, wnd ) :
		labelGather.setPyLabel( self.pyLbTitle_, "NPCTalkWnd:main", "lbTitle" )
		self.pyContent_ = ContentPanel( wnd.contentPanel.clipPanel, wnd.contentPanel.sbar )
		self.pyContent_.spacing = self.__cc_content_spacing

		self.pyBigPanel_ = PyGUI( wnd.bigPanel )

		self.pySmallPanel_ = PyGUI( wnd.smallPanel )
		self.pySmallPanel_.visible = True

		self.pyBtnShut_ = Button( wnd.smallPanel.btnShut )
		self.pyBtnShut_.visible = True
		self.pyBtnShut_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnShut_.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.pyBtnShut_, "NPCTalkWnd:main", "btnShut" )

		self.pyBtnAccept_ = Button( wnd.bigPanel.btnAccept )
		self.pyBtnAccept_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnAccept_, "NPCTalkWnd:main", "btnAccept" )

		self.pyBtnFulfil_ = Button( wnd.bigPanel.btnFulfill )
		self.pyBtnFulfil_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnFulfil_, "NPCTalkWnd:main", "btnFulfill" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reset( self ) :
		self.__trapID = None

	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		gossiptarget = GUIFacade.getGossipTarget()
		if hasattr(gossiptarget, "getRoleAndNpcSpeakDistance" ):
			distance = gossiptarget.getRoleAndNpcSpeakDistance() # + 2	# 去掉这莫名其妙的"+2" modify by gjx 2009-4-2
		self.__trapID = BigWorld.addPot( gossiptarget.matrix,distance, self.__onEntitiesTrapThrough )		# 打开窗口后为玩家添加对话陷阱s


	def __onEntitiesTrapThrough( self, enteredTrap, handle ):
		"""
		when the player is away from the trap ,this window disappear
		"""
		if not enteredTrap:
			self.__onShut()																# 隐藏当前与NPC对话窗口

	def __delTrap( self ) :
		"""
		remove the trap
		"""
		if self.__trapID :
			try:	# 如果玩家没有这个trapID，则self.__trapID = 0
				BigWorld.delPot( self.__trapID )											#删除的对话陷阱
			except:
				HACK_MSG( "trapID不对。" )
				self.__trapID = None
			self.__trapID = None

	def __onShut( self ):
		self.hide( )
		self.__delTrap()

	def __showNpcMessage( self, channel, spkID, spkName, msg, statusID = None ) :
		"""
		show npc talk message
		"""
		self.clearContent_()
		self.pyContent_.appendText( msg )
		self.show()
		self.__addTrap()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def clearContent_( self ):
		"""
		clear all content is in content panel
		"""
		self.pyContent_.clear()

	def hide( self ):
		"""
		"""
		return RootGUI.hide( self )

	def onLeaveWorld( self ) :
		self.hide()
		self.__reset()


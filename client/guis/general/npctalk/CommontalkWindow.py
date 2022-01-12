# -*- coding: gb18030 -*-
#
# $Id: CommontalkWindow.py,v 1.20 2008-08-26 02:16:14 huangyongwei Exp $

"""
implement talking window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from ContentPanel import ContentPanel
from MarkItem import MarkItem
from gbref import rds
import GUIFacade
import csconst
import csdefine
import Language
from config.client import GossipType

class CommontalkWindow( Window ) :
	__cc_content_spacing	= 4.0		# text spacing of talking content text
	__cc_respond_view_rows	= 4			# the number of respond will be show at one time
	
	def __init__( self ) :
		wnd = GUI.load( "guis/general/npctalk/commtalk.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.gossipType = GossipType.Datas
		self.__initialize( wnd )
		self.pyOptionItems_ = []
		self.triggers_ = {}
		self.registerTriggers_()
		self.__trapID = 0

		rds.mutexShowMgr.addMutexRoot( self, MutexGroup.TRADE2 )				# ��ӵ�MutexGroup.TRADE2������

	def __initialize( self, wnd ) :
		self.pyContent_ = ContentPanel( wnd.contentPanel.clipPanel, wnd.contentPanel.sbar )
		self.pyContent_.spacing = self.__cc_content_spacing

		self.pyBigPanel_ = PyGUI( wnd.bigPanel )
		labelGather.setPyLabel( self.pyLbTitle_, "NPCTalkWnd:main", "lbTitle" ) # ע�⣺�������ЧUI������lbTitle_
		
		self.pyHeader_ = PyGUI(wnd.header )
		self.pyHeader_.texture = ""

		self.pySmallPanel_ = PyGUI( wnd.smallPanel )
		self.pySmallPanel_.visible = True

		self.pyBtnShut_ = HButtonEx( wnd.smallPanel.btnShut )
		self.pyBtnShut_.visible = True
		self.pyBtnShut_.setExStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnShut_.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.pyBtnShut_, "NPCTalkWnd:main", "btnShut" )

		self.pyBtnAccept_ = HButtonEx( wnd.bigPanel.btnAccept )
		self.pyBtnAccept_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnAccept_, "NPCTalkWnd:main", "btnAccept" )

		self.pyBtnFulfil_ = HButtonEx( wnd.bigPanel.btnFulfill )
		self.pyBtnFulfil_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnFulfil_, "NPCTalkWnd:main", "btnFulfill" )
		
		self.pyCloseBtn_.onLClick.bind( self.__onShut )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __reset( self ) :
		self.__trapID = 0

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.triggers_.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	# -------------------------------------------------
	def onEndTalking_( self ) :
		self.__delTrap()
		self.hide()

	# -------------------------------------------------
	def __onItemClick( self, pyItem ) :
		pyItem.handler( *pyItem.handleArgs )

	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()

		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()  + 0.5	# +0.5 ���������С�ͶԻ�������ȶ������������Ե�Ի�ʱ�Ի����һ����ʧ�����⡣
		self.__trapID = player.addTrapExt( distance, self.__onEntitiesTrapThrough )		#�򿪴��ں�Ϊ�����ӶԻ�����s

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )											#ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()									#��ȡ��ǰ�Ի�NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:						#���NPC�뿪��ҶԻ�����
			self.__onShut()														#���ص�ǰ��NPC�Ի�����

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		"""
		register event triggers
		"""
		self.triggers_["EVT_OPEN_GOSSIP_WINDOW"] = self.onShowCommonTalking_	# show window for talking trigger
		self.triggers_["EVT_END_GOSSIP"] = self.onEndTalking_					# hide talking window
		self.triggers_["EVT_ON_ROLE_DEAD"] = self.hide
		for eventMacro in self.triggers_.iterkeys() :
			GUIFacade.registerEvent( eventMacro, self )

	# -------------------------------------------------------------
	def getPyOptionItem_( self, index, text, markType ) :
		"""
		get/create respond item
		"""
		existCount = len( self.pyOptionItems_ )
		pyItem = None
		if index < existCount :
			pyItem = self.pyOptionItems_[index]
		else :
			pyItem = MarkItem()
			pyItem.handler = lambda *args : False
			pyItem.handleArgs = ()
		
		pyItem.text = text
		pyItem.commonForeColor = ( 69, 141, 204, 255 )
		pyItem.selectedForeColor = pyItem.highlightForeColor
		pyItem.markType = markType
		pyItem.mark = self.gossipType[markType]
		return pyItem

	# -------------------------------------------------
	def clearContent_( self ) :
		self.pyContent_.clear()

	def addOptionItem_( self, index, text, markType, handler, handleArgs = () ) : # ������Ի�ѡ����������
		"""
		add a respond items
		"""
		pyItem = self.getPyOptionItem_( index, text, markType )
		pyItem.handler = handler
		pyItem.handleArgs = handleArgs
		pyItem.onLClick.bind( self.__onItemClick )
		self.pyContent_.appendOptionItem( pyItem ) # ����ѡ����ӵ�������
		
	# ---------------------------------------
	def onShowCommonTalking_( self ) :
		"""
		show common talking
		"""
#		self.pyLbTitle_.text = GUIFacade.getGossipTargetName()					# �Ի�NPC����wsf
		self.clearContent_()
		self.pyContent_.appendText( GUIFacade.getGossipText() )					# ��ͨ�Ի�����
		self.pyHeader_.texture = GUIFacade.getGossipTargetHeader()
		self.showGossipOption()
		self.__addTrap()

	def showGossipOption( self ):	# wsf add��������
		options = GUIFacade.getGossipOptions()									# ��ͨ�Ի�ѡ��
		handler = GUIFacade.selectGossipOption									# ����Ի�����ѡ��
		for index, option in enumerate( options ) :
			self.addOptionItem_( index, option[1], option[2], handler, ( index, ) )

	def __onShut( self ):
		self.hide()
		self.__delTrap()
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		event triggering
		"""
		self.triggers_[eventMacro]( *args )
	
	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )

	def onLeaveWorld( self ) :
		self.hide()
		self.__reset()
	
	def hide( self ):
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		Window.hide( self )

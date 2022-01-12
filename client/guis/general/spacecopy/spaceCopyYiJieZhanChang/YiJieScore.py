# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.controls.StaticText import StaticText
from guis.common.Window import Window
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.ButtonEx import HButtonEx
	
class YiJieScore( Window ) :
	def __init__( self ) :
		gui = GUI.load( "guis/general/spacecopyabout/spaceCopyYiJieZhanChang/score.gui" )
		uiFixer.firstLoadFix( gui )
		Window.__init__( self, gui )
		
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__pyBtns = {}			
		self.__initialize( gui )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, gui ):
		labelGather.setLabel( gui.lbTitle, "SpaceCopyJiJieZhanChang:yiJieScore", "lbTitle" )		
		for  name, btn in gui.scorePanel.header.children:
			if name.startswith("btn_"):
				pyBtn = HButtonEx( btn )
				pyBtn.setExStatesMapping( UIState.MODE_R3C1 )
				self.__pyBtns[name] = pyBtn
				labelGather.setPyBgLabel( pyBtn, "SpaceCopyJiJieZhanChang:yiJieScore", name )
		
		self.__pyScorePage = ODPagesPanel( gui.scorePanel.panel, gui.pgIdxBar )
		self.__pyScorePage.onViewItemInitialized.bind( self.__initListItem )
		self.__pyScorePage.onDrawItem.bind( self.__drawListItem )
		self.__pyScorePage.selectable = True
		self.__pyScorePage.viewSize = ( 10, 1 )
		
		self.__playerItem = ScoreItem( gui.playerItem )
	
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_RECEIVE_YIJIE_SCORES_DATAS"]	= self.__onReceiveDatas				#接收玩家的数据
		self.__triggers["EVT_ON_YIJIE_SCORE_WINDOW_HIDE"]	= self.__onHide				#隐藏界面
		
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
			
	def __initListItem( self, pyViewItem ):
		pyScoreItem = ScoreItem()
		pyViewItem.pyScoreItem = pyScoreItem
		pyViewItem.addPyChild( pyScoreItem )
		pyViewItem.focus = True
		pyScoreItem.left = 0
		pyScoreItem.top = 0
		
	def __drawListItem( self, pyViewItem ):
		roleInfo = pyViewItem.pageItem
		pyScoreItem = pyViewItem.pyScoreItem
		pyScoreItem.selected = pyViewItem.selected
		pyScoreItem.update( roleInfo )
		
	def __onReceiveDatas( self, roleInfos ):
		playerName = BigWorld.player().playerName
		for roleInfo in roleInfos:
			if roleInfo.roleName == playerName:
				self.__playerItem.update( roleInfo )
			else:
				self.__pyScorePage.addItem( roleInfo )
		self.__pyScorePage.sort( key = lambda item: item.rank, reverse = False )
		BigWorld.callback( 2, self.show )
		
	def show( self ):
		Window.show( self )
		
	def __onHide( self ):
		Window.hide( self )
			
	#--------------------------------------------------------------------			
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
		
	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.hide()

class ScoreItem( GUIBaseObject ):
	
	__score_item = None
	
	def __init__( self,gui = None, pyBinder = None ):
		if ScoreItem.__score_item is None:
			ScoreItem.__score_item = GUI.load("guis/general/spacecopyabout/spaceCopyYiJieZhanChang/scoreItem.gui")
		if gui is None:
			gui = util.copyGuiTree( ScoreItem.__score_item )
		uiFixer.firstLoadFix( gui )
		GUIBaseObject.__init__( self, gui )	
		self.__selected = False
		self.__elements = gui.elements
		self.__pyItems = []
		self.__initialize( gui )
		self.update( None )
				
	def __initialize( self, gui ):
		for name, item in gui.children:
			if name.startswith("col_"):
				pyStText = StaticText( item.lbText )
				self.__pyItems.append( pyStText )				
	
	def update( self, roleInfo ):
		if roleInfo is not None:
			rank = str ( roleInfo.rank )			#排名
			roleName = roleInfo.roleName 		#姓名
			faction = roleInfo.faction			#阵营
			killNum = str( roleInfo.killNum)	#杀敌数
			keepNum = str( roleInfo.keepNum )	#连斩数
			score = str( roleInfo.score )		#积分
			self.__pyItems[0].text = rank
			self.__pyItems[1].text = roleName
			self.__pyItems[2].text = faction
			self.__pyItems[3].text = killNum
			self.__pyItems[4].text = keepNum
			self.__pyItems[5].text = score
		else:
			self.__pyItems[0].text = ""
			self.__pyItems[1].text = ""
			self.__pyItems[2].text = ""
			self.__pyItems[3].text = ""
			self.__pyItems[4].text = ""
			self.__pyItems[5].text = ""
	
	#----------------------------------------------------------
	def _getSelected( self ):
		return self.__selected
		
	def _setSelected(self, selected ):
		self.__selected = selected
		for elem in self.__elements:
			self.__elements[elem].visible = selected
		
	selected = property( _getSelected, _setSelected )
		
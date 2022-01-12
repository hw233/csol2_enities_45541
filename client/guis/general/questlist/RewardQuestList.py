# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODListPanel import ODListPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.controls.Control import Control
import GUIFacade
import time
import Timer
import csdefine


class RewardQuestList( Window ):
	def __init__( self ):
		gui = GUI.load( "guis/general/questlist/rewardquest/rewardquest.gui" )
		uiFixer.firstLoadFix( gui )
		Window.__init__( self, gui )
		self.__remainTimerID = 0
		self.__initialize( gui )
		self.__triggers = {}
		self.__registerTriggers()
		
	def __initialize( self, wnd ):
		self.__stNumberTips = StaticText( wnd.questPanel.stQuestCompletedTips )
		self.__stNumberTips.text = ""
		
		self.__stRefreshTime = StaticText( wnd.stFlashTime )
		self.__stRefreshTime.text = ""
		
		self.__btnRefresh = HButtonEx( wnd.btnFlash )
		self.__btnRefresh.setExStatesMapping( UIState.MODE_R4C1 )
		self.__btnRefresh.onLClick.bind( self.__requestRefleshQuests )
		labelGather.setPyBgLabel( self.__btnRefresh, "QuestHelp:RewardQuestList", "btnRefresh"   )
		
		self.__pyQuestList = ODListPanel( wnd.questPanel.clipPanel, wnd.questPanel.sbar )
		self.__pyQuestList.onViewItemInitialized.bind( self.__initListItem )
		self.__pyQuestList.onDrawItem.bind( self.__drawListItem )
		self.__pyQuestList.itemHeight = 42
		self.__pyQuestList.ownerDraw = True
		
		labelGather.setPyLabel( self.pyLbTitle_, "QuestHelp:RewardQuestList", "lbTitle"  )
		
	
	def __registerTriggers( self ):	
		self.__triggers["EVT_ON_REWARD_QUEST_WINDOW_SHOW"]	 = self.__onShow
		self.__triggers["EVT_ON_REWARD_QUEST_WINDOW_HIDE"]	 = self.__onHide
		self.__triggers["EVT_ON_QUEST_STATE_CHANGED"] = self.__onQuestStateChanged	
		self.__triggers["EVT_ON_REWARD_QUESTS_UPDATE"] = self.__onRewardQuestsUpdate		
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
			
	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
		
	def __initListItem( self, pyViewItem ):
		pyQuestItem = QuestItem()
		pyViewItem.pyQuestItem = pyQuestItem
		pyViewItem.addPyChild( pyQuestItem )
		pyQuestItem.left = 0
		pyQuestItem.top = 0
		
	def __drawListItem( self, pyViewItem ):
		questInfo = pyViewItem.listItem
		pyQuestItem = pyViewItem.pyQuestItem
		pyQuestItem.updateQuest( questInfo )
		if pyViewItem.selected :							# 选中状态
			pyQuestItem.setHighLight()
		elif pyViewItem.highlight :							# 高亮状态（鼠标在其上）
			pyQuestItem.setHighLight()
		else :
			pyQuestItem.setCommonLight()
		
	def __requestRefleshQuests( self ):
		player = BigWorld.player()
		player.useItemRefreshRewardQuest()
		
	def __getTimeStr( self, remainTime ):
		"""
		格式化剩余时间
		"""
		hours = int( remainTime/3600 )
		mins = int ( ( remainTime - hours * 3600 )/60 )
		secs = int( remainTime - hours * 3600 - mins * 60 )
		timeStr = "%02d:%02d:%02d"%( hours, mins, secs )
		return timeStr
	
	def __onQuestStateChanged( self, questID, state ):
		self.__setDegree()
		for pyViewItem in self.__pyQuestList.pyViewItems:
			if pyViewItem.pyQuestItem.questID == questID:
				pyViewItem.pyQuestItem.updateQuestState( state )
				
	def __onShow( self ):
		self.show()
		
	def __onHide( self ):
		self.hide()
	
	def __onRewardQuestsUpdate( self ):
		if not self.visible:return
		self.__pyQuestList.clearItems()
		if self.__remainTimerID != 0:
			Timer.cancel( self.__remainTimerID )
			self.__remainTimerID = 0
		self.__setDegree()
		self.__remainTimerID = Timer.addTimer( 0,1, self.__setRemainTime )		
		rewardQuestRecord = GUIFacade.getRewardQuestRecord()
		self.__pyQuestList.addItems( rewardQuestRecord )
		
	def __setRemainTime( self ):
		timeInterval = GUIFacade.getNextReFreshTime() - time.time()
		if timeInterval <= 0:
			timeInterval = 0
		timeStr = self.__getTimeStr( timeInterval )
		self.__stRefreshTime.text = labelGather.getText( "QuestHelp:RewardQuestList", "stRefreshTime" ) % timeStr
		
	def __setDegree( self ):
		degree = GUIFacade.getDegree()
		degreeStr = "%s/%s" % ( csdefine.REWARD_QUEST_CAN_ACCEPT_NUM - degree, csdefine.REWARD_QUEST_CAN_ACCEPT_NUM )
		self.__stNumberTips.text = labelGather.getText( "QuestHelp:RewardQuestList", "stNumberTips" ) % ( degreeStr )
		
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def show( self ):
		self.__setDegree()
		self.__remainTimerID = Timer.addTimer( 0,1, self.__setRemainTime )		
		rewardQuestRecord = GUIFacade.getRewardQuestRecord()
		self.__pyQuestList.addItems( rewardQuestRecord )
		Window.show( self )
		
	def hide( self ):
		self.__pyQuestList.clearItems()
		if self.__remainTimerID != 0:
			Timer.cancel( self.__remainTimerID )
			self.__remainTimerID = 0
		Window.hide( self )
		
		
class QuestItem( Control ):
	
	_ITEM = None
	#品质与颜色对应字典
	_QUALITY_COLOR = { csdefine.REWARD_QUEST_QUALITY_WHITE: "c1",
					csdefine.REWARD_QUEST_QUALITY_BLUE: "c5",
					csdefine.REWARD_QUEST_QUALITY_PURPLE: "c8",
					csdefine.REWARD_QUEST_QUALITY_GREEN: "c4",
	}
	
	def __init__( self ):
		if QuestItem._ITEM is None:
			QuestItem._ITEM = GUI.load("guis/general/questlist/rewardquest/questItem.gui")
		item = util.copyGuiTree( QuestItem._ITEM )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item )
		self.__questID = ""
		self.__elements = item.elements
		self.__initialize( item )
		
	def __initialize( self, item ):
		self.__rtQuestName = CSRichText( item.rtQuestName)
		self.__rtQuestName.autoNewline = False
		self.__rtQuestName.text = ""
		
		self.__rtRewards = CSRichText( item.rtRewards )
		self.__rtRewards.autoNewline = False
		self.__rtRewards.text = ""
		
		self.__btnQuest = HButtonEx( item.btnQuest )
		self.__btnQuest.setExStatesMapping( UIState.MODE_R4C1 )
		self.__btnQuest.onLClick.bind( self.__onAcceptQuest )
		
	def __onAcceptQuest( self ):
		player = BigWorld.player()
		player.rewardQuestAccept( self.__questID )
		
	def __setQuestName( self, questTitle, questQuality ):
		"""
		设置任务名称
		"""
		titleColor = QuestItem._QUALITY_COLOR.get( questQuality )
		if titleColor is None: titleColor = "c1"
		self.__rtQuestName.text = PL_Font.getSource( questTitle, fc = titleColor )
		
	def __setQuestState( self, questState ):
		"""
		根据任务状态设置按钮的enable以及文字
		"""
		if questState == csdefine.REWARD_QUEST_CAN_ACCEPT:#可接
			self.__btnQuest.enable = True
			labelGather.setPyBgLabel( self.__btnQuest, "QuestHelp:RewardQuestList", "btnAccept" )
		elif questState == csdefine.REWARD_QUEST_ACCEPT:
			self.__btnQuest.enable = False
			labelGather.setPyBgLabel( self.__btnQuest, "QuestHelp:RewardQuestList", "btnAccept" )
		elif questState == csdefine.REWARD_QUEST_COMPLETED:
			self.__btnQuest.enable = False
			labelGather.setPyBgLabel( self.__btnQuest, "QuestHelp:RewardQuestList", "btnCompleted" )
		
	def updateQuest( self, questInfo ):
		rewardQuest = questInfo
		questID = rewardQuest.getQuestID()
		self.__questID = questID
		questTitle = rewardQuest.getTitle()
		questQuality = rewardQuest.getQuality()
		questState = GUIFacade.getQuestStateByID( questID )
		rewards = GUIFacade.getRewardByQuestID( questID )
		self.__setQuestName( questTitle, questQuality )
		self.__setQuestState( questState )
		exp = 0
		money = 0
		if rewards.has_key( "rewards_exp" ):
			exp = int( rewards["rewards_exp"].getDescription() )
		if rewards.has_key("rewards_money" ):
			money = int( rewards["rewards_money"].getDescription() )
		self.__rtRewards.text = PL_Font.getSource( labelGather.getText( "QuestHelp:RewardQuestList", "rewardsText" ), fc = ( 230, 227,185 ))
		if exp != 0:
			self.__rtRewards.text += PL_Space.getSource( 1 )
			self.__rtRewards.text += PL_Font.getSource( labelGather.getText( "QuestHelp:RewardQuestList", "expText" )% exp, fc = ( 230, 227,185 ))
		if money != 0:
			self.__rtRewards.text += PL_Space.getSource( 1 )
			moneyText = utils.currencyToViewText( money )
			self.__rtRewards.text += PL_Font.getSource( moneyText, fc = ( 230, 227, 185 ) )
		
	def updateQuestState( self, state ):
		self.__setQuestState( state )
	
	
	def setHighLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=1


	def setCommonLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=0
					
	def _getQuestID( self ):
		return self.__questID
		

	#--------------------------------------------
	#properties
	#--------------------------------------------
	questID = property( _getQuestID )					
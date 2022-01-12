# -*- coding: gb18030 -*-
#
# $Id: DspPanel.py,v 1.25 2008-07-03 10:00:26 fangpengjun Exp $

"""
implement rewawrds panel class
"""

from guis import *
import csdefine
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.general.npctalk.Rewards import RW_TYPE_ITEM
from guis.general.npctalk.Rewards import RW_TYPE_MONEY
from guis.general.npctalk.Rewards import RW_TYPE_OTHER
from guis.general.npctalk.Rewards import RW_TYPE_SKILL
from guis.general.npctalk.Rewards import RW_TYPE_AIM
from guis.general.npctalk.Rewards import CRewardPanel
from guis.general.npctalk.Rewards import CRewardItem
from guis.general.npctalk.Rewards import RW_TYPE_FIXED_RANDOM_ITEM
from ItemsFactory import ObjectItem
from ItemsFactory import SkillItem
from FactionMgr import factionMgr
from LabelGather import labelGather
from CrondScheme import Scheme
from Time import Time
from bwdebug import *
from GUIFacade import *
import Font

class DspPanel( Control ) :
	def __init__( self, pyBinder = None ) :
		wnd = GUI.load( 'guis/general/questlist/dspItem.gui' )
		uiFixer.firstLoadFix( wnd )
		Control.__init__( self,wnd  )
		self.__pyDivit = PyGUI( wnd.divition )
		self.__pyDivit.visible = False
		title = wnd.title
		self.__pyTitle = PyGUI( title )
		self.__pyPoint = PyGUI( title.point )
		self.__pyLbTitle = StaticText( title.lbText )
		self.__pyLbTitle.font = "STLITI.TTF"
		self.__pyLbTitle.color = ( 231, 205, 140, 255 )
		self.__pyLbTitle.limning = Font.LIMN_OUT
		self.__pyLbTitle.limnColor = ( 0, 0, 0,255 )
		self.__pyLbTitle.text = ""
		self.__pyStateItem = None
		self.width = pyBinder.width
		self.pyItems_ = []
		self.__viewCols = 1

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addItemRewards( self, pyPanel, rewards ) : # 在面板中添加物品
		if rewards is not None:
			for reward in rewards :
				schemeInfo = reward.query( "schemeInfo" )
				if schemeInfo:
					cmd, presistMinute = schemeInfo.split("|")
					presistMinute = int( presistMinute )
					scheme = Scheme()
					scheme.init( cmd )
					year, month, day, hour, minute = Time.localtime( Time.time() - presistMinute * 60 )[:5]
					nextTime = scheme.calculateNext( year, month, day, hour, minute )
					if nextTime > Time.time():
						continue
				pyItem = CRewardItem[RW_TYPE_ITEM]()
				pyItem.canbeSelected = False
				pyItem.updateItem( ObjectItem( reward ) )
				pyPanel.addItem( pyItem )
		else:
			pyItem = CRewardItem[RW_TYPE_ITEM]()
			pyItem.canbeSelected = False
			pyItem.updateItem( None )
			pyPanel.addItem( pyItem )
		if len( pyPanel.pyItems ) <= 0:
			pyPanel.setCommon()
			pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_4" )
		else:
			pyPanel.layout_()
		self.addItem( pyPanel )
		self.height = pyPanel.bottom

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem ) :
		pyItem.index = self.itemCount
		self.addPyChild( pyItem )
		self.pyItems_.append( pyItem )
		self.layoutItems_( self.itemCount - 1 )

	def addDescription( self, dsp ) :
		pyItem = DspItem()
		self.addItem( pyItem )
		self.height = pyItem.bottom 
		pyItem.width = self.width - pyItem.left
		pyItem.title = labelGather.getText( "QuestHelp:dspPanel", "itemTitle_1" )
		pyItem.description = dsp
		pyItem.visualSplitter( False )
#		self.__setScrollState()

	def addObjectText( self, dsp ):
		if dsp.strip() == "":return
		pyItem = DspItem()
		self.addItem( pyItem )
	#	self.height = pyItem.bottom 
		pyItem.width = self.width - pyItem.left
#		pyItem.title = labelGather.getText( "QuestHelp:dspPanel", "itemTitle_2" )
		pyItem.description = dsp
		pyItem.visualSplitter( False )
		self.height = pyItem.bottom 
#		self.__setScrollState()

	def addFinishState( self, conditions ) : # 一个任务可能有多个任务条件
		if conditions == {} : return
		aimPanel = CRewardPanel[RW_TYPE_AIM]()
		aimPanel.width = self.width
		aimPanel.clearItems()
#		aimPanel.title = labelGather.getText( "QuestHelp:dspPanel", "itemTitle_3" )
		tempConditions = []
		for index, condition in conditions.items():
			tempConditions.append( index )
		tempConditions.sort() # 任务条件按index排序
		for index in tempConditions:
			condition = conditions[index]
			condText = labelGather.getText( "QuestHelp:dspPanel", "conditions" ) % ( condition["title"], condition["tag"], condition["stateText"],condition["forceTips"] )
			pyAimItem = CRewardItem[RW_TYPE_AIM]()
			pyAimItem.aimCondition = condText
			pyAimItem.aimIndex = index
			pyAimItem.maxWidth = self.width
			aimPanel.addItem( pyAimItem )
		self.addItem( aimPanel )
		self.height = aimPanel.bottom 

		self.__pyStateItem = aimPanel

	def addCommonRewards( self, singleRewards, otherRewards ) : # 固定物品奖励，金钱，经验等
		pyPanel = None
		if singleRewards is not None :
			pyPanel = CRewardPanel[RW_TYPE_ITEM]()
			pyPanel.setCommon()
			pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" )
			self.__addItemRewards( pyPanel, singleRewards._items )
		if len( otherRewards ) > 0 :
			if pyPanel is None :
				pyPanel = CRewardPanel[RW_TYPE_OTHER]()
				pyPanel.setCommon()
				pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_4" )
			else :
				pyPanel = self
			for reward in otherRewards:
				if reward.type() == csdefine.QUEST_REWARD_MONEY:
					# 金钱奖励
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					moneyPanel.setMoney( money )
					pyPanel.addItem( moneyPanel )
					pyPanel.height += moneyPanel.height
				elif reward.type() == csdefine.QUEST_REWARD_MULTI_MONEY:
					# 多倍金钱奖励
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					multiFlag = reward._multiFlag
					moneyPanel.setMoney( money, multiFlag )
					pyPanel.addItem( moneyPanel )
					pyPanel.height += moneyPanel.height
				else:
					rwardItem = CRewardItem[RW_TYPE_OTHER]()
					if reward.type() == csdefine.QUEST_REWARD_TITLE:# 称号奖励
						arg = reward._amount
					elif reward.type() == csdefine.QUEST_REWARD_PRESTIGE:
						npcPrestigeID = reward._prestigeID
						prestigeName = factionMgr.getName( npcPrestigeID )
						arg = prestigeName+"  "+str( reward._amount ) # 声望，势力
					else:
						arg = reward.getDescription() # 经验，潜能奖励
					rwardItem.setValueText( reward.type(), arg )
					pyPanel.addItem( rwardItem )
					pyPanel.height += rwardItem.height
					
			if pyPanel != self :
				self.addItem( pyPanel )
				self.height  = pyPanel.bottom
#				self.__setScrollState()

	def addFixedItemReward( self, reward ):
		if reward is not None:
			if reward.type() == csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS: #固定随机物品
				if not reward.isItem:										# 只显示奖励描述，该值的设置见QuestReward.py。 by cwl
					pyRewardItem = CRewardItem[RW_TYPE_FIXED_RANDOM_ITEM]()
					pyRewardItem.setValueText( reward.type(), "      "+reward.str )
					self.addItem( pyRewardItem )
					self.height = pyRewardItem.bottom
				else:
					pyPanel = CRewardPanel[RW_TYPE_ITEM]()
					pyPanel.setCommon()
					pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_6" )
					self.__addItemRewards( pyPanel, reward._items )		# 附加物品显示
					#self.__setScrollState()

	def addSingleItemReward( self, rewards ) : #固定奖励
		if rewards is None : return
		pyPanel = CRewardPanel[RW_TYPE_ITEM]()
		pyPanel.setCommon()
		pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" )
		self.__addItemRewards( pyPanel, rewards._items )

	def addRandomItemsReward( self, rewards ) : # 随机奖励
		if rewards is None : return
		pyPanel = CRewardPanel[RW_TYPE_ITEM]()
		pyPanel.setCommon()
		pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_2" )
		self.__addItemRewards( pyPanel, rewards._items )

	def addOptionItemReward( self, rewards ) : # 可选奖励
		if rewards is None : return
		pyPanel = CRewardPanel[RW_TYPE_ITEM]()
		pyPanel.setCommon()
		pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_3" )
		self.__addItemRewards( pyPanel, rewards._items )

	def addRoleLevelReward( self, rewards ):
		if rewards is None : return
		pyPanel = CRewardPanel[RW_TYPE_ITEM]()
		pyPanel.setCommon()
		pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_5" )
		self.__addItemRewards( pyPanel, rewards._items )
		
	def getCurrentPercentage( self, completedTasksNum, rewards ):
		sonRewards = rewards.sonRewards
		currentReward = sonRewards.get( completedTasksNum )
		maxReward = sonRewards.get( len( sonRewards ) )
		percentage = ( float( currentReward[0].getDescription() )/float( maxReward[0].getDescription() ) ) * 100
		percentage = int( round( percentage ) )
		return percentage
	
	def addRewardsQuestPartCompleted( self, questID, rewards ): #完成部分任务目标可以获得的奖励
		if rewards is None:return
		completedTasksNum = GUIFacade.getCompletedTasksNum( questID )
		percentageStr = ""
		if completedTasksNum == 0 or completedTasksNum == 1:
			percentage = 0
			completedTasksNum = 1		#如果没有完成任何的目标，显现的是最少的奖励（即是完成一个任务目标的奖励）			
			percentageStr = PL_Font.getSource( "+%s%%"%percentage, fc = "c3" )
		else:
			percentage = self.getCurrentPercentage( completedTasksNum, rewards )
			percentageStr = PL_Font.getSource( "+%s%%"%percentage, fc = "c4" )
		sonRewards = rewards.sonRewards.get( completedTasksNum )
		pyPanel = None
		tipNum = 0
		isLastSecondTarget = completedTasksNum +1 == len( rewards.sonRewards )		# 倒数第二个才显示未知物品
		if self.checkHasItemReward( rewards.sonRewards ) and not self.checkSonRewardHasItemReward( sonRewards ) and isLastSecondTarget:	#显示个空的物品
		
			pyItemPanel = CRewardPanel[RW_TYPE_ITEM]()
			pyItemPanel.setCommon()
			if tipNum == 0:
				tipNum += 1
				pyItemPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" ) + percentageStr
			else:
				pyItemPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" )
			self.__addItemRewards( pyItemPanel, None )
			
		
		for reward in sonRewards:									
			if pyPanel is None:
				pyPanel = CRewardPanel[RW_TYPE_OTHER]()
				pyPanel.setCommon()
				pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_4" )
			if reward.type() == csdefine.QUEST_REWARD_MONEY:
				# 金钱奖励
				moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
				money = reward._amount
				moneyPanel.setMoney( money )
				pyPanel.addItem( moneyPanel )
				pyPanel.height += moneyPanel.height
			elif reward.type() == csdefine.QUEST_REWARD_MULTI_MONEY:
				# 多倍金钱奖励
				moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
				money = reward._amount
				multiFlag = reward._multiFlag
				moneyPanel.setMoney( money, multiFlag )
				pyPanel.addItem( moneyPanel )
				pyPanel.height += moneyPanel.height
			elif reward.type() == csdefine.QUEST_REWARD_ITEMS:
				pyItemPanel = CRewardPanel[RW_TYPE_ITEM]()
				pyItemPanel.setCommon()
				if tipNum == 0:
					tipNum += 1
					pyItemPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" ) + percentageStr
				else:
					pyItemPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_1" )
				self.__addItemRewards( pyItemPanel, reward._items )
			else:
				rwardItem = CRewardItem[RW_TYPE_OTHER]()
				if reward.type() == csdefine.QUEST_REWARD_TITLE:# 称号奖励
					arg = reward._amount
				elif reward.type() == csdefine.QUEST_REWARD_PRESTIGE:
					npcPrestigeID = reward._prestigeID
					prestigeName = factionMgr.getName( npcPrestigeID )
					arg = prestigeName+"  "+str( reward._amount ) # 声望，势力
				else:
					arg = reward.getDescription() # 经验，潜能奖励
				rwardItem.setValueText( reward.type(), arg )
				pyPanel.addItem( rwardItem )
				pyPanel.height += rwardItem.height
		if tipNum == 0:
			tipNum += 1
			pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_4" ) + percentageStr
		else:
			pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_4" )
		self.addItem( pyPanel )
		self.height  = pyPanel.bottom
	
	def addSkillRewards( self, skillRewards ):
		if not len( skillRewards ):return
		pyPanel = CRewardPanel[RW_TYPE_SKILL]()
		pyPanel.title = labelGather.getText( "QuestHelp:dspPanel", "CRewardTitle_7" )
		for index, skReward in enumerate( skillRewards ):
			pyItem = CRewardItem[RW_TYPE_SKILL]()
			pyItem.index = index
			pyItem.canbeSelected = False
			pyItem.foucs = True
			skillInfo = SkillItem( skReward._skill )
			pyItem.updateItem( skillInfo )
			pyPanel.addItem( pyItem )
			pyPanel.layout_()
		self.addItem( pyPanel )
		self.height = pyPanel.bottom
		
	def checkHasItemReward( self, rewards ):
		"""
		判断全部奖励是否包含物品奖励
		"""
		hasItemReward = False
		for rewards in rewards.itervalues():
			for reward in rewards:
				if reward.type() == csdefine.QUEST_REWARD_ITEMS:
					hasItemReward = True
		return hasItemReward
		
	def checkSonRewardHasItemReward( self, rewards ):
		"""
		判断子奖励中是否包含物品奖励
		"""				
		hasItemReward = False
		for reward in rewards:
			if reward.type() == csdefine.QUEST_REWARD_ITEMS:
				hasItemReward = True
		return hasItemReward

	def addFeastText( self, dsp ):
		if dsp.strip() == "":return
		pyItem = DspItem()
		self.addItem( pyItem )
		self.height = pyItem.bottom
		pyItem.width = self.width - pyItem.left
		pyItem.title = ""
		pyItem.description = dsp
		pyItem.visualSplitter( False )

	# ---------------------------------------
	def resetFinishState( self, conditions ) :
		for pyItem in self.__pyStateItem.pyItems:
			aimIndex = pyItem.aimIndex
			condition = conditions.get( aimIndex, None )
			if condition is None:return
			conditionText = "%s: %s  %s" %( condition["title"], condition["tag"], condition["stateText"] )
			pyItem.aimCondition = conditionText
			
	#--------------------------------------------
	# propected
	#---------------------------------------------
	def layoutItems_( self, startIndex = 0 ) :
		itemCount = self.itemCount
		if itemCount == 0 : return
		if startIndex >= itemCount : return
		pyItem = self.pyItems_[startIndex]
		pyItem.left = 0
		if startIndex == 0 :
			pyItem.top = 15
		else :
			pyItem.top = self.pyItems_[startIndex - 1].bottom
		for pyNextItem in self.pyItems_[( startIndex + 1 ):] :
			pyNextItem.left = 0
			pyNextItem.top = pyItem.bottom
			pyItem = pyNextItem
			
	#-----------------------------------------------
	# property methods
	#-----------------------------------------------
			
	def _getItems( self ) :
		return self.pyItems_[:]

	def _getItemCount( self ) :
		return len( self.pyItems_ )
	
	def _setDivtVisible( self, visible ):
		self.__pyDivit.visible = visible
	
	def _getDivtVisible( self ):
		return self.__pyDivit.visible
	
	def _getTitle( self ):
		return self.__pyLbTitle.text
	
	def _setTitle( self, title ):
		self.__pyLbTitle.text = title
		self.__pyLbTitle.left = self.__pyPoint.right + 5.0
		
	#----------------------------------------
	# properties
	#----------------------------------------
	itemCount = property( _getItemCount )							# get the number of items
	pyItems = property( _getItems )
	divtVisible = property( _getDivtVisible, _setDivtVisible )
	title = property( _getTitle, _setTitle )
# --------------------------------------------------------------------
# implement
# --------------------------------------------------------------------
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from  guis.general.npctalk.Rewards import CSRichText

class DspItem( Control ) :
	__cg_item = None

	def __init__( self ) :
		if DspItem.__cg_item is None :
			DspItem.__cg_item = GUI.load( "guis/general/questlist/dsppanel.gui" )

		item = util.copyGuiTree( DspItem.__cg_item )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item )
		self.__pyLbTitle = StaticText( item.lbTitle )
		self.__pyRTDsp = CSRichText( item.rtDsp )
		self.__pyRTDsp.opGBLink = True
		self.__spliter = item.spliter


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def visualSplitter( self, visible ) :
		self.__spliter.visible = visible

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTitle( self ) :
		return self.__pyLbTitle.text

	def _setTitle( self, title ) :
		self.__pyLbTitle.text = title

	# -------------------------------------------------
	def _getDescription( self ) :
		return self.__pyRTDsp.text

	def _setDescription( self, dsp ) :
		dsp = PL_Font.getSource( dsp, fc = ( 230, 227, 185, 255 ) )
		self.__pyRTDsp.text = dsp
		self.height = self.__pyRTDsp.bottom + 5

	def _setWidth( self, width ) :
		Control._setWidth( self, width )
		self.__pyRTDsp.maxWidth = width - self.__pyRTDsp.left


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	title = property( _getTitle, _setTitle )
	description = property( _getDescription, _setDescription )
	width = property( Control._getWidth, _setWidth )
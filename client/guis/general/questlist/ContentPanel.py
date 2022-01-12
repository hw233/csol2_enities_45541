# -*- coding: gb18030 -*-
from guis import *
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.CSRichText import CSRichText
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from DspPanel import DspPanel
import GUIFacade
from LabelGather import labelGather
import csdefine
import Font

class ContentPanel( ItemsPanel ):
	def __init__( self, panel, scrollBar ):
		ItemsPanel.__init__(self, panel, scrollBar )
		self.perScroll = 60.0
		self.__dspItemsCount = 0
		self.__pyQTCondition = None

		
	#--------------------------------------
	# public
	#--------------------------------------
	def addTitle( self, title ):
		pyTitle = CSRichText()
		pyTitle.maxWidth = self.width
		pyTitle.font = "STLITI.TTF"
		pyTitle.fontSize = 20.0
		pyTitle.limning = Font.LIMN_OUT
		pyTitle.foreColor = ( 231, 205, 140, 255 )
		pyTitle.limnColor = ( 0, 0, 0, 255 )
		pyTitle.align = "C"
		pyTitle.text = title
		self.addItem( pyTitle )
		pyTitle.top = 16.0
	
	def addContext( self,context ):
		"""
		"""
		pyQTContext = ContextPanel( self )
		pyQTContext.title = "任务描述"
		pyQTContext.context = context
		self.addItem( pyQTContext )	
	
	def addCondition( self, questID, itemInfo ):
		"""
		"""
		self.__pyQTCondition = DspPanel( self ) # 任务条件
		self.__pyQTCondition.title = "任务目标"
		self.__pyQTCondition.divtVisible = False
		self.__pyQTCondition.width = self.width
		if GUIFacade.getCompleteRuleType( questID ) == csdefine.QUEST_COMPLETE_RULE_PART_TASK_COM:
			conditionTips = CSRichText()
			conditionTips.autoNewline = True
			conditionTips.fontSize = 12
			conditionTips.foreColor = (0, 255, 0, 255 )
			conditionTips.maxWidth = self.__pyQTCondition.width
			conditionTips.text = labelGather.getText( "QuestHelp:dspPanel", "conditionTips" )	
			self.__pyQTCondition.addItem( conditionTips )				
		self.__dspItemsCount = len( self.__pyQTCondition.pyItems ) 	
#		self.__pyQTCondition.addObjectText( itemInfo.objectText )
		self.__pyQTCondition.addFinishState( itemInfo.conditions )
		self.addItem( self.__pyQTCondition )
		
	def addRewards( self, questID ):
		"""
		"""
		commonRewards = GUIFacade.getPreCommonRewards( questID )
		singleItemReward = GUIFacade.getPreSingleItemReward( questID )
		randomItemReward = GUIFacade.getPreRandomItemsReward( questID )
		optionalItemReward = GUIFacade.getPreOptionalItemReward( questID )
		randomfixedReward = GUIFacade.getPreFixRandomItemReward( questID )
		roleLevelReward = GUIFacade.getRoleLevelItemReward( questID )
		rewardQuestPartCompleted = GUIFacade.getPreRewardsQuestPartCompleted( questID )
		skillRewards = GUIFacade.getQuestLogSkillRewards( questID )
		fixedItemsFromClass = GUIFacade.getPreRewardsFixedItemsFromClass( questID )
		pyQTReward = DspPanel( self ) # 任务奖励
		pyQTReward.title = "任务奖励"
		pyQTReward.addRoleLevelReward( roleLevelReward ) #角色等级奖励
		pyQTReward.addCommonRewards( singleItemReward, commonRewards ) # 普通奖励，金钱，经验等奖励
		pyQTReward.addRandomItemsReward( randomItemReward ) #随机奖励
		pyQTReward.addOptionItemReward( optionalItemReward ) # 可选奖励
		pyQTReward.addFixedItemReward( randomfixedReward ) # 固定随机奖励
		pyQTReward.addSingleItemReward( fixedItemsFromClass ) #根据玩家职业给予不同的固定物品奖励
		pyQTReward.addSkillRewards( skillRewards )	#技能奖励
		pyQTReward.addRewardsQuestPartCompleted( questID, rewardQuestPartCompleted )	#完成部分任务目标就可以获得奖励
		self.addItem( pyQTReward )
		
#	def layOut( self ):
#		"""
#		重新排列版面
#		
#		"""
#		self.__pyQTContext.top = 10
#		self.__pyQTCondition.top = self.__pyQTContext.bottom 
#		self.__pyQTReward.top =  self.__pyQTCondition.bottom
		
	#-----------------------------------
	# property methods
	#-----------------------------------

		
	def _getQTCondition( self ):
		return self.__pyQTCondition
				
	def _getItems( self ) :
		return self.pyItems_[:]
		
	def _getDspItemsCount( self ):
		return self.__dspItemsCount

	
	#------------------------------------
	# properties
	#-------------------------------------
	
	pyQTCondition = property( _getQTCondition )
	dspItemsCount = property( _getDspItemsCount )
	pyItems = property( _getItems )	

class ContextPanel( PyGUI ):
	def __init__( self, pyBinder = None ):
		panel = GUI.load( "guis/general/questlist/context.gui" )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.__pyDivit = PyGUI( panel.divition )
		self.__pyDivit.visible = False
		title = panel.title
		self.__pyTitle = PyGUI( title )
		self.__pyPoint = PyGUI( title.point )
		self.__pyLbTitle = StaticText( title.lbText )
		self.__pyLbTitle.font = "STLITI.TTF"
		self.__pyLbTitle.color = ( 231, 205, 140, 255 )
		self.__pyLbTitle.limning = Font.LIMN_OUT
		self.__pyLbTitle.limnColor = ( 0, 0, 0,255 )
		self.__pyLbTitle.text = ""
		self.__pyContext = CSRichText( panel.rtContext )
		self.__pyContext.limning = Font.LIMN_NONE
		self.__pyContext.font = "MSYHBD.TTF"
		self.__pyContext.fontSize = 12.0
		self.__pyContext.text = ""
		self.__pyContext.maxWidth = pyBinder.width
		self.__pyContext.autoNewline = True
		self.__pyContext.opGBLink = True
		self.width = pyBinder.width

	def _getTitle( self ):
		return self.__pyLbTitle.text
	
	def _setTitle( self, title ):
		self.__pyLbTitle.text = title
		self.__pyLbTitle.left = self.__pyPoint.right + 5.0
	
	def _getConText( self ):
		return self.__pyContext.text
	
	def _setConText( self, context ):
		self.__pyContext.text = context
		self.height = self.__pyContext.bottom + 3.0

	title = property( _getTitle, _setTitle )
	context = property( _getConText, _setConText )
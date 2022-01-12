# -*- coding: gb18030 -*-
#
# $Id: Rewards.py,v 1.36 2008-08-25 09:26:25 huangyongwei Exp $


from guis import *
import ItemTypeEnum
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.controls.SkillItem import SkillItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csdefine
import GUIFacade
import Language
import Font

RW_TYPE_MONEY	= 0
RW_TYPE_OTHER	= 1
RW_TYPE_ITEM	= 2
RW_TYPE_AIM		= 3
RW_TYPE_TIMER	= 4
RW_TYPE_SUBMIT	= 5
RW_TYPE_FIXED_RANDOM_ITEM = 6
RW_TYPE_NONE	= 7				#无目标，做占位使用
RW_TYPE_SKILL	= 8

TITLE_FONT = "STLITI.TTF"
CONT_FONT = "MSYHBD.TTF"
CONT_FONT_SIZE = 12
TITLE_FONT_SIZE = 16
TITLE_FONT_COLOR = ( 231, 205, 140, 255 )


class RewardPanel( PyGUI ) :
	__cg_panel = None

	def __init__( self ) :
		if RewardPanel.__cg_panel is None :
			RewardPanel.__cg_panel = GUI.load( "guis/general/npctalk/rewardpanel.gui" )
		panel = util.copyGuiTree( RewardPanel.__cg_panel )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.pySpliter_ = PyGUI( panel.spliter )
		self.pyPoint = PyGUI( panel.sign )
		self.pyPoint.visible = False
		self.pyRTTitle_ = CSRichText( panel.rtTitle )
		self.pyRTTitle_.opGBLink = True
		self.pyRTTitle_.maxWidth = self.width - self.pyRTTitle_.left
		#self.pyRTTitle_.font = QuestView.getRewardTitleFont()				# QuestView 不用了,( 2008.05.19 )
		#self.pyRTTitle_.foreColor = QuestView.getRewardTitleColor()
		self.pyRTTitle_.text = ""
		self.pyRTTitle_.top = 2.0
		self.pyRTTitle_.foreColor = TITLE_FONT_COLOR
		self.pyRTTitle_.limning = Font.LIMN_OUT
		self.pyRTTitle_.font = TITLE_FONT
		self.pyRTTitle_.fontSize = TITLE_FONT_SIZE
		self.pyPoint.top = 2.0
		self.isCommn = False
		self.width = 255.0
		self.__pyItems = []

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def layout_( self ) :
		pass

	# -------------------------------------------------
	def onRewardItemSelected_( self, pyItem ) :
		pass

	def onRewardItemDeselected_( self, pyItem ) :
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addItem( self, pyItem ) :
		pyItem.index = self.itemCount
		self.addPyChild( pyItem )
		pyItem.pos = 0,0
		self.__pyItems.append( pyItem )
		if hasattr( pyItem, "onSelected" ) :
			pyItem.onSelected.bind( self.onRewardItemSelected_ )
		self.layout_()

	def delItem( self, pyItem ) :
		if pyItem in self.__pyItems :
			self.delPyChild( pyItem )
			self.__pyItems.remove( pyItem )
			if hasattr( pyItem, "onSelected" ) :
				pyItem.onSelected.unbind( self.onRewardItemSelected_ )
		self.layout_()

	def clearItems( self ) :
		for pyItem in self.__pyItems :
			self.delPyChild( pyItem )
			if hasattr( pyItem, "onSelected" ) :
				pyItem.onSelected.unbind( self.onRewardItemSelected_ )
		self.__pyItems = []
		self.layout_()

	# --------------------------------------------
	def visualSplitter( self, visible ) :
		self.pySpliter_.visible = visible
	
	def setCommon( self ):
		self.isCommn = True
		self.pyRTTitle_.foreColor = ( 51, 76, 97, 255 )
		self.pyRTTitle_.limning = Font.LIMN_NONE
		self.pyRTTitle_.font = CONT_FONT
		self.pyRTTitle_.fontSize = CONT_FONT_SIZE
		self.pyRTTitle_.top = 10.0
		self.pyPoint.visible = 0

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getTitle( self ) :
		return self.pyRTTitle_.text

	def _setTitle( self, title ) :
		self.pyRTTitle_.text = title
		
		if title == "":
			self.pyPoint.visible = False
		else:
			if self.isCommn:
				self.pyPoint.visible = False
				return
			self.pyPoint.visible = True

	# -------------------------------------------------
	def _getItemCount( self ) :
		return len( self.__pyItems )

	def _getPyItems( self ) :
		return self.__pyItems

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	title = property( _getTitle, _setTitle )
	itemCount = property( _getItemCount )
	pyItems = property( _getPyItems )

## --------------------------------------------------------------------
## implement common reward
## --------------------------------------------------------------------
#class CommonRewardPanel( RewardPanel ) : #普通奖励
#
#	__cc_item_height = 20
#
#	def __init__( self ) :
#		RewardPanel.__init__( self )
#		self.rewardType = rewardType
#
#	# ----------------------------------------------------------------
#	# protected
#	# ----------------------------------------------------------------
#	def layout_( self ) :
#		for index, pyItem in enumerate( self.pyItems ) :
#			pyItem.left = self.pyRTTitle_.left
#			itemsTop = self.pyRTTitle_.bottom + self.pySpliter_.top
#			pyItem.top = itemsTop + index * self.__cc_item_height
#		self.height = self.itemCount > 0 and self.pyItems[-1].bottom + 2 or 0
#
#	# ----------------------------------------------------------------
#	# property methods
#	# ----------------------------------------------------------------
#	def _getRewardType( self ) :
#		return RW_TYPE_COMMON
#
#	# ----------------------------------------------------------------
#	# proeprties
#	# ----------------------------------------------------------------
#	rewardType = property( _getRewardType )

# --------------------------------------------------------------------
# implement static icons panel class。
# --------------------------------------------------------------------
class ItemRewardPanel( RewardPanel ) : #物品奖励
	__cc_cols	= 2

	def __init__( self ) :
		RewardPanel.__init__( self )

		self.__pySelItem = None
		self.__cols = 2

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def layout_( self ) :
		offset = 0.0
		if self.__cols == 1:
			offset = 40.0
		else:
			offset = 25.0
		for index, pyItem in enumerate( self.pyItems ) :
			pyItem.left = ( index % self.__cols ) * s_util.getGuiWidth( pyItem.getGui() ) + offset
			itemsTop = self.pyRTTitle_.bottom + self.pySpliter_.top
			pyItem.top = itemsTop + ( index / self.__cols ) * s_util.getGuiHeight( pyItem.getGui() )
		if self.__cols > 1:
			self.width = self.__cols *  s_util.getGuiWidth( self.pyItems[0].getGui() ) + offset
		self.height = self.itemCount > 0 and self.pyItems[-1].bottom or 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRewardItemSelected_( self, pyItem ) :
		self.__pySelItem = pyItem
		for tmpItem in self.pyItems :
			if tmpItem != pyItem :
				tmpItem.selected = False

	def onRewardItemDeselected_( self, pyItem ) :
		pass

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_ITEM

	# -------------------------------------------------
	def _getSelItem( self ) :
		return self.__pySelItem

	def _setSelItem( self, pyItem ) :
		if pyItem:
			pyItem.selected = True
		self.__pySelItem = pyItem
	
	def _getCols( self ):
		return self.__cols
	
	def _setCols( self, cols ):
		self.__cols = cols

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )
	pySelItem = property( _getSelItem, _setSelItem )
	cols = property( _getCols, _setCols )

class SkillRewardPanel( ItemRewardPanel ):
	
	def __init__( self ) :
		ItemRewardPanel.__init__( self )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_SKILL

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )

class OtherPanel( RewardPanel ):

	def __init__( self ) :
		RewardPanel.__init__( self )

		self.__pySelItem = None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def layout_( self ) :
		itemsTop = self.pyRTTitle_.bottom + self.pySpliter_.top
		maxWidth = 0.0
		if len( self.pyItems ) > 0:
			maxWidth = max( [pyItem.width for pyItem in self.pyItems] )
		for index, pyItem in enumerate( self.pyItems ) :
			pyItem.left = self.pyRTTitle_.left + 2.0
			if index < 1:
				pyItem.top = itemsTop
			else:
				pyItem.top = self.pyItems[index - 1].bottom
		self.width = max( maxWidth, 325.0 )
		self.height = self.itemCount > 0 and self.pyItems[-1].bottom or 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRewardItemSelected_( self, pyItem ) :
		self.__pySelItem = pyItem
		for tmpItem in self.pyItems :
			if tmpItem != pyItem :
				tmpItem.selected = False

	def onRewardItemDeselected_( self, pyItem ) :
		pass

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_OTHER

	# -------------------------------------------------
	def _getSelItem( self ) :
		return self.__pySelItem

	def _setSelItem( self, pyItem ) :
		pyItem.selected = True

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )
	pySelItem = property( _getSelItem, _setSelItem )
# --------------------------------------------------------------------
# aimpanel
# --------------------------------------------------------------------
class AimPanel( RewardPanel ): # 任务目标Panel
	def __init__( self ):
		RewardPanel.__init__( self )
		self.__pySelItem = None

	def layout_( self ) :
		itemsTop = self.pyRTTitle_.bottom + self.pySpliter_.top
		for index, pyItem in enumerate( self.pyItems ) :
			pyItem.left = self.pyRTTitle_.left + 2.0
			if index < 1:
				pyItem.top = itemsTop
			else:
				pyItem.top = self.pyItems[index - 1].bottom
		self.height = self.itemCount > 0 and self.pyItems[-1].bottom or 0

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_AIM
#	# --------------------------------------------
#	def _getObjectText( self ):
#		return self.__pyObjectText.text
#
#	def _setObjectText( self, text ):
#		self.__pyObjectText.text = text
#	# --------------------------------------------
#
#	objectText = property( _getObjectText, _setObjectText )
	rewardType = property( _getRewardType )
# --------------------------------------------------------------------
# submitpanel
# --------------------------------------------------------------------
class SubmitPanel( RewardPanel ):
	def __init__( self ):
		RewardPanel.__init__( self )
		self.__pySelItem = None

	def layout_( self ) :
		maxWidth = 0.0
		if len( self.pyItems ) > 0:
			maxWidth = max( [pyItem.width for pyItem in self.pyItems] )
		for index, pyItem in enumerate( self.pyItems ) :
			pyItem.left = self.pyRTTitle_.left
			itemsTop = self.pyRTTitle_.bottom + self.pySpliter_.top
			pyItem.left = self.pyRTTitle_.left + 10.0
			pyItem.top = itemsTop + index * pyItem.height
			self.width =  maxWidth + 10.0
			pyItem.center = self.width/2.0
		self.height = self.itemCount > 0 and self.pyItems[-1].bottom or 0

	def _getRewardType( self ) :
		return RW_TYPE_SUBMIT

	rewardType = property( _getRewardType )

class NonePanel( RewardPanel ):
	def __init__( self ):
		RewardPanel.__init__( self )
		self.__pySelItem = None
		self.height = 20.0

	def layout_( self ) :
		pass

	def _getRewardType( self ) :
		return RW_TYPE_NONE

	rewardType = property( _getRewardType )
	
# --------------------------------------------------------------------
# moneypanel
# --------------------------------------------------------------------
class MoneyPanel( PyGUI ):
	def __init__( self ):
		panel = GUI.load("guis/general/npctalk/moneypanel.gui")
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__(self, panel )
		self.__pyMoneyText = StaticText( panel.moneyText )
		self.__pyMoneyText.limning = Font.LIMN_NONE
		self.__pyMoneyText.font = CONT_FONT
		self.__pyMoneyText.fontSize = CONT_FONT_SIZE
		self.__pyMoneyText.color = ( 51, 76, 97 )
		self.__pyMoneyText.text = labelGather.getText( "NPCTalkWnd:rewards", "reward_money"  )
		self.__pyRtMoney = CSRichText( panel.rtMoney )
		self.__pyRtMoney.align = "R" #右对齐
		self.__pyRtMoney.text = ""
		self.__pyRtMoney.top = 2.0
		self.__pyRtMoney.limning = Font.LIMN_NONE
		self.__pyRtMoney.font = CONT_FONT
		self.__pyRtMoney.fontSize = CONT_FONT_SIZE

	# ---------------public--------------------
	def setMoney( self, money, mautiFlag = 1 ):
		moneyText = utils.currencyToViewText( money )
		if mautiFlag != 1:
			moneyText = moneyText + " x " + str( mautiFlag )
		self.__pyRtMoney.text = PL_Font.getSource( moneyText, fc = ( 51, 76, 97, 255 ) )

	def clearItems( self ):
		pass

	def _getRewardType( self ):

		return RW_TYPE_MONEY
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )

class FixRanItem( PyGUI ):
	def __init__( self ):
		panel = GUI.load("guis/general/npctalk/valuepanel.gui")
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.visible = True
		self.__rewardType = RW_TYPE_FIXED_RANDOM_ITEM
		self.__pyTxtText = StaticText( panel.valueText )
		self.__pyTxtText.h_anchor = "LEFT"
		self.__pyTxtText.left = 5.0
		self.__pyTxtText.color = ( 51, 76, 97 )
		self.__pyTxtText.font = CONT_FONT
		self.__pyTxtText.fontSize = CONT_FONT_SIZE
		self.__pyTxtText.text = labelGather.getText( "NPCTalkWnd:rewards", "reward_fix_random" )
		self.__pyRtValue = CSRichText( panel.rtValue )
		self.__pyRtValue.font = CONT_FONT
		self.__pyRtValue.fontSize = CONT_FONT_SIZE
		self.__pyRtValue.maxWidth = 150.0
		self.__pyRtValue.align = "L" #左对齐
		self.__pyRtValue.text = ""
		self.__pyRtValue.left = self.__pyTxtText.right + 2.0
		if Language.LANG == Language.LANG_BIG5:
			self.__pyRtValue.top = 5.0
		else:
			self.__pyRtValue.top = 8.0

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return self.__rewardType

	def _setRewardType( self, type ):

		self.__rewardType = type

	def setValueText( self, type, arg ):
		self.__pyRtValue.text = str( arg ).strip()
		self.height = self.__pyRtValue.height + 2.0

	def clearItems( self ):
		pass

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType, _setRewardType )

# --------------------------------------------------------------------
class OtherItem( PyGUI ):

	_type_dict = { csdefine.QUEST_REWARD_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_POTENTIAL: labelGather.getText( "NPCTalkWnd:rewards", "reward_potential" ),
			csdefine.QUEST_REWARD_PRESTIGE: labelGather.getText( "NPCTalkWnd:rewards", "reward_prestige" ),
			csdefine.QUEST_REWARD_RELATION_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_MERCHANT_MONEY: labelGather.getText( "NPCTalkWnd:rewards", "reward_merchant_money" ),
			csdefine.QUEST_REWARD_TONG_MONEY: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_money" ),
			csdefine.QUEST_REWARD_EXP_FROM_ROLE_LEVEL: labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_TONG_BUILDVAL: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_buildval" ),
			csdefine.QUEST_REWARD_TONG_CONTRIBUTE: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_contribute" ),
			csdefine.QUEST_REWARD_EXP_SECOND_PERCENT: labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_TONG_CONTRIBUTE_NORMAL : labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_contribute" ),
			csdefine.QUEST_REWARD_ROLE_LEVEL_MONEY : labelGather.getText( "NPCTalkWnd:rewards", "reward_money" ),
			csdefine.QUEST_REWARD_PET_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_pet_exp" ),
			csdefine.QUEST_REWARD_RELATION_PET_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_pet_exp" ),
			csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL: labelGather.getText( "NPCTalkWnd:rewards", "reward_pet_exp" ),
			csdefine.QUEST_REWARD_PET_EXP_SECOND_PERCENT: labelGather.getText( "NPCTalkWnd:rewards", "reward_pet_exp" ),
			csdefine.QUEST_REWARD_IE_TITLE: labelGather.getText( "NPCTalkWnd:rewards", "reward_ie_title" ),
			csdefine.QUEST_REWARD_DEPOSIT: labelGather.getText( "NPCTalkWnd:rewards", "reward_deposit" ),
			csdefine.QUEST_REWARD_MULTI_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_MULTI_PET_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_pet_exp" ),
			csdefine.QUEST_REWARD_MULTI_MONEY: labelGather.getText( "NPCTalkWnd:rewards", "reward_money" ),
			csdefine.QUEST_REWARD_ITEMS_QUALITY: labelGather.getText( "NPCTalkWnd:rewards", "reward_random" ),
			csdefine.QUEST_REWARD_SPECIAL_TONG_BUILDVAL: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_buildval" ),
			csdefine.QUEST_REWARD_TONG_FETE: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_fete" ),
			csdefine.QUEST_REWARD_EXP_TONG_DART : labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_TONG_ACTIONVAL : labelGather.getText( "NPCTalkWnd:rewards", "reward_tongActionVal" ),
			csdefine.QUEST_REWARD_DAOHENG : labelGather.getText( "NPCTalkWnd:rewards", "reward_daoheng" ),
			csdefine.QUEST_REWARD_RATE_MONEY_FROM_ROLE_LEVEL:labelGather.getText( "NPCTalkWnd:rewards", "reward_money" ),
			csdefine.QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL:labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_RATE_EXP_FROM_ROLE_LEVEL:labelGather.getText( "NPCTalkWnd:rewards", "reward_exp" ),
			csdefine.QUEST_REWARD_TONG_NOMAL_MONEY: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_money" ),
			csdefine.QUEST_REWARD_TONG_EXP: labelGather.getText( "NPCTalkWnd:rewards", "reward_tong_exp" ),
			}

	def __init__( self ):
		panel = GUI.load("guis/general/npctalk/valuepanel.gui")
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.visible = True
		self.__rewardType = -1
		self.__pyTxtText = StaticText( panel.valueText )
		self.__pyTxtText.h_anchor = "LEFT"
		self.__pyTxtText.limning = Font.LIMN_NONE
		self.__pyTxtText.font = CONT_FONT
		self.__pyTxtText.fontSize = CONT_FONT_SIZE
		self.__pyTxtText.text = ""
		self.__pyTxtText.color = ( 51, 76, 97 )
		self.__pyRtValue = CSRichText( panel.rtValue )
		self.__pyRtValue.limning = Font.LIMN_NONE
		self.__pyRtValue.font = CONT_FONT
		self.__pyRtValue.fontSize = CONT_FONT_SIZE
		self.__pyRtValue.align = "R" #右对齐
		self.__pyRtValue.text = ""
		if Language.LANG == Language.LANG_BIG5:
			self.__pyRtValue.top = 5.0
		else:
			self.__pyRtValue.top = 8.0
		self.pyTips = None

	def __getText( self, type ):
		text = ""
		if self._type_dict.has_key( type ):
			text = self._type_dict[type]
		return text

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return self.__rewardType

	def _setRewardType( self, type ):

		self.__rewardType = type

	def setValueText( self, type, arg ):
		self.__rewardType = type
		titleText = self.__getText( type )
		self.__pyTxtText.text = titleText
		rwText = ""
		if type in [csdefine.QUEST_REWARD_PET_EXP,\
			csdefine.QUEST_REWARD_RELATION_PET_EXP,\
			csdefine.QUEST_REWARD_PET_EXP_FROM_ROLE_LEVEL,\
			csdefine.QUEST_REWARD_PET_EXP_SECOND_PERCENT,\
			csdefine.QUEST_REWARD_MULTI_PET_EXP]:
				questLevel = -1
				selQuestID = GUIFacade.getQuestLogSelection()
				if GUIFacade.getQuestLogs().has_key( selQuestID ):
					questLevel = GUIFacade.getQuestLogs()[selQuestID]["level"]
				outPet = BigWorld.player().pcg_getActPet()
				self.__pyRtValue.text = PL_Font.getSource( str( arg ), fc = ( 51, 76, 97, 255 ) )
				if outPet and \
				questLevel > 0 and \
				abs( outPet.level - questLevel ) >= 5:
					tips = GUI.load( "guis/general/npctalk/leveltip.gui" )
					uiFixer.firstLoadFix( tips )
					self.pyTips = CSRichText( tips )
					self.pyTips.limning = Font.LIMN_NONE
					self.pyTips.font = CONT_FONT
					self.pyTips.fontSize = CONT_FONT_SIZE
					self.pyTips.maxWidth = 305.0
					self.addPyChild( self.pyTips )
					self.pyTips.left = self.__pyTxtText.left
					self.pyTips.top = self.__pyTxtText.bottom + 3.0
					self.pyTips.visibe = True
					self.pyTips.text =  PL_Font.getSource( labelGather.getText( "NPCTalkWnd:rewards", "petLevelTip" ), fc = ( 255, 0, 0, 255 ) )
					self.height = self.pyTips.bottom + 2.0
					self.width = self.pyTips.maxWidth + 5.0
		elif type == csdefine.QUEST_REWARD_EXP \
		or type == csdefine.QUEST_REWARD_POTENTIAL:
			self.__pyRtValue.text = PL_Font.getSource( str( arg ), fc = ( 51, 76, 97, 255 ) )
		elif type == csdefine.QUEST_REWARD_DEPOSIT: #显示金钱
			moneyText = utils.currencyToViewText( int( arg ) )
			self.__pyRtValue.text = moneyText
		elif type == csdefine.QUEST_REWARD_DAOHENG: #显示道行
			self.__pyRtValue.text = ""
		else:
			self.__pyRtValue.text = PL_Font.getSource( arg, fc = ( 51, 76, 97, 255 ) )

	def clearItems( self ):
		pass
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType, _setRewardType )
#	exp = property( _getExp, _setExp,"" )

#----------------------------------------------------------------------
class TimerPanel( PyGUI ):
	__cg_panel = None

	def __init__( self ):
		if TimerPanel.__cg_panel is None :
			TimerPanel.__cg_panel = GUI.load( "guis/general/npctalk/timerpanel.gui")

		panel = util.copyGuiTree( TimerPanel.__cg_panel )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.visible = True
		self.__pyLbTimer = StaticText( panel.lbTimer )
		self.__pyLbTimer.text = ""

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_TIMER

	def _getExp( self ):
		return self.__pyLbTimer.text

	def _setExp( self, time ):
		self.__pyLbTimer.text = str( time )

	def clearItems( self ):
		pass
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )
	time = property( _getExp, _setExp,"" )

 # --------------------------------------------------------------------
 # implement common reward item
 # --------------------------------------------------------------------
#class CommonReward( StaticText ) :
#	def __init__( self ) :
#		StaticText.__init__( self )
#		QuestView.commonRewardSetting( self )
#
#	# ----------------------------------------------------------------
#	# property methods
#	# ----------------------------------------------------------------
#	def _getRewardType( self ) :
#		return RW_TYPE_COMMON
#
#	# ----------------------------------------------------------------
#	# properties
#	# ----------------------------------------------------------------
#	rewardType = property( _getRewardType )

# --------------------------------------------------------------------
# implement item reward item
# --------------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.MLUIDefine import ItemQAColorMode, QAColor


class ItemReward( Control ) :
	__cg_item = None

	class ItemIcon( BaseObjectItem ) :
		"""
		可显示装备信息对比的物品格
		"""
		def __init__( self, icon, pyBinder = None ) :
			BaseObjectItem.__init__( self, icon, pyBinder = None )
			self.focus = False
			self.dropFocus = False
			self.dragFocus = False

		def onDescriptionShow_( self ) :
			equipDsps = GUIFacade.getSameTypeEquipDecriptionsII( self.itemInfo )
			toolbox.infoTip.showItemTips( self, self.description, *equipDsps ) #显示物品的描述，有比较则显示比较
	
	class SkillIcon( SkillItem ):
		
		def __init__( self, icon, pyBinder = None ) :
			SkillItem.__init__( self, icon, pyBinder = None )
			self.focus = True
			self.dropFocus = False
			self.dragFocus = False
		
		def update( self, itemInfo ):
			SkillItem.update( self, itemInfo )

	def __init__( self ):
		if ItemReward.__cg_item is None :
			ItemReward.__cg_item = GUI.load( "guis/general/npctalk/itemreward.gui" )

		item = util.copyGuiTree( ItemReward.__cg_item )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item )
		self.focus = True
		self.__pyItem = None
		if self.rewardType == RW_TYPE_SKILL:
			self.__pyItem = ItemReward.SkillIcon( item.icon )
		elif self.rewardType == RW_TYPE_ITEM:
			self.__pyItem = ItemReward.ItemIcon( item.icon )

		self.infoPanel = item.infoPanel
		self.__pyItemBg = PyGUI( item.itemFrame )
		self.__pyRichName = CSRichText( item.infoPanel.rtName )
		self.__pyRichName.font = CONT_FONT
		self.__pyRichName.fontSize = CONT_FONT_SIZE
		self.__pyRichName.opGBLink = True
		self.__pyRichName.align = "C"
		self.__index = 0
		self.__panelState = ( 1, 1 )
		self.__canbeSelected = False
		self.__selected = False


	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生控件事件
		"""
		Control.generateEvents_( self )
		self.__onSelected = self.createEvent_( "onSelected" )				# 获得焦点时被触发
		self.__onDeselected = self.createEvent_( "onDeselected" )			# 失去焦点时触法

	# -------------------------------------------------
	@property
	def onSelected( self ) :
		"""
		获得焦点时被触发
		"""
		return self.__onSelected

	@property
	def onDeselected( self ) :
		return self.__onDeselected


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLClick_( self, mods ) :
		"""
		左键点击时标记为选中
		"""
		Control.onLClick_( self, mods )
		self.selected = True


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ) :
		self.__selected = True
		self.panelState = ( 3, 1 )
		self.onSelected()

	def __deselect( self ) :
		self.__selected = False
		self.panelState = ( 1, 1 )
		self.onDeselected()

	def __onIconClick( self ) :
		self.selected = True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def updateItem( self, itemInfo ) :
		if itemInfo is None:#空物品显示个？号
			self.__pyItem.crossFocus = False
			self.__pyItem.texture = 'icons/tb_chunjie_008.dds'
			self.__pyItem.mapping = ((0.000000, 0.000000), (0.000000, 0.562500), (0.562500, 0.562500), (0.562500, 0.000000))
			self.__pyRichName.text = PL_Font.getSource( "???", fc = "c3" )
			self.__pyRichName.middle = 22
			return
		self.__pyItem.update( itemInfo )
		baseItem = itemInfo.baseItem
		foreColor = 243, 151, 0, 255
		name = ""
		if self.rewardType == RW_TYPE_ITEM:
			foreColor = QAColor.get( baseItem.getQuality(), ( 255, 255, 255, 255 ))
			util.setGuiState( self.__pyItemBg.gui, ( 4, 2 ), ItemQAColorMode[ baseItem.getQuality() ] )
			name = baseItem.name()
		elif self.rewardType == RW_TYPE_SKILL:
			name = baseItem.getName()
		self.__pyRichName.text = PL_Font.getSource( name, fc = foreColor )
		self.__pyRichName.middle= 22
		self.panelState = ( 1, 1 )		
	

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_ITEM

	# -------------------------------------------------
	def _getItemInfo( self ) :
		return self.__pyItem.itemInfo

	# -------------------------------------------------
	def _getCanBeSelected( self ) :
		return self.__canbeSelected

	def _setCanBeSelected( self, value ) :
		self.__canbeSelected = value

	# ---------------------------------------
	def _getSelected( self ) :
		return self.__selected

	def _setSelected( self, isSelected ) :
		if not self.__canbeSelected : return
		if isSelected : self.__select()
		else : self.__deselect()

	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.infoPanel.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )
	itemInfo = property( _getItemInfo )
	canbeSelected = property( _getCanBeSelected, _setCanBeSelected )
	selected = property( _getSelected, _setSelected )
	index = property( _getIndex, _setIndex,"" )
	panelState = property( _getPanelState, _setPanelState )

class SkillReward( ItemReward ):
	
	def __init__( self ):
		ItemReward.__init__( self )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getRewardType( self ) :
		return RW_TYPE_SKILL

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	rewardType = property( _getRewardType )

# ---------------------------------------------------------------------
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
class AimItem( CSRichText ):
	def __init__( self ):
		item = GUI.load("guis/general/npctalk/aimitem.gui")
		uiFixer.firstLoadFix( item )
		CSRichText.__init__( self, item )
		self.opGBLink = True
		self.maxWidth = 320.0
		self.aimIndex = -1			#目标索引
		self.text = ""
		self.limning = Font.LIMN_NONE
		self.__pyTxtCondition = StaticText( item.lbCondition )
		self.__pyTxtCondition.text = ""
		self.__pyTxtCondition.limning = Font.LIMN_NONE
		self.__pyTxtCondition.font = CONT_FONT
		self.__pyTxtCondition.fontSize = CONT_FONT_SIZE
		self.font = CONT_FONT
		self.fontSize = CONT_FONT_SIZE

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getAimCondition( self ):
		return self.text

	def _setAimCondition( self, condition ):
		
		self.text = PL_Font.getSource( condition, fc = ( 51, 76, 97, 255 ) )
#		self.width = self.__pyTxtCondition.width + 5.0

	def _getRewardType( self ) :

		return RW_TYPE_AIM

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	aimCondition = property( _getAimCondition, _setAimCondition )
	rewardType = property( _getRewardType )

# --------------------------------------------------------------------
# global defination
# --------------------------------------------------------------------
CRewardPanel = {}
CRewardPanel[RW_TYPE_MONEY]	= MoneyPanel
CRewardPanel[RW_TYPE_OTHER]	= OtherPanel
CRewardPanel[RW_TYPE_ITEM]	= ItemRewardPanel
CRewardPanel[RW_TYPE_AIM] 	= AimPanel
CRewardPanel[RW_TYPE_TIMER] = TimerPanel
CRewardPanel[RW_TYPE_SUBMIT] = SubmitPanel
CRewardPanel[RW_TYPE_NONE] = NonePanel
CRewardPanel[RW_TYPE_SKILL] = SkillRewardPanel


CRewardItem = {}
CRewardItem[RW_TYPE_ITEM]	= ItemReward
CRewardItem[RW_TYPE_AIM]	= AimItem
CRewardItem[RW_TYPE_OTHER]	= OtherItem
CRewardItem[RW_TYPE_FIXED_RANDOM_ITEM] = FixRanItem
CRewardItem[RW_TYPE_SKILL]	= SkillReward

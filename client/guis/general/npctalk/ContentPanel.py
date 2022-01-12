# -*- coding: gb18030 -*-
#
# $Id: ContentPanel.py,v 1.24 2008-09-02 03:47:09 songpeifang Exp $

"""
implement static text panel class。
"""
"""
composing :
	GUI.Window
		-- clipPanel ( GUI.Window )-> panel for cliping items
		-- scrollBar ( gui of csui.controls.ScrollBar.ScrollBar )
"""

import Font
from guis import *
from guis.controls.ScrollPanel import VScrollPanel
from guis.controls.ListItem import SingleColListItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from Rewards import RewardPanel
from Rewards import SubmitPanel
from Rewards import AimPanel
from Rewards import TimerPanel
import Rewards
from bwdebug import *

TITLE_FONT = "STLITI.TTF"
CONT_FONT = "MSYHBD.TTF"
CONT_FONT_SIZE = 12
TITLE_FONT_SIZE = 16
TITLE_FONT_COLOR = ( 231, 205, 140, 255 )


class ContentPanel( VScrollPanel ) :
	def __init__( self, panel, scrollBar ):

		VScrollPanel.__init__( self, panel, scrollBar )

		self.__pyTextItems = []
		self.__pyOptionItems = []
		self.__pyItems = []

		self.__font = 'MSYHBD.TTF'

		self.__foreColor = ( 51, 76, 97, 255, 255 )
		self.__spacing = 2.0
		self.sbarState = ScrollBarST.SHOW
		self.perScroll = 60.0
		self.gradualScroll = True

		self.__questItemCount = 0	# wsf，添加的选项任务计数，以便控制选项组件的位置

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __layout( self ) :
		pyItems = self.__pyItems
		for index,( tp, pyItem ) in enumerate( pyItems ) :
			if index == 0 :
				pyItem.top = 0
			else :
				pyItem.top = pyItems[index - 1][1].bottom + 5.0
		endIndex = len( pyItems ) - 1

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def appendTitle( self, title ): # 任务标题
		pyItems = self.__pyItems
#		titleText = GUI.load( "guis/general/npctalk/objecttext.gui" )
#		uiFixer.firstLoadFix( titleText )
		pyTitle = CSRichText()
		pyTitle.maxWidth = self.width
		pyTitle.opGBLink = True
		title_color = ( 231, 205, 140, 255 ) 
		title = PL_Font.getSource( title, fc = title_color )
		title += PL_Font.getSource( fc = self.__foreColor )
		pyTitle.limning = Font.LIMN_OUT
		pyTitle.limnColor = ( 0, 0, 0,255 )
		pyTitle.text = title
		self.addPyChild( pyTitle )
		pyTitle.top = 20.0
		pyTitle.align = "C"
#		pyTitle.maxWidth = self.width
		self.__pyItems.append( ( CSRichText, pyTitle ) )
		self.wholeLen = pyTitle.bottom

	def appendTimer( self, pyPanel ): # 添加计时器
		pyItems = self.__pyItems
		self.addPyChild( pyPanel )
		pyPanel.top = self.itemCount > 0 and pyItems[-1][1].bottom or 0
		pyPanel.left = 100
		self.__pyItems.append( ( TimerPanel, pyPanel ) )
		self.wholeLen = pyPanel.bottom

	def appendText( self, text ) : # NPC对白
		pyItems = self.__pyItems
		pyRich = CSRichText()
		pyRich.maxWidth = self.width
		pyRich.opGBLink = True
		pyRich.limning = Font.LIMN_NONE
		pyRich.font = CONT_FONT
		pyRich.fontSize = CONT_FONT_SIZE
#		text = '\n' + text	# 换行调整文字起始位置
		text = PL_Font.getSource( text, fc = self.__foreColor )
		text += PL_Font.getSource( fc = self.__foreColor )
#		pyRich.maxWidth = self.width
		pyRich.spacing = self.__spacing
		pyRich.text += text
		self.addPyChild( pyRich )
		printStackTrace()
		pyRich.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing ) or 24.0
		pyRich.left = 0.0
		self.__pyItems.append( ( CSRichText, pyRich ) )
		self.wholeLen = pyRich.bottom
		pyRich.maxWidth = self.width
		
	def appendTypeText( self, typeStr ) : # 任务类型
		pyItems = self.__pyItems
		pyRich = CSRichText()
		pyRich.opGBLink = True
		pyRich.font = TITLE_FONT
		pyRich.foreColor = TITLE_FONT_COLOR
		pyRich.fontSize = TITLE_FONT_SIZE
		pyRich.limning = Font.LIMN_OUT
		pyRich.text += '\n' + PL_Font.getSource( typeStr  )		
		self.addPyChild( pyRich )
		pyRich.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing ) or 0
		pyRich.left = 0.0
		self.__pyItems.append( ( CSRichText, pyRich ) )
		self.wholeLen = pyRich.bottom

	#----------------------------------------------------------
	def appendOptionItem( self, pyItem ): # 任务选项标题，在接任务前对话中出现,wsf
		pyTmpItem = self.__pyItems[-1][1]
		self.addPyChild( pyItem )
		if self.__questItemCount == 0:
			pyItem.top = self.itemCount > 0 and ( pyTmpItem.bottom + self.__spacing * 6 ) or 0
		else:
			pyItem.top = pyTmpItem.bottom + self.__spacing * 2
		pyItem.left = 2.0
		self.__pyItems.append( ( SingleColListItem, pyItem ) )
		self.wholeLen = pyItem.bottom
		pyItem.width = 260.0
		self.__questItemCount += 1
		self.__pyOptionItems.append( pyItem )

	# -----------------------------------------------------------
	def appendRewardItemsPanel( self, pyPanel ) : #任务奖励物品面板
		pyItems = self.__pyItems
		self.addPyChild( pyPanel )
		pyPanel.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing )or 0
		pyPanel.left = 2.0
		self.__pyItems.append( ( RewardPanel, pyPanel ) )
		self.wholeLen = pyPanel.bottom

	# ------------------------------------------------------------
	def appendSubmitPanel( self, pyPanel ): # 任务提交物品面板
		pyItems = self.__pyItems
		self.addPyChild( pyPanel )
		pyPanel.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing )or 0
		pyPanel.left = 2.0
		self.__pyItems.append( ( SubmitPanel, pyPanel ) )
		self.wholeLen = pyPanel.bottom

	# ------------------------------------------------------------
	def appendAimPanel( self, pyPanel ): # 任务目标面板
		pyItems = self.__pyItems
		self.addPyChild( pyPanel )
		pyPanel.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing )or 0
		pyPanel.left = 2.0
		self.__pyItems.append( ( AimPanel, pyPanel ))
		self.wholeLen = pyPanel.bottom
	
	def appendGodWeapon( self, pyPanel ):
		pyItems = self.__pyItems
		self.addPyChild( pyPanel )
		pyPanel.top = self.itemCount > 0 and ( pyItems[-1][1].bottom + self.__spacing )or 0
		pyPanel.center = self.width/2.0
#		self.__pyItems.append( ( AimPanel, pyPanel ))
		self.wholeLen = pyPanel.bottom
	# ---------------------------------------
	def clear( self ) :
		for pyItem in self.__pyItems :
			self.delPyChild( pyItem[1] )
		self.__pyItems = []
		self.__pyOptionItems = []
		self.wholeLen = 0
		self.__questItemCount = 0	# wsf，计数器清0

	def getAimPanel( self ):
		for type,panel in self.__pyItems:
			if hasattr(panel,"rewardType") and panel.rewardType == Rewards.RW_TYPE_AIM:
				return panel
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemCount( self ) :
		return len( self.__pyItems )

	# -------------------------------------------------
	def _getFont( self ) :
		return self.__font

	def _setFont( self, font ) :
		self.__font = font
		for tp, pyItem in self.__pyItems :
			if tp is CSRichText :
				pyItem.font = font
				pyItem.opGBLink = True
		self.__layout()

	# ---------------------------------------
	def _getForeColor( self ) :
		return self.__foreColor

	def _setForeColor( self, color ) :
		self.__foreColor = color
		for tp, pyItem in self.__pyItems :
			if tp is CSRichText :
				pyItem.foreColor = color
				pyItem.opGBLink = True

	# -------------------------------------------------
	def _getSpacing( self, spacing ) :
		return self.__spacing

	def _setSpacing( self, spacing ) :
		self.__spacing = spacing
		for tp, pyItem in self.__pyItems :
			if tp is CSRichText:
				pyItem.spacing = spacing
				pyItem.opGBLink = True
		self.__layout()

	def _getItems( self ):

		return self.__pyItems
	
	def _getOptionItems( self ):
		return self.__pyOptionItems

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemCount = property( _getItemCount )						# get the number of items
	font = property( _getFont, _setFont )						# get or set font
	foreColor = property( _getForeColor, _setForeColor )		# get or set color
	spacing = property( _getSpacing, _setSpacing )				# get or set spacing between two lines
	pyItems = property( _getItems )
	pyOptionItems = property( _getOptionItems )
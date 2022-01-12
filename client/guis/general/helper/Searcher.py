# -*- coding: gb18030 -*-
#
# $Id: Searcher.py,v 1.1 2008-04-14 10:26:35 huangyongwei Exp $

"""
implement course helper class.

2008.04.10: writen by huangyongwei
"""

from Helper import systemHelper
from guis import *
from guis.controls.TextBox import TextBox
from guis.controls.ButtonEx import HButtonEx
from HelpPanel import HelpPanel
from guis.controls.StaticText import StaticText
from LabelGather import labelGather


class Searcher( HelpPanel ) :
	def __init__( self, panel ) :
		HelpPanel.__init__( self, panel )

		self.__pyTextBox = TextBox( panel.tbSearch.box )		# 关键字输入框
		self.__pyTextBox.onKeyDown.bind( self.__onTBKeyDown )

		self.__pySearchBtn = HButtonEx( panel.btnSearch )		# 搜索按钮
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.onLClick.bind( self.__onSearchClick )

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# 指引内容标题
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# 指引条目标题
		self.__pySTSearch = StaticText( panel.stSearch )			# “查询内容”文字


		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:searcher", "rbTpTitle" )		# 指引内容
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:searcher", "rbTvTitle" )		# 指引条目
		labelGather.setPyLabel( self.__pySTSearch, "HelpWindow:searcher", "rbSearch" )			# 查询内容
		labelGather.setPyBgLabel( self.__pySearchBtn, "HelpWindow:searcher", "btnSearcher" )	# 查询


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearTopics( self ) :
		"""
		清除所有搜索记录
		"""
		self.pyTVTopic_.pyNodes.clear()
		self.pyTPContent_.text = ""

	# -------------------------------------------------
	def __onTBKeyDown( self, pyTB, key, mods ) :
		"""
		如果焦点在输入框中，则按回车等于点击 搜索 按钮
		"""
		if ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) and mods == 0 :
			self.searchTopic( pyTB.text.strip() )
			pyTB.tabStop = False
			return True
		return False

	def __onSearchClick( self ) :
		"""
		点击 搜索 按钮
		"""
		self.searchTopic( self.__pyTextBox.text.strip() )

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			self.__onSearchClick()
			return True
		return False

	def onEnterWorld( self ) :
		"""
		当玩家进入世界时被调用
		"""
		pass

	def onLeaveWorld( self ) :
		"""
		当玩家离开世界时被调用
		"""
		self.__clearTopics()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onWindowHid( self ) :
		"""
		窗口关闭时，清除所有查询结果
		"""
		self.__clearTopics()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def searchTopic( self, key ) :
		"""
		搜索帮助指引
		"""
		if key == "" :
			# "请输入关键字！"
			showAutoHideMessage( 3.0, 0x0c61, "", pyOwner = self.pyTopParent )
			return
		if key != self.__pyTextBox.text :
			self.__pyTextBox.text = key

		self.__clearTopics()
		topics = systemHelper.searchTopics( key )
		for topic in topics :
			pyNode = self.createRootTreeNode_( topic )
			self.pyTVTopic_.pyNodes.add( pyNode )
		if self.pyTVTopic_.pyNodes.count > 0 :
			self.pyTVTopic_.pyNodes[0].selected = True
		else :
			# "找不到相关主题！"
			showAutoHideMessage( 3.0, 0x0c62, "", pyOwner = self.pyTopParent )

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

		self.__pyTextBox = TextBox( panel.tbSearch.box )		# �ؼ��������
		self.__pyTextBox.onKeyDown.bind( self.__onTBKeyDown )

		self.__pySearchBtn = HButtonEx( panel.btnSearch )		# ������ť
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.onLClick.bind( self.__onSearchClick )

		self.__pySTTpTitle = StaticText( panel.tpContent.bgTitle.stTitle )	# ָ�����ݱ���
		self.__pySTTvTitle = StaticText( panel.tvTopic.bgTitle.stTitle )	# ָ����Ŀ����
		self.__pySTSearch = StaticText( panel.stSearch )			# ����ѯ���ݡ�����


		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyLabel( self.__pySTTpTitle, "HelpWindow:searcher", "rbTpTitle" )		# ָ������
		labelGather.setPyLabel( self.__pySTTvTitle, "HelpWindow:searcher", "rbTvTitle" )		# ָ����Ŀ
		labelGather.setPyLabel( self.__pySTSearch, "HelpWindow:searcher", "rbSearch" )			# ��ѯ����
		labelGather.setPyBgLabel( self.__pySearchBtn, "HelpWindow:searcher", "btnSearcher" )	# ��ѯ


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearTopics( self ) :
		"""
		�������������¼
		"""
		self.pyTVTopic_.pyNodes.clear()
		self.pyTPContent_.text = ""

	# -------------------------------------------------
	def __onTBKeyDown( self, pyTB, key, mods ) :
		"""
		���������������У��򰴻س����ڵ�� ���� ��ť
		"""
		if ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) and mods == 0 :
			self.searchTopic( pyTB.text.strip() )
			pyTB.tabStop = False
			return True
		return False

	def __onSearchClick( self ) :
		"""
		��� ���� ��ť
		"""
		self.searchTopic( self.__pyTextBox.text.strip() )

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# ��������˻س���
			self.__onSearchClick()
			return True
		return False

	def onEnterWorld( self ) :
		"""
		����ҽ�������ʱ������
		"""
		pass

	def onLeaveWorld( self ) :
		"""
		������뿪����ʱ������
		"""
		self.__clearTopics()


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onWindowHid( self ) :
		"""
		���ڹر�ʱ��������в�ѯ���
		"""
		self.__clearTopics()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def searchTopic( self, key ) :
		"""
		��������ָ��
		"""
		if key == "" :
			# "������ؼ��֣�"
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
			# "�Ҳ���������⣡"
			showAutoHideMessage( 3.0, 0x0c62, "", pyOwner = self.pyTopParent )

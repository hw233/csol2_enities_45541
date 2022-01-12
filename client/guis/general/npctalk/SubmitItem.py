# -*- coding: gb18030 -*-
#
# $Id: SubmitItem.py,v 1.18 2008-08-18 02:05:56 zhangyuxing Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
from guis.tooluis.CSRichText import CSRichText
import GUIFacade
import csdefine
import csconst

class SubmitItem( PyGUI ):

	def __init__( self ):
		panel = GUI.load("guis/general/npctalk/submitpanel.gui")
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.__pyTxtName = CSRichText( panel.lbName )
		self.__pyTxtName.foreColor = 0.0,128.0,0.0,255  # 颜色
		self.__pyItemFrame = PyGUI( panel.itemFrame )
		self.__pySubItem = Item( panel.itemFrame.submitItem, self )
		self.__index = 0
		self.__space = 6.0	 # 隔开物品描述和物品格子

	# ------------------------------------------------
	# private
	# ------------------------------------------------
	def __select( self ):
		self.__selected = True

	def updateItem( self, itemInfo, taskType ): #服务器需求信息
		if itemInfo == {}:
			return
		nameText = itemInfo["ItemName"]
		if taskType != csdefine.QUEST_OBJECTIVE_SUBMIT_LQEQUIP:
			tasks = GUIFacade.getQuestLogs()[GUIFacade.getQuestID()]['tasks'].getTasks()
			submitTask = None
			for task in tasks.itervalues():
				if task.getType() in csconst.QUEST_OBJECTIVE_SUBMIT_TYPES or \
				task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE or \
				task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY or \
				task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE:
					submitTask = task
					break
			if submitTask.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_PICTURE or \
			task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_CHANGE_BODY or \
			task.getType() == csdefine.QUEST_OBJECTIVE_SUBMIT_DANCE:
				self.__pyTxtName.text = labelGather.getText( "NPCTalkWnd:submit", "pleaseInput" )%(nameText + itemInfo["npcName"])
			else:
				self.__pyTxtName.text = labelGather.getText( "NPCTalkWnd:submit", "pleaseInput" )%(nameText + submitTask.getPorpertyName())
		else: #仙灵换物
			self.__pyTxtName.text = labelGather.getText( "NPCTalkWnd:submit", "pleaseInput" )%nameText

		self.__pyItemFrame.left = self.__pyTxtName.right + self.__space
		self.width = self.__pyTxtName.width + self.__space*2 + self.__pyItemFrame.width			#调整面板长度

	def _getKitbag( self ):
		if self.__pySubItem.itemInfo == None:
			return -1
		return self.__pySubItem.itemInfo.kitbagID

	def _getOrder( self ):
		if self.__pySubItem.itemInfo == None:
			return -1
		return self.__pySubItem.itemInfo.orderID

	kitbag = property( _getKitbag )
	order = property( _getOrder )

	# ------------------------------------------------------------------
class Item( CompareDspItem ):
	def __init__( self, item = None, pyBinder = None ):
		CompareDspItem.__init__( self, item, pyBinder )
		self.focus = True
		self.__itemInfo = None
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------

	def __clearItem( self ):
		self.update( None )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		CompareDspItem.onRClick_( self, mods )
		self.__clearItem( ) # 移除任务提交物品
		return True

	def onDragStop_( self, pyDrogged ) :
		CompareDspItem.onDragStop_( self, pyDrogged )
		if ruisMgr.isMouseHitScreen() :
			self.__clearItem( )
		return True

	def onDrop_( self,  pyTarget, pyDropped ) :
		if pyDropped.dragMark != DragMark.KITBAG_WND : return
		itemInfo = pyDropped.itemInfo
		self.update( itemInfo )
		CompareDspItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		CompareDspItem.update( self, itemInfo )
		if itemInfo is not None :
			self.itemInfo = itemInfo

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )			# get or set the checking state of the checkbox
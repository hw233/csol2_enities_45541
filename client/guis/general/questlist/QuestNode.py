# -*- coding: gb18030 -*-
#
#$Id: QuestNode.py,v 1.10 2008-09-05 02:41:21 fangpengjun Exp $
#

"""
implement friendnode item class
"""

import csdefine
import Const
from Weaker import RefEx
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.TreeView import TreeNode
import GUIFacade
import Font

class QuestNode( TreeNode ):
	def __init__( self, pyBiner ):
		node = GUI.load( "guis/general/questlist/node.gui")
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node )
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.__itemInfo = None
		self.__isTraced = False
		self.__isComp = False
		self.autoWidth = False
		self.__triggers = {}
		self.__pyHooker = PyGUI( node.hook )
		self.__pyHooker.visible = False
		self.__pyNodeBg = PyGUI( node.nodeBg )
		self.__pyNodeBg.visible = False
		self.pyBiner = pyBiner
		self.font = "MSYHBD.TTF"
		self.fontSize = 12.0
		self. limning = Font.LIMN_NONE
		self.__pyIsComp = None
		if hasattr( node, "isComp" ):
			self.__pyIsComp = PyGUI( node.isComp )
			self.__pyIsComp.visible = False
		self.__registerTriggers()

	def dispose( self ):
		TreeNode.dispose( self )
		self.pyBiner = None

	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = RefEx( self.__onUpdateLevel )			# level changed trigger

		for eventMacro in self.__triggers :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers :
			ECenter.unregisterEvent( eventMacro, self )

	def __onUpdateLevel( self, odlLevel, level ):
		"""
		角色等级改变，重新设置颜色
		"""
		if self.itemInfo is None:return
		temp = self.itemInfo.level - level
		if temp <= -5:
			tempColor = ( 51, 76, 97, 255 )	#灰色
		elif temp > -5 and temp <= 0:
			tempColor = ( 255, 255, 255, 255 )	#白色
		elif temp > 0 and temp <=3:
			tempColor = ( 255, 127, 0, 255 ) #橙色
		else:
			tempColor = ( 193, 23, 0, 255 ) #红色
		self.commonForeColor = tempColor
		self.highlightForeColor = tempColor
		if not self.selected:
			self.foreColor = self.commonForeColor

	def __isTraceQuest( self, questID ):
		"""
		是否可追踪的任务，是则返回True
		"""
		typeList = GUIFacade.getTaskGoalType( questID )
		for i in typeList:
			return i in Const.TRACE_QUEST_TYPE
		return False

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]()( *args )

	# ---------------------------------------------
	# property methods
	# ---------------------------------------------
	def onLClick__( self, mods ):
		TreeNode.onLClick__( self, mods )
		if self.pyBiner is None:return
		if self.itemInfo is None: return
		if mods == MODIFIER_SHIFT:
			self.pyBiner.onQuestNodeLClick( )
#		if mods == 0:
#			GUIFacade.setQuestLogSelect( self.itemInfo.id )
		return True

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	def _getItemInfo( self ):
		return self.__itemInfo

	def _getTraceState( self ) :
		return self.__isTraced

	def _setTraceState( self, isTraced ) :
		self.__isTraced = isTraced
		self.__pyHooker.visible = isTraced

	def _setSelected( self, selected ) :
		if self.selected == selected : return
		self.__pyNodeBg.visible = selected
		self.selectedBackColor = self.commonForeColor
#		if self.commonForeColor != ( 255, 255, 255, 255 ):
		self.selectedForeColor = ( 0, 128, 0, 255 )
		TreeNode._setSelected( self, selected )
	
	def _getIsComp( self  ):
		return self.__isComp
	
	def _setIsComp( self, isComp ):
		self.__isComp = isComp
		if self.__pyIsComp:
			self.__pyIsComp.visible = True
			if isComp:
				util.setGuiState( self.__pyIsComp.getGui(), (2,1),(1,1))
			else:
				util.setGuiState( self.__pyIsComp.getGui(), (2,1),(2,1))

	itemInfo = property( _getItemInfo, _setItemInfo )
	isTraced = property( _getTraceState, _setTraceState )
	selected = property( TreeNode._getSelected, _setSelected )
	isComp = property( _getIsComp, _setIsComp )
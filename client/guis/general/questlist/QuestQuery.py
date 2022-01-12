# -*- coding: gb18030 -*-
#
# $Id: QuestQuery.py,v 1.26 2008-08-04 10:23:11 huangyongwei Exp $

"""
implement quest list class
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListPanel import ListPanel
from guis.controls.ItemsPanel import ItemsPanel
from guis.controls.ODListPanel import ODListPanel
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TextBox import TextBox
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem
from guis.controls.ListItem import MultiColListItem
from guis.tooluis.fulltext.FullText import FullText
from Helper import questHelper
from NPCDatasMgr import npcDatasMgr
import csdefine
import GUIFacade
import Timer
from QuestDetails import QuestDetails
import csconst
import csstatus
import Font
#import time

class QuestQuery( TabPanel ):
	def __init__( self, panel = None, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.monsterItems = []
		self.questItems = []
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyTextBoxs = []
		self.sortByQuestLevel = False
		self.sortByQuestName = False
		self.sortByQuestArea = False
		self.sortByQuestNPC = False
		self.sortByMonsterLevel = False
		self.sortByMonsterName = False
		self.sortByMonsterArea = False
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		labelGather.setLabel( panel.typeChoice, "QuestHelp:QuestQuery", "selContent" )
		labelGather.setLabel( panel.levelText, "QuestHelp:QuestQuery", "level" )
		labelGather.setLabel( panel.keyText, "QuestHelp:QuestQuery", "keyWords" )
		labelGather.setLabel( panel.preQuestPanel.bgTitle.stTitle, "QuestHelp:QuestQuery", "preQuest" )
		labelGather.setLabel( panel.nextQuestPanel.bgTitle.stTitle, "QuestHelp:QuestQuery", "nextQuest" )

		self.__pyUpperBox = TextBox( panel.upperBox.box )
		self.__pyUpperBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyUpperBox.font = "MSYHBD.TTF"
		self.__pyUpperBox.fontSize = 12.0
		self.__pyUpperBox.inputMode = InputMode.INTEGER
		self.__pyUpperBox.filterChars = ['-', '+']
		self.__pyUpperBox.maxLength = 3
		self.__pyUpperBox.enable = True
		self.__pyTextBoxs.append( self.__pyUpperBox )

		self.__pyLowerBox = TextBox( panel.lowerBox.box )
		self.__pyLowerBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyLowerBox.font = "MSYHBD.TTF"
		self.__pyLowerBox.fontSize = 12.0
		self.__pyLowerBox.inputMode = InputMode.INTEGER
		self.__pyLowerBox.filterChars = ['-', '+']
		self.__pyLowerBox.maxLength = 3
		self.__pyLowerBox.enable = True
		self.__pyTextBoxs.append( self.__pyLowerBox )

		self.__pySearchBtn = Button( panel.searchBtn )
		self.__pySearchBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.enable = False
		labelGather.setPyBgLabel( self.__pySearchBtn, "QuestHelp:QuestQuery", "btnSearch" )
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		
		self.__pyRunBtn = HButtonEx( panel.btnRun )
		self.__pyRunBtn.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyRunBtn, "QuestHelp:QuestQuery","btnRun" )
		self.__pyRunBtn.visible = 0
		self.__pyRunBtn.onLClick.bind( self.__onRunToNPC )
		
		self.__pyFlyBtn = HButtonEx( panel.btnFly )
		self.__pyFlyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyFlyBtn, "QuestHelp:QuestQuery","btnFly" )
		self.__pyFlyBtn.visible = 0
		self.__pyFlyBtn.onLClick.bind( self.__onFlyToNPC )

		self.__pyMonsterBar = PyGUI( panel.monsterBar )
		self.__pyQuestBar = PyGUI( panel.questBar )

#		self.__pyPreQuestPanel = PyGUI( panel.questPanel )
#		self.__pyPreQuestPanel.visible = False
		#self.panel=panel

		self.__pyListPanel = ODListPanel(panel.listPanel.clipPanel, panel.listPanel.sbar )
		self.__pyListPanel.itemHeight = 23
		self.__pyListPanel.ownerDraw = True								# 开启自定义绘制
		self.__pyListPanel.visible=True


#		self.__pyQuestPanel = ItemsPanel( panel.questPanel.clipPanel, panel.questPanel.sbar )

		self.__pyQuestlevel = HButtonEx( panel.questBar.questLevel )
		self.__pyQuestlevel.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyQuestlevel, "QuestHelp:QuestQuery", "level" )
		self.__pyQuestlevel.onLClick.bind( self.__onSortByQuestLevel )

		self.__pyQuestName = HButtonEx( panel.questBar.questName )
		self.__pyQuestName.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyQuestName, "QuestHelp:QuestQuery", "questName" )
		self.__pyQuestName.onLClick.bind( self.__onSortByQuestName )

		self.__pyQuestArea = HButtonEx( panel.questBar.questArea )
		self.__pyQuestArea.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyQuestArea, "QuestHelp:QuestQuery", "area" )
		self.__pyQuestArea.onLClick.bind( self.__onSortByQuestArea )

		self.__pyMonsterLevel = HButtonEx( panel.monsterBar.monsterLevel )
		self.__pyMonsterLevel.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyMonsterLevel, "QuestHelp:QuestQuery", "level" )
		self.__pyMonsterLevel.onLClick.bind( self.__onSortByMonsterLevel )

		self.__pyMonsterName = HButtonEx( panel.monsterBar.monsterName )
		self.__pyMonsterName.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyMonsterName, "QuestHelp:QuestQuery", "monsterName" )
		self.__pyMonsterName.onLClick.bind( self.__onSortByMonsterName )

		self.__pyMonsterArea = HButtonEx( panel.monsterBar.monsterArea )
		self.__pyMonsterArea.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyMonsterArea, "QuestHelp:QuestQuery", "area" )
		self.__pyMonsterArea.onLClick.bind( self.__onSortByMonsterArea )

		self.__pyKeyBox = TextBox( panel.keyBox.box )
		self.__pyKeyBox.font = "MSYHBD.TTF"
		self.__pyKeyBox.fontSize = 12.0
		self.__pyKeyBox.text = ""
		self.__pyKeyBox.onTextChanged.bind( self.onTextChange_ )
#		self.__pyKeyBox.onKeyDown.bind( self.__onTBKeyDown )

		self.__pyCBOption = ComboBox( panel.cbOption )
		self.__pyCBOption.font = "MSYHBD.TTF"
		self.__pyCBOption.fontSize = 12.0
		self.__pyCBOption.onItemSelectChanged.bind( self.__onOPtionSelected )
	
		self.__preQuestPanel = PyGUI( panel.preQuestPanel )
		self.__preQuestPanel.visible = False
		self.__nextQuestPanel = PyGUI(panel.nextQuestPanel )
		self.__nextQuestPanel.visible = False
		
		self.__preQuestItem = ProntItem( panel.preQuestPanel.item, self )
		self.__preQuestItem.visible = 0
		self.__nextQuestItem = ProntItem( panel.nextQuestPanel.item, self )
		self.__nextQuestItem.visible = 0
		
		self.__pyCBOption.autoSelect = True
		
		self.pyQuestDetails = QuestDetails( )

		#self.__pyCBOption.text = "查询内容"
		pyOPtion0 = ComboItem( labelGather.getText( "QuestHelp:QuestQuery", "monster" ) )
		pyOPtion0.h_anchor = "CENTER"
		pyOPtion0.font = "MSYHBD.TTF"
		pyOPtion0.fontSize = 12.0
		pyOPtion1 = ComboItem( labelGather.getText( "QuestHelp:QuestQuery", "quest" ) )
		pyOPtion1.h_anchor = "CENTER"
		pyOPtion1.font = "MSYHBD.TTF"
		pyOPtion1.fontSize = 12.0
		self.__pyCBOption.addItems( [pyOPtion0, pyOPtion1] )
		

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initListItem( self, pyViewItem ) :
		"""
		初始化添加的NPC列表项
		"""
		pyNPCItem = MonsterItem( pyViewItem )
		pyViewItem.pyNPCItem = pyNPCItem
		pyViewItem.addPyChild( pyNPCItem )
		pyNPCItem.left = 0
		pyNPCItem.middle = pyViewItem.height * 0.5

	def __drawListItem( self, pyViewItem ) :
		monsterInfo = pyViewItem.listItem
		pyNPCItem = pyViewItem.pyNPCItem
		pyNPCItem.resetMonster( monsterInfo )
		pyNPCItem.selected = pyViewItem.selected

	def __initListItemTask( self, pyViewItem ) :
		"""
		初始化添加的NPC列表项
		"""
		pyNPCItem = QuestItem( pyViewItem )
		pyViewItem.pyNPCItem = pyNPCItem
		pyViewItem.addPyChild( pyNPCItem )
		pyNPCItem.left = 0
		pyNPCItem.middle = pyViewItem.height * 0.5

	def __drawListItemTask( self, pyViewItem ) :
		questInfo = pyViewItem.listItem
		pyNPCItem = pyViewItem.pyNPCItem
		pyNPCItem.resetQuest( questInfo )
		pyNPCItem.selected = pyViewItem.selected

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_QUESTS_QUERY_LEVEL"] = self.__toggleQuestQueryLevel
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# ----------------------------------------------------------------
	def onTextChange_( self ):
		self.__pySearchBtn.enable = self.__pyUpperBox.text != "" and \
			self.__pyLowerBox.text != "" or self.__pyKeyBox.text != ""
			
	def __onItemSelected( self, pyViewItem ): #显示前置任务
		questInfo = self.__pyListPanel.getItem(pyViewItem)
#		self.__pyQuestPanel.clearItems()
		self.__preQuestItem.reset()
		self.__nextQuestItem.reset()
		if self.__pyCBOption.selIndex == 1:  #为任务查询
			self.pyQuestDetails.show( questInfo, self )
			fronts = []
			def getTFronts( quest ):
				frontQuest = questHelper.queryPreQuest( quest )
				if frontQuest is None:return
				fronts.append( frontQuest )
				getTFronts( frontQuest )
				return fronts
			frontQuests = getTFronts( questInfo )
			if frontQuests is None :
				frontQuest = None
			else:
				frontQuest = frontQuests[0]
			self.__preQuestItem.updateItem( frontQuest )
			
			nextQuest = questHelper.queryNextQuest( questInfo )		#后置任务
			self.__nextQuestItem.updateItem( nextQuest )
				
		else:
			npcInfo = self.__pyListPanel.getItem( pyViewItem )
			npcPosition = npcInfo.getPosition()
			if npcPosition is None:
				self.__pyRunBtn.enable = False
				self.__pyFlyBtn.enable = False
			else:
				self.__pyRunBtn.enable = True
				self.__pyFlyBtn.enable = True
			
	def __onOPtionSelected( self, pyOption ):
		self.__pyListPanel.clearItems()

		#self.__clearTexts()
		self.__pyUpperBox.enable = self.__pyCBOption.pySelItem is not None
		self.__pyLowerBox.enable = self.__pyCBOption.pySelItem is not None
		index = self.__pyCBOption.selIndex
		self.__pyMonsterBar.visible = index == 0
		self.__pyQuestBar.visible = index == 1
#		self.__pyPreQuestPanel.visible = index == 1
		self.__preQuestPanel.visible = index == 1
		self.__nextQuestPanel.visible = index == 1
		self.__pyCBOption.pySelItem = self.__pyCBOption.pyItems[index]
		self.__pyListPanel.onItemLClick.unbind( self.__onItemSelected )
		if index==0:
			self.__pyRunBtn.visible = 1
			self.__pyFlyBtn.visible = 1
			self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
			self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
			self.__pyListPanel.onItemLClick.bind( self.__onItemSelected )
		else:
			self.__preQuestItem.reset()
			self.__nextQuestItem.reset()
			self.__pyRunBtn.visible = 0
			self.__pyFlyBtn.visible = 0
			self.__pyListPanel.onViewItemInitialized.bind( self.__initListItemTask )
			self.__pyListPanel.onDrawItem.bind( self.__drawListItemTask )
			self.__pyListPanel.onItemLClick.bind( self.__onItemSelected )


	def __onSearch( self ):
		#searchTime = time.time()
		player = BigWorld.player()
		self.__pyListPanel.clearItems()
		searchText = self.__pyKeyBox.text.strip()
		upperText = self.__pyUpperBox.text.strip()
		lowerText = self.__pyLowerBox.text.strip()
		msgID = 0
		if self.__pyCBOption.selIndex == 0: # 查询特定等级段内所有任务怪
			msgID = 0x0c63
			monsters = {}
			if upperText !="" and lowerText != "":
				#dataTime = time.time()
				monsters = npcDatasMgr.getMonsters( max( 1, int( lowerText ) ), min( int( upperText ), 150 ), 2 )
				#print "怪物数据获得时间：" ,time.time() - dataTime
			elif ( upperText == "" or lowerText == "" ) and searchText != "":
				lowerLevel = 1
				upperLevel = 150
				if upperText == "":upperLevel = 150
				else: upperLevel = int( upperText )
				if lowerText == "":lowerLevel = 1
				else: lowerLevel = int( lowerText )
				monsters = npcDatasMgr.getMonsters( lowerLevel, upperLevel, 2 )
			for level, monstersList in monsters.iteritems():
				if len( monstersList ) == 0:continue

				if searchText != "":
					for monster in monstersList:
						if (monster.name+monster.area).find(searchText)!=-1:
							self.__pyListPanel.addItem(monster)

				else:
					for monster in monstersList:
						self.__pyListPanel.addItem(monster)
			npcInfo = self.__pyListPanel.selItem
			if npcInfo is None:
				npcPosition = None
			else:
				npcPosition = npcInfo.getPosition()
			if npcPosition is None:
				self.__pyRunBtn.enable = 0
				self.__pyFlyBtn.enable = 0
			else:
				self.__pyRunBtn.enable = 1
				self.__pyFlyBtn.enable = 1

		elif self.__pyCBOption.selIndex == 1: # 查询特定等级段内所有可接任务
			msgID = 0x0c64
			quests = {}
			if upperText !="" and lowerText != "":
				quests = questHelper.queryQuestsInRange( min( int( lowerText ), int( upperText ) ), max( int( lowerText ), int( upperText ) ), player.getClass() )
			elif ( upperText == "" or lowerText == "" ) and searchText != "":
				lowerLevel = 1
				upperLevel = 160
				if upperText == "":upperLevel = 160
				else: upperLevel = int( upperText )
				if lowerText == "":lowerLevel = 1
				else: lowerLevel = int( lowerText )
				quests = questHelper.queryQuestsInRange( lowerLevel, upperLevel, player.getClass() )
			for level, questsList in quests.iteritems():
				if len( questsList ) == 0:continue
				names = []
				for quest in  questsList:
					if quest.profession not in [player.getClass(),0]:		# 不显示其他职业的任务 ,0表示没有职业限定
						continue
					npcID = quest.npcID
					textID = npcID.replace( ' ', '' )
					name = ""
					position = ""
					spaceLabel = ("","")
					if not textID.isdigit():
						name = ""
					else:
						npc = npcDatasMgr.getNPC( textID )
						if npc is None:
							name = ""
						else:
							name = npc.name
							spaceLabel = npcDatasMgr.getNPCSpaceLabel( npc.id )
							position = npc.getPosition( spaceLabel[0] )
							if position is None: #如果没找到NPC的坐标，则设其为(0, 0)
								position = ( 0, 0 )
							else:
								position = ( int(position[0]), int(position[2]) )
					if searchText != "":
						content = str( quest.level ) + quest.title + spaceLabel[1] + name \
						 + str( position ).replace( ' ', "")
						if content.find(searchText)!=-1:
							quest.spaceLabel=spaceLabel[1]
							quest.npcName=name
						 	self.__pyListPanel.addItem( quest )
					else:
						quest.spaceLabel=spaceLabel[1]
						quest.npcName=name
						self.__pyListPanel.addItem( quest )
		if self.__pyListPanel.itemCount == 0 :
			showAutoHideMessage( 3.0, msgID, "", pyOwner = self.pyTopParent )

	def __clearTexts( self ):
		for textBox in self.__pyTextBoxs:
			textBox.clear()

	def __onSortByQuestLevel( self ):
		flag = self.sortByQuestLevel and True or False
		self.__pyListPanel.sort( key = lambda quest: quest.level, reverse = flag )
		self.sortByQuestLevel = not self.sortByQuestLevel

	def __onSortByQuestName( self ):
		flag = self.sortByQuestName and True or False
		self.__pyListPanel.sort( key = lambda quest:quest.title, reverse = flag )
		self.sortByQuestName = not self.sortByQuestName

	def __onSortByQuestArea( self ):
		flag = self.sortByQuestArea and True or False
		self.__pyListPanel.sort( key =lambda quest :quest.spaceLabel, reverse = flag )
		self.sortByQuestArea = not self.sortByQuestArea

	def __onSortByMonsterLevel( self ):
		flag = self.sortByMonsterLevel and True or False
		self.__pyListPanel.sort( key = lambda monster: monster.level, reverse = flag )
		self.sortByMonsterLevel = not self.sortByMonsterLevel

	def __onSortByMonsterName( self ):
		flag = self.sortByMonsterName and True or False
		self.__pyListPanel.sort( key = lambda monster: monster.name, reverse = flag )
		self.sortByMonsterName = not self.sortByMonsterName

	def __onSortByMonsterArea( self ):
		flag = self.sortByMonsterArea and True or False
		self.__pyListPanel.sort( key = lambda monster: monster.area, reverse = flag )
		self.sortByMonsterArea = not self.sortByMonsterArea

	def __toggleQuestQueryLevel( self, levelUp, levelDown ):
		"""
		"""
		self.__pyCBOption.pySelItem = self.__pyCBOption.pyItems[1]
		self.__pyUpperBox.text = str(levelDown)
		self.__pyLowerBox.text = str(levelUp)
		self.__onSearch()
		
	def __onRunToNPC( self ) :
		"""
		自动寻路
		"""
		npcInfo = self.__pyListPanel.selItem
		if npcInfo is None : return
		self.pyBinder.hide()
		player = BigWorld.player()
		npcPosition = npcInfo.getPosition()
		npcID = npcInfo.id
		dstSpace = rds.npcDatasMgr.getNPCSpaceLabel( npcID )[0]		# 根据ID获取NPC所在的地图
		player.setExpectTarget( npcID )							# 设置追踪目标NPC的ID
		player.autoRun( npcPosition, csconst.COMMUNICATE_DISTANCE - 2, dstSpace )
	
	def __onFlyToNPC( self ) :
		"""
		使用引路蜂
		"""
		npcInfo = self.__pyListPanel.selItem
		if npcInfo is None : return
		npcID = npcInfo.id
		player = BigWorld.player()
		items = player.findItemsByIDFromNKCK( 50101003 )
		if items == []:
			items = player.findItemsByIDFromNKCK( 50101002 )
		if items == []:
			player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
			return
		if not player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.stopMove()											# 必须先停止移动，以保证追踪目标不被清空
			player.cell.flyToNpc( npcID, 0, items[0].order )
			player.setExpectTarget( npcID )						# 设置追踪目标NPC的ID
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )
			return
		self.pyBinder.hide()
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			if self.__pySearchBtn.enable :
				self.__onSearch()
				return True
		return False

	def reset( self ) :
		self.__pyUpperBox.text = ""
		self.__pyLowerBox.text = ""
		self.__pyKeyBox.text = ""
		self.__preQuestItem.visible = 0
		self.__preQuestItem.reset()
		self.__nextQuestItem.visible = 0
		self.__nextQuestItem.reset()
		self.__pyListPanel.clearItems()

# --------------------------------------------------------------
# MonsterItem
# --------------------------------------------------------------
class MonsterItem( MultiColListItem ):

	def __init__( self, pyBinder=None ):
		gui= GUI.load( "guis/general/questlist/questquery/monsterbar.gui")
		self.__monster = None
		uiFixer.firstLoadFix( gui )
		MultiColListItem.__init__( self, gui , pyBinder )
		self.commonForeColor = ( 51, 76, 97, 255 )
		self.selectedForeColor = ( 0, 128, 0, 255 )
		self.content = ""
		self.focus=False
		for pyCol in self.pyCols_:
			pyCol.font = "MSYHBD.TTF"
			pyCol.fontSize = 12.0
			pyCol.limning = Font.LIMN_NONE


	def resetMonster( self, monster ):
		self.__monster = monster
		position = ""
		if monster.position is None:
			position = ""
		else:
			position = ( int(monster.position[0]), int(monster.position[2]) )
			if position == (0,0,0):
				position = ""
		self.setTextes( monster.level, monster.name , monster.area + str( position ).replace( ' ', "") )
		self.content = str( monster.level ) + monster.name + str( position ).replace( ' ', "") + monster.area

	def getMonster( self ):
		return self.__monster

# --------------------------------------------------------------
# QuestItem
# --------------------------------------------------------------
class QuestItem( MultiColListItem ):
	def __init__( self, pyBinder=None ):
		gui= GUI.load( "guis/general/questlist/questquery/questbar.gui" )
		uiFixer.firstLoadFix( gui )
		MultiColListItem.__init__( self, gui,pyBinder )
		self.__quest = None
		self._areaName = ""
		self.content = ""
		self.focus=False
		self.commonForeColor = ( 51, 76, 97, 255 )
		self.selectedForeColor = ( 0, 128, 0, 255 )
		for pyCol in self.pyCols_:
			pyCol.font = "MSYHBD.TTF"
			pyCol.fontSize = 12.0
			pyCol.limning = Font.LIMN_NONE
		
	def resetQuest( self, quest ):
		self.__quest = quest
		npcID = quest.npcID
		textID = npcID.replace( ' ', '' )
		spaceLabel = ("","")
		if textID.isdigit():
			npc = npcDatasMgr.getNPC( textID )
			if npc is  not None:
				spaceLabel = npcDatasMgr.getNPCSpaceLabel( npc.id )
		self._areaName = spaceLabel[1]
		self.setTextes( str( quest.level ), quest.title, spaceLabel[1] )
		self.content = str( quest.level ) + quest.title + spaceLabel[1]

	def getQuest( self ):
		return self.__quest

	def getArea( self ):
		return self._areaName
# -----------------------------------------------------------------
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText

class ProntItem( Control ):
	def __init__( self, item , pyBinder = None ):
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.crossFocus = True
		self.focus = True
		self.__quest = None
		self.__pyStName = StaticText( item.stName )
		self.__pyStName.text = ""
		self.__pyStName.font = "MSYHBD.TTF"
		self.__pyStName.fontSize = 12.0
		self.__pyStName.limning = Font.LIMN_NONE
		
		self.__pyStLevel = StaticText( item.stLevel )
		self.__pyStLevel.text = ""
		self.__pyStLevel.font = "MSYHBD.TTF"
		self.__pyStLevel.fontSize = 12.0
		self.__pyStLevel.limning = Font.LIMN_NONE
#		self.__pyStNPC = StaticText( item.stNPC )
#		self.__pyStNPC.text = ""
		self.__pyBg = PyGUI( item.itemBg )
		 	
	def onLClick_( self, mods ):
		Control.onLClick_( self, mods )
		if self.__quest is None :return False
		self.pyBinder.pyQuestDetails.show( self.__quest, self )
		return True

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		self.__pyBg.color = ( 0, 0, 255 )
		return True

	def onMouseLeave_( self ) :
		Control.onMouseLeave_( self )
		self.__pyBg.color = ( 255, 255, 255 )
		return True
		
	def updateItem( self, quest) :
		self.__quest = quest
		if self.__quest is None :
			self.visible = False
			return 
		self.visible = True
		self.__pyStName.text = '"' + quest.title +  '"'

		self.__pyStLevel.text = labelGather.getText( "QuestHelp:QuestCacept", "questLevel" )%quest.questLevel
		self.__quest.level = quest.questLevel
		
		npcID = quest.npcID
		npc = npcDatasMgr.getNPC( npcID )
		position = ( 0, 0 )
		if npc is None:
			name = ""
		else:
			name = npc.name
			spaceLabel = npcDatasMgr.getNPCSpaceLabel( npc.id )
			self.__quest.npcName = name
			self.__quest.spaceLabel =  spaceLabel[1] 
#		self.__pyStNPC.text = name
		
		player = BigWorld.player()
		questID =  quest.id
		if player.isQuestInDoing( questID ):
			self.__pyStName.color = 255, 255, 255, 255
		if player.isQuestCompleted( questID ):
			self.__pyStName.color = 127, 127, 127, 255
		else:
		 	self.__pyStName.color = 242.0, 236.0, 189.0, 255.0
		 	
	def reset( self ):
		self.__quest = None
		self.__pyStLevel.text = ""
		self.__pyStName.text = ""
#		self.__pyStNPC.text = ""
		self.visible = False
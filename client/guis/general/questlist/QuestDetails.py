# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
from guis.tooluis.CSRichText import CSRichText
from config.client.ForbidLinkNPCID import Datas as forbidNPCs
from guis.tooluis.richtext_plugins.PL_Link import PL_Link
from NPCDatasMgr import npcDatasMgr

class QuestDetails( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/questlist/questquery/questDetail.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "questDetails" )
		self.__initPanel( panel )
		
	def __initPanel( self, wnd ):
		self.__pyTitle = StaticText( wnd.lbTitle )
		self.__pyTitle.text = labelGather.getText( "QuestHelp:QuestDetails", "lbTitle")
		self.__pyTitle.charSpace = 2
		
		self.__pyStLevel = StaticText( wnd.contentPanel.level)
		self.__pyStLevel.text = ""
		
		self.__pyStTitle = CSRichText( wnd.contentPanel.title )
		self.__pyStTitle.text = ""
		self.__pyStTitle.foreColor = ( 230, 227, 185 )
		
		self.__pyStArea = CSRichText( wnd.contentPanel.area )
		self.__pyStArea.text = ""
		self.__pyStArea.foreColor = ( 230, 227, 185 )
		
		self.__pyStNPC = CSRichText( wnd.contentPanel.npc )
		self.__pyStNPC.opGBLink = True
		self.__pyStNPC.text = ''
		self.__pyStNPC.foreColor = ( 230, 227, 185 )
		
		labelGather.setLabel( wnd.contentPanel.questLevel, "QuestHelp:QuestDetails", "questLevel" )
		labelGather.setLabel( wnd.contentPanel.questTitle, "QuestHelp:QuestDetails", "questTitle" )
		labelGather.setLabel( wnd.contentPanel.questArea, "QuestHelp:QuestDetails", "questArea" )
		labelGather.setLabel( wnd.contentPanel.questNPC, "QuestHelp:QuestDetails", "questNPC" )	
		
	def __getNPCPosition( self, npcID ):
		"""
		获取NPC坐标
		"""
		position = ""
		textID = npcID.replace( ' ', "" )
		npc = npcDatasMgr.getNPC( textID )
		if npc is not None:
			spaceLabel = npcDatasMgr.getNPCSpaceLabel( npc.id )
			position = npc.getPosition( spaceLabel[0] )
			if position is None: #如果没找到NPC的坐标，则设其为(0, 0)
				position = ( 0, 0 )
			else:
				position = ( int(position[0]), int(position[2]) )
		return position
		
	def hide( self ):
		self.__pyStTitle.text = ""
		self.__pyStLevel.text = ""
		self.__pyStArea.text = ""
		self.__pyStNPC.text = ""
		Window.hide( self )
		
	def show( self, questInfo, pyOwner = None ):
		self.__pyStTitle.text = questInfo.title
		self.__pyStLevel.text = questInfo.level
		self.__pyStArea.text = questInfo.spaceLabel
		npcName = questInfo.npcName
		npcID = questInfo.npcID
		npcPosition = self.__getNPCPosition( npcID )
		if npcID not in [item["npcID"] for item in forbidNPCs]:	#将NPC信息转换为超链接文本
			linkMark = "goto:%s" % npcID
			npcName = PL_Link.getSource( npcName, linkMark, cfc = "c4", hfc = "c3" )
		NPCtText = npcName + str( npcPosition ).replace( ' ',"" )
		self.__pyStNPC.text = NPCtText
		Window.show( self, pyOwner )
		
		
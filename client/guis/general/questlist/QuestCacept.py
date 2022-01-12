# -*- coding: gb18030 -*-
#
# $Id: QuestCacept.py, fangpengjun Exp $

"""
implement quest can accept list class
"""
from Weaker import RefEx
from guis import *
from LabelGather import labelGather
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.controls.TreeView import VTreeView as TreeView, TreeNode
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBox
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.controls.StaticText import StaticText
from Helper import questHelper
from config.client.QuestTypeDatas import Datas as QTDatas
from AbstractTemplates import MultiLngFuncDecorator
import GUIFacade
import csdefine
import csstatus
import csol
import StringFormat
import string
import Font

class deco_initPyQName( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF, font, size ) :
		"""
		"""
		deco_initPyQName.originalFunc( SELF, "MSJHBD.ttf", 17 )


class QuestCacept( TabPanel ):

	_ring_ids = ( 301,302,305,306 ) # ����������

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__typeNodes = {} #�������ͽڵ�
		self.__questsDict = {}
		self.__triggers = {}
		self.__registerTriggers()
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		labelGather.setLabel( panel.stQuests, "QuestHelp:QuestCacept", "canAcList" )
		self.__pyQuestNum = StaticText( panel.stNumber ) #�ɽ���������
		self.__pyQuestNum.text = ""

		self.__pyTVQuets = TreeView( panel.tvQuests, panel.vSBQuests ) # ��������ͼ
		self.__pyTVQuets.nodeOffset = 15.0
		self.__pyTVQuets.onTreeNodeBeforeExtend.bind( self.__onNodeBeforeExtend )

		self.__pyContenPanel = ContentPanel( panel.contentPanel )

		self.__pyBtnShut = HButtonEx( panel.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "QuestHelp:QuestCacept", "btnShut" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUEST_CAN_ACCEPT_ADD"] = self.__onQuestAdd				#�������
		self.__triggers["EVT_ON_QUEST_CAN_ACCEPT_REMOVE"] =  self.__onQuestRemove		#ɾ������
		self.__triggers["EVT_ON_QUEST_CAN_ACCEPT_SELECTED"] = self.__onCaceptSelected	#ѡ��ɽ�����ڵ�
		self.__triggers["EVT_ON_QUEST_LOG_ADD"] = self.__onQuestRemove					#������־��ӣ���ɽ�����ɾ��
		#self.__triggers["EVT_ON_QUEST_LOG_REMOVED"] = self.__onQuestAdd					#������־ɾ������ɽ��������
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onLevelChange
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# ---------------------------------------------------------------------
	def __addQuestNodes( self, typeID, quests ) :
		"""
		���ĳһ���͵�����ڵ�
		"""
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		questsSet = self.__questsDict.get( typeID )
		if questsSet is None :
			questsSet = set()
			self.__questsDict[typeID] = questsSet
		typeNode = self.__typeNodes.get( typeID )
		for quest in quests :
			questsSet.add( quest.id )
			typeNode.onQuestAdded( quest )
		typeNode.pyNodes.sort( key = lambda q : q.itemInfo.level )

	def __addQuestTypeNode( self, typeID ) :
		"""
		���ĳһ��������ĸ��ڵ�
		"""
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		if self.__typeNodes.has_key( typeID ) : return
		typeNode = TypeNode( typeID, self )
		self.__typeNodes[typeID] = typeNode
		typeNode.selectable = False
		typeNode.nodeOffset = 0.0
		typeNode.text = QTDatas.get( str( typeID ), "XX" )
		self.__pyTVQuets.pyNodes.add( typeNode )
		typeNode.showPlusIcon()

	def __removeTypeNodes( self, types ) :
		"""
		ɾ��ĳЩ�������ͼ�������������ڵ�
		"""
		for typeID in types :
			if typeID in self._ring_ids :
				typeID = self._ring_ids[0]
			typeNode = self.__typeNodes.get( typeID )
			if typeNode is None : continue
			typeNode.dispose()
			del self.__typeNodes[ typeID ]
			if self.__questsDict.has_key( typeID ) :
				del self.__questsDict[ typeID ]

	def __onQuestAdd( self, questID ):
		"""
		�������ڵ�,��������������������ڵ�
		"""
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		questsSet = self.__questsDict.get( typeID, [] )
		if questID in questsSet : return
		quest = questHelper.queryQuestByID( questID )
		if not quest : return										# ����Ҳ����������������
		if quest.questLevel == 0 : return							# �ȼ�Ϊ0��������ʾ
		self.__addQuestTypeNode( typeID )
		self.__addQuestNodes( typeID, [quest] )
		self.__pyTVQuets.pyNodes.sort( key = lambda pyNode : pyNode.typeID )

	def __onQuestRemove( self, questID ) :
		"""
		�Ƴ�����ڵ�
		"""
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		if typeID in self._ring_ids :
			typeID = self._ring_ids[0]
		questsSet = self.__questsDict.get( typeID, set() )
		if questID not in questsSet : return
		questsSet.remove( questID )
		typeNode = self.__typeNodes.get( typeID )
		typeNode.onQuestRemoved( questID )
		if typeNode.pyNodes.count <= 0 :
			del self.__typeNodes[ typeID ]
			del self.__questsDict[ typeID ]
		self.__pyContenPanel.reset()
		self.__pyContenPanel.title = ""

	def __onCaceptSelected( self, questID ):
		pass

	def __onNodeBeforeExtend( self, pyNode ):
		"""
		չ��ĳһ������ڵ�
		"""
		if not isinstance( pyNode, TypeNode ) : return
		typeID = pyNode.typeID
		isRingType = typeID == self._ring_ids[0]
		types = isRingType and self._ring_ids or [typeID]
		quests = questHelper.queryAcceptableQuestsByTypes( types )
		self.__addQuestNodes( typeID, quests )
		freshIDs = questHelper.queryAcceptableQuestIdsByTypes( types )
		datedIDs = self.__questsDict.get( typeID, set() )
		scrapIDs = datedIDs - freshIDs
		for questID in scrapIDs :
			self.__onQuestRemove( questID )

	def __onLevelChange( self, oldLevel, level ):
		"""
		�ȼ��ı�ʱ����£���нڵ㣬�Ա�չ��ʱ������������
		"""
		freshTypes = questHelper.queryAcceptableQuestTypes()
		datedTypes = set( self.__typeNodes.keys() )
		scrapTypes = datedTypes - freshTypes
		newTypes = freshTypes - datedTypes
		self.__removeTypeNodes( scrapTypes )								# ȥ����Ч���������ͽڵ�
		for typeID in newTypes :											# ����������������ͽڵ�
			self.__addQuestTypeNode( typeID )
		self.__pyTVQuets.collapseAll()
		self.__pyTVQuets.pyNodes.sort( key = lambda pyNode : pyNode.typeID )

	def __onShut( self ):
		self.pyBinder.hide()


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onQuestNodeClicked__( self, pyNode ) :
		"""
		ѡ��ĳһ������ڵ�
		"""
		questInfo = pyNode.itemInfo
		if questInfo is None : return
		self.__pyContenPanel.title = questInfo.name
		self.__pyContenPanel.setQuestInfo( questInfo )


	# ----------------------------------------------------------------------
	# public
	# ----------------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def initQuests( self ):
		self.reset()
		validTypes = questHelper.queryAcceptableQuestTypes()
		for typeID in validTypes :
			self.__addQuestTypeNode( typeID )
		self.__pyTVQuets.pyNodes.sort( key = lambda pyNode : pyNode.typeID )

	def reset( self ) :
		self.__typeNodes = {}
		self.__questsDict = {}
		self.__pyTVQuets.pyNodes.clear()
		self.__pyContenPanel.reset()
		self.__pyContenPanel.title = ""


# -----------------------------------------------------------
# ������ʾ���
# -----------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from NPCDatasMgr import npcDatasMgr

class ContentPanel( PyGUI ):
	def __init__( self, contentPanel ):
		PyGUI.__init__( self, contentPanel )
		self.__questID = -1

		self.__pyBgTitle = StaticText( contentPanel.stQName )
		self.__pyBgTitle.text = ""
		self.__initPyQName( "STLITI.TTF", 18 )

		self.__pyRtInfo = CSRichText( contentPanel.infoPanel ) #������Ϣ��ʾ
		self.__pyRtInfo.spacing = 2.0
		self.__pyRtInfo.font = "MSYHBD.TTF"
		self.__pyRtInfo.fontSize = 12.0
		self.__pyRtInfo.limning = Font.LIMN_NONE
		self.__countLimit = 88

		self.__pyAutoRunBtn = HButtonEx( contentPanel.autoRunBtn ) #�Զ�Ѱ·
		self.__pyAutoRunBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAutoRunBtn.visible = False
		self.__pyAutoRunBtn.onLClick.bind( self.__onAutoRun )

		self.__pyAutoFlyBtn = HButtonEx( contentPanel.autoFlyBtn ) #��·��
		self.__pyAutoFlyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyAutoFlyBtn.visible = False
		self.__pyAutoFlyBtn.onLClick.bind( self.__onAutoFly )

		self.__defaultColor = ( 51, 76, 97, 255 )
		self.__questInfo = None

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
#		labelGather.setLabel( contentPanel.frmQuestInfo.bgTitle.stTitle, "QuestHelp:QuestCacept", "questDsp" )
		labelGather.setPyBgLabel( self.__pyAutoRunBtn, "QuestHelp:QuestCacept", "autoRunBtn" )
		labelGather.setPyBgLabel( self.__pyAutoFlyBtn, "QuestHelp:QuestCacept", "autoFlyBtn" )

	@deco_initPyQName
	def __initPyQName( self, font, size ) :
		"""
		"""
		self.__pyBgTitle.font = font
		self.__pyBgTitle.fontSize = size

	def __onAutoRun( self ):
		if not self.__questInfo:return
		player = BigWorld.player()
		npcID = self.__questInfo.npcID
		spaceLabel = player.getSpaceLabel()
		pos = rds.npcDatasMgr.getNPCPosition( npcID, spaceLabel )
		if pos is None :
			return
		player.setExpectTarget( npcID )					# ����׷��Ŀ��NPC��ID
		npcSpace = rds.npcDatasMgr.getNPCSpaceLabel( npcID )[0]
		player.autoRun( pos, 8, npcSpace )

	def __onAutoFly( self ):
		if not self.__questInfo:return
		player = BigWorld.player()
		items = []
		items = player.findItemsByIDFromNKCK( 50101003 )
		npcID = self.__questInfo.npcID
		questID = self.__questInfo.id
		if items == []:
			items = player.findItemsByIDFromNKCK( 50101002 )
		if items == []:
			player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
			return
		if not player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.stopMove()									# ������ֹͣ�ƶ����Ա�֤׷��Ŀ�겻�����
			player.cell.flyToNpc( npcID, questID, items[0].order )
			player.setExpectTarget( npcID )				# ����׷��Ŀ��NPC��ID
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )

	def setQuestInfo( self, questInfo ):
		self.__pyAutoRunBtn.visible = questInfo is not None
		self.__pyAutoFlyBtn.visible = questInfo is not None
		if questInfo is None:return
		self.__questInfo = questInfo
		npcID = questInfo.npcID
		textID = npcID.replace( ' ', '' )
		level = questInfo.level
		npc = npcDatasMgr.getNPC( textID )
		content = questInfo.content
		spaceLabel = ("","")
		name = ""
		if npc is not None:
			name = npc.name
			spaceLabel = npcDatasMgr.getNPCSpaceLabel( npc.id )
			position = npc.getPosition( spaceLabel[0] )
			self.__pyAutoRunBtn.enable = position is not None
			self.__pyAutoFlyBtn.enable = position is not None

		content = csol.asWideString( content )
		if len( content ) < self.__countLimit:
			content = content
		else:
			# ��������ת���ַ�//
			enStr = string.punctuation + string.letters + string.digits + " "
			if content[self.__countLimit] in enStr:
				for i in xrange( self.__countLimit ):
					if content[self.__countLimit + i ] in enStr: continue
					else:
						content = content[:self.__countLimit + i] + "......"
						break
			else:
				content = content[:self.__countLimit] + "......"
		content = csol.asString( content )
		content = StringFormat.format( content )
		contentText = PL_Font.getSource( "%s"%content, n = "MSYHBD.TTF", fc = ( 51, 76, 97, 255 ) ) #��������

		localText = PL_Font.getSource( "%s"%spaceLabel[1], n = "MSYHBD.TTF", fc = ( 0, 128, 0, 255 )) #�������ڵ�
		localText = PL_Font.getSource( labelGather.getText( "QuestHelp:QuestCacept", "questArea" )%( PL_NewLine.getSource(), localText ), fc = self.__defaultColor )

		nameText = PL_Font.getSource( "%s"%name, n = "MSYHBD.TTF", fc = ( 0, 128, 0, 255 ) ) #��������NPC����
		nameText = PL_Font.getSource( labelGather.getText( "QuestHelp:QuestCacept", "questPublisher" )%( PL_NewLine.getSource(), nameText ), fc = self.__defaultColor )

		levelText = PL_Font.getSource( labelGather.getText( "QuestHelp:QuestCacept", "questLevel" )%level, fc = ( 0, 128, 0, 255 ) ) #����ȼ�
		levelText = PL_Font.getSource( labelGather.getText( "QuestHelp:QuestCacept", "levelInfo" )%( PL_NewLine.getSource(), levelText ), fc = self.__defaultColor )

		self.__pyRtInfo.text = contentText + localText + nameText + levelText
		
		self.__pyAutoFlyBtn.top = self.__pyRtInfo.bottom + 20.0
		self.__pyAutoRunBtn.top = self.__pyAutoFlyBtn.bottom + 5.0

	def reset( self ):
		self.__pyRtInfo.text = ""
		self.__pyAutoRunBtn.visible = False
		self.__pyAutoFlyBtn.visible = False

	def _setTitle( self, name ):
		self.__pyBgTitle.text = name

	def _getTitle( self ):
		return self.__pyBgTitle.text

	title = property( _getTitle, _setTitle )


# --------------------------------------------------------------
class TypeNode( TreeNode ):
	def __init__( self, typeID, binder ):
		node = GUI.load( "guis/general/questlist/node.gui" )
		uiFixer.firstLoadFix( node )
		TreeNode.__init__( self, node, binder )
		self.autoWidth = False
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.font = "STLITI.TTF"
		self.fontSize = 16.0
		self.commonForeColor = ( 231, 205, 140, 255 )
		self.highlightForeColor = ( 231, 205, 140, 255 )
		self.selectedForeColor = ( 231, 205, 140, 255 )
		self.limning = Font.LIMN_OUT
		self.limnColor = (0, 0, 0, 255 )
		self.__pyHooker = PyGUI( node.hook )
		self.__pyHooker.visible = False
		self.__pyNodeBg = PyGUI( node.nodeBg )
		self.__pyNodeBg.visible = False
		self.__typeID = typeID
		self.__quests = {} # �����ӽ��
		self.itemInfo = None

	# -----------------------------------------
	# public
	# -----------------------------------------
	def onQuestAdded( self, newItemInfo ):
		if newItemInfo is None : return
		questID = newItemInfo.id
		if self.__quests.has_key( questID ):return
		questNode = QuestNode( self.pyBinder )
		questItemInfo = QuestItemInfo( newItemInfo )
		questNode.showPlusMinus = False
		questNode.crossFocus = False
		questNode.itemInfo = questItemInfo
		questNode.text ="(%d)%s"%( questItemInfo.level, questItemInfo.name )

		# �������񼶱����ɫ������������ɫ
		temp =  questItemInfo.level - BigWorld.player().level
		if temp <= -5:
			tempColor = ( 51, 76, 97, 255 )	#��ɫ
		elif temp> -5 and temp <= 0:
			tempColor = ( 255, 255, 255, 255 )	#��ɫ
		elif temp > 0 and temp <=3:
			tempColor = ( 255, 127, 0, 255 ) #��ɫ
		else:
			tempColor = ( 193, 23, 0, 255 ) #��ɫ
		questNode.commonForeColor = tempColor
		questNode.foreColor = questNode.commonForeColor
		self.__quests[questID] = questNode
		self.pyNodes.add( questNode )

	def __addResortNode( self, questNode ): # *��Ӳ�����
		if self.pyNodes.count <= 0:
			self.pyNodes.add( questNode )
		tempLevel = questNode.itemInfo.level
		for index, existNode in enumerate( self.pyNodes ):
			if existNode.itemInfo.level > tempLevel:
				self.pyNodes.insert( index,questNode )
			else:
				self.pyNodes.add( questNode )
				return

	def onQuestRemoved( self, questID ):
		if not self.__quests.has_key( questID ):
			return
		questNode = self.__quests.pop( questID )
		self.pyNodes.remove( questNode )
		if self.pyNodes.count <= 0: #�ӽ��Ϊ�գ��������Լ�
			self.dispose()

	def getQuestItemInfo( self, questID ):
		if self.__quests.has_key( questID ):
			questNode = self.__quests[questID]
			itemInfo = questNode.itemInfo
			return 	itemInfo

	def isCanAdd( self, quests ):
		"""
		�Ƿ����������ڵ�
		"""
		for quest in quests:
			if quest.questLevel > 0:
				return True
		return False

	#	 ---------------------------------------------
	#	 property methods
	#	 ---------------------------------------------
	def _setForeColor( self, color ) : #�������;�����ɫ
		TreeNode._setForeColor( self, color )
#		self.__pyLbLevel.color = color
#		self.__pyLbOption.color = color

	def _getForeColor( self ):
		return TreeNode._getForeColor( self )
#		return self.__pyLbLevel.color

	def _setTypeID( self, id ):
		self.__typeID = id

	def _getTypeID( self ):
		return self.__typeID

	foreColor = property( _getForeColor, _setForeColor )
	typeID = property( _getTypeID, _setTypeID )

# --------------------------------------------------------------------
# quest info
# --------------------------------------------------------------------
class QuestItemInfo :
	def __init__( self, itemInfo ) :
		self.id = itemInfo.id			# quest id
		self.name = itemInfo.title				# quest name
		self.level = itemInfo.questLevel				# quest level
		self.content = itemInfo.content				# quest content
		self.npcID = itemInfo.npcID


# --------------------------------------------------------------------------------
class QuestNode( TreeNode ):
	def __init__( self, pyBiner ):

		TreeNode.__init__( self )
		self.focus = True
		self.crossFocus = True
		self.selectable = True
		self.font = "MSYHBD.TTF"
		self.fontSize = 12.0
		self. limning = Font.LIMN_NONE
		self.__itemInfo = None
		self.__isTraced = False
		self.__triggers = {}
		
		self.pyBiner = pyBiner
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

	def __onUpdateLevel( self, oldLevel, level ):
		"""
		��ɫ�ȼ��ı䣬����������ɫ
		"""
		if self.itemInfo is None:return
		temp = self.itemInfo.level - level
		if temp <= -5:
			tempColor = ( 51, 76, 97, 255 )	#��ɫ
		elif temp> -5 and temp <= 0:
			tempColor = ( 255, 255, 255, 255 )	#��ɫ
		elif temp > 0 and temp <=3:
			tempColor = ( 255, 127, 0, 255 ) #��ɫ
		else:
			tempColor = ( 193, 23, 0, 255 ) #��ɫ
		self.commonForeColor = tempColor
		self.highlightForeColor = tempColor
		if not self.selected:
			self.foreColor = self.commonForeColor

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]()( *args )


	# ---------------------------------------------
	# property methods
	# ---------------------------------------------
	def onLClick__( self, mods ):
		TreeNode.onLClick__( self, mods )
		if self.itemInfo is None: return
		if self.pyBiner is None: return
		self.pyBiner.onQuestNodeClicked__( self )
		return True

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	def _getItemInfo( self ):
		return self.__itemInfo

	def _setSelected( self, selected ) :
		if self.selected == selected : return
		self.selectedBackColor = self.commonForeColor
		self.selectedForeColor = ( 0, 128, 0, 255 )
		TreeNode._setSelected( self, selected )

	itemInfo = property( _getItemInfo, _setItemInfo )
	selected = property( TreeNode._getSelected, _setSelected )

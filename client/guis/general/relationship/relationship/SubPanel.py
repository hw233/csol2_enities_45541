# -*- coding: gb18030 -*-
#
# $Id: SubPanel.py $

"""
implement SubPanel class
"""
from guis import *
from LabelGather import labelGather
from guis.controls.ListPanel import ListPanel
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListItem import MultiColListItem as MCItem
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.general.tongabout.WarIntergral import TaxisButton
from guis.general.chatwindow.playmatechat.PLMChatMgr import plmChatMgr
from ChatFacade import chatFacade
from InfosBox import InfosBox
import csdefine
import csconst
import Const
import csstatus
import csstring

MASTER_PRENTICE = csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE|csdefine.ROLE_RELATION_PRENTICE_EVER|csdefine.ROLE_RELATION_MASTER_EVER
LIMITED_MAX_LENGTH = 16

class SubPanel( TabPanel ):
	def __init__( self, panel, groupID ):
		TabPanel.__init__( self, panel )
		self.groupID = groupID

		self.sortByNameFlag = False	# ����������ı�ǣ����Ϊ0��ʾ��ǰ�Ǵ�С�����ţ�Ϊ1���ʾ�Ӵ�С��
		self.sortByLevelFlag = 0	# ���ȼ�����ı��
		self.sortByMetierFlag = 0	# ��ְҵ����ı��
		self.areaQueryTime	= 0		#�������������ʱ����

		self.__pyBtnName = HButtonEx( panel.header.header_0 )
		self.__pyBtnName.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnName.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnName, "RelationShip:main", "btnName" )
		self.__pyBtnName.onLClick.bind( self.__onSortByName )

		self.__pyBtnLevel = HButtonEx( panel.header.header_1 )
		self.__pyBtnLevel.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnLevel.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnLevel, "RelationShip:main", "btnLevel" )
		self.__pyBtnLevel.onLClick.bind( self.__onSortByLevel )

		self.__pyBtnPro = HButtonEx( panel.header.header_2 )
		self.__pyBtnPro.setExStatesMapping( UIState.MODE_R3C1 )
		#self.__pyBtnPro.isSort = True
		labelGather.setPyBgLabel( self.__pyBtnPro, "RelationShip:main", "btnProf" )
		self.__pyBtnPro.onLClick.bind( self.__onSortByPro )

		self.__pyOptionCB = ComboBox( panel.header.optionBox ) # ��ᣬ�����ѡ��
		self.__pyOptionCB.text = labelGather.getText( "RelationShip:TongPanel", "options" )
		self.__pyOptionCB.foreColor = ( 0, 255, 186, 255 )
		self.__pyOptionCB.autoSelect = False
		self.__pyOptionCB.onItemSelectChanged.bind( self.__onOptionChange )

		pyTong = ComboItem( labelGather.getText( "RelationShip:RelationPanel", "tong" ) )
		pyArea = ComboItem( labelGather.getText( "RelationShip:RelationPanel", "area" ) )
		pyAppShip = ComboItem( labelGather.getText( "RelationShip:RelationPanel", "apprenticeship" ) )
		self.__pyOptionCB.addItems( [pyTong, pyArea] )
		if groupID == MASTER_PRENTICE:
			self.__pyOptionCB.addItem( pyAppShip )
		for pyComText in self.__pyOptionCB.pyItems:
			pyComText.h_anchor = "CENTER"

		self.__pyListPanel = ListPanel( panel.listPanel, panel.listBar )
		self.__pyListPanel.rowSpace = 1.0
		self.__pyListPanel.autoSelect = False
		self.__pyListPanel.rMouseSelect = True

		#self.__pyInfosBox = InfosBox( )

		self.__createNodeMenu()

	def __onSortByName( self ):	# wsf add
		"""
		����������Ŀǰֻ������ѡ�
		��ָ�������ĸ��ڵ����жϵ�ǰ���������ĸ��ڵ�
		"""
		flag = self.sortByNameFlag and True or False
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.playerName, reverse = flag, filter = self.blackFilter )
		self.sortByNameFlag = not self.sortByNameFlag

	def __onSortByLevel( self ):	# wsf add
		"""
		���ȼ�����
		"""
		flag = self.sortByLevelFlag and True or False
		print "eer flag",flag
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.level, reverse = flag, filter = self.blackFilter )
		self.sortByLevelFlag = not self.sortByLevelFlag

	def __onSortByPro( self ): # wsf add
		"""
		��ְҵ����
		"""
		flag = self.sortByMetierFlag and True or False
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.raceStr, reverse = flag, filter = self.blackFilter )
		self.sortByMetierFlag = not self.sortByMetierFlag

	def __createNodeMenu( self ):
		"""
		�����Ҽ��˵�( rewriten by huangyongwei at 2008.04.17)
		"""
		self.__pyNodeMenu = ContextMenu( )
		self.__pyNodeMenu.addBinder( self.__pyListPanel )
		self.__pyNodeMenu.onItemClick.bind( self.__onItemClick )
		self.__pyNodeMenu.onBeforePopup.bind( self.__onMenuPopUp )
		self.pyItem0 = DefMenuItem( "" )
		self.pyItem0.enable = False
		self.pyItem1 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "sendMsg" ) )		#������Ϣ
		self.pyItem3 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "teamInvite" ) )		#���
		self.pyItem4 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "tongInvite" ) )		#�������
		self.pyItem5 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "addFriend" ) )		#��������
		self.pyItem6 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "blackList" ) )		#������
		self.pyItem7 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "delFriend" ) )		#ɾ������
		self.pyItem8 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "delBlack" ) )		#ɾ��������
		self.pyItem9 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "shutDown" ) )		#�ر�
		self.pyItem10 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "checkInfo" ) )		#�鿴��Ϣ
		self.pyItem11 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "originateChat" ) )	#��������
		self.pyItem12 = DefMenuItem( labelGather.getText( "RelationShip:RelationPanel", "browseChatLog" ) )	#�鿴�����¼

	def __onItemClick( self, pyItem ):
		player = BigWorld.player()
		pySelItem = self.__pyListPanel.pySelItem
		if pySelItem is None:return
		name = pySelItem.relation.playerName
		relation = pySelItem.relation
		if relation is None:return
		relationUID = relation.relationUID
		if pyItem == self.pyItem1:
			chatFacade.whisperWithChatWindow( name )
		elif pyItem == self.pyItem3: # �������
			player.inviteJoinTeam( name )
		elif pyItem == self.pyItem4:# �������
			player.tong_requestJoinByPlayerName( name )
		elif pyItem == self.pyItem5: #��Ϊ����
			player.addFriend( name )
		elif pyItem == self.pyItem6: # ���������
			if not player.blackList.has_key( name ):
				player.addBlacklist( name )
				return
			player.statusMessage( csstatus.BLACKLIST_NAME_REPEAT, name )
			return
		elif pyItem == self.pyItem7: # ɾ������
			if player.friends.has_key( name ):
				player.removeFriend( relationUID )
				return
			player.statusMessage( csstatus.ROLE_NOT_FIND_IN_FRIEND_LIST )
			return
		elif pyItem == self.pyItem8: # ɾ��������
			player.removeBlackList( relationUID )
		elif pyItem == self.pyItem10:
			InfosBox.instance().show( pySelItem )
			BigWorld.player().base.queryTongGrade( pySelItem.relation.relationUID )
			self.queryAreaInfo( self.groupID )		#�����ȡλ����Ϣ
#			BigWorld.player().base.rlt_queryAreaInfo( self.groupID )
		elif pyItem == self.pyItem11 : # ��������
			self.__originateChat( relation )
		elif pyItem == self.pyItem12 : # �鿴���������¼
			self.__browseChatLog( relation )

	def __onMenuPopUp( self ): # �����Ҽ��˵�
		"""
		�˵�����ʱ����( rewriten by huangyongwei at 2008.04.17 )
		"""
		pySelItem = self.__pyListPanel.pySelItem			# ��ȡ�����е��Ǹ��ڵ�
		if pySelItem is None : return -1						# ���� -1 ��ʾ�ܾ���ʾ�˵�
		self.__pyNodeMenu.pyItems.clear()
		relation = pySelItem.relation
		name = relation.playerName
		self.pyItem0.text = name
		player = BigWorld.player()
		isOnline = relation.online
		grade = player.tong_grade
		canCons = player.isJoinTong() and relation.tong == 0 and player.tong_checkDutyRights( grade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
		isFriend = name in player.friends
		isBlackList = name in player.blackList
		self.__pyNodeMenu.pyItems.adds( [self.pyItem0, self.pyItem10] ) # ��ʾ��ϵ�������
		if self.groupID == csdefine.ROLE_RELATION_FRIEND: #�ں�������
			self.__pyNodeMenu.pyItems.adds( [self.pyItem11, self.pyItem12] )			
			if isOnline: # ����
				self.__pyNodeMenu.pyItems.adds( [self.pyItem1, self.pyItem3, self.pyItem4, self.pyItem6, self.pyItem7] )
				self.pyItem4.visible = canCons
			else: # ������
				self.__pyNodeMenu.pyItems.adds( [self.pyItem6, self.pyItem7] )
			self.pyItem6.visible = not isBlackList
		elif self.groupID == csdefine.ROLE_RELATION_BLACKLIST: # �ں�������
			self.__pyNodeMenu.pyItems.adds( [self.pyItem5, self.pyItem8] )
			self.pyItem5.visible = not isBlackList
		elif self.groupID == MASTER_PRENTICE: # ʦͽ
			if isOnline: # ����
				self.__pyNodeMenu.pyItems.adds( [self.pyItem1, self.pyItem3, self.pyItem4] )
				self.pyItem4.visible = canCons
			else: # ������
				return -1
		elif self.groupID == csdefine.ROLE_RELATION_SWEETIE: # ���޻�����
			if isOnline:
				self.__pyNodeMenu.pyItems.adds( [self.pyItem1, self.pyItem3, self.pyItem4] )
				self.pyItem4.visible = canCons
			else:
				return -1
		elif self.groupID == csdefine.ROLE_RELATION_FOE: #����
			if isOnline:
				self.__pyNodeMenu.pyItems.adds( [self.pyItem1, self.pyItem3] )
			else:
				return -1
		self.__pyNodeMenu.pyItems.add( self.pyItem9 ) # �رղ˵�
		return True											# ���� True ͬ����ʾ�˵�

	def __onOptionChange( self, pyItem ):
		selIndex = self.__pyOptionCB.selIndex
		player = BigWorld.player()
		if selIndex == 0: # ���
			for pyItem in self.__pyListPanel.pyItems:
				tongStr = labelGather.getText( "RelationShip:RelationPanel", "without" )
				if pyItem.relation.online:
					if pyItem.relation != "":
						tongStr = pyItem.relation.tong
				else:
					tongStr = "--"
				pyItem.pyCols[3].text = tongStr
			self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.tong, reverse = True, filter = self.blackFilter )
		elif selIndex == 1: # ����
			if BigWorld.stime() - self.areaQueryTime < 5.0:
				return
			self.areaQueryTime = BigWorld.stime()
			for pyItem in self.__pyListPanel.pyItems:
				pyItem.pyCols[3].text = "--"
			self.queryAreaInfo( self.groupID )
		else: #ʦͽ��ʦ״̬
			for pyItem in self.__pyListPanel.pyItems:
				playerName = pyItem.relation.playerName
				if pyItem.relation.online:
					if player.prenticeEverDict.has_key( playerName ) or \
						player.masterEverDict.has_key( playerName ):
							pyItem.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "apprenticed" )
					if player.prenticeDict.has_key( playerName ) or \
						player.masterDict.has_key( playerName ):
							pyItem.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "inpractice" )
				else:
					pyItem.pyCols[3].text = "--"

	def __originateChat( self, relation ) :
		"""
		�����������
		"""
		name = relation.playerName
		plmChatMgr.onOriginateChat( name )

	def __browseChatLog( self, relation ) :
		"""
		�鿴�����¼
		"""
		name = relation.playerName
		plmChatMgr.onBrowseChatLog( name )

	def addRelation( self, relationUID ):
		"""
		��ӹ�ϵ
		"""
		player = BigWorld.player()
		relation = player.relationDatas.get( relationUID, None )
		if relation is None:return		
		relationUIDs = [pyItem.relation.relationUID for pyItem in self.__pyListPanel.pyItems]
		if not relationUID in relationUIDs:
			pyItem = RelationItem( relation, self )
			self.__pyListPanel.addItem( pyItem )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.playerName, filter = self.blackFilter )

	def delRelation( self, relationUID ):
		"""
		ɾ����ϵ
		"""
		for pyItem in self.__pyListPanel.pyItems:
			relation = pyItem.relation
			if relation is None:continue
			curRelationUID = relation.relationUID
			playerName = relation.playerName
			if self.groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE: #���ˡ�����
				if BigWorld.player().sweetieDict.has_key( playerName ): #������޹�ϵ�����������˹�ϵ
					self.updateRelation( relationUID ) #���¸��½�����Ϣ
				else:
					if curRelationUID == relationUID:
						self.__pyListPanel.removeItem( pyItem ) #ֻ�з��޹�ϵ�����������˹�ϵ
			else:
				if curRelationUID == relationUID:
					self.__pyListPanel.removeItem( pyItem )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.playerName, filter = self.blackFilter )


	def updateRelation( self, relationUID ):
		"""
		���¹�ϵ��Ϣ
		"""
		player = BigWorld.player()
		relation = player.relationDatas.get( relationUID, None )
		if relation is None:return
		relationUIDs = [pyItem.relation.relationUID for pyItem in self.__pyListPanel.pyItems]
		if relationUID in relationUIDs:
			for pyItem in self.__pyListPanel.pyItems:
				if pyItem.relation.relationUID == relationUID:
					pyItem.updateRelation( relation )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.playerName, filter = self.blackFilter )
		
	def updateAllItems( self ):
		"""
		ˢ������ѡ��
		"""
		player = BigWorld.player()
		for pyItem in self.__pyListPanel.pyItems:
			relationUID = pyItem.relation.relationUID
			relation = player.relationDatas.get( relationUID, None )
			if relation is None:return
			pyItem.updateRelation( relation )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.playerName, filter = self.blackFilter )
		
	def updateFriendly( self, relationUID, friendlyValue ):
		"""
		���º��Ѷ�
		"""
		for pyRelation in self.__pyListPanel.pyItems:
			relation = pyRelation.relation
			curRelationUID = relation.relationUID
			if curRelationUID == relationUID:
				pyRelation.updateFriendly( friendlyValue )

	def updateLevel( self, relationUID, level ):
		"""
		���µȼ�
		"""
		for pyRelation in self.__pyListPanel.pyItems:
			relation = pyRelation.relation
			curRelationUID = relation.relationUID
			if curRelationUID == relationUID:
				pyRelation.updateLevel( level )
				
	def updateTongGrade( self, relationUID, tongGrade ) :
		InfosBox.instance().updateTongGrade( relationUID, tongGrade )

	def updateArea( self, relationUID, spaceType, position, lineNumber ):
		"""
		���¹�ϵ������Ϣ
		"""
#		if self.__pyOptionCB.selIndex != 1:return
		selIndex = self.__pyOptionCB.selIndex
		player = BigWorld.player()
		param = {"spaceType":spaceType,"position":position,"lineNumber":lineNumber}
		for pyItem in self.__pyListPanel.pyItems:
			relation = pyItem.relation
			curRelationUID = relation.relationUID
			if curRelationUID == relationUID:
				pyItem.updateLastColumn( 0, relationUID,selIndex, param )
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.pyCols[3].text, reverse = False, filter = self.blackFilter )

	def updateOffLine( self, relationUID ):
		for pyItem in self.__pyListPanel.pyItems:
			relation = pyItem.relation
			curRelationID = relation.relationUID
			if curRelationID == relationUID:
				pyItem.onOffLine()

	def onTongNameChange( self, relationUID, tongName ):
#		if self.__pyOptionCB.selIndex != 1:return
		for pyItem in self.__pyListPanel.pyItems:
			relation = pyItem.relation
			if relationUID == relation.relationUID:
				pyItem.updateTongName( tongName )
				
	def queryAreaInfo( self, groupID ) :
		prenticeAndMasterList =[csdefine.ROLE_RELATION_MASTER, csdefine.ROLE_RELATION_PRENTICE,\
		csdefine.ROLE_RELATION_PRENTICE_EVER,csdefine.ROLE_RELATION_MASTER_EVER]		#ʦͽ�б��ҳ�������ֹ�ϵ
		if groupID == MASTER_PRENTICE :
			 for igroupID in prenticeAndMasterList :
			 	 BigWorld.player().base.rlt_queryAreaInfo( igroupID )
		else:
			BigWorld.player().base.rlt_queryAreaInfo( groupID )

	def getRelations( self ):
		"""
		��ȡ��ϵ�б�
		"""
		return self.__pyListPanel.pyItems

	def getSelItem( self ):
		"""
		��ȡ��ǰѡ��Ĺ�ϵ�ؼ�
		"""
		return self.__pyListPanel.pySelItem

	def isShowOffLine( self, isShow ):
		"""
		�Ƿ���ʾ���������
		"""
		self.__pyListPanel.clearItems()
		relations = []
		player = BigWorld.player()
		relationDatas = BigWorld.player().relationDatas
		for relationUID, relationData in relationDatas.iteritems():
			if self.groupID&relationData.relationStatus:
				relations.append( relationData )
		for relation in relations:
			relationUID = relation.relationUID
			if isShow:
				self.addRelation( relationUID )
			else:
				if not relation.online:continue
				self.addRelation( relationUID )

	def clearItems( self ):
		"""
		��ս����ϵ�б�
		"""
		self.__pyListPanel.clearItems()
	
	def filter( self, items ):
		filterItem = items
		item1 = [item for item in filterItem if item.relation.online]
		item2 = [item for item in filterItem if not item.relation.online]
		return [item1, item2]

	def blackFilter( self, items ):
		player = BigWorld.player()
		filterItem = items
		item1 = [item for item in filterItem if item.relation.online and not item.relation.playerName in player.blackList]
		item2 = [item for item in filterItem if item.relation.online and item.relation.playerName in player.blackList]
		item3 = [item for item in filterItem if not item.relation.online and not item.relation.playerName in player.blackList]
		item4 = [item for item in filterItem if not item.relation.online and item.relation.playerName in player.blackList]
		return [item1, item2, item3, item4]

	def reset( self ) :
		self.clearItems()
		InfosBox.instance().hide()

	def setOption( self ):
		self.__pyOptionCB.selIndex = 0
		for pyItem in self.__pyListPanel.pyItems:
			tongStr = labelGather.getText( "RelationShip:RelationPanel", "without" )
			if pyItem.relation.tong != 0:
				if pyItem.relation.online:
					tongStr = pyItem.relation.tong
				else:
					tongStr = "--"
			pyItem.pyCols[3].text = tongStr
		self.__pyListPanel.sort2( key = lambda pyItem: pyItem.relation.tong, reverse = True, filter = self.blackFilter )

	def _getOptionIndex( self ):
		return self.__pyOptionCB.selIndex

	def _setOptionIndex( self, index ):
		pySelItem = self.__pyOptionCB.pyItems[index]
		self.__pyOptionCB.pySelItem = pySelItem

	optionIndex = property( _getOptionIndex, _setOptionIndex )

# ------------------------------------------------
from guis.controls.ListItem import ListItem
from guis.controls.Label import Label
import csconst
class RelationItem( ListItem ):

	__cc_item = None

	def __init__( self, relation, pyBinder = None ) :
		if RelationItem.__cc_item is None :
			RelationItem.__cc_item = GUI.load( "guis/general/relationwindow/relationship/relationitem.gui" )
		item = util.copyGuiTree( RelationItem.__cc_item )
		uiFixer.firstLoadFix( item )
		ListItem.__init__( self, item, pyBinder )
		self.pyCols_ = []
		self.__initialize( item )
		#self.pyCols[0].pyText_.h_anchor = "LEFT"
		self.online = False
		self.area = ""
		self.raceStr = ""
		self.relation = relation
		self.updateRelation( relation )

	def subclass( self, item, pyBinder = None ) :
		ListItem.subclass( self, item, pyBinder )
		self.__initialize( item )

	def __del__( self ) :
		ListItem.__del__( self )
		if Debug.output_del_ListItem :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, item ) :
		if item is None : return
		self.__initCells( item )
		self.foreColors_ = {}
		self.foreColors_[UIState.COMMON] = self.foreColor
		self.foreColors_[UIState.HIGHLIGHT] = 255, 255, 255, 255
		self.foreColors_[UIState.SELECTED] = 10, 255, 10, 255
		self.foreColors_[UIState.DISABLE] = 128, 128, 128, 255
		for pyCol in self.pyCols_ :
			pyCol.foreColors_ = copy.copy( self.foreColors_ )

	def __initCells( self, panel ) :
		for name, ch in panel.children :
			if "col_" not in name : continue
			pyCol = CelItem( ch, self )
			self.pyCols_.append( pyCol )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		for pyCol in self.pyCols_ :
			pyCol.onStateChanged_( state )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setTextes( self, *textes ) :
		if isDebuged :
			assert len( textes ) == len( self.pyCols_ )
		for index, pyCol in enumerate( self.pyCols_ ) :
			pyCol.setText( textes[index] )

	def updateRelation( self, relation ):
		player = BigWorld.player()
		if relation is None:return
		self.relation = relation
		level = relation.level
		raceClass = relation.raceClass
		playerName = relation.playerName
		relationStatus = relation.relationStatus
		tongName = relation.tong
		familyName = relation.family
		optionIndex = self.pyBinder.optionIndex
		groupID = self.pyBinder.groupID
		if groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE:
			if player.couple_lover: #���ڷ��޹�ϵ����������ʾ
				coupleName = player.couple_lover.playerName
				if coupleName == playerName:
					gender = player.getGender()
					if gender == csdefine.GENDER_MALE:
						playerName = labelGather.getText( "RelationShip:RelationPanel", "wifeTag" )%playerName
					else:
						playerName = labelGather.getText( "RelationShip:RelationPanel", "husbandTag" )%playerName
			else: #�����ڷ��޹�ϵ����������˹�ϵ
				if player.sweetieDict.has_key( playerName ):
					playerName = labelGather.getText( "RelationShip:RelationPanel", "sweeteTag" )%playerName
		elif groupID == MASTER_PRENTICE:
			if player.prenticeDict.has_key( playerName ) or \
				player.prenticeEverDict.has_key( playerName ):
				playerName = labelGather.getText( "RelationShip:RelationPanel", "prenticeTag" )%playerName
			if player.masterDict.has_key( playerName ) or \
				player.masterEverDict.has_key( playerName ):
				playerName = labelGather.getText( "RelationShip:RelationPanel", "masterTag" )%playerName
		elif groupID == csdefine.ROLE_RELATION_BLACKLIST:
			self.online = False
			self.setTextes( playerName, "--", "--", "--" )
			return
		raceStr = "--"
		levelStr = "--"
		if level != 0:
			levelStr = str( level )
		if raceClass != 0:
			raceStr =  csconst.g_chs_class[raceClass & csdefine.RCMASK_CLASS]
		self.raceStr = raceStr
		name = self.relation.playerName
		if relation.online and not name in player.blackList:
			lastInfo = labelGather.getText( "RelationShip:RelationPanel", "without" )
			if optionIndex == 0 and tongName != "":
				lastInfo = tongName
			if optionIndex == 1:
				lastInfo = "--"
				self.pyBinder.queryAreaInfo( self.pyBinder.groupID )
			elif optionIndex == 2:
				player = BigWorld.player()
				if player.prenticeEverDict.has_key( name ) or \
					player.masterEverDict.has_key( name ):
						lastInfo = labelGather.getText( "RelationShip:RelationPanel", "apprenticed" )
				if player.prenticeDict.has_key( name ) or \
					player.masterDict.has_key( name ):
						lastInfo = labelGather.getText( "RelationShip:RelationPanel", "inpractice" )
			self.commonForeColor = 255,255,255,255
			self.setTextes( playerName, levelStr, raceStr, lastInfo )
		else:
			self.commonForeColor = 127,127,127,255
			self.setTextes( playerName, "--", "--", "--" )

	def updateLastColumn( self, type, relationUID, selIndex, param = {} ):
		if not self.relation.online:		# �����������ʼ����ʾδ֪
			self.pyCols[3].text = "--"
			return
		spaceType = param.get( "spaceType" )
		if spaceType.startswith("fu_ben") and spaceType not in Const.CC_FUBENNAME_DONOT_CONVERT_LIST:
			self.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "spaceCopy" )
			return
		area = rds.mapMgr.getArea( spaceType, param.get("position") )
		lineNumber = param.get("lineNumber")
		areaStr = lineNumber and labelGather.getText( "RelationShip:RelationPanel", "lineNumber" )%(area.name,lineNumber) or area.name
		self.area = areaStr
		if InfosBox.instance().visible :
			InfosBox.instance().updateArea( relationUID, areaStr )
		if selIndex == 1:
			self.pyCols[3].text = areaStr
		

	def onOffLine( self ):
		self.commonForeColor = 127,127,127,255
		playerName = self.relation.playerName
		groupID = self.pyBinder.groupID
		player = BigWorld.player()
		if groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE:
			if player.couple_lover: #���ڷ��޹�ϵ����������ʾ
				coupleName = player.couple_lover.playerName
				if coupleName == playerName:
					gender = player.getGender()
					if gender == csdefine.GENDER_MALE:
						playerName = labelGather.getText( "RelationShip:RelationPanel", "wifeTag" )%playerName
					else:
						playerName = labelGather.getText( "RelationShip:RelationPanel", "husbandTag" )%playerName
			else: #�����ڷ��޹�ϵ����������˹�ϵ
				if player.sweetieDict.has_key( playerName ):
					playerName = labelGather.getText( "RelationShip:RelationPanel", "sweeteTag" )%playerName
		elif groupID == MASTER_PRENTICE:
			if player.prenticeDict.has_key( playerName ) or \
				player.prenticeEverDict.has_key( playerName ):
				playerName = labelGather.getText( "RelationShip:RelationPanel", "prenticeTag" )%playerName
			if player.masterDict.has_key( playerName ) or \
				player.masterEverDict.has_key( playerName ):
				playerName = labelGather.getText( "RelationShip:RelationPanel", "masterTag" )%playerName
		self.setTextes( playerName, "--", "--", "--"  )

	def updateFriendly( self, friendlyValue ):
		pass

	def updateLevel( self, level ):
		self.pyCols[1].text = str( level )

	def updateTongName( self, tongName ):
		if tongName == "":
			self.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "without" )
		else:
			self.pyCols[3].text = tongName

	def updateFamilyName( self, familyName ):
		if familyName == "":
			self.pyCols[3].text = labelGather.getText( "RelationShip:RelationPanel", "without" )
		else:
			self.pyCols[3].text = familyName

	def _getOnline( self ):
		return self.__online

	def _setOnline( self, online ):
		self.__online  = online
		if online:
			self.commonForeColor = 255,255,255,255
		else:
			self.commonForeColor = 127,127,127,255

	def _getMetier( self ):
		return self.__metier

	def _setMetier( self, metier ):
		self.__metier = metier & csdefine.RCMASK_CLASS
		self.pyCols[2].text = csconst.g_chs_class[self.__metier]

	def _getArea( self ):
		return self.pyCols[3].text
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCols( self ) :
		return self.pyCols_[:]

	# ---------------------------------------
	def _getForeColor( self ) :
		"""
		get color of the label
		"""
		return self.pyCols_[0].foreColor

	def _setForeColor( self, color ) :
		"""
		set forecolor
		"""
		for pyCol in self.pyCols_ :
			pyCol.foreColor = color

	# -------------------------------------------------
	def _getCommonForeColor( self ) :
		return self.foreColors_[UIState.COMMON]

	def _setCommonForeColor( self, color ) :
		self.foreColors_[UIState.COMMON] = color
		if self.viewState == UIState.COMMON :
			self.foreColor = color
			for pyCol in self.pyCols_ :
				pyCol.foreColors_[UIState.COMMON] = color
				pyCol.foreColor = color
		else :
			for pyCol in self.pyCols_ :
				pyCol.foreColors_[UIState.COMMON] = color

	# ---------------------------------------
	def _getHighlightForeColor( self ) :
		return self.foreColors_[UIState.HIGHLIGHT]

	def _setHighlightForeColor( self, color ) :
		self.foreColors_[UIState.HIGHLIGHT] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.HIGHLIGHT] = color

	# ---------------------------------------
	def _getSelectedForeColor( self ) :
		return self.foreColors_[UIState.SELECTED]

	def _setSelectedForeColor( self, color ) :
		self.foreColors_[UIState.SELECTED] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.SELECTED] = color

	# ---------------------------------------
	def _getDisableForeColor( self ) :
		return self.foreColors_[UIState.DISABLE]

	def _setDisableForeColor( self, color ) :
		self.foreColors_[UIState.DISABLE] = color
		for pyCol in self.pyCols_ :
			pyCol.foreColors_[UIState.DISABLE] = color

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	online = property( _getOnline, _setOnline )
	pyCols = property( _getCols )
	foreColor = property( _getForeColor, _setForeColor )

	commonForeColor = property( _getCommonForeColor, _setCommonForeColor )
	highlightForeColor = property( _getHighlightForeColor, _setHighlightForeColor )
	selectedForeColor = property( _getSelectedForeColor, _setSelectedForeColor )
	disableForeColor = property( _getDisableForeColor, _setDisableForeColor )


import csstring
class CelItem( Label ):
	def __init__( self, item, pyBinder ) :
		Label.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = True
		del self.backColors_			# �����õ�����ɫ
		del self.mappings_				# �����õ� mapping
		self.trueText = ""
		self.trueWidth = 0.0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		"""
		������ʱ������
		ע�⣺���ﲻҪ�ص� Lavel �� onMouseEnter_
		"""
		self.pyBinder.onMouseEnter_()
		if self.trueWidth > self.width :
			toolbox.infoTip.showToolTips( self, self.trueText )
		return True

	def onMouseLeave_( self ) :
		"""
		����뿪ʱ������
		ע�⣺���ﲻҪ�ص� Lavel �� onMouseLeave_
		"""
		self.pyBinder.onMouseLeave_()
		toolbox.infoTip.hide( self )
		return True

	# -------------------------------------------------
	def onStateChanged_( self, state ) :
		"""
		״̬�ı�ʱ������
		"""
		self.foreColor = self.foreColors_[state]

	def setText( self, text ):
		self.text = text
		self.trueText = text
		self.trueWidth = self.pyText_.width
		if self.trueWidth > self.width :
#			wideText = csstring.toWideString( text )
			formatText = self.cut_str( text, 4 )
			self.text= formatText

	def cut_str( self, str, length = 13 ):
		"""
		��ȡ�ַ�����ʹ���ַ������ȵ���length�������ַ��������ʡ�Ժ�
		"""
		is_encode = False
		try:
			str_encode = str.encode('gb18030') #Ϊ�����ĺ�Ӣ�ĵĳ���һ�£����İ�����2����
			is_encode = True
		except:
			pass
		if is_encode:
			l = length*2
			if l < len(str_encode):
				l = l - 3
				str_encode = str_encode[:l]
				try:
					str = str_encode.decode('gb18030') + '...'
				except:
					str_encode = str_encode[:-1]
					try:
						str = str_encode.decode('gb18030') + '...'
					except:
						is_encode = False
		if not is_encode:
			if length < len(str):
				length = length - 2
				return str[:length] + '...'
		return str

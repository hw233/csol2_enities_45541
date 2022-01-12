# -*- coding: gb18030 -*-
#
# $Id: RelationPanel.py $

"""
implement RelationPanel class
"""
from guis import *
import BigWorld
from LabelGather import labelGather
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabCtrl
from guis.controls.CheckBox import CheckBoxEx
from SubPanel import SubPanel
from AddRelationBox import AddRelationBox
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine

MASTER_PRENTICE = csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE|csdefine.ROLE_RELATION_PRENTICE_EVER|csdefine.ROLE_RELATION_MASTER_EVER

RELATION_MAPS = { 0:( csdefine.ROLE_RELATION_FRIEND, labelGather.getText( "RelationShip:RelationPanel", "btn_0" ) ),
			1:( MASTER_PRENTICE,	labelGather.getText( "RelationShip:RelationPanel", "btn_1" ) ),
			2:( csdefine.ROLE_RELATION_FOE, 		labelGather.getText( "RelationShip:RelationPanel", "btn_2" ) ),
			3:( csdefine.ROLE_RELATION_BLACKLIST, labelGather.getText( "RelationShip:RelationPanel", "btn_3" ) ),
			4:( csdefine.ROLE_RELATION_ALLY, labelGather.getText( "RelationShip:RelationPanel", "btn_4" ) ),
		}
from AbstractTemplates import MultiLngFuncDecorator

class deco_InitCheckEx( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyCheckEx ) :
		"""
		����������µ���������������ĳߴ�
		"""
		pyCheckEx.pyText_.charSpace = -1
		pyCheckEx.pyText_.fontSize = 12

class RelationPanel( TabPanel ):

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__triggers = {}
		self.__registerTriggers()
		self.showOffLine = True
		self.__initialize( panel )

	def __initialize( self, panel ):
		self.__pyFilterCK = CheckBoxEx( panel.filterCK ) # ȫ��������ѡ��
#		self.__pyFilterCK.checked = False
		self.__pyFilterCK.onCheckChanged.bind( self.__doOnClickFilter )
		self.__pyFilterCK.text = labelGather.getText( "RelationShip:main", "ckOffline" )
		
		self.__pyBtnAdd = Button( panel.btnAdd )				#��ӹ�ϵ
		self.__pyBtnAdd.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnAdd.onLClick.bind( self.__addRelation )
		labelGather.setPyBgLabel( self.__pyBtnAdd, "RelationShip:RelationPanel", "btnAdd" )

		self.__pyBtnDel = Button( panel.btnDel)				#ɾ����ϵ
		self.__pyBtnDel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDel.onLClick.bind( self.__delRelation )
		labelGather.setPyBgLabel( self.__pyBtnDel, "RelationShip:RelationPanel", "btnDel" )

		self.__pyTabCtrl = TabCtrl( panel.subTc )

		index = 0
		while True :											#��ʼ��TabCtrl
			tabName = "btn_" + str( index )
			tab = getattr( panel.subTc, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			subPanel = getattr( panel.subTc, panelName, None )
			if panel is None : break
			pyBtn = TabButton( tab )
			pyBtn.setStatesMapping( UIState.MODE_R3C1 )
			labelGather.setPyBgLabel( pyBtn, "RelationShip:RelationPanel", tabName )
			groupID = RELATION_MAPS[index][0]
			pyPanel = SubPanel( subPanel, groupID )
			pyPage = TabPage( pyBtn, pyPanel )
			pyPage.selected = False
			pyPage.groupType = index
			self.__pyTabCtrl.addPage( pyPage )
			index += 1

		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onSubPageSelected )
		
		self.__initCheckEx( self.__pyFilterCK )
		
	@deco_InitCheckEx
	def __initCheckEx( self, pyCheckEx ):
		pyCheckEx.pyText_.charSpace = 0
		pyCheckEx.pyText_.fontSize = 12

	# --------------------------------------------------------------------
	# private
	# --------------------------------------------------------------------
	def __registerTriggers( self ):
		#��ϵ
		self.__triggers["EVT_ON_ROLE_ADD_RELATION"] = self.__onAddRelation
		self.__triggers["EVT_ON_ROLE_REMOVE_RELATION"] = self.__onRemoveRelation
		self.__triggers["EVT_ON_ROLE_UPDATE_RELATION"] = self.__onUpdateInfo
		#��ϵ�������Ѻöȡ��ȼ���Ϣ
		self.__triggers["EVT_ON_RELATION_AREA_UDATE"] = self.__onUpdateArea
		self.__triggers["EVT_ON_RELATION_FRIENDLY_UDATE"] = self.__onUpdateFriendly
		self.__triggers["EVT_ON_RELATION_LEVEL_UDATE"] = self.__onUpdateLevel
		self.__triggers["EVT_ON_RELATION_OFFLINE"] = self.__onOffLine
		self.__triggers["EVT_ON_COUPLE_DIVORCE_SUCCESS"] = self.__onDivorceSucc
		self.__triggers["EVT_ON_RELATION_TONGNAME_CHANGED"] = self.__onTongNameChanged
		self.__triggers["EVT_ON_RELATION_TONG_RECEIVE_TONG_GRADE"] = self.__onUpdateTongGrade
		
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# -------------------------------------------------------------------
	def __onAddRelation( self, relationUID, relationStatus ):
		"""
		��ӹ�ϵ
		"""
		for key, tuple in RELATION_MAPS.iteritems():
			pySubPanel = self.__pyTabCtrl.pyPages[key].pyPanel
			if tuple[0]&relationStatus:
				pySubPanel.addRelation( relationUID )
		if relationStatus ==  csdefine.ROLE_RELATION_BLACKLIST:
			self.__updateSelPanel()

	def __updateSelPanel( self ):
		pySelPage = self.__pyTabCtrl.pySelPage
		if pySelPage is None:return
		pySubPanel = pySelPage.pyPanel
		pySubPanel.updateAllItems()
				
	def __onRemoveRelation( self, relationUID, relationStatus ):
		for key, tuple in RELATION_MAPS.iteritems():
			if tuple[0]&relationStatus:
				pySubPanel = self.__pyTabCtrl.pyPages[key].pyPanel
				pySubPanel.delRelation( relationUID )

	def __onRemoveLover( self, relationUID ):
		"""
		�Ƴ�����
		"""
		pySubPanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pySubPanel.delRelation( relationUID )

	def __onUpdateInfo( self, relationUID, relationStatus ):
		"""
		���¹�ϵ��Ϣ
		"""
		for key, tuple in RELATION_MAPS.iteritems():
			if tuple[0]&relationStatus:
				pySubPanel = self.__pyTabCtrl.pyPages[key].pyPanel
				pySubPanel.addRelation( relationUID )
				self.__updateSelPanel()

	def __onMarriedSucc( self ):
		"""
		���ɹ�
		"""
		dbid = BigWorld.player().couple_lover.relationUID
		pySweetiePanel = self.__pyTabCtrl.pyPages[1].pyPanel
		pySweetiePanel.addRelation( relationUID )

	def __onDivorceSucc( self ):
		"""
		���ɹ�
		"""
		relationUID = BigWorld.player().couple_lover.relationUID
		self.__onRemoveRelation( relationUID, csdefine.ROLE_RELATION_COUPLE )

	def __onUpdateArea( self, relationUID, spaceType, position, lineNumber ):
		"""
		����������Ϣ
		"""
		relation = BigWorld.player().relationDatas.get( relationUID, None )
		if relation is None:return
		for index, tuple in RELATION_MAPS.iteritems():
			if not relation.relationStatus&tuple[0]:continue
			pySubPanel = self.__pyTabCtrl.pyPages[index].pyPanel
			pySubPanel.updateArea( relationUID, spaceType, position, lineNumber )

	def __onUpdateFriendly( self, relationUID, friendlyValue ):
		"""
		�����Ѻö�
		"""
		relation = BigWorld.player().relationDatas.get( relationUID, None )
		if relation is None:return
		for index, tuple in RELATION_MAPS.iteritems():
			if not relation.relationStatus&tuple[0]:continue
			pySubPanel = self.__pyTabCtrl.pyPages[index].pyPanel
			pySubPanel.updateFriendly( relationUID, friendlyValue )

	def __onUpdateLevel( self, relationUID, level ):
		"""
		���µȼ���Ϣ
		"""
		relation = BigWorld.player().relationDatas.get( relationUID, None )
		if relation is None:return
		for index, tuple in RELATION_MAPS.iteritems():
			if not relation.relationStatus&tuple[0]:continue
			pySubPanel = self.__pyTabCtrl.pyPages[index].pyPanel
			pySubPanel.updateLevel( relationUID, level )
			
	def __onUpdateTongGrade( self, relationUID, tongGrade ) :
		"""
		���°��ְ��
		"""
		relation = BigWorld.player().relationDatas.get( relationUID, None )
		if relation is None:return
		for index, tuple in RELATION_MAPS.iteritems():
			if not relation.relationStatus&tuple[0]:continue
			pySubPanel = self.__pyTabCtrl.pyPages[index].pyPanel
			pySubPanel.updateTongGrade( relationUID, tongGrade )

	def __onOffLine( self, relationUID, offLine ):
		relation = BigWorld.player().relationDatas.get( relationUID, None )
		if relation is None:return
		for index, tuple in RELATION_MAPS.iteritems():
			if not relation.relationStatus&tuple[0]:continue
			pySubPanel = self.__pyTabCtrl.pyPages[index].pyPanel
			pySubPanel.updateOffLine( relationUID )

	def __onTongNameChanged( self, relationUID, tongName ):
		"""
		��ϵ���ı�
		"""
		pySubPanel = self.__pyTabCtrl.pySelPage.pyPanel
		pySubPanel.onTongNameChange( relationUID, tongName )

	def __doOnClickFilter( self, checked ):
		self.showOffLine = checked
		pyPage = self.__pyTabCtrl.pySelPage
		if pyPage is None:return
		relationPanel = pyPage.pyPanel
		if relationPanel.groupID == csdefine.ROLE_RELATION_BLACKLIST:
			return
		if not BigWorld.player().inWorld:return
		relationPanel.isShowOffLine( checked )

	def __addRelation( self ):
		"""
		��ӹ�ϵ
		"""
		player = BigWorld.player()
		targetEntity = player.targetEntity
		pySelPage = self.__pyTabCtrl.pySelPage
		if pySelPage is None:#���û��ѡȡ��ϵ�ڵ㣬��Ĭ��Ϊ��Ӻ���
			if targetEntity is not None and targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and targetEntity != player:
				def query( rs_id ):
					if rs_id == RS_OK:
						player.addFriend( targetEntity.getName() )
				# "�Ƿ�ȷ�������%s��ӽ���������?"
				showMessage( mbmsgs[0x0661] % targetEntity.getName(), "",MB_OK_CANCEL, query, pyOwner = self )
				return True
			else:
				def query( name ): # ��Ӻ���
					player.addFriend( name )
				AddRelationBox.instance().title= RELATION_MAPS[0][1]
				AddRelationBox.instance().show( query, self )
		
		else: #���ѡ���˽ڵ�,û��ѡ��Ŀ�꣬����Ŀ��ΪNPC��monster��role
			groupID = pySelPage.pyPanel.groupID
			
			if targetEntity is not None and targetEntity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) and targetEntity != player:
				if groupID == csdefine.ROLE_RELATION_FRIEND:
					def query( rs_id ):
						if rs_id == RS_OK:
							player.addFriend( targetEntity.getName() )
					# "�Ƿ�ȷ�������%s��ӽ���������?"
					showMessage( mbmsgs[0x0661] % targetEntity.getName(), "",MB_OK_CANCEL, query, pyOwner = self )
					return True
				elif groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE:
					def query( rs_id ):
						if rs_id == RS_OK:
							player.addSweetie( targetEntity.getName() )
					# "�Ƿ�ȷ�������%s��Ϊ����?"
					showMessage( mbmsgs[0x0662] % targetEntity.getName(), "",MB_OK_CANCEL, query, pyOwner = self )
					return True
				elif groupID == csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE:
					pass
				elif groupID == csdefine.ROLE_RELATION_FOE:
					def query( rs_id ):
						if rs_id == RS_OK:
							player.base.addFoe( targetEntity.getName() )
					# "�Ƿ�ȷ�������%s��ӽ������б�?"
					showMessage( mbmsgs[0x0663] % targetEntity.getName(), "",MB_OK_CANCEL, query, pyOwner = self )
					return True
				else:
					def query( rs_id ):
						if rs_id == RS_OK:
							player.addBlacklist( targetEntity.getName() )
					# "�Ƿ�ȷ�������%s��ӽ�������?"
					showMessage( mbmsgs[0x0664] % targetEntity.getName(), "",MB_OK_CANCEL, query, pyOwner = self )
					return True

			else:
				if groupID == csdefine.ROLE_RELATION_FRIEND:
					def query( name ): # ��Ӻ���
						player.addFriend( name )
				elif groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE:
					def query( name ): # ������˻��߷���
						player.addSweetie( name )
				elif groupID == csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE: #���ʦͽ
					pass
				elif groupID == csdefine.ROLE_RELATION_FOE: #��ӳ���
					def query( name ):
						player.base.addFoe( name )
				else: #��Ӻ�����
					def query( name ):
						player.addBlacklist( name )
				for tuple in RELATION_MAPS.itervalues():
					if tuple[0] == groupID:
						AddRelationBox.instance().title = tuple[1]
						AddRelationBox.instance().show( query, self )
			# target Ϊ�������,��ֱ����target��ȡ����
			

	def __delRelation( self ):
		"""
		ɾ����ϵ
		"""
		player = BigWorld.player()
		pyPage = self.__pyTabCtrl.pySelPage
		if pyPage is None:return False
		groupID = pyPage.pyPanel.groupID
		pyItem= pyPage.pyPanel.getSelItem()
		if pyItem is None:return
		relationUID = 0
		relation = pyItem.relation
		relationUID = relation.relationUID
		name = pyItem.relation.playerName
		if groupID == csdefine.ROLE_RELATION_FRIEND:
			player.removeFriend( relationUID )
		elif groupID == csdefine.ROLE_RELATION_SWEETIE|csdefine.ROLE_RELATION_COUPLE:
			def query( rs_id ):
				if rs_id == RS_OK:
					player.base.removeSweetie( relationUID ) # ������˹�ϵ
			# "�Ƿ�ȷ��ɾ������:%s?"
			showAutoHideMessage( 30.0, mbmsgs[0x0665] % name, "", MB_OK_CANCEL, query )
		elif groupID == csdefine.ROLE_RELATION_MASTER|csdefine.ROLE_RELATION_PRENTICE: #ֻ����NPC�����ʦͽ��ϵ
			pass
		elif groupID == csdefine.ROLE_RELATION_FOE:
			def query( rs_id ):
				if rs_id == RS_OK:
					player.base.removeFoe( relationUID ) # ������˹�ϵ
			# "�Ƿ�ȷ��ɾ������:%s?"
			showAutoHideMessage( 30.0, mbmsgs[0x0666] %name, "", MB_OK_CANCEL, query )
		elif groupID == csdefine.ROLE_RELATION_BLACKLIST:
			player.removeBlackList( relationUID )

	def __onSubPageSelected( self, pyCtrl ):
		"""
		ʦͽ��ϵֻ����NPC�����
		"""
		disEnable = [MASTER_PRENTICE, csdefine.ROLE_RELATION_ALLY]
		groupID = self.__pyTabCtrl.pySelPage.pyPanel.groupID
		self.__pyBtnAdd.visible = not groupID in disEnable
		self.__pyBtnDel.visible = not groupID in disEnable
		self.__pyFilterCK.visible = not groupID == csdefine.ROLE_RELATION_BLACKLIST
		relationPanel = self.__pyTabCtrl.pySelPage.pyPanel
		optionIndex = relationPanel.optionIndex
		if optionIndex < 0:
			relationPanel.optionIndex = 0
		elif optionIndex ==1 :
			relationPanel.queryAreaInfo( relationPanel.groupID )
		if relationPanel.groupID == csdefine.ROLE_RELATION_BLACKLIST:
			relationPanel.isShowOffLine( True )
		else:
			relationPanel.isShowOffLine( self.showOffLine )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def initUIs( self ):
		self.__pyFilterCK.checked = self.showOffLine
		pySelPage = self.__pyTabCtrl.pyPages[0]
		self.__pyTabCtrl.pySelPage = pySelPage
		pySelPage.pyPanel.optionIndex = 0

	def reset( self ):
		self.showOffLine = True
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPanel = pyPage.pyPanel
#			pyPanel.clearItems()
			pyPanel.reset()
	
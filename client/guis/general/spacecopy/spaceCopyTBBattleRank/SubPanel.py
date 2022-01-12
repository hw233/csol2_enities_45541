# -*- coding: gb18030 -*-
#
from guis import *
from LabelGather import labelGather
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.TabCtrl import TabPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ODListPanel import ODListPanel
from ChatFacade import chatFacade
from guis.general.chatwindow.playmatechat.PLMChatMgr import plmChatMgr
from guis.controls.ContextMenu import DefMenuItem
from guis.controls.ContextMenu import ContextMenu
from guis.tooluis.CSRichText import CSRichText
from RewardDetails import RewardDetails
import csdefine
from EspialTargetRemotely import espialRemotely

class SubPanel( TabPanel ):

	def __init__( self, panel, groupID ):
		TabPanel.__init__( self, panel )
		self.__groupID = groupID
		self.__menuItems = {}	

		self.__initPanel( panel )
		self.__createMenuItems()

	def __initPanel( self, panel ):
		self.__pyBtnTongName = HButtonEx( panel.subPanel.btn_0 )
		self.__pyBtnTongName.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnTongName, "SpaceCopyTBBattleRank:main", "btn_tongName" )
		
		self.__pyBtnRank = HButtonEx( panel.subPanel.btn_1 )
		self.__pyBtnRank.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnRank, "SpaceCopyTBBattleRank:main", "btn_rank" )
		
		self.__pyBtnPlayerName = HButtonEx( panel.subPanel.btn_2 )
		self.__pyBtnPlayerName.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnPlayerName, "SpaceCopyTBBattleRank:main", "btn_playerName" )
		
		self.__pyBtnTotal = HButtonEx( panel.subPanel.btn_3 )
		self.__pyBtnTotal.setExStatesMapping( UIState.MODE_R3C1 )
		
		
		self.__pyBtnReward = HButtonEx( panel.subPanel.btn_4 )
		self.__pyBtnReward.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnReward, "SpaceCopyTBBattleRank:main", "btn_rewards" )
		
		self.__pyListPanel = ODListPanel( panel.subPanel.clipPanel, panel.subPanel.sbar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23
		self.__pyListPanel.autoSelect = False
		
		self.__pyCMenu = ContextMenu()
		self.__pyCMenu.addBinder( self )
		self.__pyCMenu.onBeforePopup.bind( self.__onMenuPopUp )
		self.__pyCMenu.onItemClick.bind( self.__onMenuItemClick )
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		pyRankItem = RankItem()
		pyViewItem.addPyChild( pyRankItem )
		pyViewItem.pyItem = pyRankItem
		pyRankItem.left = 0
		pyRankItem.top = 0
	
	def __drawListItem( self, pyViewItem ):
		pyRankItem = pyViewItem.pyItem
		pyRankItem.resetText( pyViewItem.listItem )	
		if pyViewItem.selected :							# ѡ��״̬
			pyRankItem.setHighLight()
			pyRankItem.resetColor( ( 60, 255, 0, 255 ) )
		elif pyViewItem.highlight :							# ����״̬����������ϣ�
			pyRankItem.setHighLight()
		else :
			pyRankItem.setCommonLight()
			pyRankItem.resetColor( ( 255, 255, 255, 255 ) )
	
	def __createMenuItems( self ) :
		"""
		�������п����õ��Ĳ˵���
		"""
		menuList = []
		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miWhisper" ) )
		pyItem0.handler = self.__whisper
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )
		
		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miEspial" ) )
		pyItem0.handler = self.__espialTarget
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		menuList.extend( [pyItem0, pySplitter] )
		self.__menuItems["persistence"] = menuList						# ������һ�飬����˵�ÿ�ε���������ʾ

		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miAddToBuddy" ) )	# ��Ӻ���
		pyItem0.handler = self.__addToBuddy
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["addToBuddy"] = [pySplitter, pyItem0]
		
		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miFriendChat" ) )   # ��������
		pyItem0.handler = self.__friendChat
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["friendChat"] = [pySplitter, pyItem0]
		
		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miAddToBlackList" ) ) #��������
		pyItem0.handler = self.__addToBlackList
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["addToBlackList"] = [pySplitter, pyItem0]				

		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miJoinTeam" ) )
		pyItem0.handler = self.__inviteJoinTeam
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["inviteJoinTeam"] = [pySplitter, pyItem0]		# ���������飬�������

		pyItem0 = DefMenuItem( labelGather.getText( "SpaceCopyTBBattleRank:main", "miJoinTong" ) )
		pyItem0.handler = self.__InviteJoinTong
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		self.__menuItems["joinTong"] = [pySplitter, pyItem0]			# �����飬���������
					
	def __onMenuPopUp( self ) :
		"""
		�˵�����ǰ������
		"""
		player = BigWorld.player()
		pySelItem = self.__pyListPanel.selItem			# ��ȡ�����е��Ǹ��ڵ�
		if pySelItem is None : return -1						# ���� -1 ��ʾ�ܾ���ʾ�˵�
		targetName = pySelItem["playerName"]
		targetTongName = pySelItem["tongName"]
		if targetName == player.playerName:return -1
		# ���ݵ�ǰ�����Ŀ���״̬��������Ҫ��ʾ��Щ�˵���
		self.__pyCMenu.clear()
		pyItems = self.__menuItems["persistence"]					# ÿ�ζ�����ʾ�Ĳ˵���
		self.__pyCMenu.pyItems.adds( pyItems )
		grade = player.tong_grade
		consGrade = player.tong_checkDutyRights( grade, csdefine.TONG_RIGHT_MEMBER_MANAGE )
		if targetName in player.friends:							# Ŀ�����ҵĺ����б�
			pyItems0 = self.__menuItems["friendChat"]
			self.__pyCMenu.pyItems.adds( pyItems0 )
			pyItems1 = self.__menuItems["addToBlackList"]
			self.__pyCMenu.pyItems.adds( pyItems1 )
		else:
			pyItems = self.__menuItems["addToBuddy"]
			self.__pyCMenu.pyItems.adds( pyItems )
		if not player.isJoinTeam() or not player.isTeamMember( target.id ) :
			pyItems = self.__menuItems["inviteJoinTeam"]			# �������
			self.__pyCMenu.pyItems.adds( pyItems )
			
		if player.isJoinTong() and consGrade and targetTongName == "":
			pyItems = self.__menuItems["joinTong"]					# ���������
			self.__pyCMenu.pyItems.adds( pyItems )
		return True	
	
	def __onMenuItemClick( self, pyItem ) :
		"""
		����˵�ѡ��ʱ������
		"""
		pyItem.handler( pyItem )
		
	# ----------------------------------------------------------------
	# menuitem handlers
	# ----------------------------------------------------------------
	def __whisper( self, pyItem ) :
		"""
		��Ŀ�����˽��
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		chatFacade.whisperWithChatWindow( targetName )
		
	def __espialTarget( self, pyItem ):
		"""
		�鿴�Է�װ��ģ��
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		espialRemotely.queryRoleEquip( targetName )
		
	def __addToBuddy( self, pyItem ) :
		"""
		��Ϊ����
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		BigWorld.player().addFriend( targetName )
		
	def __friendChat( self, pyItem ):
		"""
		��������
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		plmChatMgr.onOriginateChat( targetName )

	def __addToBlackList( self, pyItem ) :
		"""
		�ӵ�������
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		BigWorld.player().addBlacklist( targetName )
		
	def __inviteJoinTeam( self, pyItem ) :
		"""
		�������
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		BigWorld.player().inviteJoinTeam( targetName )
		
	def __InviteJoinTong( self, pyItem ):
		"""
		���������
		"""
		if self.__pyListPanel.selItem is None: return
		targetName = self.__pyListPanel.selItem["playerName"]
		BigWorld.player.tong_requestJoinByPlayerName( targetName )
		
	#------------------------------------------------------------------------
	#public
	#------------------------------------------------------------------------
	def onShow( self ):
		if self.__groupID == 0:
			labelGather.setPyBgLabel( self.__pyBtnTotal, "SpaceCopyTBBattleRank:main", "btn_damage" )
		elif self.__groupID == 1:
			labelGather.setPyBgLabel( self.__pyBtnTotal, "SpaceCopyTBBattleRank:main", "btn_cure" )
		elif self.__groupID == 2:
			labelGather.setPyBgLabel( self.__pyBtnTotal, "SpaceCopyTBBattleRank:main", "btn_die" )
	
	def addRankInfo( self,battleResultList ):
		#����
		damageList  = []	
		cureList 	= []
		dieList		= []
		firstDamagerDict = {}
		for rankInfo in battleResultList:
			if rankInfo["isFirstDamager"] == True:	#�״����
				firstDamagerDict["tongName"] 	 = rankInfo["tongName"]
				firstDamagerDict["order"]		 = labelGather.getText("SpaceCopyTBBattleRank:main", "firstDamager" )
				firstDamagerDict["playerName"] 	 = rankInfo["playerName"]
				firstDamagerDict["total"]		 = rankInfo["totalDamage"]
				firstDamagerDict["reward"]		 = rankInfo["firDamageReward"]
				
			if rankInfo["damageOrder"] > 0:		
				damageDict = {}
				damageDict["tongName"] 		= rankInfo["tongName"]
				damageDict["order"] 		= str( rankInfo["damageOrder"] )
				damageDict["playerName"]	= rankInfo["playerName"]
				damageDict["total"]			= rankInfo["totalDamage"]
				damageDict["reward"]		= rankInfo["damageReward"]
				damageList.append( damageDict.copy() )
			
			if rankInfo["cureOrder"] > 0:
				cureDict = {}
				cureDict["tongName"] 		= rankInfo["tongName"]
				cureDict["order"] 			= str( rankInfo["cureOrder"] )
				cureDict["playerName"]		= rankInfo["playerName"]
				cureDict["total"]			= rankInfo["totalCureHP"]
				cureDict["reward"]			= rankInfo["cureReward"]
				cureList.append( cureDict.copy() )
			
			if rankInfo["dieOrder"] > 0:
				dieDict = {}
				dieDict["tongName"] 		= rankInfo["tongName"]
				dieDict["order"] 			= str( rankInfo["dieOrder"] )
				dieDict["playerName"]		= rankInfo["playerName"]
				dieDict["total"]			= rankInfo["dieCount"]
				dieDict["reward"]			= rankInfo["dieReward"]
				dieList.append( dieDict.copy() )
			
		if self.__groupID == 0:	#�˺�����
			if firstDamagerDict:
				self.__pyListPanel.addItem( firstDamagerDict )
			self.__pyListPanel.addItems( damageList )
			self.__pyListPanel.sort( key = lambda item: item["order"], reverse = False )
		elif self.__groupID == 1:
			self.__pyListPanel.addItems( cureList )
			self.__pyListPanel.sort( key = lambda item: item["order"], reverse = False )
		elif self.__groupID == 2:
			self.__pyListPanel.addItems( dieList )
			self.__pyListPanel.sort( key = lambda item: item["order"], reverse = False )
	
	def clearItems( self ):
		self.__pyListPanel.clearItems()


class RankItem( GUIBaseObject ) :

	__rank_item = None

	def __init__( self, pyBinder = None ) :
		if RankItem.__rank_item is None :
			RankItem.__rank_item = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/xmItem.gui" )
		gui = util.copyGuiTree( RankItem.__rank_item )
		uiFixer.firstLoadFix( gui )
		GUIBaseObject.__init__( self, gui )
		self.__rewards = []
		self.__elements =gui.elements
		self.focus = False
		self.crossFocus = False
		self.__initialize( gui, pyBinder )

	def __initialize( self, gui, pyBinder ) :
		self.__pyRtTongName = CSRichText( gui.rtTongName )
		self.__pyRtTongName.text = ""
		
		self.__pyRtRank = CSRichText( gui.rtRank )
		self.__pyRtRank.text = ""
		self.__pyRtRank.align = "C"
		
		self.__pyRtPlayerName = CSRichText( gui.rtPlayerName )
		self.__pyRtPlayerName.text = ""
		
		self.__pyRtTotal = CSRichText( gui.rtTotal )
		self.__pyRtTotal.text = ""
		self.__pyRtTotal.align = "C"
		
		self.__pyBtnReward = Button( gui.reward )
#		self.__pyBtnReward.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnReward.onLClick.bind( self.__onShowRewardDetails )
		self.__pyBtnReward.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnReward.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnReward.onLMouseDown.bind( self.__onMouseDown )


	def __onMouseEnter( self, pyBtn ):
		if pyBtn is None:return
		dsp = labelGather.getText("SpaceCopyTBBattleRank:main", "rewardTips" )
		toolbox.infoTip.showItemTips( self, dsp )
		
	def __onMouseLeave( self ):
		toolbox.infoTip.hide()
		
	def __onMouseDown( self ):
		toolbox.infoTip.hide()
		
	def __onShowRewardDetails( self ):
		RewardDetails.instance().show( self.__rewards )

	def resetText( self, info ) :
		"""
		�����б����ı�
		"""
		self.__pyRtTongName.text 		= str( info["tongName"] )
		self.__pyRtRank.text			= str( info["order"] )
		self.__pyRtPlayerName.text		= str( info["playerName"] )
		self.__pyRtTotal.text			= str( info["total"] )
		self.__rewards 					= info["reward"]

	def resetColor( self, color ) :
		"""
		�����б���������ɫ
		"""
		self.__pyRtTongName.foreColor = color
		self.__pyRtRank.foreColor = color
		self.__pyRtPlayerName.foreColor = color
		self.__pyRtTotal.foreColor = color

	def setHighLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=1

	def setCommonLight(self):
		for elem in self.__elements:
			self.__elements[elem].visible=0

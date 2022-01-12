# -*- coding: gb18030 -*-
#
# $Id: QuestTalkWindow.py,v 1.53 2008-08-25 09:26:25 huangyongwei Exp $

"""
implement quest talking window��
"""

from guis import *
from LabelGather import labelGather
from CommontalkWindow import CommontalkWindow as CTWindow
from ItemsFactory import ObjectItem
from ItemsFactory import SkillItem
from SubmitItem import SubmitItem
from SubmitPet import SubmitPet
import cscustom
import csdefine
import csstatus
import csconst
import Const
import GUIFacade
from guis.common.RootGUI import RootGUI
from guis.common.Window import Window
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from UnchainPrentice import UnchainPrentice
from Rewards import RW_TYPE_ITEM
from Rewards import RW_TYPE_MONEY
from Rewards import RW_TYPE_OTHER
from Rewards import RW_TYPE_AIM
from Rewards import RW_TYPE_TIMER
from Rewards import RW_TYPE_SUBMIT
from Rewards import RW_TYPE_NONE
from Rewards import RW_TYPE_SKILL
from Rewards import CRewardPanel
from Rewards import CRewardItem
import Timer
import event.EventCenter as ECenter
from FactionMgr import factionMgr
from TitleMgr import TitleMgr
titleMgr = TitleMgr.instance()
from CrondScheme import Scheme
from Time import Time
from guis.OpIndicatorObj import OpIndicatorObj
from cscustom import Rect

QUESTTALKINGWINDOW 	= 1
QUESTINCOMPLETE 	= 2
QUESTPRECOMPLETE 	= 3
QUESTCOMPLETE 		= 4
COMMONTALKING		= 5
first_questIDs = [20101356, 20101357, 20101358, 20101359] #����ɫ��һ�������б�
skill_npcs = {	csdefine.CLASS_FIGHTER	:['10122001','10122008'],
				csdefine.CLASS_SWORDMAN	:['10122002','10122007'],
				csdefine.CLASS_ARCHER	:['10122003','10122005'],
				csdefine.CLASS_MAGE		:['10122004','10122006']
			}
quest_marks = [0, 1, 2, 3, 4, 25]	#����Ի�ѡ���־

# --------------------------------------------------------------------
# implement quest talking window
# --------------------------------------------------------------------
def isMainQuest( questID ):
	return questID / 100000 == 201
	
class QuestTalkWindow( CTWindow, OpIndicatorObj ) :

	def __init__( self ) :
		CTWindow.__init__( self )
		OpIndicatorObj.__init__( self )
		self.__questUpdateTimeID = 0
		self.pyBtnAccept_.onLClick.bind( self.__onAccept )
		self.pyBtnFulfil_.onLClick.bind( self.__onComplete )
		self.pyContent_.onScrollChanged.bind( self.__onScrollChange )
		self.pyOptionPanel = None
		self.pySubmitItem = None
		self.subPets = []
		self.currentWindow = 0
		self.nextQuest = False
		self.oldTargetName = ""
		self.__trapID = None

		self.__unPrentice = UnchainPrentice()
		
		self.__mainQuestAutoTimerID = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerTriggers_( self ) :
		self.triggers_["EVT_QUEST_SHOW_DETAIL_TEXT"] = self.__onShowQuestTalking			# show window for quest trigger
		self.triggers_["EVT_QUEST_SHOW_INCOMPLETE_TEXT"] = self.__showQuestIncomplete 		# show window for showing content of quest unfinishing
		self.triggers_["EVT_QUEST_SHOW_PRECOMPLETE_TEXT"] = self.__showQuestPrecomplete		# show window for showing content of quest complete
		self.triggers_["EVT_QUEST_SHOW_COMPLETE_TEXT"] = self.__showQuestComplete			# show window for showing prelude content of quest
		self.triggers_["EVT_CLOSE_GOSSIP_WINDOW"] = self.__closeWindow
		self.triggers_["EVT_ON_UNCHAIN_PRENTICE" ] = self.__showUnchainWindow
		self.triggers_["EVT_ON_ROLE_DEAD"] = self.hide										# ��ɫ���������ش���
		self.triggers_["EVT_ON_ROLE_END_WITHNPC_TRADE"] = self.hide							# ��NPC�����Ի�
		CTWindow.registerTriggers_( self )

	def __closeWindow( self ):
		self.currentWindow = 0

	def __addTrap( self ):
		if self.__trapID:
			self.__delTrap()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance() # + 2	# ȥ����Ī�������"+2" modify by gjx 2009-4-2
		gossiptarget = GUIFacade.getGossipTarget()
		self.__trapID = BigWorld.addPot(gossiptarget.matrix, distance, self.__onEntitiesTrapThrough )		# �򿪴��ں�Ϊ�����ӶԻ�����s


	def __delTrap( self ) :
		if self.__trapID :
			try:	# ������û�����trapID����self.__trapID = 0
				BigWorld.delPot( self.__trapID )											#ɾ����ҵĶԻ�����
			except:
				HACK_MSG( "trapID���ԡ�" )
				self.__trapID = None
			self.__trapID = None

	def __onEntitiesTrapThrough( self, enteredTrap, handle):
		if not enteredTrap:															#���NPC�뿪��ҶԻ�����
			self.__onShut()																#���ص�ǰ��NPC�Ի�����

	def __onShut( self ):
		self.currentWindow = 0
		self.hide()
		self.__delTrap()

	def __showUnchainWindow( self, npcID ):
		self.__unPrentice.showWindow( npcID )

	# -------------------------------------------------
	def __onShowQuestTalking( self ) :
		"""
		show quest acception dialog
		"""
		# set title of the window
		self.clearIndications()							# ����֮�ƣ�������ɵ���ʾ
		questTarget = GUIFacade.getQuestTarget()
		if questTarget:
			targetName = questTarget.getName()
		else:
			targetName = ""
		if self.currentWindow in [ QUESTCOMPLETE, QUESTPRECOMPLETE ] and self.oldTargetName == targetName:
			self.nextQuest = True
			self.oldTargetName = ""
			return

		title, level = GUIFacade.getQuestTitle()

		# set talking content
		self.clearContent_()
		storyText, objectiveText = GUIFacade.getQuestDetail()
		
		questID = GUIFacade.getQuestID()
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )

		self.pyContent_.appendTitle( title )
		self.pyContent_.appendTypeText( typeStr )
		self.pyContent_.appendText( storyText)

		self.__checkQuestTimer( GUIFacade.getQuestLogSelection() )
		self.show()
		self.__addRewards()
		self.pyBigPanel_.visible = True
		self.pyBtnShut_.visible = True
		self.pyBtnFulfil_.visible = False
		self.pyBtnAccept_.visible = True
		self.currentWindow = QUESTTALKINGWINDOW
		if questTarget:
			self.__addTrap()	# wsf
		
		if isMainQuest( questID ):#�����Զ�������ʱ��
			self.__mainQuestAutoTimerID = BigWorld.callback( Const.QUEST_MAIN_QUEST_AUTO_TIME, self.__onAccept )
#		toolbox.infoTip.showOperationTips( 0x0031, self.pyBtnAccept_ )

	def __checkQuestTimer( self, questID ): # ʱ����
		if not GUIFacade.hasQuestLog( questID ):
			self.__closeQuestTimer()
			return
		if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TIME ):
			if self.__questUpdateTimeID == 0:
				self.__questUpdateTimeID = Timer.addTimer( 0, 1, self.__persistChange )
		else:
			self.__closeQuestTimer()

	def __closeQuestTimer( self ):
		Timer.cancel( self.__questUpdateTimeID )
		self.__questUpdateTimeID = 0

	def __persistChange( self ):
		if not self.visible:
			self.__closeQuestTimer()
			return
		if self.currentWindow == QUESTPRECOMPLETE:		# ˢ��ʣ��ʱ��
			self.__refreshPreCompleteQuest()
		#		self.__onQuestStateChagned( GUIFacade.getQuestLogSelection() )

	# -------------------------------------------------------------
	def __showQuestIncomplete( self ):
		self.clearIndications()							# ����֮�ƣ�������ɵ���ʾ
		title, level = GUIFacade.getQuestTitle()
		self.clearContent_()
		questID = GUIFacade.getQuestID()
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		incompleteText = GUIFacade.getQuestIncompleteText()
		self.pyContent_.appendTypeText( typeStr )
		self.pyContent_.appendText( incompleteText )
		questID = GUIFacade.getQuestID()
		if str(questID).startswith( "50101"):					#ֱ�������������,�߻�Ҫ����ʾ��������
			self.__addRewards()
		self.pyBigPanel_.visible = False
		self.currentWindow = QUESTINCOMPLETE
		self.show()
		self.__addTrap()

	def __onAccept( self ):
		if self.__mainQuestAutoTimerID:
			BigWorld.cancelCallback( self.__mainQuestAutoTimerID )
			self.__mainQuestAutoTimerID = 0
			
		GUIFacade.acceptQuest()
		self.currentWindow = 0
		self.hide()
		ECenter.fireEvent( "EVT_ON_ACCEPT_TRUE" )

	# --------------------------------------------------------------
	def __showQuestPrecomplete( self ):
		"""
		"""
		self.clearIndications()							# ����֮�ƣ�������ɵ���ʾ
		title, level = GUIFacade.getQuestTitle()
		self.pyContent_.appendTitle( title )

		preCompleteText = GUIFacade.getQuestPrecompleteText()
		title, level = GUIFacade.getQuestTitle()
		self.clearContent_()
		questID = GUIFacade.getQuestID()
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		self.pyContent_.appendTypeText( typeStr )
		self.pyContent_.appendText( preCompleteText )
		self.show()
		self.pyBigPanel_.visible = True
		self.pyBtnAccept_.visible = False
		self.pyBtnFulfil_.visible = True
		self.__addRewards( )
		self.currentWindow = QUESTPRECOMPLETE
#		toolbox.infoTip.showOperationTips( 0x0033, self.pyBtnFulfil_ )
		self.__addTrap()
		#--����������ʱ�����Ƶ��������ύ�������Ҳ�ܼ�ʱˢ��
		questID = GUIFacade.getQuestID()
		taskTypes = GUIFacade.getTaskGoalType(questID)
		if csdefine.QUEST_OBJECTIVE_TIME in taskTypes:
			self.__checkQuestTimer( GUIFacade.getQuestID() )
		
		if not GUIFacade.getChooseRewardItems() and isMainQuest( questID ): #�����Զ�������ʱ��
			self.__mainQuestAutoTimerID = BigWorld.callback( Const.QUEST_MAIN_QUEST_AUTO_TIME, self.__onComplete )

	# --------------------------------------------------------------
	def __showQuestComplete( self ):
		completeText = GUIFacade.getQuestCompleteText()
		title, level = GUIFacade.getQuestTitle()
		self.clearContent_()
		questID = GUIFacade.getQuestID()
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		self.pyContent_.appendTypeText( typeStr )
		self.pyContent_.appendText( completeText )
		self.pyBigPanel_.visible = False
		self.pyBtnAccept_.visible = False
		self.pyBtnFulfil_.visible = False
		self.currentWindow = QUESTCOMPLETE
		self.oldTargetName  = GUIFacade.getQuestTarget().getName()
		self.show()
		self.__addTrap()

	def __refreshPreCompleteQuest( self ):

		questObjectText = GUIFacade.getQuestObjectiveText()
		questAimItems = GUIFacade.getObjectiveDetail( GUIFacade.getQuestID())
		aimPanel  = self.pyContent_.getAimPanel()
		i=0
		for taskType, index, title, tag, isCollapsed, isComplete, itemID, showOrder, npcID in questAimItems:
			stateText = ""
			if isComplete : stateText = labelGather.getText( "NPCTalkWnd:main", "finished" )
			else:stateText = labelGather.getText( "NPCTalkWnd:main", "unfinished" )
			if isCollapsed : stateText = labelGather.getText( "NPCTalkWnd:main", "failure" )
			if taskType == csdefine.QUEST_OBJECTIVE_TIME:
				stateText = ""
			condition = "%s: %s  %s" % ( title, tag, stateText )
			if i >= len( aimPanel.pyItems ):
				return
			aimPanel.pyItems[ i ].aimCondition = condition # ��������
			i = i+1

	def __onComplete( self ):
		if self.__mainQuestAutoTimerID:
			BigWorld.cancelCallback( self.__mainQuestAutoTimerID )
			self.__mainQuestAutoTimerID = 0
			
		self.hide()
		ECenter.fireEvent( "EVT_ON_ACCEPT_TRUE" )
		codeStr = ""
		index = -1
		if self.pyOptionPanel:
			pySelItem = self.pyOptionPanel.pySelItem
			if pySelItem is None:
				# "��ѡ��һ����������Ʒ"
				showAutoHideMessage( 3.0, 0x0c81, "", pyOwner = self )
				return
			else:
				index = pySelItem.index
		if self.pySubmitItem:
			kitbag = self.pySubmitItem.kitbag
			order = self.pySubmitItem.order
			order = kitbag * csdefine.KB_MAX_SPACE + order
			codeStr += "questKitTote" + ':' + str(kitbag) + ','
			codeStr += "questOrder" + ':' + str(order) + ','
		for i, dbid in enumerate( self.subPets ):
			codeStr += "pet%iDBID"%i + ':' + dbid + ','
		GUIFacade.completeQuest( index, codeStr )

	# --------------------------------------------------------------
	def __getRewardPanel( self, rwType ) : # ���������͵ĵõ��������
		"""
		get/create a reward items panel
		"""
		pyPanel = CRewardPanel[rwType]()
		return pyPanel

	def __getRewardItem( self, rwType ) : #�õ�������Ʒ
		"""
		get/create a reward item
		"""
		pyItem = CRewardItem[rwType]()
		return pyItem

	def __onItemMouseEnter( self, pyItem ):
		itemInfo = pyItem.itemInfo
		toolbox.itemCover.highlightItem( pyItem )
		if itemInfo is not None:
			dsp = itemInfo.getDescription()
			toolbox.infoTip.showItemTips( pyItem, dsp )

	def __onItemMouseLeave( self ):
		toolbox.infoTip.hide()
		toolbox.itemCover.normalizeItem()

	def __addTimerPanel( self, time ): #
		pyTimerPanel = self.__getRewardPanel( RW_TYPE_TIMER )
		pyTimerPanel.time = time
		self.pyContent_.appendTimer( pyTimerPanel )

	# ---------------------------------------
	def __addAimItems( self, text, aimItems ): # �������Ŀ�����
		pyAimPanel = None
		if text == "" and len( aimItems ) == 0:
			pyAimPanel = self.__getRewardPanel( RW_TYPE_NONE )
		else:
			pyAimPanel = self.__getRewardPanel( RW_TYPE_AIM )
			pyAimPanel.title = labelGather.getText( "NPCTalkWnd:main", "questAim" )
			if text != "":
				objectText = GUI.load( "guis/general/npctalk/objecttext.gui" )
				uiFixer.firstLoadFix( objectText )
				pyRichText = CSRichText( objectText )
				pyRichText.opGBLink = True
				pyRichText.maxWidth = pyAimPanel.width - 3.0
				pyRichText.onComponentMouseEnter.bind( self.__onCompEnter )
				text = PL_Font.getSource( text, fc = ( 230, 227, 185, 255 ) )
				pyRichText.text = text
				pyAimPanel.addItem( pyRichText )
			for taskType, title, tag, isCollapsed, isComplete in aimItems:
				stateText = ""
				if isComplete : stateText = labelGather.getText( "NPCTalkWnd:main", "finished" )
				else:stateText = labelGather.getText( "NPCTalkWnd:main", "unfinished" )
				if isCollapsed : stateText = labelGather.getText( "NPCTalkWnd:main", "failure" )
				if taskType == csdefine.QUEST_OBJECTIVE_TIME:
					stateText = ""
				condition = "%s: %s  %s" % ( title, tag, stateText )
				pyAimItem = self.__getRewardItem( RW_TYPE_AIM )
				pyAimItem.aimCondition = condition # ��������
				pyAimPanel.addItem( pyAimItem )
		self.pyContent_.appendAimPanel( pyAimPanel )

	def __onCompEnter( self, component ):
		if component.__class__.__name__ == "LinkLabel":
			rds.ccursor.normal()

	def __addCommonRewards( self, otherRewards, singleRewards, questID ) : # �õ��̶�������Ʒ,��Ǯ�������
		"""
		append common reward
		"""
		if singleRewards is not None:
			pyRewardPanel = CRewardPanel[RW_TYPE_ITEM]()
			pyRewardPanel.cols = 1
			title = labelGather.getText( "NPCTalkWnd:main", "followReward" )
			for reward in singleRewards._items:
				schemeInfo = reward.query( "schemeInfo" )
				if schemeInfo:
					cmd, presistMinute = schemeInfo.split("|")
					presistMinute = int( presistMinute )
					scheme = Scheme()
					scheme.init( cmd )
					year, month, day, hour, minute = Time.localtime( Time.time() - presistMinute * 60 )[:5]
					nextTime = scheme.calculateNext( year, month, day, hour, minute )
					if nextTime > Time.time():continue
				pyItem = self.__getRewardItem( RW_TYPE_ITEM )
				pyItem.selected = False
				pyItem.canbeSelected = False
				pyItem.foucs = False
				pyItem.updateItem( ObjectItem( reward ) )
				pyRewardPanel.addItem( pyItem )
			if len( pyRewardPanel.pyItems ) > 0:
				title = labelGather.getText( "NPCTalkWnd:GroupRewards", "followReward" )
			pyRewardPanel.title = title
			pyRewardPanel.layout_()
			self.pyContent_.appendRewardItemsPanel( pyRewardPanel )
			for reward in otherRewards :
				if reward.type() == csdefine.QUEST_REWARD_MONEY:
					# ��Ǯ����
					pyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					pyPanel.setMoney( money )
				elif reward.type() == csdefine.QUEST_REWARD_MULTI_MONEY:
					# �౶��Ǯ����
					pyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					multiFlag = reward._multiFlag
					pyPanel.setMoney( money, multiFlag )
				else:
					pyPanel = CRewardItem[RW_TYPE_OTHER]()
					if reward.type() in [csdefine.QUEST_REWARD_TITLE,csdefine.QUEST_REWARD_IE_TITLE] :# �ƺŽ���
						arg = titleMgr.getName( reward._title )
					elif reward.type() == csdefine.QUEST_REWARD_PRESTIGE:
						npcPrestigeID = reward._prestigeID
						prestigeName = factionMgr.getName( npcPrestigeID )
						arg = prestigeName+"  "+str( reward._amount ) # ����������
					else:
						arg = str( reward._amount ) # ���飬Ǳ�ܽ���
					pyPanel.setValueText( reward.type(), arg )
				self.pyContent_.appendRewardItemsPanel( pyPanel )
		if singleRewards is None and len( otherRewards ) > 0:
			pyRewardPanel = CRewardPanel[RW_TYPE_OTHER]()
#			pyRewardPanel.cols = 1
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:main", "followReward" )
			for reward in otherRewards:
				if reward.type() == csdefine.QUEST_REWARD_MONEY:
					# ��Ǯ����
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					moneyPanel.setMoney( money )
					pyRewardPanel.addItem( moneyPanel )
				elif reward.type() == csdefine.QUEST_REWARD_MULTI_MONEY:
					# �౶��Ǯ����
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					multiFlag = reward._multiFlag
					moneyPanel.setMoney( money, multiFlag )
					pyRewardPanel.addItem( moneyPanel )
				else:
					rwardItem = CRewardItem[RW_TYPE_OTHER]()
					if reward.type() == csdefine.QUEST_REWARD_TITLE:# �ƺŽ���
						arg = reward._title
					elif reward.type() == csdefine.QUEST_REWARD_PRESTIGE:
						npcPrestigeID = reward._prestigeID
						prestigeName = factionMgr.getName( npcPrestigeID )
						arg = prestigeName+"  "+str( reward._amount ) # ����������
					elif reward.type() == csdefine.QUEST_REWARD_TONG_FETE:
						arg = labelGather.getText( "NPCTalkWnd:rewards", "sacrificeReward" )
					else:
						arg = reward.getDescription()  # ���飬Ǳ�ܽ���
					rwardItem.setValueText( reward.type(), arg )
					pyRewardPanel.addItem( rwardItem )
			self.pyContent_.appendRewardItemsPanel( pyRewardPanel )

	def __addItemsReward( self, rewardItems ) : #�õ���Ʒ�������̶�����ѡ���������Ʒ
		"""
		add object item reward
		"""
		if rewardItems is None or len( rewardItems._items ) == 0: return
		pyRewardPanel = self.__getRewardPanel( RW_TYPE_ITEM )
		pyRewardPanel.cols = 1
		pyRewardPanel.pySelItem = None
		if rewardItems.type() in [csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND ]:# ��ѡ��������
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "choiceItem" )
		elif rewardItems.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "randomItem" )
		elif rewardItems.type() == csdefine.QUEST_REWARD_FIXED_RANDOM_ITEMS:
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "fixedRandomItem" )
		for index, item in enumerate( rewardItems._items ) :
			schemeInfo = item.query( "schemeInfo" )
			if schemeInfo:
				cmd, presistMinute = schemeInfo.split("|")
				presistMinute = int( presistMinute )
				scheme = Scheme()
				scheme.init( cmd )
				year, month, day, hour, minute = Time.localtime( Time.time() - presistMinute * 60 )[:5]
				nextTime = scheme.calculateNext( year, month, day, hour, minute )
				if nextTime > Time.time():continue
			pyItem = self.__getRewardItem( RW_TYPE_ITEM )
			if rewardItems.type() in [csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND ]: #��ѡ����
				pyItem.index = index
				pyItem.canbeSelected = True
				pyItem.selected = False
				pyItem.foucs = True
				pyItem.pyRewardPanel = pyRewardPanel
				self.pyOptionPanel = pyRewardPanel
			pyItem.updateItem( ObjectItem( item ) )
			pyRewardPanel.addItem( pyItem )
		self.pyContent_.appendRewardItemsPanel( pyRewardPanel )

	def __addItemsSubmit( self, items, taskType = 0 ): # ��������ύ��Ʒ
		if items == {} or items == None :return
		pySubmit = SubmitItem()
		pySubmit.updateItem( items, taskType ) # ��Ҫ�ύ��Ʒ��Ϣ
		pySubmitPanel = self.__getRewardPanel( RW_TYPE_SUBMIT )
		pySubmitPanel.title = labelGather.getText( "NPCTalkWnd:main", "querySubmit" )
		pySubmitPanel.addItem( pySubmit )
		self.pySubmitItem = pySubmitPanel.pyItems[0]
		self.pyContent_.appendSubmitPanel( pySubmitPanel )

	def __addPetsSubmit( self, questAimItems ):#����ύ����
		subpet = GUI.load( "guis/general/npctalk/submitpet.gui" )
		uiFixer.firstLoadFix( subpet )
		pySubPet = SubmitPet( subpet )
		pySubPet.initMyPets()
		pySubPet.setAimText( questAimItems[0] )
		pySubmitPanel = self.__getRewardPanel( RW_TYPE_SUBMIT )
		pySubPet.center = pySubmitPanel.width/2.0
		pySubmitPanel.addItem( pySubPet )
		self.subPets = pySubPet.getSubPets()
		self.pyContent_.appendSubmitPanel( pySubmitPanel )
	
	def __addSkillsReward( self, skillRewards ):
		if not len( skillRewards ):return
		pyRewardPanel = self.__getRewardPanel( RW_TYPE_SKILL )
		pyRewardPanel.pySelItem = None
		pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:rewards", "reward_skill" )
		for index, skReward in enumerate( skillRewards ):
			pyItem = self.__getRewardItem( RW_TYPE_SKILL )
			pyItem.index = index
			pyItem.canbeSelected = False
			pyItem.selected = False
			pyItem.foucs = True
			pyItem.pyRewardPanel = pyRewardPanel
			skillInfo = SkillItem( skReward._skill )
			pyItem.updateItem( skillInfo )
			pyRewardPanel.addItem( pyItem )
		self.pyContent_.appendRewardItemsPanel( pyRewardPanel )
	# ------------------------------------------------------------
	def __addRewards( self ) : # ������з������˷����Ľ���,�ٷ���
		"""
		add rewards
		"""
		if self.pyContent_.itemCount == 0 : return
		questObjectText = GUIFacade.getQuestObjectiveText()
		questAimItems = GUIFacade.getObjectiveDetailFromServer()		# ����Ŀ��
		aptoticRewards = GUIFacade.getFixedRewardItems()		# �̶���Ʒ����
		fixedRndRewards = GUIFacade.getFixedRandomRewardItems()
		skillRewards = GUIFacade.getRewardSkills()				#���ܽ���
		optionalRewards = GUIFacade.getChooseRewardItems()		# ��ѡ��Ʒ����
		optionalSubmit	= GUIFacade.getSubmitInfoFromServer()	# ���ύ��Ʒ��Ϣ
		classItemRewards = GUIFacade.getRewardsFixedItemsFromClass()	#ְҵ��Ʒ����
		questID = GUIFacade.getQuestID()
		if GUIFacade.getQuestLogs().has_key( questID ):
			for i in GUIFacade.getQuestLogs()[questID]["tasks"]._tasks.itervalues():
				if i.getType() == csdefine.QUEST_OBJECTIVE_DELIVER_PET:
					self.__addPetsSubmit( questAimItems )
					break
		rndReward = GUIFacade.getRndRewardItems()				# �����Ʒ����
		otherRewards = GUIFacade.getOtherRewards()				# ������Ʒ����
		self.__addAimItems( "", [] )									#ռλ
		if len( questAimItems ) > 0:							# �ύ��������Ʒ
			self.__addItemsSubmit( optionalSubmit, questAimItems[0][0] )
		else:
			self.__addItemsSubmit( optionalSubmit )
		self.__addItemsReward( optionalRewards ) # ʵ����ѡ������Ʒ
#		self.__addItemsReward( aptoticRewards )	# ʵ���̶���Ʒ�������
		self.__addItemsReward( rndReward )		# ʵ�����������Ʒ
		self.__addItemsReward( fixedRndRewards )
		self.__addCommonRewards( otherRewards, aptoticRewards, questID ) # ʵ������ͨ��������Ǯ�������
		self.__addSkillsReward( skillRewards )
		self.__addItemsReward( classItemRewards )

	def __searchOptionByQuestId( self, questId ):
		"""
		ͨ������id���Ҷ�Ӧ����ѡ��
		"""
		if len( self.pyContent_.pyOptionItems ):
			for pyOption in self.pyContent_.pyOptionItems:
				try :
					if GUIFacade.getGossipQuestIdByIndex( pyOption.handleArgs[0] ) == questId:
						return pyOption
				except :
					pass
		return None

	def __searchOptionByDlgKey( self, dlgKey ):
		"""
		ͨ���Ի��ؼ��ֲ�����ͨ�Ի�ѡ��
		"""
		if len( self.pyContent_.pyOptionItems ):
			for pyOption in self.pyContent_.pyOptionItems:
				if pyOption.handler == GUIFacade.selectGossipOption :					# ����������ͨ�Ի�ѡ����
					try :
						if GUIFacade.getDlgKeyByOptionIndex( pyOption.handleArgs[0] ) == dlgKey:
							return pyOption
					except :
						pass
		return None

	def __onScrollChange( self, dz ):
		self.relocateIndications()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def clearContent_( self ):
		"""
		clear all content is in content panel
		"""
		for pyItem in self.pyOptionItems_ :
			if hasattr( pyItem, "pyRewardPanel" ) :
				del pyItem.pyRewardPanel

		self.subPets = []
		self.pyOptionPanel = None
		CTWindow.clearContent_( self )

	# -------------------------------------------------
	def onShowCommonTalking_( self ) :	# wsf modify
		self.clearIndications()							# ����֮�ƣ�������ɵ���ʾ
		self.pyBigPanel_.visible = False
		self.clearContent_()
		questID = GUIFacade.getQuestID()
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		if typeStr != "":
			self.pyContent_.appendTypeText( typeStr )
		self.pyContent_.appendText( GUIFacade.getGossipText() )					# ��ͨ�Ի�����
		questOptions = GUIFacade.getGossipQuests()

		completeQuest = []
		completeQuestIDs = []
		incompleteQuest = []
		canSelectQuest = []
		for index, questInfo in enumerate( questOptions ):							# ��������࣬���ɽ����񡢲��ɽ����񡢿ɽ���������
			if GUIFacade.getQuestLogs().has_key( questInfo[ 0 ] ):	# �����ҽ��˴�����
				if GUIFacade.questIsCompleted( questInfo[ 0 ] ):		# �������Ѿ���ɴ�����
					completeQuest.append( index )
					completeQuestIDs.append( ( index, questInfo[0] ) )
				else:
					incompleteQuest.append( index )
				continue
			else:
				canSelectQuest.append( index )

		def addOptionItems( options, handler, indexList ) :
			tempList = zip( options, indexList )
			for index, option in enumerate( tempList ) :
				self.addOptionItem_( index, option[0][1], option[0][2], handler, ( option[1], ) )
		tempQuestOptions = []
		indexList = []
		for index in completeQuest:
			tempQuestOptions.append( questOptions[ index ] )
			indexList.append( index )
		for index in incompleteQuest:
			tempQuestOptions.append( questOptions[ index ] )
			indexList.append( index )
		for index in canSelectQuest:
			tempQuestOptions.append( questOptions[ index ] )
			indexList.append( index )
		addOptionItems( tempQuestOptions, GUIFacade.selectGossipQuest, indexList )				# �������ѡ��
		CTWindow.showGossipOption( self )											# �����ͨ�Ի�ѡ��
		self.currentWindow = COMMONTALKING
		self.show()
		self.__addTrap()
		talkNpc = GUIFacade.getGossipTarget()
		if talkNpc is None:return
		for index, questID in completeQuestIDs:
			if isMainQuest( questID ):					# ���������������ɿɽ�
				self.hide()
				GUIFacade.selectGossipQuest( index )	# ֱ����ʾ���������
				return
		GUIFacade.gossipWithTrainer()					# ����ѵ��ʦ�Ի�

	def __hasQuestOption( self ):
		hasQuestOPtion = False
		for pyOption in self.pyContent_.pyOptionItems:
			if pyOption.markType in quest_marks:
				hasQuestOPtion = True
				break
		return hasQuestOPtion

	def onEndTalking_( self ):
		self.currentWindow = 0
		CTWindow.onEndTalking_( self )

	def onMove_( self, dx, dy ) :
		CTWindow.onMove_( self, dx, dy )
		toolbox.infoTip.moveHelpTips( 0x0006 )
		toolbox.infoTip.moveHelpTips( 0x0007 )
		toolbox.infoTip.moveHelpTips( 0x0008 )
		toolbox.infoTip.moveHelpTips( 0x0009 )
		toolbox.infoTip.moveHelpTips( 0x000a )
		toolbox.infoTip.moveHelpTips( 0x000b )
		self.relocateIndications()

	def show( self ) :
		CTWindow.show( self )
		name = labelGather.getText( "NPCTalkWnd:main", "lbTitle" )
		headTexture = ""
		target = GUIFacade.getGossipTarget()
		if target:
			name = target.getName()
			headTexture = target.getHeadTexture()
		self.pyLbTitle_.text = name
		self.pyHeader_.texture = headTexture
		#rds.opIndicator.triggerIdtsBindedToGUI( self, ("gui_visible","talkingWindow") )

	def hide( self ):
		"""
		"""
		if self.__mainQuestAutoTimerID:
			BigWorld.cancelCallback( self.__mainQuestAutoTimerID )
			self.__mainQuestAutoTimerID = 0
			
		GUIFacade.clearVoiceBuff()
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		if self.currentWindow in [ QUESTCOMPLETE, QUESTPRECOMPLETE] and self.nextQuest == True:
			self.currentWindow = 0
			self.__onShowQuestTalking()
			self.nextQuest = False
		else:
			return RootGUI.hide( self )
		self.clearIndications()

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setPos( self, ( left, top ) ) :
		Window._setPos( self, ( left, top ) )
		self.relocateIndications()

	pos = property( Window._getPos, _setPos )

	# ----------------------------------------------------------------
	# operate indication methods
	# ----------------------------------------------------------------
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		# ��ʾ�������������
		trigger = ( "gui_visible","talkingWindow" )
		condition = ( "talking_npc","talking_quest","has_no_quest" )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showAcceptQuestIndication
		# ��ʾ�������ѡ��
		condition = ( "talking_npc","quest_completed", )
		condition2 = ( "quest_completed", )								# ��Щ����߻�û��Ի���NPCID�������ж���Ի�NPC
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		idtIds += rds.opIndicator.idtIdsOfCmd( condition2, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showQuestOptionIndication
		# ��ʾ������������
		condition = ( "talking_npc","talking_quest","quest_completed", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showCompelteQuestIndication
		# ��ʾ�����ͨ�Ի�
		condition = ( "talking_npc","has_quest", )
		condition2 = ( "talking_npc","quest_uncompleted", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		idtIds += rds.opIndicator.idtIdsOfCmd( condition2, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showGossipOptionIndication

	def __showQuestOptionIndication( self, idtId, questId ) :
		"""
		"""
		pyGui = self.__searchOptionByQuestId( questId )
		if pyGui and pyGui.rvisible :
			toolbox.infoTip.showHelpTips( idtId, pyGui, Rect( (0, 0), (250.0, pyGui.height) ) )
			self.addVisibleOpIdt( idtId )

	def __showGossipOptionIndication( self, idtId, dlgKey ) :
		"""
		"""
		pyGui = self.__searchOptionByDlgKey( dlgKey )
		if pyGui and pyGui.rvisible :
			toolbox.infoTip.showHelpTips( idtId, pyGui, Rect( (0, 0), (250.0, pyGui.height) ) )
			self.addVisibleOpIdt( idtId )

	def __showAcceptQuestIndication( self, idtId ) :
		"""
		"""
		if self.pyBtnAccept_.rvisible :
			toolbox.infoTip.showHelpTips( idtId, self.pyBtnAccept_ )
			self.addVisibleOpIdt( idtId )
		else :
			INFO_MSG( "Accept btn unvisible." )

	def __showCompelteQuestIndication( self, idtId ):
		"""
		"""
		if self.pyBtnFulfil_.rvisible :
			toolbox.infoTip.showHelpTips( idtId, self.pyBtnFulfil_ )
			self.addVisibleOpIdt( idtId )
		else :
			INFO_MSG( "Fulfill btn unvisible." )

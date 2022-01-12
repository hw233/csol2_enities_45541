# -*- coding: gb18030 -*-
#
# $Id: GroupRewards.py,v 1.10 2008-08-25 09:26:25 huangyongwei Exp $

"""
implement quest talking window��
"""

from guis import *
from LabelGather import labelGather
from CommontalkWindow import CommontalkWindow as CTWindow
from ItemsFactory import ObjectItem
from Rewards import ItemRewardPanel
from Rewards import ItemReward
from SubmitItem import SubmitItem
import csdefine
import GUIFacade.QuestLogFacade
from QuestModule import QuestReward

from Rewards import RW_TYPE_ITEM
from Rewards import RW_TYPE_MONEY
from Rewards import RW_TYPE_OTHER
from Rewards import RW_TYPE_SUBMIT
from Rewards import CRewardPanel
from Rewards import CRewardItem


class GroupRewards( CTWindow ):
	def __init__( self ):
		CTWindow.__init__( self )
		self.__pyRewardsPanels = []
		self.__pyRewardItems = []
		#self.pyAcceptBtn_.onLClick.bind( self.__onAccept )
		#self.pyFulfilBtn_.onLClick.bind( self.__onComplete )
		self.pyBtnShut_.onLClick.bind( self.__onClose )
		self.pyOptoinPanel = None

	def registerTriggers_( self ):
		self.triggers_["EVT_QUEST_SHOW_GROUP_REWARDS_DETAIL"] = self.__onShowRewardsDetail

		CTWindow.registerTriggers_( self )

	def __onClose( self ):
		"""
		"""
		self.hide()

	def __onShowRewardsDetail( self, questID, rewards ):
		#targetName = GUIFacade.getQuestTarget().getName()
		#title, level = GUIFacade.getQuestTitle()
		#self.title = targetName

		self.clearContent_()
		#self.pyContent_.appendTitle( title )
		#self.pyContent_.appendText( storyText )
		self.__addRewards( rewards )
		self.show()

	# ------------------------------------------------------------
	def __addRewards( self, rewards ) : # ������з������˷����Ľ���,�ٷ���
		"""
		add rewards
		"""
		reward_choose_items = None
		reward_rnd_items = None
		reward_fixed_items = None
		reward_others = []

		for reward in rewards:
			qr = QuestReward.createByStream( reward )
			if qr.type() in [ csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND]:
				reward_choose_items = qr
			elif qr.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:
				reward_rnd_items = qr
			elif qr.type() in [csdefine.QUEST_REWARD_ITEMS,csdefine.QUEST_REWARD_FUBI_ITEMS, csdefine.QUEST_REWARD_ITEMS_FROM_ROLE_LEVEL]:
				reward_fixed_items = qr
			else:
				reward_others.append( qr )

		#if self.pyContent_.itemCount == 0: return
		#aptoticRewards = GUIFacade.getFixedRewardItems()		# �̶���Ʒ����
		#optionalRewards = GUIFacade.getChooseRewardItems()		# ��ѡ��Ʒ����
		#rndReward = GUIFacade.getRndRewardItems()				# �����Ʒ����
		#otherRewards = GUIFacade.getOtherRewards()				# ������Ʒ����
		#self.__addAimItems( questObjectText, questAimItems )
		self.__addItemsReward( reward_choose_items ) # ʵ����ѡ������Ʒ
		self.__addItemsReward( reward_rnd_items )		# ʵ�����������Ʒ
		self.__addCommonRewards( reward_others, reward_fixed_items ) # ʵ������ͨ��������Ǯ�������

	def __addCommonRewards( self, otherRewards, singleRewards ) : # �õ��̶�������Ʒ,��Ǯ�������
		"""
		append common reward
		"""
		if singleRewards is not None and len( otherRewards ) > 0:
			pyPanel = CRewardPanel[RW_TYPE_ITEM]()
			pyPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "followReward" )
			for reward in singleRewards._items:
				pyItem = self.__getRewardItem( RW_TYPE_ITEM )
				pyItem.updateItem( ObjectItem( reward ) )
				pyPanel.addItem( pyItem )
			self.pyContent_.appendRewardItemsPanel( pyPanel )
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
					if reward.type() == csdefine.QUEST_REWARD_TITLE: # �ƺŽ���
						arg = reward._amount
					else:
						arg = reward.getDescription() # ���飬Ǳ�ܽ���
					pyPanel.setValueText( reward.type(), arg )
				self.pyContent_.appendRewardItemsPanel( pyPanel )

		if singleRewards is None and len( otherRewards ) > 0 :
			pyPanel = CRewardPanel[RW_TYPE_OTHER]()
			pyPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "groupExtrReward" )
			for reward in otherRewards:
				if reward.type() == csdefine.QUEST_REWARD_MONEY:
					# ��Ǯ����
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					moneyPanel.setMoney( money )
					pyPanel.addItem( moneyPanel )
				elif reward.type() == csdefine.QUEST_REWARD_MULTI_MONEY:
					# �౶��Ǯ����
					moneyPanel = CRewardPanel[RW_TYPE_MONEY]()
					money = reward._amount
					multiFlag = reward._multiFlag
					moneyPanel.setMoney( money, multiFlag )
					pyPanel.addItem( moneyPanel )
				else:
					rwardItem = CRewardItem[RW_TYPE_OTHER]()
					if reward.type() == csdefine.QUEST_REWARD_TITLE:# �ƺŽ���
						arg = reward._title
					else:
						arg = reward.getDescription() # ���飬Ǳ�ܽ���
					rwardItem.setValueText( reward.type(), arg )
					pyPanel.addItem( rwardItem )
			self.pyContent_.appendRewardItemsPanel( pyPanel )
		if singleRewards is None and len( otherRewards ) == 0:
			pyPanel = CRewardPanel[RW_TYPE_ITEM]()
			pyPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "randomStuff" )
			self.pyContent_.appendRewardItemsPanel( pyPanel )			



	def __addItemsReward( self, rewardItems ) : #�õ���Ʒ�������̶�����ѡ���������Ʒ
		"""
		add object item reward
		"""
		if rewardItems is None or len( rewardItems._items ) == 0: return
		pyRewardPanel = self.__getRewardPanel( RW_TYPE_ITEM )
		if rewardItems.type() in [ csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND]:# ��ѡ��������
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "choiceItem" )

		elif rewardItems.type() == csdefine.QUEST_REWARD_RANDOM_ITEMS:
			pyRewardPanel.title = labelGather.getText( "NPCTalkWnd:GroupRewards", "randomItem" )

		for index, item in enumerate( rewardItems._items ) :
			pyItem = self.__getRewardItem( RW_TYPE_ITEM )
			if rewardItems.type() in [csdefine.QUEST_REWARD_CHOOSE_ITEMS, csdefine.QUEST_REWARD_CHOOSE_ITEMS_AND_BIND ]: #��ѡ����
				pyItem.index = index
				pyItem.canbeSelected = True
				pyItem.foucs = True
				pyItem.pyRewardPanel = pyRewardPanel
				self.pyOptoinPanel = pyRewardPanel
			pyItem.updateItem( ObjectItem( item ) )
			pyRewardPanel.addItem( pyItem )
		self.pyContent_.appendRewardItemsPanel( pyRewardPanel )

	# --------------------------------------------------------------
	def __getRewardPanel( self, rwType ) : # ���������͵ĵõ��������
		"""
		get/create a reward items panel
		"""
		for pyPanel in self.__pyRewardsPanels :
			if pyPanel.used : continue
			if pyPanel.rewardType != rwType : continue
			pyPanel.used = True
			return pyPanel
		pyPanel = CRewardPanel[rwType]( )
		pyPanel.used = True
		self.__pyRewardsPanels.append( pyPanel )
		return pyPanel

	def __getRewardItem( self, rwType ) : #�õ�������Ʒ
		"""
		get/create a reward item
		"""
		for pyItem in self.__pyRewardItems :
			if pyItem.used : continue
			if pyItem.rewardType != rwType : continue
			pyItem.used = True
			return pyItem
		pyItem = CRewardItem[rwType]()
#		pyItem.onComponentMouseEnter.bind( self.__onItemMouseEnter )
#		pyItem.onComponentMouseLeave.bind( self.__onItemMouseLeave )
		pyItem.used = True
		self.__pyRewardItems.append( pyItem )
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


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def clearContent_( self ):
		"""
		clear all content is in content panel
		"""
		for pyPanel in self.__pyRewardsPanels :
			pyPanel.clearItems()
			pyPanel.used = False
		for pyItem in self.__pyRewardItems :
			pyItem.used = False
			pyItem.handler = lambda *args : False
		for pyItem in self.pyOptionItems_ :
			if hasattr( pyItem, "pyRewardPanel" ) :
				del pyItem.pyRewardPanel
		CTWindow.clearContent_( self )

	# -------------------------------------------------
	def onShowCommonTalking_( self ) :
		self.pyBigPanel_.visible = False
		CTWindow.onShowCommonTalking_( self )
		questOptions = GUIFacade.getGossipQuests()

		def addOptionItems( options, handler ) :
			for index, option in enumerate( options ) :
				self.addOptionItem_( index, option[1], option[2], handler, ( index, ) )
		addOptionItems( questOptions, GUIFacade.selectGossipQuest )

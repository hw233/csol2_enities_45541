# -*- coding: gb18030 -*-
#
# $Id: RewardBoxDetails.py $
from guis import *
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from ItemsFactory import ObjectItem
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from items.ItemDataList import ItemDataList
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.CSRichText import CSRichText
from OnlineRewardMgr import OnlineRewardMgr
import csdefine
import csconst
import Timer

g_items = ItemDataList.instance()
rewardMgr = OnlineRewardMgr.instance()

REWARD_EXP_TYPE  = 1	#经验
REWARD_POTE_TYPE = 2	#潜能
REWARD_ITEM_TYPE = 3	#物品

class RewardBoxDetails( Window ):
	
	def __init__( self ):
		boxDetails = GUI.load( "guis/tooluis/fixrewardbox/boxDetails.gui" )
		uiFixer.firstLoadFix( boxDetails )
		Window.__init__( self, boxDetails )
		self.addToMgr( "rewardBoxDetails" )
		self.rewardTimer = 0
		self.remainTime =0.0
		self.isNewPlayerReward = True
		self.oldItemID = 0
		self.__initPanel( boxDetails )
		
	def __initPanel( self, panel ):
		self.__pyRtNextRewardTime = CSRichText( panel.bg.stNextRewardTime )
		self.__pyRtNextRewardTime.align = "L"
		self.__pyRtNextRewardTime.text = ""
		
		self.__pyRtRemainRewardTimes = CSRichText( panel.bg.stRemainRewardTimes )
		self.__pyRtRemainRewardTimes.align = "L"
		self.__pyRtRemainRewardTimes.text = ""
		
		self.__pyPanel = PyGUI( panel.bg )
		
		self.__pyStLastTimeReward = StaticText( panel.bg.stLastTimeReward )
		self.__pyStLastTimeReward.text = ""
		self.__pyStLastTimeReward.color = ( 255, 248, 158 )
		
		self.__pyItem = RewardItem( panel.bg.item, self )
		self.__pyItem.update( None, 0, 0, 1 )
		
		self.__btnOk = HButtonEx( panel.btnOk )
		self.__btnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__btnOk.onLClick.bind( self.__confirmToReceiveReward )
		self.__btnOk.enable = False
		labelGather.setPyBgLabel( self.__btnOk, "FixRewardBox:main", "btnOk" )
		
		self.__btnCancel = HButtonEx( panel.btnCancel )
		self.__btnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__btnCancel.onLClick.bind( self.__shut )
		labelGather.setPyBgLabel( self.__btnCancel, "FixRewardBox:main", "btnCancel" )	
		
	#-----------------------------------------------------
	# private
	#----------------------------------------------------		
	def __confirmToReceiveReward( self ):
		"""
		通知服务器可以给玩家奖励
		"""		
		player = BigWorld.player()
		if self.isNewPlayerReward:	
			player.base.confirmToReceiveNewPlayerReward()		#新手在在线奖励接口
		else:
			player.base.confirmToReceiveOldPlayerReward()		#老手在线奖励接口
			
	def __shut( self ):
		self.hide()
				
	def __rewardCountdown( self ):
		self.remainTime -= 1.0
		timeStr = self.__getTimeStr()
		self.__pyRtNextRewardTime.text = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "nextRewardTime")%timeStr, fc = ( 255, 248, 158 ))
		if self.remainTime <= 0:
			Timer.cancel( self.rewardTimer )
			self.rewardTimer = 0
			labelGather.setPyBgLabel( self.__pyRtNextRewardTime, "FixRewardBox:main", "rewardThisTimeReward" )
			self.__btnOk.enable = True
			
	def __getTimeStr( self ):
		timeStr = ""
		if self.remainTime < 60 and self.remainTime > 0:
			timeStr = "00:%.2d"%self.remainTime
		if self.remainTime  >= 60:
			mins = int( self.remainTime/60 )
			secs = int( self.remainTime%60 )
			timeStr = "%.2d:%.2d" %( mins, secs )
		timeStr = PL_Font.getSource( "%s"%timeStr, fc = ( 255, 0, 0, 255 ) )
		return timeStr
		
	def __layOut( self ):
		self.__pyItem.center = self.__pyPanel.width/2.0
		self.__pyRtRemainRewardTimes.center = self.__pyPanel.width/2.0
		self.__pyRtNextRewardTime.center = self.__pyPanel.width/2.0
		self.__pyStLastTimeReward.center = self.__pyPanel.width/2.0
				
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyOwner = None ):
		self.__layOut()
		Window.show( self, pyOwner )
		
	def hide( self ):
		self.oldItemID  = 0
		Window.hide( self )
		
	def updateFixTimeReward( self, nextTimeTick, itemID, rewardOrder,lifeTime, lastRewardID ):
		"""
		新手在线奖励
		"""
		self.isNewPlayerReward = True
		self.__btnOk.enable = False
		labelGather.setPyLabel( self.pyLbTitle_, "FixRewardBox:main", "newPlayerTitle" )
		if nextTimeTick is not None: #可以获取下次奖励时间
			Timer.cancel( self.rewardTimer )
			self.rewardTimer = 0
			if lifeTime >= nextTimeTick + 3:
				self.remainTime = 0
				self.__btnOk.enable = True
			else:
				self.remainTime = nextTimeTick - lifeTime + 3 #减去服务器与客户端之间的误差
			if itemID > 0:
				item = BigWorld.player().createDynamicItem( itemID )
				itemInfo = ObjectItem( item )
				self.__pyItem.update( itemInfo, REWARD_ITEM_TYPE, self.remainTime, 1 )
			self.rewardTimer = Timer.addTimer( 0, 1, self.__rewardCountdown )
			if rewardOrder >= 0:
				fixTimeTotalNum = rewardMgr.getCount()	 #新手总奖励次数
				remainRewardTimes = fixTimeTotalNum - rewardOrder  
			else:
				remainRewardTimes = 0	
			remainRewardText = PL_Font.getSource( "%d"%remainRewardTimes, fc = ( 255, 0, 0, 255 ) )
			self.__pyRtRemainRewardTimes.text = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "remainRewardTimes" ) % remainRewardText )
			self.oldItemID = lastRewardID
			if self.oldItemID == 0:
				self.__pyStLastTimeReward.text = ""
			else:
				oldItemName = g_items.id2name( self.oldItemID )
				self.__pyStLastTimeReward.text = labelGather.getText( "FixRewardBox:main", "lastTimeReward" )%oldItemName
			timeStr = self.__getTimeStr()
			self.__pyRtNextRewardTime.text = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "nextRewardTime")%timeStr )
			self.__layOut()
				
	def updateOldPlayerReward( self, timeTick, rewardOrder, rewardType, param):
		"""
		老手在线奖励
		"""
		self.isNewPlayerReward = False
		self.__btnOk.enable = False
		labelGather.setPyLabel( self.pyLbTitle_, "FixRewardBox:main", "oldPlayerTitle" )
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		if rewardType == 1:
			self.__pyStLastTimeReward.text = labelGather.getText( "FixRewardBox:main", "reward_exp" )%param
		elif rewardType == 2:
			self.__pyStLastTimeReward.text = labelGather.getText( "FixRewardBox:main", "reward_potential" )%param
		elif rewardType == 3:
			nameStr = g_items.id2name( param )
			self.__pyStLastTimeReward.text = labelGather.getText( "FixRewardBox:main", "lastTimeReward" )%nameStr
		else:
			self.__pyStLastTimeReward.text = ""
		remainAmount = max( BigWorld.player().getLevel()/10, 3 ) - rewardOrder
		if timeTick == 0:
			nextOrder = rewardOrder + 1
			self.remainTime = 600*nextOrder
		elif timeTick > 0:
			self.remainTime = timeTick
		remainAmountStr = PL_Font.getSource( "%d"%remainAmount, fc = ( 255, 0, 0, 255 ))
		self.__pyRtRemainRewardTimes.text = labelGather.getText( "FixRewardBox:main", "oldPlayerRemainTimes")%remainAmountStr
		self.__pyItem.update( None, 0, self.remainTime, 1 )
		timeStr = self.__getTimeStr()
		self.__pyRtNextRewardTime.text = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "nextRewardTime")%timeStr )
		self.rewardTimer = Timer.addTimer( 0, 1, self.__rewardCountdown ) 
		self.__layOut()
		
	def onLeaveWorld( self ) :
		self.hide()
		self.__pyItem.update( None, 0, 0, 1 )
# -------------------------------------------------------------------------
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.MLUIDefine import ItemQAColorMode, QAColor


class RewardItem( PyGUI ):

	def __init__( self, item, pyBinder = None ):
		PyGUI.__init__( self, item )
		self.__pyItem = Item( item.item, pyBinder )
		self.__pyItem.dragFocus = False
		self.itemInfo = None

	def update( self, itemInfo, rewardType, remain = 0, rewardAmount = 1 ):
		self.__pyItem.update( itemInfo, rewardType, remain, rewardAmount )
		self.itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )

from guis.controls.CircleCDCover import CircleCDCover as CDCover
class Item( BOItem ):

	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.rewardType = -1
		self.rewardAmount = 0
		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

	def onRClick_( self, mods ):
		"""
		右键拾取
		"""
		BOItem.onRClick_( self, mods )
		if self.rewardType < 0:return

	def onDescriptionShow_( self ):
		dsp = ""
		player = BigWorld.player()
		if self.rewardType == REWARD_EXP_TYPE:
			dsp = labelGather.getText( "FixRewardBox:item", "reward_exp1", self.rewardAmount )
			standExp = int( 3 * ((self.pyBinder.curOrder + 1)**0.5) * (player.getLevel()**1.4) * 10 )
			if self.rewardAmount > 2*standExp: #经验暴击
				dsp = labelGather.getText( "FixRewardBox:item", "reward_exp2", self.pyBinder.curOrder, self.rewardAmount )
		elif self.rewardType == REWARD_POTE_TYPE:
			dsp = labelGather.getText( "FixRewardBox:item", "reward_potential1", self.rewardAmount )
			standProt = int( ((self.pyBinder.curOrder + 1)**0.5) * (player.getLevel()**1.4) * 10 )
			if self.rewardAmount > 2*standProt:
				dsp = labelGather.getText( "FixRewardBox:item", "reward_potential2", self.pyBinder.curOrder, self.rewardAmount )
		elif self.rewardType == REWARD_ITEM_TYPE:
			item = self.itemInfo.baseItem
			dsp = item.description( BigWorld.player() )
		else:
			if self.pyBinder.isNewPlayerReward:			#新手奖励
				player = BigWorld.player()
				fixTimeRewardTick = rewardMgr.rewardKeys()
				rewardData = rewardMgr.getRewardItemIDsByGenAndCar( fixTimeRewardTick[0], player.getGender(), player.getClass() )
				rewards = rewardData.get( fixTimeRewardTick[0], None )
				if rewards is None:return
				itemNames = ""
				for index, reward in enumerate( rewards ):
					rewardID = int( reward.split( ":" )[0] )
					itemName = ""
					if index < len( rewards ) - 1:
						itemName = "%s %s"%( g_items.id2name( rewardID ), PL_NewLine.getSource() )
					else:
						itemName = g_items.id2name( rewardID )
					quality = g_items.id2quality( rewardID )
					color = QAColor.get( quality, ( 255, 255, 255, 0 ) )
					itemNames += PL_Font.getSource( "%s"%itemName, fc = color )
				dsp = labelGather.getText( "FixRewardBox:item", "random_item" )%itemNames
		toolbox.infoTip.showItemTips( self, dsp )

	def update( self, itemInfo, rewardType, remain, rewardAmount ):
		player = BigWorld.player()
		self.rewardType = rewardType
		self.rewardAmount = rewardAmount
		self.hideParticle()
		self.__pyCDCover.unfreeze( remain )
		if rewardType == REWARD_EXP_TYPE:
			standExp = int( 3 * ((self.pyBinder.curOrder + 1)**0.5) * (player.getLevel()**1.4) * 10 )
			self.icon = ( "icons/tb_jing_yan_001.dds", ((0.000000, 0.000000), (0.000000, 0.562500), (0.562500, 0.562500), (0.562500, 0.000000)))
			if rewardAmount > 2*standExp:
				player.statusMessage( csstatus.REWARD_3_TIMES_SUCCESS, rewardAmount )
				self.upDateParticle( 7 )
		elif rewardType == REWARD_POTE_TYPE:
			standProt = int( ((self.pyBinder.curOrder + 1)**0.5) * (player.getLevel()**1.4) * 10 )
			self.icon = ( "icons/tb_qian_neng_001.dds", ((0.000000, 0.000000), (0.000000, 0.562500), (0.562500, 0.562500), (0.562500, 0.000000)))
		 	if rewardAmount > 2*standProt:
				player.statusMessage( csstatus.REWARD_3_TIMES_SUCCESS, rewardAmount )
				self.upDateParticle( 8 )
		elif rewardType == REWARD_ITEM_TYPE:
			BOItem.update( self, itemInfo )
		else: #未知物品
			self.icon = ( "icons/tb_rw_z_011.dds",  ((0.000000, 0.000000), (0.000000, 0.562500), (0.562500, 0.562500), (0.562500, 0.000000)))
	



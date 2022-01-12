# -*- coding: gb18030 -*-
#
# $Id: FixRewardBox.py fangpengjun $

from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.FrameEx import HVFrameEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from items.ItemDataList import ItemDataList
from LabelGather import labelGather
from RewardBoxDetails import RewardBoxDetails
import ShareTexts
import GUIFacade
import Timer
import cscustom
import csdefine
import csstatus
import csconst

REWARD_EXP_TYPE  = 1	#经验
REWARD_POTE_TYPE = 2	#潜能
REWARD_ITEM_TYPE = 3	#物品

class FixRewardBox( RootGUI ):
	def __init__( self ):
		box = GUI.load( "guis/tooluis/fixrewardbox/box.gui")
		uiFixer.firstLoadFix( box )
		RootGUI.__init__( self, box )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ = False
		self.rewardTimer = 0
		self.addToMgr()
		self.__flashSign = True # 用于控制窗口闪烁
		self.remainTime = 0.0
		self.__initBox( box )
		self.__triggers = {}
		self.__registerTriggers()

	def dispose( self ) :
		RootGUI.dispose( self )

	def __initBox( self, box ):
		self.__pyRewardBoxDetails = RewardBoxDetails()
		self.__pyRewardItem = RewardItem( box.item.item, self )
		self.__pyRewardItem.onLClick.bind( self.__showBoxDetails )
		
		self.__pyRtRewardInfo = CSRichText( box.rtInfo )
		self.__pyRtRewardInfo.text = ""
		
		self.__ringFader = box.fader
		self.__ringFader.speed = 0.4
		self.__ringFader.value = 1.0
		self.__flashID = 0

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_FIX_TIME_REWARD"] = self.__onFixTimeReward #新手定时奖励
		self.__triggers["EVT_ON_OLD_FIX_TIME_REWARD"] = self.__onOldTimeReward #老手定时奖励
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onUpdateLevel
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------
	def __flash( self ):
		"""
		窗口闪烁 淡入淡出
		"""
		BigWorld.cancelCallback( self.__flashID )
		self.__flashID = 0
		if self.__flashSign:
			self.__ringFader.value = 1.0
		else:
			self.__ringFader.value = 0.2
		self.__flashSign = not self.__flashSign
		self.__flashID = BigWorld.callback( self.__ringFader.speed + 0.1, self.__flash )
		
	def __stopFlash( self ):
		"""
		停止闪烁
		"""
		if self.__flashID:
			BigWorld.cancelCallback( self.__flashID )
			self.__flashID = 0
			self.__ringFader.value = 1.0
	
	def __showBoxDetails( self, isSelected ):
		if isSelected:
			self.__stopFlash()
			self.__pyRewardBoxDetails.show( self )
		
	def __onFixTimeReward( self, nextTimeTick, itemID, rewardOrder, lifeTime, lastRewardID  ):
		"""
		获取物品信息,领取奖励后 把奖励信息记录下来作为oldItem信息。
		"""
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		if rewardOrder == -1: #不能获取下次奖励时间，说明已经领取完,则隐藏界面
			self.hide()
			return
		self.__pyRtRewardInfo.text = ""
		if nextTimeTick is not None: #可以获取下次奖励时间
			if lifeTime > nextTimeTick + 3:
				self.remainTime = 0.0
			else:
				self.remainTime = nextTimeTick - lifeTime + 3
			self.__pyRewardItem.update( self.remainTime )
			self.__pyRewardBoxDetails.updateFixTimeReward( nextTimeTick, itemID, rewardOrder, lifeTime, lastRewardID )
			self.rewardTimer = Timer.addTimer( 0, 1, self.__rewardCountdown )
			self.show()

	def __onOldTimeReward( self, timeTick, rewardOrder, rewardType, param ):
		"""
		奖励物品数量、类型
		"""
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		self.__pyRtRewardInfo.text = ""
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		if timeTick == 0:
			nextOrder = rewardOrder + 1
			self.remainTime = 600*nextOrder
		elif timeTick > 0: #初次上线，剩余时间由服务器端传来,
			self.remainTime = timeTick	
		elif timeTick < 0:#领完今天最后一份奖励了
			self.hide()
			return
		self.__pyRewardItem.update( self.remainTime )
		self.rewardTimer = Timer.addTimer( 0, 1, self.__rewardCountdown )
		self.show()
		self.__pyRewardBoxDetails.updateOldPlayerReward( timeTick, rewardOrder, rewardType, param )
			
	def __rewardCountdown( self ):
		self.remainTime -= 1.0
		if self.remainTime <= 0:
			Timer.cancel( self.rewardTimer )
			self.rewardTimer = 0
#			self.__pyRtRewardInfo.text = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "rewardTips" ), fc = (0,255,0,255) )
			self.__pyRtRewardInfo.center = self.width/2.0
			self.__flash()

	def __onUpdateLevel( self, oldLevel, newLevel ):
		if oldLevel != csconst.OLD_REWARD_LEVEL_LIM + 1 and \
		newLevel == csconst.OLD_REWARD_LEVEL_LIM + 1:
			if self.rewardTimer >0:
				Timer.cancel( self.rewardTimer )
			description = labelGather.getText( "FixRewardBox:main", "levelLimit" )%( csconst.OLD_REWARD_LEVEL_LIM + 1 )
			self.__pyRtRewardInfo.text = description
			self.__pyRtRewardInfo.center = self.width/2.0
			self.show()
			Timer.addTimer( 10.0, 0, self.hide )
			


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def show( self ):
		RootGUI.show( self )
#		toolbox.infoTip.showOperationTips( 0x0020, self.__pyRewardItem )

	def hide( self ):
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		self.remainTime = 0
		self.__stopFlash()
		self.__pyRtRewardInfo.text = ""
		RootGUI.hide( self )
#		toolbox.infoTip.hideOperationTips( 0x0020 )

	def onLeaveWorld( self ) :
		self.hide()

# -------------------------------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
class RewardItem( BOItem ):

	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.icon = ( "icons/tb_rw_z_011.dds",  ((0.000000, 0.000000), (0.000000, 0.562500), (0.562500, 0.562500), (0.562500, 0.000000)))
		self.remainTime = 0.0
		self.rewardTips = ''
		self.rewardTimer = 0
		self.__isFixTimeReward = True
		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

#	def onRClick_( self, mods ):
#		"""
#		右键拾取
#		"""
#		BOItem.onRClick_( self, mods )
#		if self.rewardType < 0:return
		
	def onDescriptionShow_( self ):
		toolbox.infoTip.showItemTips( self, self.rewardTips)
		
	def __rewardCountdown( self ):
		self.remainTime -= 1.0
		timeStr = self.__getTimeStr()
		self.rewardTips = PL_Font.getSource( labelGather.getText( "FixRewardBox:main", "nextRewardTime")%timeStr )
		if self.remainTime <= 0:
			Timer.cancel( self.rewardTimer )
			self.rewardTimer = 0
			self.rewardTips = labelGather.getText( "FixRewardBox:main", "rewardThisTimeReward")
			
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

	def update( self, remainTime ):
		self.hideParticle()
		self.__pyCDCover.unfreeze( remainTime )
		self.remainTime = remainTime
		Timer.cancel( self.rewardTimer )
		self.rewardTimer = 0
		self.rewardTimer = Timer.addTimer( 0, 1, self.__rewardCountdown )

# --------------------------------------------------------------------------------------------
class RewardNotify( RootGUI ):

	def __init__( self ):
		notify = GUI.load( "guis/tooluis/fixrewardbox/notify.gui" )
		uiFixer.firstLoadFix( notify )
		RootGUI.__init__( self, notify )
		self.moveFocus = False
		self.focus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.notifyTimer = 0
		self.order = -1
		self.remainTime = 0.0
		self.addToMgr()
		self.__initNotify( notify )

	def dispose( self ) :
		RootGUI.dispose( self )

	def __initNotify( self, notify ):
		self.__pyRtNotify = CSRichText( notify.rtNotify )
		self.__pyRtNotify.text = ""

	def __rewardNotify( self ):
		self.remainTime -= 1.0
		timeStr = ""
		if self.remainTime < 60 and self.remainTime > 0:
			timeStr = "%d%s"% ( self.remainTime, ShareTexts.CHTIME_SECOND )
		if self.remainTime  >= 60:
			mins = int( self.remainTime/60 )
			secs = int( self.remainTime%60 )
			if secs > 0:
				timeStr = ShareTexts.CHTIME_MS %( mins, secs )
			else:
				timeStr = "%d%s"% ( mins, ShareTexts.CHTIME_MINUTE )
		orderStr = PL_Font.getSource( "%d"%self.order, fc = ( 255, 93, 19, 255 ) )
		timeStr = PL_Font.getSource( "%s"%timeStr, fc = ( 255, 93, 19, 255 ) )
		notifyStr = labelGather.getText( "FixRewardBox:notify", "waitForReward", orderStr, timeStr )
		self.__pyRtNotify.text = notifyStr
		if self.remainTime <= 0.0:
			Timer.cancel( self.notifyTimer )
			self.notifyTimer = 0
#			self.hide()

	def show( self, time, order ):
		"""
		显示距下一个奖励剩余时间
		"""
		Timer.cancel( self.notifyTimer )
		self.notifyTimer = 0
		self.order = order
		self.remainTime = time
		self.notifyTimer = Timer.addTimer( 0, 1, self.__rewardNotify )
		RootGUI.show( self )

	def hide( self ):
		"""
		隐藏提示面板
		"""
		Timer.cancel( self.notifyTimer )
		self.notifyTimer = 0
		self.__pyRtNotify.text = ""
		self.order = -1
		self.remainTime = 0.0
		RootGUI.hide( self )

	def onLeaveWorld( self ) :
		self.hide()

# -------------------------------------------------------------
from guis.tooluis.messagebox.MsgBox import OkBox
class FirstLogonBox( OkBox ):
	__instance = None
	def __init__( self ):
		OkBox.__init__( self )
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.__callback = None
		self.__callbackID = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __feedback( self, resultID ) :
		"""
		点击按钮后的返回
		"""
		self.__callback( resultID )

	def __del__(self):
		"""
		"""
		pass

	def dispose( self ) :
		OkBox.dispose( self )
		self.__callback = None
		FirstLogonBox.__instance=None
		self.removeFromMgr()
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, lastTime, msg, title, callback = None, pyOwner = None ) :
		self.__callback = callback
		if lastTime > 0:
			self.__callbackID = BigWorld.callback( lastTime, self.hide )
		OkBox.show( self, msg, title, self.__feedback, pyOwner )

	def hide( self ):
		BigWorld.cancelCallback( self.__callbackID )
		self.dispose()

	@staticmethod
	def instance():
		"""
		to get the exclusive instance of TongCancelOkBox
		"""
		if FirstLogonBox.__instance is None:
			FirstLogonBox.__instance = FirstLogonBox()
		return FirstLogonBox.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the exclusive instance of TongCancelOkBox
		"""
		return FirstLogonBox.__instance

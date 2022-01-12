# -*- coding: gb18030 -*-
#
# $Id: CopyInfo.py fangpengjun $

from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from LabelGather import labelGather
import event.EventCenter as ECenter
from Time import Time
import Timer
from Function import Functor
import copy
import csdefine
import csconst
from config.client.msgboxtexts import Datas as mbmsgs
from CircleHPBar import CircleHPBar
from CircleAngerBar import CircleAngerBar
from PlanePanel import PlanePanel
from YaoqiGourd import YaoqiGourd

SHOWN_INDEX_DICT_DEFAULT = { 0:-1, 1:-1, 2:-1, 3:-1, 4:-1, 5:-1, 6:-1, 7:-1, 8:-1, 9:-1, 10:-1, 11:-1, 12:-1, 13:-1,18:-1, 19:-1, 21:-1, 22:-1 }

class CopySpaceInfo( RootGUI ):

	def __init__( self ):
		panel = GUI.load( "guis/otheruis/copyinfo/panel.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.focus = False
		self.passelNum = ""
		self.preTimerID = 0
		self.leaveTime = 0.0
		self.monsterLevel = 0
		self.__triggers = {}
		self.__pyRtInfos = {}
		self.__viewInfos = [] #需要显示的信息
		self.__registerTriggers()
		self.__initPanel( panel )
		self.__shownIndexDict = copy.deepcopy( SHOWN_INDEX_DICT_DEFAULT )
		self.__shownNums = []
		self.__initTop = self.top

	def __initPanel( self, panel ):
		for name, item in panel.children:
			if name.startswith( "rt_" ):
				pyRtInfo = CSRichText( item )
				pyRtInfo.text = ""
				pyRtInfo.maxWidth = 200.0
				index = int( name.split( "_" )[1] )
				self.__pyRtInfos[index] = pyRtInfo

		self.__pyLolPanel = LolPanel( panel.lolPanel )
		self.__pyLolPanel.visible = False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_OPEN_COPY_INTERFACE"] = self.__onOpenInterFace		# 打开副本界面
		self.__triggers["EVT_ON_COPY_TIME_UPDATE"] = self.__onTimeUpdate			# 更新时间
		self.__triggers["EVT_ON_COPY_MONSTERS_UPDATE"] = self.__onMonsterUpdate		# 更新小怪数量
		self.__triggers["EVT_ON_COPY_PASSEL_UPDATE"] = self.__onPasselUpdate		# 小怪批次更新
		self.__triggers["EVT_ON_COPY_BOSS_UPDATE"]  = self.__onBossUpdate			# 更新boss数量
		self.__triggers["EVT_ON_COPY_MENGMENG_UPDATE"]  = self.__onMengmengUpdate	# 更新蒙蒙数量
		self.__triggers["EVT_ON_COPY_MOWENHU_UPDATE"]  = self.__onMoWenHuUpdate		# 更新剩余小怪数量
		self.__triggers["EVT_ON_COPY_ZHENGUIYING_UPDATE"]  = self.__onGuiyingUpdate	# 更新剩余真鬼影狮数量
		self.__triggers["EVT_ON_COPY_NEXT_LEVEL_TIME"]  = self.__onNextLevelTimeUpdate	# 下一波剩余时间
		self.__triggers["EVT_ON_CLOSE_COPY_INTERFACE"] = self.__onCloseInterFace	# 离开副本
		self.__triggers["EVT_ON_COPY_YAYU_HP_PRECENT"] = self.__onYayuHPChange	# 猰貐血量比例
		self.__triggers["EVT_ON_COPY_TREE_HP_PRECENT"] = self.__onTreeHPChange	# 神树血量比例
		self.__triggers["EVT_ON_COPY_CHALLENGE_GATE"] = self.__onChallengeGateChange	# 华山阵法当前层数
		self.__triggers["EVT_ON_COPY_TCHALLENGE_OWNER_NUM"] = self.__onTChallengeOwnerChange	# 组队擂台己方人数显示
		self.__triggers["EVT_ON_COPY_TCHALLENGE_ENEMY_NUM"] = self.__onTChallengeEnemyChange	# 组队擂台敌方人数显示
		self.__triggers["EVT_ON_COPY_POTENTIAL_FLAG_HP"] = self.__onPotentialFlagHPChange	# 潜能乱斗，圣魂旗血量
		self.__triggers["EVT_ON_SHOW_YXLMCOPY_MINIMAP"] = self.__onShowLoLMinMap
		self.__triggers["EVT_ON_HIDE_YXLMCOPY_MINIMAP"] = self.__onHideLoLMinMap
		self.__triggers["EVT_ON_BAOZANG_PVP_REQ_TIME"] = self.__onPVPReqTime				#宝藏副本申请时间
		self.__triggers["EVT_ON_BAOZANG_PVP_CANCEL_QUEUE"] = self.__onPVPCancelQueue		#宝藏副本取消排队
		self.__triggers["EVT_ON_COPY_YAYU_BATCH"] = self.__onYayuBatchChange				# 拯救猰貐当前阶段
		self.__triggers["EVT_ON_COPY_NEXT_BATCH_TIME"]  = self.__onNextBatchTimeUpdate		# 下一波怪物到达时间
		self.__triggers["EVT_ON_COPY_YAYU_NEW_HP"] = self.__onYayuNewHPChange				# 猰貐血量比例
		self.__triggers["EVT_ON_TRIGGER_CIRCLE_HP_BAR"] = self.__onTriggerCircleHPBar		# 触发圆环血条
		self.__triggers["EVT_ON_TRIGGER_CIRCLE_ANGER_BAR"] = self.__onTriggerCircleAngerBar	# 显示、隐藏环形怒气值
		self.__triggers["EVT_ON_COPY_TREE_ANGER_PRECENT"] = self.__onAngerChange		#斋南怒气值比例
		self.__triggers["EVT_ON_COPY_SHMZ_BOSS_UPDATE"] = self.__onCopySHMZBossUpdate	# 更新摄魂迷阵副本BOSS数量
		self.__triggers["EVT_ON_DANCECOPY_DATA_UPDATE_COMOBOPOINT"] = self.__onDanceCopyUpdateComboPoint	# 更新斗舞副本连击数
		self.__triggers["EVT_ON_DANCECOPY_DATA_UPDATE_TIMILIMIT"] = self.__onDanceCopyUpdateRemainTime	# 更新斗舞副本时间限制
		self.__triggers["EVT_ON_ENTER_PLANE"] = self.__onShowLeavePlaneButton	# 进入位面显示离开位面按钮
		self.__triggers["EVT_ON_LEAVE_PLANE"] = self.__onHideLeavePlaneButton	# 离开位面隐藏离开位面按钮
		self.__triggers["EVT_ON_TRIGGER_GOURD_YAOQI_BAR"] = self.__onTriggerYaoqiGourd		# 显示、隐藏炼妖炉妖气值
		self.__triggers["EVT_ON_MMP_YAOQI_PERCENT_CHANGED"] = self.__onYaoqiChange		# 炼妖壶妖气值
		self.__triggers["EVT_ON_COPY_MONSTER_WAVE_UPDATE"] = self.__onMonsterWaveUpdate		# 剩余怪物波数
		self.__triggers["EVT_ON_NPC_HP_UPDATE"] = self.__onNpcHPChange						# NPC剩余血量(百分比)
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	# ------------------------------------------------------------------
	def __onOpenInterFace( self ):
		if not self.visible:
			self.visible = True
		lolMinMap = rds.ruisMgr.lolMiniMap
		if lolMinMap.visible:
			self.top = lolMinMap.bottom + 20.0
		if self.__pyLolPanel.visible:
			self.__pyLolPanel.visible = False

	def __onTimeUpdate( self, startTime, persistTime ): #持续时间
		if persistTime == "-1": #为-1则没有时间限制
			index = self.__shownIndexDict[0]
			if index == -1:
				index = 0
			self.__pyRtInfos[index].text = ""
			if 0 in self.__shownNums:
				self.__shownNums.remove( 0 )
			self.__shownIndexDict[0] = -1
		else:
			endTime = float( startTime ) + float( persistTime )
			remainTime = endTime - Time().time()
			mins = int( remainTime/60 )
			secs= int( remainTime%60 )
			if remainTime < 0:
				mins = 0
				secs = 0
			if secs < 10 :
				timeText = PL_Font.getSource( "%d:0%d"%( mins, secs ), fc = ( 230, 227, 185, 255 ) )
			else:
				timeText = PL_Font.getSource( "%d:%d"%( mins, secs ), fc = ( 230, 227, 185, 255 ) )
			if not 0 in self.__shownNums:
				self.__shownNums.append( 0 )
			if self.__shownIndexDict[0] == -1:
				self.__shownIndexDict[0] = len( self.__shownNums ) - 1
			timeText = labelGather.getText( "CopySpaceInfo:main", "timeStr" ) % timeText
			self.__pyRtInfos[self.__shownIndexDict[0]].text = PL_Font.getSource( timeText, fc = ( 84, 194, 23, 255 ) )
			self.__viewInfos.append( self.__pyRtInfos[self.__shownIndexDict[0]] )

	def __onMonsterUpdate( self, monsterNum ):
		if not 1 in self.__shownNums:
			self.__shownNums.append( 1 )
		if self.__shownIndexDict[1] == -1:
			self.__shownIndexDict[1] = len( self.__shownNums ) - 1
		monsterText = PL_Font.getSource( str( monsterNum ), fc = ( 230, 227, 185, 255 ) )
		monsterText = labelGather.getText( "CopySpaceInfo:main", "mstStr" ) % monsterText
		self.__pyRtInfos[self.__shownIndexDict[1]].text = PL_Font.getSource( monsterText, fc = ( 232, 232, 32, 255 ) )

	def __onPasselUpdate( self, passelNum ): #小怪批次
		self.passelNum = passelNum
		if passelNum == "":
			if 2 in self.__shownNums:
				self.__shownNums.remove( 2 )
			self.__shownIndexDict[2] = -1
			return
		else:
			if not 2 in self.__shownNums:
				self.__shownNums.append( 2 )
			if self.__shownIndexDict[2] == -1:
				self.__shownIndexDict[2] = len( self.__shownNums ) - 1
			passelText = PL_Font.getSource( passelNum, fc = ( 230, 227, 185, 255 ) )
			passelText = labelGather.getText( "CopySpaceInfo:main", "mstGroupStr" ) % passelText
			self.__pyRtInfos[self.__shownIndexDict[2]].text = PL_Font.getSource( passelText, fc = ( 232, 232, 32, 255 ) )

	def __onBossUpdate( self, bossNum ):
		bossText = PL_Font.getSource( str( bossNum ), fc = ( 230, 227, 185, 255 ) )
		if not 3 in self.__shownNums:
			self.__shownNums.append( 3 )
		if self.__shownIndexDict[3] == -1:
			self.__shownIndexDict[3] = len( self.__shownNums ) - 1
		bossText = labelGather.getText( "CopySpaceInfo:main", "bossStr" ) % bossText
		self.__pyRtInfos[self.__shownIndexDict[3]].text = PL_Font.getSource( bossText, fc = ( 255, 2, 2, 255 ) )

	def __onMengmengUpdate( self, mengmengNum ):
		mengmengText = PL_Font.getSource( str( mengmengNum ), fc = ( 230, 227, 185, 255 ) )
		if not 4 in self.__shownNums:
			self.__shownNums.append( 4 )
		if self.__shownIndexDict[4] == -1:
			self.__shownIndexDict[4] = len( self.__shownNums ) - 1
		mengmengText = labelGather.getText( "CopySpaceInfo:main", "mengStr" ) % mengmengText
		self.__pyRtInfos[self.__shownIndexDict[4]].text = PL_Font.getSource( mengmengText, fc = ( 255, 2, 2, 255 ) )

	def __onMoWenHuUpdate( self, mowenhuNum ):
		mowenhuText = PL_Font.getSource( str( mowenhuNum ), fc = ( 230, 227, 185, 255 ) )
		if not 5 in self.__shownNums:
			self.__shownNums.append( 5 )
		if self.__shownIndexDict[5] == -1:
			self.__shownIndexDict[5] = len( self.__shownNums ) - 1
		mowenhuText = labelGather.getText( "CopySpaceInfo:main", "tigerStr" ) % mowenhuText
		self.__pyRtInfos[self.__shownIndexDict[5]].text = PL_Font.getSource( mowenhuText, fc = ( 255, 2, 2, 255 ) )

	def __onGuiyingUpdate( self, guiyingNum ):
		guiyingText = PL_Font.getSource( str( guiyingNum ), fc = ( 230, 227, 185, 255 ) )
		if not 6 in self.__shownNums:
			self.__shownNums.append( 6 )
		if self.__shownIndexDict[6] == -1:
			self.__shownIndexDict[6] = len( self.__shownNums ) - 1
		guiyingText = labelGather.getText( "CopySpaceInfo:main", "lionStr" ) % guiyingText
		self.__pyRtInfos[self.__shownIndexDict[6]].text = PL_Font.getSource( guiyingText, fc = ( 255, 2, 2, 255 ) )

	def __onNextLevelTimeUpdate( self, timeLeave ):
		"""
		这段代码似乎是针对某个副本专门设计的，非公用代码
		作者应该写上注释！gjx 2/4/13
		"""
		if len( timeLeave.split("_") ) == 4:
			monsterLevel,nextTime,serverTime,difficulty = timeLeave.split("_")
		else:
			monsterLevel,nextTime,serverTime = timeLeave.split("_")

		if self.monsterLevel == int( monsterLevel ):
			return

		self.monsterLevel = int( monsterLevel )

		if self.monsterLevel in [ 11,16,21 ] and int( difficulty ) == 0:
			if self.preTimerID != 0:
				Timer.cancel( self.preTimerID )
				self.preTimerID = 0
			if not 7 in self.__shownNums:
				self.__shownNums.append( 7 )
			if self.__shownIndexDict[7] == -1:
				self.__shownIndexDict[7] = len( self.__shownNums ) - 1
			hundunText = labelGather.getText( "CopySpaceInfo:main", "hundunStr" )
			self.__pyRtInfos[self.__shownIndexDict[7]].text = PL_Font.getSource( hundunText, fc = ( 255, 2, 2, 255 ) )
			return

		if self.monsterLevel == [ 16,21 ] and int( difficulty ) == 1:
			if self.preTimerID != 0:
				Timer.cancel( self.preTimerID )
				self.preTimerID = 0
			if not 7 in self.__shownNums:
				self.__shownNums.append( 7 )
			if self.__shownIndexDict[7] == -1:
				self.__shownIndexDict[7] = len( self.__shownNums ) - 1
			hundunText = labelGather.getText( "CopySpaceInfo:main", "hundunStr" )
			self.__pyRtInfos[self.__shownIndexDict[7]].text = PL_Font.getSource( hundunText, fc = ( 255, 2, 2, 255 ) )
			return

		if self.monsterLevel == 21 and int( difficulty ) == 2:
			if self.preTimerID != 0:
				Timer.cancel( self.preTimerID )
				self.preTimerID = 0
			if not 7 in self.__shownNums:
				self.__shownNums.append( 7 )
			if self.__shownIndexDict[7] == -1:
				self.__shownIndexDict[7] = len( self.__shownNums ) - 1
			hundunText = labelGather.getText( "CopySpaceInfo:main", "hundunStr" )
			self.__pyRtInfos[self.__shownIndexDict[7]].text = PL_Font.getSource( hundunText, fc = ( 255, 2, 2, 255 ) )
			return

		if self.preTimerID > 0:
			Timer.cancel( self.preTimerID )
			self.preTimerID = 0
		self.leaveTime = int( nextTime ) + int( serverTime ) - ( Time.time() )
		callback = Functor( self.__timeCountdown, 7 )
		self.preTimerID = Timer.addTimer( 0, 1, callback )

	def __timeCountdown( self, shownNum ):
		"""倒计时回调函数"""
		self.leaveTime -= 1.0
		if self.leaveTime > 0.0:
			min = int( self.leaveTime )/60
			sec = int( self.leaveTime )%60
			timeText = labelGather.getText( "CopySpaceInfo:main", "secMinStr" )
			timeText = PL_Font.getSource( timeText % ( min, sec ) , fc = ( 230, 227, 185, 255 ) )
			if not shownNum in self.__shownNums:
				self.__shownNums.append( shownNum )
			if self.__shownIndexDict[shownNum] == -1:
				self.__shownIndexDict[shownNum] = len( self.__shownNums ) - 1
			timeText = labelGather.getText( "CopySpaceInfo:main", "nextAttachStr" ) % timeText
			self.__pyRtInfos[self.__shownIndexDict[shownNum]].text = PL_Font.getSource( timeText, fc = ( 255, 2, 2, 255 ) )
		else:
			if self.preTimerID != 0:
				Timer.cancel( self.preTimerID )
				self.preTimerID = 0

	def __onYayuHPChange( self, hpp ):
		hpText = PL_Font.getSource( str( hpp )+"%", fc = ( 230, 227, 185, 255 ) )
		if not 8 in self.__shownNums:
			self.__shownNums.append( 8 )
		if self.__shownIndexDict[8] == -1:
			self.__shownIndexDict[8] = len( self.__shownNums ) - 1
		hpText = labelGather.getText( "CopySpaceInfo:main", "yayuHpStr" ) % hpText
		self.__pyRtInfos[self.__shownIndexDict[8]].text = PL_Font.getSource( hpText, fc = ( 255, 2, 2, 255 ) )
		CircleHPBar.cls_update(int(hpp))

	def __onYayuNewHPChange( self, hpp ):
		hpText = PL_Font.getSource( str( hpp )+"%", fc = ( 230, 227, 185, 255 ) )
		if not 13 in self.__shownNums:
			self.__shownNums.append( 13 )
		if self.__shownIndexDict[13] == -1:
			self.__shownIndexDict[13] = len( self.__shownNums ) - 1
		hpText = labelGather.getText( "CopySpaceInfo:main", "yayuHpStr" ) % hpText
		self.__pyRtInfos[self.__shownIndexDict[13]].text = PL_Font.getSource( hpText, fc = ( 255, 2, 2, 255 ) )
		CircleHPBar.cls_update(int(hpp))

	def __onTreeHPChange( self, hpp ):
		hpText = PL_Font.getSource( str( hpp )+"%", fc = ( 230, 227, 185, 255 ) )
		if not 8 in self.__shownNums:
			self.__shownNums.append( 8 )
		if self.__shownIndexDict[8] == -1:
			self.__shownIndexDict[8] = len( self.__shownNums ) - 1
		hpText = labelGather.getText( "CopySpaceInfo:main", "treeHpStr" ) % hpText
		self.__pyRtInfos[self.__shownIndexDict[8]].text = PL_Font.getSource( hpText, fc = ( 255, 2, 2, 255 ) )

	def __onChallengeGateChange( self, gate ):
		gateText = ""
		if int( gate ) == csconst.HUA_SHAN_PI_SHAN_GATE:
			gateText = PL_Font.getSource( mbmsgs[ 0x0ef1 ], fc = ( 230, 227, 185, 255 ) )
		else:
			gateText = PL_Font.getSource( str( gate ), fc = ( 230, 227, 185, 255 ) )

		if not 9 in self.__shownNums:
			self.__shownNums.append( 9 )

		if self.__shownIndexDict[9] == -1:
			self.__shownIndexDict[9] = len( self.__shownNums ) - 1

		gateText = labelGather.getText( "CopySpaceInfo:main", "challengeGate" ) % gateText
		self.__pyRtInfos[self.__shownIndexDict[9]].text = PL_Font.getSource( gateText, fc = (  232, 232, 32, 255 ) )

	def __onTChallengeOwnerChange( self, num ):
		numText = PL_Font.getSource( str( num ), fc = ( 230, 227, 185, 255 ) )

		if not 10 in self.__shownNums:
			self.__shownNums.append( 10 )

		if self.__shownIndexDict[10] == -1:
			self.__shownIndexDict[10] = len( self.__shownNums ) - 1

		numText = labelGather.getText( "CopySpaceInfo:main", "tchallengeOwner" ) % numText
		self.__pyRtInfos[self.__shownIndexDict[10]].text = PL_Font.getSource( numText, fc = (  2, 255, 2, 255 ) )

	def __onTChallengeEnemyChange( self, num ):
		numText = PL_Font.getSource( str( num ), fc = ( 230, 227, 185, 255 ) )

		if not 11 in self.__shownNums:
			self.__shownNums.append( 11 )

		if self.__shownIndexDict[11] == -1:
			self.__shownIndexDict[11] = len( self.__shownNums ) - 1

		numText = labelGather.getText( "CopySpaceInfo:main", "tchallengeEnemy" ) % numText
		self.__pyRtInfos[self.__shownIndexDict[11]].text = PL_Font.getSource( numText, fc = (  255, 2, 2, 255 ) )

	def __onPotentialFlagHPChange( self, hpp ):
		hpText = PL_Font.getSource( str( hpp )+"%", fc = ( 230, 227, 185, 255 ) )
		if not 12 in self.__shownNums:
			self.__shownNums.append( 12 )
		if self.__shownIndexDict[12] == -1:
			self.__shownIndexDict[12] = len( self.__shownNums ) - 1
		hpText = labelGather.getText( "CopySpaceInfo:main", "potentialFlagHP" ) % hpText
		self.__pyRtInfos[self.__shownIndexDict[12]].text = PL_Font.getSource( hpText, fc = ( 255, 2, 2, 255 ) )

	def __onShowLoLMinMap( self, spaceLabel ):
		"""
		显示英雄联盟副本小地图
		"""
		lolMinMap = rds.ruisMgr.lolMiniMap
		self.top = lolMinMap.bottom + 20.0

	def __onHideLoLMinMap( self ):
		"""
		隐藏英雄联盟副本小地图
		"""
		self.top = self.__initTop

	def __onPVPReqTime( self, startTime ):
		"""
		宝藏副本排队倒计时
		"""
		player = BigWorld.player()
		spaceType = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY )
		self.__pyLolPanel.visible = not int( spaceType ) in csconst.HAVE_SPACE_COPY_INTERFACE
		self.visible = True
		self.__pyLolPanel.onPVPReqTime( startTime )

	def __onPVPCancelQueue( self, isMatch ):
		"""
		宝藏副本排队取消
		"""
		self.__pyLolPanel.visible = isMatch
		self.__pyLolPanel.onPVPCancelQueue( isMatch )

	def __setPanelWidth( self ):
		maxWidth = max( pyPanel.width for pyPanel in self.__pyRtInfos.values() )
		self.width = maxWidth + 10.0

	def __onCloseInterFace( self ):
		for pyInfo in self.__pyRtInfos.itervalues():
			pyInfo.text = ""
		self.__shownIndexDict = copy.deepcopy( SHOWN_INDEX_DICT_DEFAULT )
		self.__shownNums = []
		self.top = self.__initTop
		if self.preTimerID > 0:
			Timer.cancel( self.preTimerID )
			self.preTimerID = 0
			self.leaveTime = 0.0
		timeCBID = self.__pyLolPanel.timeCBID
		self.visible =  timeCBID > 0
		self.__pyLolPanel.visible = timeCBID > 0
		CircleHPBar.cls_trigger( False )
		CircleAngerBar.cls_trigger( False )
		PlanePanel.cls_trigger(False)
		YaoqiGourd.cls_trigger( False )

	def __onYayuBatchChange( self, batch ):
		"""
		猰貐刷怪阶段
		"""
		if not 11 in self.__shownNums:
			self.__shownNums.append( 11 )
		if self.__shownIndexDict[11] == -1:
			self.__shownIndexDict[11] = len( self.__shownNums ) - 1
		if batch == "0":
			batchText = labelGather.getText( "CopySpaceInfo:main", "notReady" )
		else:
			batchNum, startTime = batch.split("_")
			passTime = int(Time.time() - float(startTime))
			passTimeStr = labelGather.getText( "CopySpaceInfo:main", "secMinStr", passTime/60, passTime%60 )
			batchText = "%s  %s" % ( batchNum, passTimeStr )
		batchText = PL_Font.getSource( batchText, fc = ( 255, 255, 255, 255 ) )
		batchText = labelGather.getText( "CopySpaceInfo:main", "yayuBatch", batchText )
		self.__pyRtInfos[self.__shownIndexDict[11]].text = PL_Font.getSource( batchText, fc = ( 255, 2, 2, 255 ) )

	def __onNextBatchTimeUpdate( self, timeLeave ):
		"""
		显示新版拯救猰貐下一批刷怪时间(测试用)
		"""
		if len( timeLeave.split("_") ) == 4:
			monsterLevel,nextTime,serverTime,difficulty = timeLeave.split("_")
		else:
			monsterLevel,nextTime,serverTime = timeLeave.split("_")

		if self.preTimerID > 0:
			Timer.cancel( self.preTimerID )
			self.preTimerID = 0
		self.leaveTime = int( nextTime ) + int( serverTime ) - ( Time.time() )
		callback = Functor( self.__timeCountdown, 12 )
		self.preTimerID = Timer.addTimer( 0, 1, callback )

	def __onTriggerCircleHPBar( self, visible ):
		CircleHPBar.cls_trigger( visible )

	def __onTriggerCircleAngerBar( self, isShow ):
		CircleAngerBar.cls_trigger( isShow )

	def __onAngerChange( self, anger ):
		CircleAngerBar.cls_update(int(anger))

	def __onCopySHMZBossUpdate( self, bossNum, totalBossNum ):
		"""
		更新摄魂迷阵BOSS数量
		"""
		bossText = PL_Font.getSource( str( bossNum ), fc = ( 230, 227, 185, 255 ) )
		totalBossText = PL_Font.getSource( str( totalBossNum ), fc = ( 230, 227, 185, 255 ) )
		if not 3 in self.__shownNums:
			self.__shownNums.append( 3 )
		if self.__shownIndexDict[3] == -1:
			self.__shownIndexDict[3] = len( self.__shownNums ) - 1
		bossText = labelGather.getText( "CopySpaceInfo:main", "copySHMZBossStr", bossText, totalBossText )
		self.__pyRtInfos[self.__shownIndexDict[3]].text = PL_Font.getSource( bossText, fc = ( 255, 2, 2, 255 ) )

	def __onDanceCopyUpdateComboPoint( self, comboPoint ):
		"""
		斗舞副本连击数
		"""
		comboPointText = PL_Font.getSource( "%02d"%( comboPoint ), fc = ( 230, 227, 185, 255 ) )
		if not 18 in self.__shownNums:
			self.__shownNums.append( 18 )
		if self.__shownIndexDict[18] == -1:
			self.__shownIndexDict[18] = len( self.__shownNums ) - 1
		comboPointText = labelGather.getText( "CopySpaceInfo:main", "comboPoint", comboPointText )
		self.__pyRtInfos[ self.__shownIndexDict[18]].text = PL_Font.getSource( comboPointText, fc = ( 255, 2, 2, 255 ) )

	def __onDanceCopyUpdateRemainTime( self, endTime ):
		"""
		斗舞副本等待回答时间
		"""
		remainTime =  endTime - Time().time()
		if remainTime <= 0:
			remainTime = 0
		remainTimeText = PL_Font.getSource( "%02d"%( remainTime ), fc = ( 230, 227, 185, 255 ) )
		if not 19 in self.__shownNums:
			self.__shownNums.append( 19 )
		if self.__shownIndexDict[19] == -1:
			self.__shownIndexDict[19] = len( self.__shownNums ) - 1
		remainTimeText = labelGather.getText( "CopySpaceInfo:main", "remainTime", remainTimeText )
		self.__pyRtInfos[ self.__shownIndexDict[19]].text = PL_Font.getSource( remainTimeText, fc = ( 255, 2, 2, 255 ) )

	def __onMonsterWaveUpdate( self, passelNum ): #剩余怪物波数
		self.passelNum = passelNum
		if passelNum == "":
			if 21 in self.__shownNums:
				self.__shownNums.remove( 21 )
			self.__shownIndexDict[21] = -1
			return
		else:
			if not 21 in self.__shownNums:
				self.__shownNums.append( 21 )
			if self.__shownIndexDict[21] == -1:
				self.__shownIndexDict[21] = len( self.__shownNums ) - 1
			passelText = PL_Font.getSource( passelNum, fc = ( 230, 227, 185, 255 ) )
			passelText = labelGather.getText( "CopySpaceInfo:main", "leaveWaveStr" ) % passelText
			self.__pyRtInfos[self.__shownIndexDict[21]].text = PL_Font.getSource( passelText, fc = ( 232, 232, 32, 255 ) )

	def __onNpcHPChange( self, hpp ):	# NPC剩余血量百分比
		hpText = PL_Font.getSource( str( hpp )+"%", fc = ( 230, 227, 185, 255 ) )
		if not 22 in self.__shownNums:
			self.__shownNums.append( 22 )
		if self.__shownIndexDict[22] == -1:
			self.__shownIndexDict[22] = len( self.__shownNums ) - 1
		hpText = labelGather.getText( "CopySpaceInfo:main", "npcHpStr" ) % hpText
		self.__pyRtInfos[self.__shownIndexDict[22]].text = PL_Font.getSource( hpText, fc = ( 255, 2, 2, 255 ) )
		CircleHPBar.cls_update(int(hpp))

	def __onShowLeavePlaneButton(self):
		"""
		显示离开位面按钮
		"""
		PlanePanel.cls_trigger(True)

	def __onHideLeavePlaneButton(self):
		"""
		隐藏离开位面按钮
		"""
		PlanePanel.cls_trigger(False)

	def __onTriggerYaoqiGourd( self, isShow ):
		"""
		是否显示妖气葫芦
		"""
		YaoqiGourd.cls_trigger( isShow )

	def __onYaoqiChange( self, percent ):
		"""
		更新妖气值
		"""
		YaoqiGourd.cls_update( percent )
		YaoqiGourd.cls_trigger( True )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		for pyInfo in self.__pyRtInfos.itervalues():
			pyInfo.text = ""
		self.visible = False
		self.__shownIndexDict = copy.deepcopy( SHOWN_INDEX_DICT_DEFAULT )
		self.__shownNums = []
		self.top = self.__initTop
		Timer.cancel( self.preTimerID )
		self.preTimerID = 0
		self.leaveTime = 0.0

# ----------------------------------------------------------------------------------------------

class LolPanel( PyGUI ):
	"""
	宝藏副本匹配等待时间
	"""
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyRtTime = CSRichText( panel.rtTime )
		self.__pyRtTime.align = "R"
		self.__pyRtTime.text = ""

		self.__pyBtnCancel = HButtonEx( panel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "LolPVP:main", "btnCancel" )
		self.__lastTime = 0.0
		self.__timeCBID = 0

	def onPVPReqTime( self, startTime ):
		"""
		宝藏副本排队倒计时
		"""
		if self.__timeCBID:
			Timer.cancel( self.__timeCBID )
			self.__timeCBID = 0
		self.__lastTime = 0.0
		self.__timeCBID = Timer.addTimer( 0, 1, self.__timing )

	def onPVPCancelQueue( self, isMatch ):
		"""
		取消匹配
		"""
		self.__pyRtTime.text = ""
		if self.__timeCBID:
			Timer.cancel( self.__timeCBID )
			self.__timeCBID = 0
		self.__lastTime = 0.0
		self.visible = False

	def __timing( self ):
		"""
		倒计时
		"""
		self.__lastTime += 1.0
		if self.__lastTime >= 0.0:
			min = int( self.__lastTime )/60
			sec = int( self.__lastTime )%60
			timeText = "%02d:%02d"%( min, sec )
			timeText = PL_Font.getSource( timeText , fc = ( 230, 227, 185, 255 ) )
			timeText = labelGather.getText( "CopySpaceInfo:main", "matchTime" ) % timeText
			self.__pyRtTime.text = PL_Font.getSource( timeText, fc = ( 84, 194, 23, 255 ) )

	def __onCancel( self, pyBtn ):
		"""
		主动取消排队
		"""
		if pyBtn is None:return
		p = BigWorld.player()
		if p.isRequestCampYingXiongCopy:
			BigWorld.player().cell.yingXiongCampCancel()
		else:
			BigWorld.player().cell.baoZangPVPcancel()

	def _getTimeCBID( self ):

		return self.__timeCBID

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	timeCBID = property( _getTimeCBID,  )

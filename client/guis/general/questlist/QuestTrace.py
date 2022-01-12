# -*- coding: gb18030 -*-
#
# $Id: QuestTrace.py,v 1.22 2008-09-05 08:30:47 pengju Exp $

import bwdebug
import csdefine
import csstatus
import Const
import weakref
import ResMgr
import Timer
import GUIFacade
from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.common.WndResizer import WndResizer
from guis.controls.Label import Label
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel
from ItemsFactory import ObjectItem
from guis.controls.Button import Button
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Link import PL_Link
from config.client.labels import QuestList as lbs_QuestList
from config.client.ForbidLinkNPCID import Datas as forbidNPCs
from guis.OpIndicatorObj import OpIndicatorObj
from NPCDatasMgr import npcDatasMgr
import math

MAX_TRACE_QUEST_NUM = 20					# 策划要求任务追踪无次数限制，这里先把追踪限制改为最大可接任务数
ROW_DISTANCE = 3.0							# 行距
MAX_WIDTH = 240								# 窗口最大宽度，任务描述超过此宽度将自动换行

COLORS = {
	1: ( 11, 227, 174 ),	# 标题颜色
	2: ( 255, 243, 189 ),	# 普通字颜色
	}


class QuestTraceWindow( RootGUI, OpIndicatorObj ):
	"""
	任务追踪窗口
	"""
	__cc_width_range		= ( 200, 260 )
	__cc_height_range		= ( 310, 350 )

	__init_quests = {csdefine.ENTITY_CAMP_TAOISM:[20101500, 20101574, 20101575, 20101576],
					csdefine.ENTITY_CAMP_DEMON:[20101521, 20101700, 20101710, 20101691],
						}	#第一个任务需要追踪

	__cc_quest_config	= "config/client/help/QuestData.xml"		# 等级与可做任务的配置，这里主要读取交任务的NPC
	def __init__( self, wnd, pyBinder ):
		"""
		"""
		RootGUI.__init__( self, wnd )
		OpIndicatorObj.__init__( self )
		self.focus = False
		self.escHide_ = False
		self.posZSegment = ZSegs.L4
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.TQuestDict = {}				# 当前显示在窗口上的任务数据字典，key为questID，value为[ 任务名字Label, 任务条件Label ]
		self.TQuestIDList = []				# 当前显示在窗口上的任务id列表，根据这个顺序显示和删除TQuestDict的数据
		self.bottomHeight = 0.0					# 当前显示的任务Label最低位置
		self.__traceTimerID = 0				# 限时任务追踪计时器
		self.__questTimerID = 0				# 距离显示追踪计时器
		self.__top = self.top				# 记住顶部，用于隐藏再显示后恢复位置！
		self.__right = self.right			# 记住右边，用于隐藏再显示后恢复位置！
		self.__triggers = {}
		self.__pyBinder = weakref.ref( pyBinder )
		self.__cfgPath = ""
		self.__cfgSect = None
		self.isLogInited = False

		self.__initialize( wnd )
		self.__registerTriggers()

	def __initialize( self, wnd ) :
		labelGather.setLabel( wnd.titlePanel.lbText, "QuestHelp:QuestTrace", "lbTitle" )
		self.__titlePanel = Label( wnd.titlePanel )	# 标题
		self.__titlePanel.onLMouseDown.bind( self.__onLMouseDownTitle )

		self.__pyItemsPanel = ItemsPanel( wnd.contentPanel.clipPanel, wnd.contentPanel.sbar )

		self.__pyItemsPanel.itemPerScroll = False
		self.__pyItemsPanel.sbarState = ScrollBarST.AUTO
		self.__pyItemsPanel.perScroll = 30
		self.__pyItemsPanel.onScrollChanged.bind( self.__hideOperationTips ) # 滚动条滚动时隐藏互动型提示
		self.__pyItemsPanel.h_dockStyle = "HFILL"
		self.__pyItemsPanel.v_dockStyle = "VFILL"

		self.__contentPanel = wnd.contentPanel

		self.__pyUpBtn = Button( wnd.titlePanel.upBtn )
		self.__pyUpBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUpBtn.onLClick.bind( self.__onContentHide )
		self.__pyUpBtn.visible = True

		self.__pyDownBtn = Button( wnd.titlePanel.downBtn )
		self.__pyDownBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDownBtn.onLClick.bind( self.__onContentShow )
		self.__pyDownBtn.visible = False

		self.__pyUpBtn_1 = Button( wnd.titlePanel.upBtn_1 )
		self.__pyUpBtn_1.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUpBtn_1.onLClick.bind( self.__onSortByNotComplete )
		self.__pyUpBtn_1.visible = False

		self.__pyDownBtn_1 = Button( wnd.titlePanel.downBtn_1 )
		self.__pyDownBtn_1.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyDownBtn_1.onLClick.bind( self.__onSortByIsComplete )
		self.__pyDownBtn_1.visible = False

		self.__pyCloseBtn = Button( wnd.titlePanel.closeBtn )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onAbandonTrace )

		boards = {}
		boards["l"] = wnd.resizeHit_l
		boards["t"] = wnd.resizeHit_t
		boards["lt"] = wnd.resizeHit_lt
		self.__pyWndResizer = WndResizer( self, boards )
		self.__pyWndResizer.setWidthRange( self.__cc_width_range )
		self.__pyWndResizer.setHeightRange( self.__cc_height_range )
		self.__pyWndResizer.autoReisize = True
		self.__pyWndResizer.onBeginResized.bind( self.__hideOperationTips )
		self.__pyWndResizer.onEndResized.bind( self.__onEndResize )
		self.__pyWndResizer.onResizing.bind( self.__onResizing )

		self.width = self.__cc_width_range[0]
		self.height = self.__cc_height_range[0]

	def __registerTriggers( self ):
		self.__triggers[ "EVT_ON_QUEST_LOG_REMOVED" ] = self.__abandonQuest
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onLevelChange
		self.__triggers["EVT_ON_SHOW_TRACE_OPERATION_TIPS"] = self.__showOperationTips # 显示任务追踪提示帮助
		self.__triggers["EVT_ON_INDICATE_QUEST_TRACE"] = self.__showOperateIndication	 # 显示任务追踪提示帮助
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	def __searchAcceptTraceByQuestId( self, questId, condIndex ):
		"""
		获取追踪
		"""
		if not self.visible: return None
		pyConditions = self.TQuestDict.get( questId, None )
		if pyConditions is None:return None
		if condIndex <= 0:
			if pyConditions:
				for pyCondition in pyConditions[1:]:
					if pyCondition.text.find( "@L" ) != -1:
						if pyCondition.getTopToUI( self.__pyItemsPanel ) < 0:
							self.__pyItemsPanel.scrollRate = 0.0
						elif pyCondition.getTopToUI( self.__pyItemsPanel ) > self.__pyItemsPanel.height:
							self.__pyItemsPanel.scrollRate = 1.0
						rtPanel = pyCondition.rtPanel
						if rtPanel.text != "":
							return rtPanel
						return pyCondition
		else:
			for pyCondition in pyConditions[1:]:
					if pyCondition.condIndex == condIndex:
						if pyCondition.getTopToUI( self.__pyItemsPanel ) < 0:
							self.__pyItemsPanel.scrollRate = 0.0
						elif pyCondition.getTopToUI( self.__pyItemsPanel ) > self.__pyItemsPanel.height:
							self.__pyItemsPanel.scrollRate = 1.0
						rtPanel = pyCondition.rtPanel
						if rtPanel.text != "":
							return rtPanel
						return pyCondition
		return None

	def __searchCompeleteTraceByQuestId( self, questId, condIndex ):
		if not self.visible: return None
		pyConditions = self.TQuestDict.get( questId, None )
		if pyConditions :
			if len( pyConditions ) == 1 :
				return pyConditions[0]
			elif len( pyConditions ) == 2 :
				index = pyConditions[1].condIndex
				if index == 0 or index == condIndex :
					return pyConditions[1]
			else :
				for pyCondition in pyConditions[1:]:
					if pyCondition.condIndex == condIndex:
						if pyCondition.getTopToUI( self.__pyItemsPanel ) < 0:
							self.__pyItemsPanel.scrollRate = 0.0
						elif pyCondition.getTopToUI( self.__pyItemsPanel ) > self.__pyItemsPanel.height:
							self.__pyItemsPanel.scrollRate = 1.0
						rtPanel = pyCondition.rtPanel
						if rtPanel.text != "":
							return rtPanel
						return pyCondition
		return None

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __isTraceQuest( self, questID ):
		"""
		是否可追踪的任务，是则返回True
		"""
		typeList = GUIFacade.getTaskGoalType( questID )
		for i in typeList:
			if i in Const.TRACE_QUEST_TYPE:
				return True
		return True

	def __addTraceQuest( self, questID ):
		"""
		添加追踪任务
		"""
		self.show()
		if self.__cfgPath != "" :
			ResMgr.purge( self.__cfgPath )
		accountName = rds.gameMgr.getCurrAccountInfo()["accountName"]
		roleName = rds.gameMgr.getCurrRoleHexName()
		self.__cfgPath = "account/%s/%s/questtrace.xml"%( accountName, roleName )
		self.__cfgSect = ResMgr.openSection( self.__cfgPath )
		if self.__cfgSect is None:
			self.__cfgSect = ResMgr.openSection( self.__cfgPath, True )
			self.__cfgSect.createSection( "quests" )
			self.__cfgSect.writeString( "quests", "" )
			self.__cfgSect.save()
			ResMgr.purge( self.__cfgPath )
		self.__titlePanel.visible = len( self.TQuestIDList ) > 0
		self.__pyWndResizer.visible = True
		if not self.isAddSucced( questID ):
			return
		self.TQuestIDList.append( questID )
		title = TitleItem()
		self.__pyItemsPanel.addItem( title )
		title.left = 0.0
		typeID, typeStr = GUIFacade.getQuestTypeStr( questID )
		text= ( lbs_QuestList.QuestTrace_questType % typeStr[:4] ) + GUIFacade.getQuestLogTitle( questID )[ 0 ] # 截取任务类型的前两个字
		newText = PL_Font.getSource( text, fc = COLORS[1] )
		newText += PL_Font.getSource( fc = COLORS[1] )				# 任务标题
		title.text = newText
		title.questID = questID
		self.TQuestDict[ questID ] = [ title ]
		if self.__checkIsComplete( questID ): # 如果是已经完成的任务
			title.onQuestCompleted()
			tText = labelGather.getText( "QuestHelp:QuestTrace", "fulfillText" )
			cText = PL_Font.getSource( tText, fc = COLORS[1] )
			title.text += cText
		self.TQuestDict[ questID ] += self.__getNewTraceItem( questID )

		# 增加“交任务”超链接，计时任务完成时还有时间在跳转，交任务只能放到最后加入
		if self.__checkCancommit( questID ): # 如果是已经完成的任务
			conditionPanel = self.__getText( questID, 0, True )
			self.TQuestDict[ questID ].append( conditionPanel )
		self.__reSort()														# 垂直方向排列
		self.__checkTraceTimer()
		self.__checkQuestTimer()

	def isAddSucced( self, questID ):
		isSucced = False
		player = BigWorld.player()
		if self.isLogInited: #任务初始化完成
			if not questID in self.getLocalTrace():
				tcQuests = self.getLocalTrace().append( questID )
				qtStr = ""
				for tcQuest in self.TQuestIDList:
					qtStr += "%d|"%tcQuest
				qtStr += "%d|"%questID
				self.__cfgSect.writeString( "quests", qtStr )
				self.__cfgSect.save()
				ResMgr.purge( self.__cfgPath )
				isSucced = True
		else: #未初始化完成
			camp = player.getCamp()
			quests = self.__init_quests.get( camp, [] )
			if questID in quests: #第一个任务写配置,在任务日志初始化之前就发到客户端
				qtStr = "%d|"%questID
				self.__cfgSect.writeString( "quests", qtStr )
				self.__cfgSect.save()
				ResMgr.purge( self.__cfgPath )
				isSucced = True
			if questID in self.getLocalTrace():
				isSucced = True
		return isSucced

	def __delQuestTrace( self, questID ):
		"""
		删除任务追踪
		"""
		items = self.TQuestDict.get( questID, None )
		if items is None:return
		for item in items:
			self.__pyItemsPanel.removeItem( item )
		self.TQuestIDList.remove( questID )
		del self.TQuestDict[ questID ]
		if questID in self.getLocalTrace():
			qtStr = ""
			for tcQuest in self.TQuestIDList:
				qtStr += "%d|"%tcQuest
			self.__cfgSect.writeString( "quests", qtStr )
			self.__cfgSect.save()
			ResMgr.purge( self.__cfgPath )
		if len( self.TQuestIDList ) <= 0:
			self.hide()
		self.__reSort()											# 重新排列追踪任务
		self.__checkTraceTimer()
		self.__checkQuestTimer()

	def __onQtLogInited( self ):
		"""
		任务日志初始化完成
		"""
		self.__isLogInited = True

	def __reSort( self ):
		"""
		重新在窗口排列追踪任务
		"""
		self.__titlePanel.visible = len( self.TQuestIDList ) > 0
		self.bottomHeight = 0.0
		maxWidth = self.width - self.__pyItemsPanel.pySBar.width - 5.0
		for questID in self.TQuestIDList:						# 重新排列控件
			pyItems = self.TQuestDict[ questID ]
			pyTitle = pyItems[0]								# 获取任务标题
			pyTitle.top = self.bottomHeight						# 设定任务的起始位置
			pyTitle.rtMaxWidth = maxWidth
			self.bottomHeight = pyTitle.bottom
			for index in range( 1, len( pyItems ) ):			# 排列任务内容
				item = pyItems[index]
				item.rtMaxWidth = maxWidth
				item.top = self.bottomHeight					# 设定内容项之间的间隔
				self.bottomHeight = item.bottom
		self.__titlePanel.width = self.width
		self.__pyItemsPanel.pySBar.right = self.width
		self.__pyCloseBtn.right = self.__titlePanel.right - 2
		self.__pyItemsPanel.wholeLen = self.bottomHeight
		self.relocateIndications()

	def __onTraceStateChagned( self, questID ) :
		"""
		任务条件的状态改变
		"""
		if not questID in self.TQuestIDList : return
		self.__updateQuest( questID )

	def __refreshQuestTimer( self, questID ):
		"""
		更新距离显示
		"""
		if not self.TQuestDict.has_key( questID ):
			DEBUG_MSG( "没有追踪此任务。" )
			return

		questItemList = []
		questText = "[" + labelGather.getText( "QuestHelp:QuestTrace", "distance" )
		for item in self.TQuestDict[ questID ]:
			if item.text.find( questText ) != -1:
				questItemList.append( item )
		if not len( questItemList ): return
		for questItem in questItemList:
			text = questItem.text
			lt = text.split( "@F" )
			d = lt[len( lt )-1]
			npcID = questItem.npcID
			itemID = questItem.itemID
			task = GUIFacade.getTaskFromIndex( questID, questItem.condIndex )
			if task and task.getType() in [ csdefine.QUEST_OBJECTIVE_CAMP_KILL, csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER,\
								 csdefine.QUEST_OBJECTIVE_CAMPACT_TALK, csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM ]:
				conditionText = text.replace( "@F" + d, self.__getDiffSpaceDistance( npcID, questID, questItem.condIndex  ) )
			else:
				conditionText = text.replace( "@F" + d, self.__getDistance( npcID ) )
			if itemID == "":
				questItem.updateCondition( conditionText, npcID, questID )
			else:
				questItem.updateCondition( conditionText, npcID, questID, itemID )

	def __updateQuest( self, questID ):
		"""
		更新任务内容
		"""
		if not self.TQuestDict.has_key( questID ):
			DEBUG_MSG( "没有追踪此任务。" )
			return

		temp = self.TQuestDict[ questID ]
		for i in xrange( len( temp ) - 1 ):
			self.__pyItemsPanel.removeItem( temp[ i + 1 ] )

		tempList = [ self.TQuestDict[ questID ][ 0 ] ]			# 名字不变
		if self.__checkIsComplete( questID ): # 如果是已经完成的任务
			if tempList[0].text.find( labelGather.getText( "QuestHelp:QuestTrace", "fulfillText" ) ) == -1:
				text = labelGather.getText( "QuestHelp:QuestTrace", "fulfillText" )
				newText = PL_Font.getSource( text, fc = COLORS[1] )
				tempList[0].text += newText
				tempList[0].onQuestCompleted()
		else:
			if tempList[0].text.find( labelGather.getText( "QuestHelp:QuestTrace", "fulfillText" ) ) != -1: # 如果是从完成转为未完成，则改变标签
				tempList[0].text = tempList[0].text.replace( labelGather.getText( "QuestHelp:QuestTrace", "fulfillText" ), "" )
				tempList[0].onQuestIncompleted()
		tempList += self.__getNewTraceItem( questID )

		# 增加“交任务”超链接，计时任务完成时还有时间在跳转，交任务只能放到最后加入
		if self.__checkCancommit( questID ):
			conditionPanel = self.__getText( questID, 0, True )
			tempList.append( conditionPanel )

		self.TQuestDict[ questID ] = tempList
		self.__reSort()

	def __getNewTraceItem( self, questID ):
		"""
		获取最新的任务条件
		"""
		tempList = []
		args = GUIFacade.getObjectiveDetail( questID )			# 重新设置任务条件信息放到原来的位置
		maxCompleteCount = len( args )
		completeCount = 0
		args.sort( key = lambda e : e[1], reverse = False ) # 任务条件按index排序显示

		#修改任务失败时的追踪显示add by wuxo 2011-12-26
		#获取当前需要显示的那个任务目标（任务目标排序显示add by wuxo 2012-4-16）
		questOrders = []	#排序的任务目标索引
		questIdx = []  #未完成的目标索引在questOrders中的索引
		for taskType, idx, title, tag, isCollapsed, isComplete, itemID, showOrder, npcID in args:
			if isCollapsed:
				conditionPanel = self.__getText( questID, idx )
				tText = labelGather.getText( "QuestHelp:QuestTrace", "failQuest" )
				conditionText = PL_Font.getSource( "--%s"%tText, fc = (255,0,0,255) )
				conditionPanel.updateCondition( conditionText, npcID, questID )
				tempList  = [conditionPanel]
				return tempList
			if str( idx ) in showOrder:
				if len(questOrders) == 0:
					questOrderStr =  showOrder.split(";")
					questOrders = [ int(i) for i in questOrderStr ]
				if not isComplete:
					questIdx.append( questOrders.index( idx ))

		showQuest = 0 #排序显示的任务目标add by wuxo 2012-4-16
		questIdx.sort()
		if len( questIdx ) > 0:
			showQuest = questOrders[questIdx[0]]

		for taskType, idx, title, tag, isCollapsed, isComplete, itemID, showOrder, npcID in args:
			if str( idx ) in showOrder:
				if showQuest != idx:
					continue
			if isComplete: continue # 完成的任务条件不显示
			conditionPanel = self.__getText( questID, idx )
			color = COLORS[2]
			if not tag: # tag 有可能为空
				text = "--%s" % title
			elif isCollapsed:
				tag = PL_Font.getSource( tag, fc =( 255, 0, 0 ))
				text = "--%s(%s)" % ( title, tag )

			else:
				tag = PL_Font.getSource( tag, fc =( 255, 0, 0 ))
				text = "--%s:(%s)" % ( title, tag )
			conditionText = text
			if npcID:	# NPC需要显示距离
				if taskType in [ csdefine.QUEST_OBJECTIVE_CAMP_KILL, csdefine.QUEST_OBJECTIVE_CAMPACT_DELIVER,\
								 csdefine.QUEST_OBJECTIVE_CAMPACT_TALK, csdefine.QUEST_OBJECTIVE_CAMPACT_EVENT_USE_ITEM ]:
					conditionText = text + self.__getDiffSpaceDistance( npcID, questID, idx )
				else:
					conditionText = text + self.__getDistance( npcID )
			if itemID == "":
				conditionPanel.updateCondition( conditionText, npcID, questID )
			else:
				conditionPanel.updateCondition( conditionText, npcID, questID, itemID )
			tempList.append( conditionPanel )
		return tempList

	def __getDistance( self, npcID ):
		"""
		获取与玩家的距离
		"""
		if npcID == "": return ""
		player = BigWorld.player()
		spaceData = npcDatasMgr.getNPCSpaceLabel( npcID )
		pos = npcDatasMgr.getNPCPosition( npcID )
		if pos == None or pos == ( 0,0,0 ) or spaceData[0] != player.getSpaceLabel():
			disStr = labelGather.getText( "QuestHelp:QuestTrace", "distanceUnknow" )
			return "@F{fc=c3}[%s]" % disStr	 # 红色显示
		dis = pos.distTo( player.position )
		unit = "m"
		if dis >= 1000.0:
			dis = int( math.floor( dis/1000 ) )
			unit = "km"
		else:
			dis = int( math.floor( dis ) )
		dis = str( dis ) + unit
		disStr = labelGather.getText( "QuestHelp:QuestTrace", "distance" )
		return "@F{fc=c6}[%s]" % ( disStr + dis )	# 黄色显示
		
	def __getDiffSpaceDistance( self, npcID, questID, idx ):
		"""
		获取特定地图特定ID的目标与玩家的距离，目前只适用于阵营活动任务
		"""
		if npcID == "": return ""
		task = GUIFacade.getTaskFromIndex( questID, idx )
		spaceLabel = task.getSpaceLabel()
		if spaceLabel == "":
			return self.__getDistance( npcID )
		player = BigWorld.player()
		pos = rds.npcDatasMgr.getNPCPosition( npcID, spaceLabel )
		if pos == None or pos == ( 0,0,0 ) or spaceLabel != player.getSpaceLabel():
			disStr = labelGather.getText( "QuestHelp:QuestTrace", "distanceUnknow" )
			return "@F{fc=c3}[%s]" % disStr	 # 红色显示
		dis = pos.distTo( player.position )
		unit = "m"
		if dis >= 1000.0:
			dis = int( math.floor( dis/1000 ) )
			unit = "km"
		else:
			dis = int( math.floor( dis ) )
		dis = str( dis ) + unit
		disStr = labelGather.getText( "QuestHelp:QuestTrace", "distance" )
		return "@F{fc=c6}[%s]" % ( disStr + dis )	# 黄色显示

	def __updateTraceTimer( self, questID ):
		"""
		更新计时任务的时间
		"""
		args = GUIFacade.getObjectiveDetail( questID )
		questText = labelGather.getText( "QTTask:main", "miTimeRemain" )
		questItem = None
		for item in self.TQuestDict[ questID ]:
			if item.text.find( questText ) != -1:
				questItem = item
		if questItem:
			for taskType, index, title, tag, isCollapsed, isComplete, itemID, showOrder, npcID in args:
				if isCollapsed:
					self.__onTraceStateChagned( questID )
				else:
					if title.find( questText ) != -1:
						color = COLORS[2]
						text = "--%s:(%s)" % ( title, tag )
						questItem.text = PL_Font.getSource( text, fc = color )

	def __getText( self, questID, index, isFinishText = False ):
		"""
		获取经过处理的文字
		"""
		taskPanel = ConditionItem( index )
		taskPanel.rtPanel.onComponentLClick.bind( self.__hideOperationTips )
		self.__pyItemsPanel.addItem( taskPanel )

		# 是否获取“交任务”超链接
		if isFinishText: #
			ltext = PL_Font.getSource( "--", fc = COLORS[2] )
			npcClassName = self.__getCompleteNPC( questID )
			if npcClassName != "" and npcClassName not in [item["npcID"] for item in forbidNPCs]:
				linkMark = "goto:%s" % npcClassName
				taskText = ltext + PL_Link.getSource( labelGather.getText( "QuestHelp:QuestTrace", "dealQuest" ), linkMark, cfc = "c4", hfc = "c3" )	# 将怪物信息转化为超链接文本
				taskText += self.__getDistance( npcClassName )
			else:
				taskText = ltext + PL_Font.getSource( labelGather.getText( "QuestHelp:QuestTrace", "dealQuest" ), fc = COLORS[2] )
			taskPanel.updateCondition( taskText, npcClassName, questID )
		return taskPanel

	def __abandonQuest( self, questID ):
		"""
		放弃任务，删除相应的追踪任务
		"""
		if not self.TQuestDict.has_key( questID ):
			DEBUG_MSG( "没有追踪此任务。" )
			return

		self.__delQuestTrace( questID )

	def __onEndResize( self, pyBoard ):
		"""
		结束改变宽度时调用
		"""
		width = self.width
		self.__contentPanel.width = self.__titlePanel.width = width
		self.__pyItemsPanel.width = width - self.__pyItemsPanel.pySBar.width
		self.__pyItemsPanel.pySBar.right = self.__pyItemsPanel.right + self.__pyItemsPanel.pySBar.width
		self.__pyCloseBtn.right = self.__titlePanel.right - 2.0
		self.__pyUpBtn_1.right = self.__titlePanel.right - 20.0
		self.__pyDownBtn_1.right = self.__titlePanel.right - 20.0
		self.__pyItemsPanel.height = self.__contentPanel.height = self.height - self.__titlePanel.bottom
		pySBar = self.__pyItemsPanel.pySBar
		pySBar.height = self.__pyItemsPanel.height
		incTop = pySBar.pyIncBtn_.top + 3.0
		elements = pySBar.getGui().elements
		elem_t = elements["frm_t"]
		elem_bg = elements["frm_bg"]
		elem_b = elements["frm_b"]
		elem_b.position.y = incTop - elem_b.size.y
		elem_bg.size.y = elem_b.position.y - elem_bg.position.y
		self.__reSort()

	def __resortItems( self, maxWidth ):
		"""
		重新排列任务列表
		"""
		self.bottomHeight = 0.0
		for questID in self.TQuestIDList:
			pyItems = self.TQuestDict[ questID ]
			pyTitle = pyItems[0]
			pyTitle.top = self.bottomHeight
			pyTitle.rtMaxWidth = min( MAX_WIDTH - 20.0, maxWidth )
			self.bottomHeight = pyTitle.bottom
			for index in range( 1, len( pyItems ) ):
				item = pyItems[index]
				item.top = self.bottomHeight
				item.rtMaxWidth = maxWidth
				self.bottomHeight = item.bottom
		self.__pyItemsPanel.wholeLen = self.bottomHeight

	def __onResizing( self, pyBoard, x, y ):
		"""
		拉伸过程中
		"""
		self.__onEndResize( pyBoard )

	def __checkTraceTimer( self ):
		"""
		检测限时任务
		"""
		if not self.visible:
			self.__closeTimer()
			return
		for questID in self.TQuestDict.keys() :
			if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TIME ) : 	# 找到限时任务
				if self.__traceTimerID == 0 :
					self.__traceTimerID = Timer.addTimer( 0, 1, self.__persistTrace )
				break
		else :							# 如果循环不是因break而终止，意味着没有限时任务追踪，关闭计时器
			self.__closeTimer()

	def __persistTrace( self ) :
		for questID in self.TQuestDict.keys() :
			if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_TIME ) : 	# 找到限时任务
				self.__updateTraceTimer( questID )

	def __closeTimer( self ) :
		if self.__traceTimerID != 0 :
			Timer.cancel( self.__traceTimerID )
			self.__traceTimerID = 0

	def __checkQuestTimer( self ):
		"""
		检测距离显示
		"""
		if not self.visible:
			self.__closeQuestTimer()
			return
		if self.__questTimerID == 0:
			self.__questTimerID = Timer.addTimer( 0, 3, self.__refreshQuest )

	def __refreshQuest( self ):
		"""
		"""
		for questID in self.TQuestDict.keys():
			self.__refreshQuestTimer( questID )

	def __closeQuestTimer( self ):
		"""
		"""
		if self.__questTimerID != 0 :
			Timer.cancel( self.__questTimerID )
			self.__questTimerID = 0

	def __getCompleteNPC( self, questID ) :
		"""
		获取交任务的NPC的className
		"""
		className = ""
		sect = Language.openConfigSection( self.__cc_quest_config )
		if sect is None :
			ERROR_MSG( "open %s fail, check whether it is exist please!" % self.__cc_quest_config )
			return className
		for tag, subSect in sect.items() :
			for tags, subSects in subSect.items() :
				if subSects.readInt( "id" ) == questID :
					className = subSects.readString( "CnpcClassName" )
		return className

	def __checkIsComplete( self, questID ):
		"""
		检查任务是否已完成
		"""
		args = GUIFacade.getObjectiveDetail( questID )
		for taskType, index, title, tag, isCollapsed, isComplete, itemID ,showOrder, npcID in args:
			if isCollapsed: # 任务时间到
				return False
			if taskType == csdefine.QUEST_OBJECTIVE_DART_KILL and isComplete: # 劫镖任务强制完成
				return True
			if taskType != csdefine.QUEST_OBJECTIVE_TIME and not isComplete: # 不属于时间限制类型的未完成的任务
				return False
		return True
		
	def __checkCancommit( self, questID ):
		"""
		检查任务是否可以提交了（和完成不同，有些任务完成了一个任务目标也可以提交）
		"""
		completeRuleType = GUIFacade.getCompleteRuleType( questID )
		if completeRuleType == csdefine.QUEST_COMPLETE_RULE_DEFAULT:
			return self.__checkIsComplete( questID )
		elif completeRuleType == csdefine.QUEST_COMPLETE_RULE_PART_TASK_COM:#只要有一个目标完成就可以交了
			return GUIFacade.getCompletedTasksNum( questID )	> 0

	def __onContentHide( self ):
		"""
		隐藏任务内容，保留标题
		"""
		self.__contentPanel.visible = False
		self.__pyUpBtn.visible = False
		self.__pyDownBtn.visible = True

	def __onContentShow( self ):
		"""
		显示任务内容
		"""
		self.__contentPanel.visible = True
		self.__pyDownBtn.visible = False
		self.__pyUpBtn.visible = True
		self.__pyWndResizer.visible = False

	def __onSortByIsComplete( self ):
		"""
		任务按照完成情况排序（已经完成了的排在后面）
		"""
		questIDList = []
		for questID in self.TQuestIDList:
			if self.__checkIsComplete( questID ):
				questIDList.append( questID )
		for questID in questIDList:
			self.TQuestIDList.remove( questID )

		self.TQuestIDList.extend( questIDList )
		self.__reSort()

		self.__pyDownBtn_1.visible = False
		self.__pyUpBtn_1.visible = True

	def __onSortByNotComplete( self ):
		"""
		任务按照完成情况排序（已经完成了的排在前面）
		"""
		questIDList = []
		for questID in self.TQuestIDList:
			if not self.__checkIsComplete( questID ):
				questIDList.append( questID )
		for questID in questIDList:
			self.TQuestIDList.remove( questID )

		self.TQuestIDList.extend( questIDList )
		self.__reSort()

		self.__pyDownBtn_1.visible = True
		self.__pyUpBtn_1.visible = False

	def __onAbandonTrace( self ) :
		"""取消任务追踪"""
		self.__pyBinder().enableQuestTraced( False )

	def __onLMouseDownTitle( self, mods ):
		"""
		这里的作用是使主窗口能接收鼠标事件
		"""
		self.focus = True
		self.onLMouseDown_( mods )

	def __onLevelChange( self, oldLevel, level ):
		"""
		等级改变时调用
		"""
		if oldLevel == level: return
		if not rds.statusMgr.isInWorld(): return
		for questID in self.TQuestDict.keys() :
			if GUIFacade.hasQuestTaskType( questID, csdefine.QUEST_OBJECTIVE_LEVEL ) : 	# 找到要求等级类任务
				self.__updateQuest( questID )

	def __onResolutionChanged( self, preReso ):
		self.__top = self.top
		self.__right = self.right

	def __showOperationTips( self ):
		"""
		显示任务追踪界面的提示帮助
		"""
		if self.visible:
			for values in self.TQuestDict.values():
				for value in values:
					if value.text.find( "@L" ) != -1: # 找到第一个超链接，显示提示帮助
						# 根据超链接的位置设置下拉条的位置，预防超链接不在面板里面
						if value.getTopToUI( self.__pyItemsPanel ) < 0:
							self.__pyItemsPanel.scrollRate = 0.0
						elif value.getTopToUI( self.__pyItemsPanel ) > self.__pyItemsPanel.height:
							self.__pyItemsPanel.scrollRate = 1.0
						return

	def __showOperateIndication( self, idtId, *args ) :
		"""
		"""
		self.showOpIndication( idtId, *args )

	def __hideOperationTips( self, pyCom = None ):
		"""
		隐藏提示帮助
		"""
		toolbox.infoTip.hideOperationTips( 0x0010 )
		self.hideIndications()

	def getLocalTrace( self ):
		"""
		获取本地保存的追踪任务
		"""
		quests = []
		qtStr = self.__cfgSect["quests"].asString
		for qt in qtStr.split( "|" ):
			if qt == "":continue
			quests.append(int(qt))
		return quests

	def __isSubItemsMouseHit( self ):
		"""
		鼠标是否点在界面上
		"""
		if self.__titlePanel.isMouseHit():
			return True
		for questID in self.TQuestIDList:
			for pyItem in self.TQuestDict[questID]:
				if pyItem.isMouseHit():
					return True
		return False

	# --------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[ macroName ]( *args )

	def isMouseHit( self ):
		return self.__isSubItemsMouseHit()

	def showQuestTrace( self, questID ):
		"""
		接收外部消息的接口，判断任务列表中是否存在此索引，存在则关闭相应的任务追踪，
		不存在则去QuestInfo中取任务的信息生成

		param questID	: 任务的索引id
		"""
		if not self.__isTraceQuest( questID ):		# 判断是否是收集与杀怪任务，不可追踪任务不显示
			DEBUG_MSG( "不可追踪任务。" )
			BigWorld.player().statusMessage( csstatus.ROLE_QUEST_CANT_TRACE )
			return
		if questID in self.TQuestIDList:			# 如果已追踪此任务，删除之
			self.__delQuestTrace( questID )
			return
		if len( self.TQuestIDList ) >= MAX_TRACE_QUEST_NUM:
			DEBUG_MSG( "最多只能追踪MAX_TRACE_QUEST_NUM个任务。" )
			return
		self.__addTraceQuest( questID )				# 增加追踪任务

	def autoQuestTrace( self, questID ):
		"""
		当任务状态改变时，自动追踪
		param questID	: 任务的索引id
		"""
		if not self.__isTraceQuest( questID ):		# 判断是否是收集与杀怪任务，不可追踪任务不显示
			return False
		if questID in self.TQuestIDList:			# 如果已追踪此任务，删除之
			return False
		if len( self.TQuestIDList ) > MAX_TRACE_QUEST_NUM:
			return False
		self.__addTraceQuest( questID )				# 增加追踪任务
		return True

	def onQuestStateChagned( self, questID ):
		self.__onTraceStateChagned( questID )

	def hide( self ):
		RootGUI.hide( self )
		self.top = self.__top
		self.right = self.__right
		self.__hideOperationTips()
		self.__pyWndResizer.visible = False
		self.clearIndications()

	def reset( self ):
		"""
		"""
		for questID in self.TQuestIDList:
			for temp in self.TQuestDict[ questID ]:
				self.__pyItemsPanel.removeItem( temp )
		self.TQuestDict.clear()
		self.TQuestIDList = []
		self.bottomHeight = 0.0
		self.isLogInited = False
		if self.__cfgSect is not None:	#add by wuxo 2011-12-12
			self.__cfgSect.save()
		ResMgr.purge( self.__cfgPath )
		self.__closeTimer()
		self.hide()

	def onEnterWorld( self ) :
		self.__checkTraceTimer()
		self.__checkQuestTimer()
		self.__onSortByNotComplete()

	def onLeaveWorld( self ) :
		self.__closeTimer()

	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		self.__titlePanel.focus = False

	def onLMouseUp_( self, mods ) :
		RootGUI.onLMouseUp_( self, mods )
		self.__titlePanel.focus = True
		self.focus = False

	def onMove_( self, dx, dy ) :
		RootGUI.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0010 )
		self.relocateIndications()

	# ----------------------------------------------------------------
	# operate indication methods
	# ----------------------------------------------------------------
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		# 提示普通追踪
		trigger = ( "fire_quest_trace",None )
		condition1 = ( "adding_quest", )
		idtsOfNormalTrace = rds.opIndicator.idtIdsOfCmd( condition1, trigger )
		for i in idtsOfNormalTrace :
			self._opIdtHandlers[i] = self.__showQuestAcceptTraceIndication
		# 提示任务目标完成追踪
		condition2 = ( "updating_quest","qtask_completed", )
		idtsOfCompleteTrace = rds.opIndicator.idtIdsOfCmd( condition2, trigger )
		for i in idtsOfCompleteTrace :
			self._opIdtHandlers[i] = self.__showQuestCompeleteTraceIndication

	def __showQuestAcceptTraceIndication( self, idtId, questId, condIndex = 0 ) :
		"""
		接受任务时追踪提示
		"""
		pyTrace = self.__searchAcceptTraceByQuestId( questId, condIndex )
		if pyTrace and pyTrace.rvisible :
			toolbox.infoTip.showHelpTips( idtId, pyTrace )
			self.addVisibleOpIdt( idtId )

	def __showQuestCompeleteTraceIndication( self, idtId, questId, condIndex ):
		"""
		完成时追踪提示
		"""
		pyTrace = self.__searchCompeleteTraceByQuestId( questId, condIndex )
		if pyTrace:
			toolbox.infoTip.showHelpTips( idtId, pyTrace )
			self.addVisibleOpIdt( idtId )

class TitleItem( PyGUI ):
	"""
	任务追踪标题
	"""
	def __init__( self ):
		panel = GUI.load("guis/general/questlist/questtrace/traceTitle.gui")
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__(self, panel )

		self.__pyIconBtn = Button( panel.iconBtn )
		self.__pyIconBtn.setStatesMapping( UIState.MODE_R1C1 )
		self.__pyIconBtn.onLClick.bind( self.__onShowQuestLog )
		self.__pyIconBtn.texture = "guis/general/questlist/questtrace/unFinishBtn.dds"

		self.__pyRtText = CSRichText( panel.rtText )
		self.__pyRtText.opGBLink = True
		self.__pyRtText.text = ""


		self.__questID = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onShowQuestLog( self ):
		if GUIFacade.getQuestLogSelection() == self.__questID :
			ECenter.fireEvent( "EVT_ON_TOGGLE_QUEST_WINDOW" )
		else :
			GUIFacade.setQuestLogSelect( self.__questID, isTraceSelect = True )
			ECenter.fireEvent( "EVT_ON_SHOW_QUEST_WINDOW" )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onQuestCompleted( self ):
		self.__pyIconBtn.texture = "guis/general/questlist/questtrace/finishBtn.dds"

	def onQuestIncompleted( self ):
		self.__pyIconBtn.texture = "guis/general/questlist/questtrace/unFinishBtn.dds"

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	def _getquestID( self ) :
		return self.__questID

	def _setquestID( self, questID ) :
		self.__questID = questID

	def _getText( self ) :
		return self.__pyRtText.text

	def _setText( self, text ) :
		self.__pyRtText.text = text

	def _getRtMaxWidth( self ) :
		return self.__pyRtText.maxWidth



	def _setRtMaxWidth( self, maxwidth ) :
		self.width = maxwidth + 1.0 # 动态设置宽度，防止显示不全，+1的理由同上
		self.__pyRtText.maxWidth = maxwidth - self.__pyIconBtn.width - 1.0 # +1是因为字体有描边，需要延长以显示描边
		if self.__pyRtText.width > self.__pyRtText.maxWidth:
			self.width = self.__pyRtText.width + 17.0
			self.pyParent.width = self.width - 1.0
		self.height = self.__pyRtText.height # 设置标题的高与文本的高一致，防止显示不全

	questID = property( _getquestID, _setquestID )
	text = property( _getText, _setText )
	rtMaxWidth = property( _getRtMaxWidth, _setRtMaxWidth )

from guis.common.ScriptObject import ScriptObject

class ConditionItem( ScriptObject ):
	def __init__( self, index ):
		panel = GUI.load("guis/general/questlist/questtrace/conditionItem.gui")
		uiFixer.firstLoadFix( panel )
		ScriptObject.__init__( self, panel )
		self.condIndex = index
		self.npcID = ""
		self.itemID = ""
		self.questID = ""

		self.__pyRtText = CSRichText( panel.conditionText )
		self.__pyRtText.opGBLink = True

		self.__pyQuickLink = PyGUI( panel.linkItem )
		self.__pyQuickLink.visible = False

		self.__pyLinkItem = LinkItem( panel.linkItem.item, self )


	#-------------------------------------
	#public
	#------------------------------------
	def updateCondition( self, text, npcID, questID, itemID = "" ) :
		if itemID == "":
			self.__pyQuickLink.visible = False
		else:
			result = self.__pyLinkItem.update( itemID )
			if result:
				self.__pyQuickLink.visible = True
			else:
				self.__pyQuickLink.visible = False
		self.npcID = npcID
		self.itemID = itemID
		self.questID = questID
		self.__pyRtText.text = text

	#--------------------------------------------
	#property method
	#--------------------------------------------
	def _getRtPanel( self ):
		return self.__pyRtText

	def _getConditionText( self ):
		return self.__pyRtText.text

	def _setConditionText( self, text ):
		if text != "":
			self.__pyRtText.text = text

	def _getRtMaxWidth( self ) :
		return self.__pyRtText.maxWidth

	def _setRtMaxWidth( self, maxwidth ) :
		self.width = maxwidth + 1.0 # 动态设置宽度，防止显示不全，+1的理由同上
		if self.itemID == "":
			self.__pyRtText.maxWidth = self.width
		else:
			self.__pyRtText.maxWidth = maxwidth - self.__pyQuickLink.width
			self.__pyQuickLink.left = self.__pyRtText.right
		self.height = self.__pyRtText.height # 设置标题的高与文本的高一致，防止显示不全

	def _getLinkItem( self ):
		if self.__pyQuickLink.visible:
			return self.__pyQuickLink
		return None


	#--------------------------------------------
	#properties
	#--------------------------------------------
	rtPanel =property( _getRtPanel )
	text = property( _getConditionText, _setConditionText )
	rtMaxWidth = property( _getRtMaxWidth, _setRtMaxWidth )

from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from ItemsFactory import ObjectItem
class LinkItem( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False
		self.focus = True

	def onLClick_( self, mods ):
		BOItem.onLClick_( self, mods )
		itemID = self.itemInfo.id
		player = BigWorld.player()
		if player.iskitbagsLocked() : # 如果背包已上锁，则返回
			player.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		itemList = player.findItemsFromNKCK_( int( itemID ) )		#从普通背包和神机匣中搜索指定类型的物品
		if len(itemList) > 0:
			player.useItem( itemList[0].uid )
		return True

	def update( self, itemID ) :
		if itemID == "":
			return False
		player = BigWorld.player()
		item = BigWorld.player().createDynamicItem( int(itemID) )
		itemInfo = ObjectItem( item )
		if itemInfo is None:
			return False
		BOItem.update( self, itemInfo )
		cdInfo = itemInfo.getCooldownInfo()
		self.__pyCDCover.unfreeze( *cdInfo )
		return True



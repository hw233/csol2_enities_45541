# -*- coding: gb18030 -*-
#
# $Id: GossipFacade.py,v 1.23 2008-02-26 02:03:30 zhangyuxing Exp $

from bwdebug import *
import csdefine
import BigWorld as bw
import QuestLogFacade as QLF
from event.EventCenter import *
import StringFormat
from QuestModule import QuestReward
import QuestLogFacade
import QuestFacade
from gbref import rds
import config.client.labels.GUIFacade as lbDatas
from Function import Functor
import csconst
import Timer

class GossipFacade:
	@staticmethod
	def reset():
		GossipFacade.current_target = None

		GossipFacade.text = ""						# 用于存放从服务器传来的数据
		GossipFacade.options = []
		GossipFacade.quests = []

		GossipFacade.current_text = ""				# 用于记录当前(最后)的对话内容
		GossipFacade.current_options = []

		GossipFacade.current_targetID = -1
		GossipFacade.current_qusetID = -1
		GossipFacade.current_quests = []
		GossipFacade.turnCBID = 0
		GossipFacade.trapID = 0

# ------------------------------->
# 用于让底层调用
# ------------------------------->
def onSetGossipText( msg ):
	"""
	有新的对话消息

	@param msg: 对话内容
	@type  msg: string
	"""
	GossipFacade.text = StringFormat.format( msg )

def onAddGossipOption( id, title, type ):
	"""
	加入聊天内容
	普通对话

	@param    id: talk key
	@type     id: String
	@param title: title
	@type  title: String
	"""
	GossipFacade.options.append( (id, StringFormat.format( title ), type ) )

def onAddGossipQuestOption( questID, questTitle, state, lv ):
	"""
	加入当前目标的任务
	任务对话

	@param    questID: quest id
	@type     questID: int32
	@param questTitle: title
	@type  questTitle: String
	"""
	title = StringFormat.format( questTitle )
	postfix = ""
	if title != lbDatas.QUEST_POTENTIAL: #潜能任务名称和类型名一样，只取其一
		title += "(" +QuestLogFacade.getQuestTypeStr( questID )[1] + ")"
	player = bw.player()
	showLevel = getQuestShowLevelByID( questID, lv )
	if player.level - lv > 5:
		# 大于5级加上等级提示
		if title == lbDatas.QUEST_POTENTIAL:
			 postfix = lbDatas.QUEST_LVALTERABLE
		else:
			postfix = str( showLevel ) + lbDatas.LEVEL
		title += postfix
	GossipFacade.quests.append ( ( questID, title , state ) )

def getQuestShowLevelByID( questID, showLevel ):
	"""
	获得任务应该显示出来的级别
	（显示任务级别还是玩家级别）
	"""
	questIDStr = str( int( questID ) )
	typeStr = int( questIDStr[0:3] )
	if not typeStr in [ 101, 102, 201, 202, 203, 204, 401 ]:
		showLevel2 = bw.player().level
		if showLevel == 0:	# 如果读取配置为0，则取角色的等级
			return showLevel2
		return min( showLevel2, showLevel )
	return showLevel

def onGossipComplete( targetID ):
	"""
	@param    questID: quest id
	@type     questID: int32
	"""
	#	普通聊天数据传送完毕，聊天开始
	if GossipFacade.current_targetID != targetID: #与不同的NPC对话，使原来对话NPC模型转向复位
		gossipEntity = bw.entities.get( GossipFacade.current_targetID )
		cancelTurnCB( gossipEntity )
	GossipFacade.current_targetID = targetID
	GossipFacade.current_options = GossipFacade.options
	GossipFacade.current_text = GossipFacade.text
	GossipFacade.current_quests = GossipFacade.quests
	GossipFacade.text = ""
	GossipFacade.options = []
	GossipFacade.quests = []
	gossipEntity = bw.entities.get( targetID )
	cancelTurnCB( gossipEntity )
	if not hasattr( gossipEntity, "model" ) :
		ERROR_MSG( "npc %i has no model!" % gossipEntity.id )
	elif hasattr( gossipEntity.model, "motors" ) :
		func = Functor( turnEntityCB, gossipEntity )
		GossipFacade.turnCBID = Timer.addTimer( 0, 0.1, func )
	if len( GossipFacade.current_quests ) == 1 and len( GossipFacade.current_options ) == 0:
		selectGossipQuest( 0 )	# 遇到只有一个任务且没有对话选项时,直接就要求与任务对话(无论这个任务是接还是交的)
		fireEvent( "EVT_CLOSE_GOSSIP_WINDOW" )
		return
	QuestFacade.setCurrQuestID( None )
	if len( GossipFacade.current_text ) or \
		len( GossipFacade.current_quests ) or \
		len( GossipFacade.current_options ):
		if gossipEntity and gossipEntity.isEntityType( csdefine.ENTITY_TYPE_EIDOLON_NPC ) :
			fireEvent( "EVT_ON_TRIGGER_PIXIE_GOSSIP" )		# 与小精灵NPC对话
		else :
			fireEvent( "EVT_OPEN_GOSSIP_WINDOW" )			# 与普通NPC对话
	if hasattr( gossipEntity, "move_speed" ):
		move_speed = gossipEntity.move_speed
		if move_speed > 0:
			cancelTurnCB( gossipEntity )

def gossipWithTrainer():
	"""
	与技能训练师对话（csol-2814）
	"""
	gossipEntity = getGossipTarget()
	player = bw.player()
	questInfos = getGossipQuests()
	optionInfos = getGossipOptions()
	for questInfo in questInfos:
		questID = questInfo[0]
		if player.isDoingLearnSkillQuest( questID ) and not QuestLogFacade.questIsCompleted( questID ):
			for optionInfo in optionInfos:
				talkID = optionInfo[0]
				type = optionInfo[2]
				if type == csdefine.GOSSIP_TYPE_SKILL_LEARN:	# 技能学习类型
					onEndGossip( gossipEntity )
					player.gossipWith( gossipEntity, talkID )
					return

def onEndGossip( targetEntity ) :
	"""
	结束对话，发送关闭对话窗口信息
	"""
	fireEvent( "EVT_END_GOSSIP" )
	if targetEntity is None:return
	cancelTurnCB( targetEntity )

def turnEntityCB( gossipEntity ):
	"""
	NPC转向回调
	"""
	if not hasattr( gossipEntity, "model" ) :
		ERROR_MSG( "npc %i has no model!" % gossipEntity.id )
		return
	if not gossipEntity.model: #add by wuxo 2011-12-7
		return
	motors = gossipEntity.model.motors
	player = bw.player()
	if len( motors ) :
		motors[0].turnModelToEntity = False
		gossipEntity.model.yaw = ( player.position - gossipEntity.position ).yaw
	distance = csconst.COMMUNICATE_DISTANCE
	if hasattr( gossipEntity, "getRoleAndNpcSpeakDistance" ):
		distance = gossipEntity.getRoleAndNpcSpeakDistance()
	GossipFacade.trapID = player.addTrapExt( distance, onEntitiesTrapThrough )
	if hasattr( gossipEntity, "state" ):
		state = gossipEntity.state
		if state in [csdefine.ENTITY_STATE_FIGHT, csdefine.ENTITY_STATE_DEAD]: #对话NPC进入战斗状态，取消转向
			onEndGossip( gossipEntity )

def onEntitiesTrapThrough( entitiesInTrap ):
	gossipEntity = getGossipTarget()
	if gossipEntity and gossipEntity not in entitiesInTrap:
		cancelTurnCB( gossipEntity )
		if GossipFacade.trapID > 0:
			bw.player().delTrap( GossipFacade.trapID )
			GossipFacade.trapID = 0

def cancelTurnCB( gossipEntity ):
	"""
	取消回调
	"""
	Timer.cancel( GossipFacade.turnCBID )
	GossipFacade.turnCBID = 0
	if gossipEntity is None:return
	if not hasattr( gossipEntity, "model" ) :
		ERROR_MSG( "npc %i has no model!" % gossipEntity.id )
		return
	if gossipEntity.model is None:return
	motors = gossipEntity.model.motors
	if len( motors ):	# 对话结束后设置模型和entity的旋转角度一致
		motors[0].turnModelToEntity = True

# ------------------------------->
# gossip about
# ------------------------------->
def getGossipTargetID():
	return GossipFacade.current_targetID

def getGossipQuestID():
	return GossipFacade.current_qusetID

def getGossipTarget():
	if bw.entities.has_key( getGossipTargetID() ):	# wsf, getGossipQuestID---->getGossipTargetID
		return bw.entities[getGossipTargetID()]

def getGossipTargetClassNameInt() :
	return int( getattr( getGossipTarget(), "className", 0 ) )

def getGossipTargetName():
	try:
		uname = getGossipTarget().getName()
	except AttributeError:
		uname = ''
	return uname

def getGossipTargetHeader():
	try:
		header = getGossipTarget().getHeadTexture()
	except AttributeError:
		header = ""
	return header

def gossipHello( entity ):
	"""
	开始对话

	@param entity: 对话目标(instance of GameObject of class)
	@type  entity: Entity
	"""
	bw.player().gossipWith( entity, "Talk" )

def selectGossipOption( index ):
	"""
	与普通NPC对话，选择对话中的一个功能选项

	@param index: 普通选项索引
	@type  index: int
	"""
	targetEnity = bw.entities[getGossipTargetID()]
	try:
		dlgKey = GossipFacade.current_options[index][0]
	except IndexError:
		ERROR_MSG( "list index out of range" )
		return
	bw.player().gossipWith( targetEnity, dlgKey )

"""
def gossipQuest( index ):

	与任务NPC对话，选择对话中的一个任务选项

	@param index: 任务选项索引
	@type  index: int

	try:
		questID = GossipFacade.current_quests[index][0]
		dlgkey = GossipFacade.current_quests[index][1]
	except IndexError:
		ERROR_MSG( "list index out of range" )
		return
	bw.player().cell.questGossip( getGossipTargetID(), questID, dlgkey )
"""

def selectGossipQuest( index ):
	"""
	选择对话中的一个可接任务

	@param index: 可用的选项索引
	@type  index: int
	"""
	try:
		questID = GossipFacade.current_quests[index][0]
	except IndexError:
		ERROR_MSG( "list index(%i) out of range " % index )
		return
	if QuestFacade.getCurrQuestID() == questID:return   # 同一个对话多次点击只产生一次响应
	bw.player().cell.questSelect( questID, getGossipTargetID() )

def getGossipQuestIdByIndex( index ) :
	"""
	"""
	if 0 <= index < len( GossipFacade.current_quests ) :
		return GossipFacade.current_quests[index][0]
	else :
		return None

def getDlgKeyByOptionIndex( index ) :
	"""
	获取对话关键字
	"""
	if 0 <= index < len( GossipFacade.current_options ) :
		return GossipFacade.current_options[index][0]
	else :
		return None

def getGossipOptions():
	"""
	取得所有对话选项

	@return: like as [title, ...]
	@rtype:  list
	"""
	return [ e for e in GossipFacade.current_options ]

def getGossipQuests():
	"""
	@return: like as [questTitle, ...]
	@rtype:  list
	"""
	return [ e for e in GossipFacade.current_quests ]

def getGossipText():
	"""
	取得对话内容

	@return: string
	@rtype:  string
	"""
	return GossipFacade.current_text

#
# $Log: not supported by cvs2svn $
# Revision 1.22  2008/01/24 02:24:37  zhangyuxing
# no message
#
# Revision 1.21  2008/01/19 02:08:50  wangshufeng
# method modify：getGossipTarget,修正了接口使用错误的bug
#
# Revision 1.20  2007/12/19 01:26:33  fangpengjun
# 修改了获得对话npcID的错误
#
# Revision 1.19  2007/12/06 00:45:58  fangpengjun
# e[2] for e in GossipFacade.current_quests -->
#   e[1] for e in GossipFacade.current_quests
#
# Revision 1.18  2007/11/02 03:48:18  phw
# 任务系统调整，去掉了一些接口中不需要的参数，以及增添/删除了一些接口。
#
# Revision 1.17  2007/09/29 07:20:00  fangpengjun
# 调整了NPC对话的方式，注释掉了一些没有用到的接口
#
# Revision 1.16  2007/01/13 09:47:28  huangyongwei
#
# 修改了函数 def getCurGossipFinishQuest():
# return [GossipFacade.current_finish_quest[1]]
# --->
# return [option[1] for option in [GossipFacade.current_finish_quest]]
#
# Revision 1.15  2007/01/06 08:14:03  phw
# 修改对entity.uname的访问为entity.getName()
#
# Revision 1.14  2006/12/29 07:24:04  huangyongwei
# 将获取完成任务确认选项的获取，改为跟普通对话选择相同的接口
#
# Revision 1.13  2006/12/23 06:29:36  huangyongwei
# 去掉了最后一个 getGossipTarge 函数
# －－发觉原来已经有该函数
#
# Revision 1.12  2006/12/23 06:19:38  huangyongwei
# 添加了 getGossipTarge 函数，用于获取当前对话的 NPC
#
# Revision 1.11  2006/12/21 09:31:44  phw
# function removed: onGossipQuestRewards(); disuse
#
# Revision 1.10  2006/12/20 03:52:41  kebiao
# attribute added:
# 	#配合新的任务规则，普通对话走普通对话路线，任务对话走任务对话，而交任务则走交任务路线
# 	GossipFacade.current_take_quest = []
# 	GossipFacade.current_give_quest = []
# 	GossipFacade.current_gossip_quest = 0
# 	GossipFacade.current_finish_quest = 0
# 	GossipFacade.finish_quest = 0
# method added:
# 	onAddGossipQuestOption
# 	onAddFinishQuest();	按照新的规则玩家交任务时将走这个接口
# 	startGossipQuest();	与一个可接任务对话
# 	finishGossipQuest();	与一个可交任务对话
# 	getStartGossipQuests();	取得所有可接的任务
# 	getFinishGossipQuests();取得所有可交的任务
# 	getCurGossipFinishQuest();取得当前准备完成的任务
#
# method modified:
# 	getGossipTargetName() 由于目前策划未
# method deleted:
# 	getGossipQuestRewards(); 未使用的方法
# 	gossipQuestChooseReward(); 未使用的方法
#
# Revision 1.9  2006/08/17 09:33:57  huangyongwei
# 添加了结束对话消息
#
# Revision 1.8  2006/06/12 03:15:00  phw
# no message
#
# Revision 1.7  2006/06/08 09:10:24  phw
# no message
#
# Revision 1.6  2006/03/25 02:50:49  phw
# 修正了显示空对话的BUG
#
# Revision 1.5  2006/03/22 02:17:50  phw
# 对任务相关的接口加放了level和hardLevel参数，并对内容作相应的修改
#
# Revision 1.4  2006/03/06 05:06:37  phw
# 处理"$"开头的字符串
#
# Revision 1.3  2006/02/28 08:01:32  phw
# no message
#
# Revision 1.2  2006/02/27 08:11:40  phw
# no message
#
# Revision 1.1  2006/02/23 09:44:30  phw
# no message
#
#
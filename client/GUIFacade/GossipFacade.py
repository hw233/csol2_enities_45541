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

		GossipFacade.text = ""						# ���ڴ�Ŵӷ���������������
		GossipFacade.options = []
		GossipFacade.quests = []

		GossipFacade.current_text = ""				# ���ڼ�¼��ǰ(���)�ĶԻ�����
		GossipFacade.current_options = []

		GossipFacade.current_targetID = -1
		GossipFacade.current_qusetID = -1
		GossipFacade.current_quests = []
		GossipFacade.turnCBID = 0
		GossipFacade.trapID = 0

# ------------------------------->
# �����õײ����
# ------------------------------->
def onSetGossipText( msg ):
	"""
	���µĶԻ���Ϣ

	@param msg: �Ի�����
	@type  msg: string
	"""
	GossipFacade.text = StringFormat.format( msg )

def onAddGossipOption( id, title, type ):
	"""
	������������
	��ͨ�Ի�

	@param    id: talk key
	@type     id: String
	@param title: title
	@type  title: String
	"""
	GossipFacade.options.append( (id, StringFormat.format( title ), type ) )

def onAddGossipQuestOption( questID, questTitle, state, lv ):
	"""
	���뵱ǰĿ�������
	����Ի�

	@param    questID: quest id
	@type     questID: int32
	@param questTitle: title
	@type  questTitle: String
	"""
	title = StringFormat.format( questTitle )
	postfix = ""
	if title != lbDatas.QUEST_POTENTIAL: #Ǳ���������ƺ�������һ����ֻȡ��һ
		title += "(" +QuestLogFacade.getQuestTypeStr( questID )[1] + ")"
	player = bw.player()
	showLevel = getQuestShowLevelByID( questID, lv )
	if player.level - lv > 5:
		# ����5�����ϵȼ���ʾ
		if title == lbDatas.QUEST_POTENTIAL:
			 postfix = lbDatas.QUEST_LVALTERABLE
		else:
			postfix = str( showLevel ) + lbDatas.LEVEL
		title += postfix
	GossipFacade.quests.append ( ( questID, title , state ) )

def getQuestShowLevelByID( questID, showLevel ):
	"""
	�������Ӧ����ʾ�����ļ���
	����ʾ���񼶱�����Ҽ���
	"""
	questIDStr = str( int( questID ) )
	typeStr = int( questIDStr[0:3] )
	if not typeStr in [ 101, 102, 201, 202, 203, 204, 401 ]:
		showLevel2 = bw.player().level
		if showLevel == 0:	# �����ȡ����Ϊ0����ȡ��ɫ�ĵȼ�
			return showLevel2
		return min( showLevel2, showLevel )
	return showLevel

def onGossipComplete( targetID ):
	"""
	@param    questID: quest id
	@type     questID: int32
	"""
	#	��ͨ�������ݴ�����ϣ����쿪ʼ
	if GossipFacade.current_targetID != targetID: #�벻ͬ��NPC�Ի���ʹԭ���Ի�NPCģ��ת��λ
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
		selectGossipQuest( 0 )	# ����ֻ��һ��������û�жԻ�ѡ��ʱ,ֱ�Ӿ�Ҫ��������Ի�(������������ǽӻ��ǽ���)
		fireEvent( "EVT_CLOSE_GOSSIP_WINDOW" )
		return
	QuestFacade.setCurrQuestID( None )
	if len( GossipFacade.current_text ) or \
		len( GossipFacade.current_quests ) or \
		len( GossipFacade.current_options ):
		if gossipEntity and gossipEntity.isEntityType( csdefine.ENTITY_TYPE_EIDOLON_NPC ) :
			fireEvent( "EVT_ON_TRIGGER_PIXIE_GOSSIP" )		# ��С����NPC�Ի�
		else :
			fireEvent( "EVT_OPEN_GOSSIP_WINDOW" )			# ����ͨNPC�Ի�
	if hasattr( gossipEntity, "move_speed" ):
		move_speed = gossipEntity.move_speed
		if move_speed > 0:
			cancelTurnCB( gossipEntity )

def gossipWithTrainer():
	"""
	�뼼��ѵ��ʦ�Ի���csol-2814��
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
				if type == csdefine.GOSSIP_TYPE_SKILL_LEARN:	# ����ѧϰ����
					onEndGossip( gossipEntity )
					player.gossipWith( gossipEntity, talkID )
					return

def onEndGossip( targetEntity ) :
	"""
	�����Ի������͹رնԻ�������Ϣ
	"""
	fireEvent( "EVT_END_GOSSIP" )
	if targetEntity is None:return
	cancelTurnCB( targetEntity )

def turnEntityCB( gossipEntity ):
	"""
	NPCת��ص�
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
		if state in [csdefine.ENTITY_STATE_FIGHT, csdefine.ENTITY_STATE_DEAD]: #�Ի�NPC����ս��״̬��ȡ��ת��
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
	ȡ���ص�
	"""
	Timer.cancel( GossipFacade.turnCBID )
	GossipFacade.turnCBID = 0
	if gossipEntity is None:return
	if not hasattr( gossipEntity, "model" ) :
		ERROR_MSG( "npc %i has no model!" % gossipEntity.id )
		return
	if gossipEntity.model is None:return
	motors = gossipEntity.model.motors
	if len( motors ):	# �Ի�����������ģ�ͺ�entity����ת�Ƕ�һ��
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
	��ʼ�Ի�

	@param entity: �Ի�Ŀ��(instance of GameObject of class)
	@type  entity: Entity
	"""
	bw.player().gossipWith( entity, "Talk" )

def selectGossipOption( index ):
	"""
	����ͨNPC�Ի���ѡ��Ի��е�һ������ѡ��

	@param index: ��ͨѡ������
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

	������NPC�Ի���ѡ��Ի��е�һ������ѡ��

	@param index: ����ѡ������
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
	ѡ��Ի��е�һ���ɽ�����

	@param index: ���õ�ѡ������
	@type  index: int
	"""
	try:
		questID = GossipFacade.current_quests[index][0]
	except IndexError:
		ERROR_MSG( "list index(%i) out of range " % index )
		return
	if QuestFacade.getCurrQuestID() == questID:return   # ͬһ���Ի���ε��ֻ����һ����Ӧ
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
	��ȡ�Ի��ؼ���
	"""
	if 0 <= index < len( GossipFacade.current_options ) :
		return GossipFacade.current_options[index][0]
	else :
		return None

def getGossipOptions():
	"""
	ȡ�����жԻ�ѡ��

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
	ȡ�öԻ�����

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
# method modify��getGossipTarget,�����˽ӿ�ʹ�ô����bug
#
# Revision 1.20  2007/12/19 01:26:33  fangpengjun
# �޸��˻�öԻ�npcID�Ĵ���
#
# Revision 1.19  2007/12/06 00:45:58  fangpengjun
# e[2] for e in GossipFacade.current_quests -->
#   e[1] for e in GossipFacade.current_quests
#
# Revision 1.18  2007/11/02 03:48:18  phw
# ����ϵͳ������ȥ����һЩ�ӿ��в���Ҫ�Ĳ������Լ�����/ɾ����һЩ�ӿڡ�
#
# Revision 1.17  2007/09/29 07:20:00  fangpengjun
# ������NPC�Ի��ķ�ʽ��ע�͵���һЩû���õ��Ľӿ�
#
# Revision 1.16  2007/01/13 09:47:28  huangyongwei
#
# �޸��˺��� def getCurGossipFinishQuest():
# return [GossipFacade.current_finish_quest[1]]
# --->
# return [option[1] for option in [GossipFacade.current_finish_quest]]
#
# Revision 1.15  2007/01/06 08:14:03  phw
# �޸Ķ�entity.uname�ķ���Ϊentity.getName()
#
# Revision 1.14  2006/12/29 07:24:04  huangyongwei
# ����ȡ�������ȷ��ѡ��Ļ�ȡ����Ϊ����ͨ�Ի�ѡ����ͬ�Ľӿ�
#
# Revision 1.13  2006/12/23 06:29:36  huangyongwei
# ȥ�������һ�� getGossipTarge ����
# ��������ԭ���Ѿ��иú���
#
# Revision 1.12  2006/12/23 06:19:38  huangyongwei
# ����� getGossipTarge ���������ڻ�ȡ��ǰ�Ի��� NPC
#
# Revision 1.11  2006/12/21 09:31:44  phw
# function removed: onGossipQuestRewards(); disuse
#
# Revision 1.10  2006/12/20 03:52:41  kebiao
# attribute added:
# 	#����µ����������ͨ�Ի�����ͨ�Ի�·�ߣ�����Ի�������Ի��������������߽�����·��
# 	GossipFacade.current_take_quest = []
# 	GossipFacade.current_give_quest = []
# 	GossipFacade.current_gossip_quest = 0
# 	GossipFacade.current_finish_quest = 0
# 	GossipFacade.finish_quest = 0
# method added:
# 	onAddGossipQuestOption
# 	onAddFinishQuest();	�����µĹ�����ҽ�����ʱ��������ӿ�
# 	startGossipQuest();	��һ���ɽ�����Ի�
# 	finishGossipQuest();	��һ���ɽ�����Ի�
# 	getStartGossipQuests();	ȡ�����пɽӵ�����
# 	getFinishGossipQuests();ȡ�����пɽ�������
# 	getCurGossipFinishQuest();ȡ�õ�ǰ׼����ɵ�����
#
# method modified:
# 	getGossipTargetName() ����Ŀǰ�߻�δ
# method deleted:
# 	getGossipQuestRewards(); δʹ�õķ���
# 	gossipQuestChooseReward(); δʹ�õķ���
#
# Revision 1.9  2006/08/17 09:33:57  huangyongwei
# ����˽����Ի���Ϣ
#
# Revision 1.8  2006/06/12 03:15:00  phw
# no message
#
# Revision 1.7  2006/06/08 09:10:24  phw
# no message
#
# Revision 1.6  2006/03/25 02:50:49  phw
# ��������ʾ�նԻ���BUG
#
# Revision 1.5  2006/03/22 02:17:50  phw
# ��������صĽӿڼӷ���level��hardLevel������������������Ӧ���޸�
#
# Revision 1.4  2006/03/06 05:06:37  phw
# ����"$"��ͷ���ַ���
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
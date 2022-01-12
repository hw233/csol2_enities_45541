# -*- coding: gb18030 -*-

"""
�¼����

EVT_OPEN_QUEST_WINDOW
EVT_OPEN_QUEST_LOG_WINDOW
EVT_ON_NPC_QUEST_STATE_CHANGED				# ��ʾ NPC ������״̬,

EVT_OPEN_GOSSIP_WINDOW						# None; fire while a gossip is receive.
EVT_END_GOSSIP								# None; �رնԻ�����
EVT_QUEST_SHOW_DETAIL_TEXT					# None; ��ʾ����Ի���ϸ����(������ʱ).
EVT_QUEST_SHOW_INCOMPLETE_TEXT				# None; ��ʾ����Ŀ�껹û�����ʱ�ĶԻ�
EVT_QUEST_SHOW_PRECOMPLETE_TEXT				# None; ��ʾ����Ŀ�������ʱ�ĶԻ�
EVT_QUEST_SHOW_COMPLETE_TEXT				# None; ��ʾ��������ĶԻ�
EVT_QUEST_SHOW_PREBEGIN_TEXT				# None; ��ʾ������֮ǰ�ķϻ�(����)�԰�
EVT_ON_QUEST_TASK_STATE_CHANGED				# questID; ֪ͨ��һ�������Ŀ��״̬���ı�
EVT_ON_QUEST_LOG_ADD						# questID; fire while a quest log is add.
EVT_ON_QUEST_LOG_REMOVED					# questID; fire while a quest log is abandon.
EVT_ON_QUEST_LOG_SELECTED					# questID; fire while a quest log is selected.
EVT_ON_QUEST_REWARDS_CHANGED				# questID; fire while a quest log is receive reward list.
EVT_ON_RECEIVE_CHAT_COMMON_MESSAGE			# ����������ʾ��ͨ��Ϣ��channelID, msg;
EVT_ON_RECEIVE_CHAT_SYSTEM_MESSAGE			# ����������ʾϵͳ��Ϣ��channelID, msg;
EVT_ON_SHOW_LEARN_SKILL_WINDOW				# None; show learn skill window
EVT_ON_SKILL_LEARNT							# None; fire while player learnt a skill

# team message
EVT_ON_INVITE_JOIN_TEAM						# inviterName; someone invite player join in team
EVT_ON_INVITE_FOLLOW						# entityid �����ߵ�id, ������Ҹ���
EVT_ON_REQUEST_JOIN_TEAM					# requesterName; someone request join in team
EVT_ON_TEAM_MEMBER_ADDED					# member; instance of TeamMember
EVT_ON_TEAM_MEMBER_LEFT						# entityID
EVT_ON_TEAM_MEMBER_HP_CHANGED				# entityID, hp, hpMax;
EVT_ON_TEAM_MEMBER_MP_CHANGED				# entityID, mp, mpMax;
EVT_ON_TEAM_MEMBER_LEVEL_CHANGED			# entityID, level;
EVT_ON_TEAM_MEMBER_SPACE_CHANGED			# entityID, spaceID;
EVT_ON_TEAM_MEMBER_NAME_CHANGED				# entityID, name;
EVT_ON_TEAM_MEMBER_HEADER_CHANGED			# entityID, iconFileName;
EVT_ON_TEAM_MEMBER_POSITION_CHANGED			# entityID, position;
EVT_ON_TEAM_CAPTAIN_CHANGED					# entityID;
EVT_ON_TEAM_DISBANDED						# �����ɢ֪ͨ
EVT_ON_TEAM_MEMBER_REJOIN					# oldEntityID, newEntityID, ����������ߣ����¼������

# corps about
EVENT_CORPS_ADDMEMBER_INFO					# PlayerName,ְλ,�ȼ�,λ��,ְҵ,����,��ѫ,״̬,�ϴ�����ʱ��;
EVENT_CORPS_CHANGEMEMBER_INFO				# PlayerName,ְλ,�ȼ�,λ��,ְҵ,����,��ѫ,״̬,�ϴ�����ʱ��;
EVENT_CORPS_DELMEMBER_INFO 					# PlayerName;
EVENT_CORPS_UPDATEMEMBERCOUNT_INFO			# MemberMaxCount

# merchant message
EVT_ON_BUYBAG_INFO_CHANGE					# order, itemInfo; ֪ͨ���ﳵ��ĳ��λ�õ���Ʒ��Ϣ�ı䣬��Ʒ����������itemInfo=None; itemInfo is instance of ItemInfo
EVT_ON_BUYBAG_PRICE_TOTAL_CHANGED			# price; ���������Ʒ�ܼ�ֵ
EVT_ON_TRADE_WITH_NPC						# chapmanEntity; ��ĳ��NPC���н���

EVT_ON_INVOICES_BAG_SPACE_CHANGED			# space; ���˵���Ʒ����
EVT_ON_INVOICES_BAG_INFO_CHANGED			# order, itemInfo; ��һ����Ʒ���ݱ��ı䣬��Ʒ����������itemInfo=None; itemInfo is instance of ItemInfo

EVT_ON_SELLBAG_INFO_CHANGE					# order, itemInfo; ֪ͨ���ﳵ��ĳ��λ�õ���Ʒ��Ϣ�ı䣬��Ʒ����������itemInfo=None; itemInfo is instance of ItemInfo
EVT_ON_SELLBAG_PRICE_TOTAL_CHANGED			# price; ���������Ʒ�ܼ�ֵ
EVT_ON_PLAYER_INVOICES_BAG_SPACE_CHANGED	# space; ��ҵĿɳ�����Ʒ����
EVT_ON_PLAYER_INVOICES_BAG_INFO_CHANGED		# order, itemInfo; ��һ����Ʒ���ݱ��ı䣬��Ʒ����������itemInfo=None; itemInfo is instance of ItemInfo

# ItemsBag
EVT_ON_KITBAG_ITEM_LOCK_CHANGED				# kitbagOrder, itemOrder, isLocked; ĳ�����ӵ�����״̬�ı�
EVT_ON_KITBAG_ITEM_INFO_CHANGED				# kitbagOrder, itemOrder, itemInfo; ĳ��λ�õ���Ʒ��Ϣ�ı䣬��Ʒ����������itemInfo=None��

# player role about
EVT_ON_ROLE_MONEY_CHANGED					# old, new; ��ҽ�Ǯ�ı�
EVT_ON_ROLE_EXP_CHANGED						# exp, maxExp; ��ǰ����,��һ����������
EVT_ON_ROLE_HP_CHANGED						# hp, hpMax; ��ǰhp,���hp
EVT_ON_ROLE_MP_CHANGED						# mp, mpMax; ��ǰmp,���mp
EVT_ON_ROLE_EN_CHANGED						# en, enMax; ��ǰenerey,���enerey
EVT_ON_ROLE_LEVEL_CHANGED					# level; �ȼ�
EVT_ON_ROLE_POTENTIAL_CHANGED				# value; Ǳ��
EVT_ON_ROLE_PHYSICS_DAMAGE_CHANGED			# value; ������
EVT_ON_ROLE_ELEMENT_DAMAGE_CHANGED			# value; ��Ȼ����
EVT_ON_ROLE_POISON_DAMAGE_CHANGED			# value; ���ع���
EVT_ON_ROLE_SPIRIT_DAMAGE_CHANGED			# value; ���񹥻�
EVT_ON_ROLE_ELEMENT_RESIST_CHANGED			# value; ��Ȼ��ж
EVT_ON_ROLE_POISON_RESIST_CHANGED			# value; ���ط�ж
EVT_ON_ROLE_SPIRIT_RESIST_CHANGED			# value; �����ж
EVT_ON_ROLE_HITTED_CHANGED					# value; ����
EVT_ON_ROLE_DODGE_CHANGED					# value; ����
EVT_ON_ROLE_DOUBLE_DAMAGE_CHANCE_CHANGED	# value; ����һ������
EVT_ON_ROLE_MOVED							# isMoving; �ƶ�״̬�ı�
EVT_ON_ROLE_BEGIN_COOLDOWN					# cooldownType, overTime; ����һ��cooldown
EVT_ON_ROLE_ENTER_WORLD						# ��ҽ�����Ϸ����, player: ���
EVT_ON_ROLE_LEAVE_WORLD						# ����뿪��Ϸ����, player: ���

# offline ( by hyw )
EVT_ON_ROLE_QUIT							# �˳���ɫ��None
EVT_ON_GAME_LOGOFF							# ʧȥ������������ӡ�None
EVT_ON_GAME_QUIT							# �˳���Ϸ�ͻ��ˡ�None
EVT_ON_GAME_RECONNECT						# �Ͽ�����������������

# about skill of player role( by hyw )
EVT_ON_PLAYERROLE_ADD_SKILL					# ��Ҽ������ӣ�skillID�����ӵļ��� ID
EVT_ON_PLAYERROLE_REMOVE_SKILL				# ��Ҽ��ܱ�ɾ����skillID: ��ɾ���ļ��� ID
EVT_ON_PLAYERROLE_UPDATE_SKILL				# ��Ҽ��ܸ��£�oldSkillID: �ɼ��� ID, newSkillID: �¼��� ID

EVT_ON_ROLE_ADD_SKILL						# ���һ��ܣ�skillInfo : SkillItem ʵ����λ�� GUIFacade.SkillListFacade �У�
EVT_ON_ROLE_REMOVE_SKILL					# ɾ��һ��ܣ�skillID	  : skillID
EVT_ON_ROLE_UPDATE_SKILL						# ����һ�����ܣ�oldSkillID, newSkillID

# about buff ( by hyw )
EVT_ON_ROLE_ADD_BUFF						# ��� buffer��buffData ��buff ��Ϣ����
EVT_ON_ROLE_ADD_DUFF						# ��� buffer��buffData ��duff ��Ϣ����
EVT_ON_ROLE_REMOVE_BUFF						# ɾ��һ�� buff��index ��buff ����
EVT_ON_ROLE_REMOVE_DUFF						# ɾ��һ�� duff��index ��duff ����

# swap item
EVT_ON_RSI_INVITE_SWAP_ITEM					# name; ������Ҽ佻��
EVT_ON_RSI_SWAP_ITEM_BEGIN					# name; ��ʼ���н���(��ʾ����)
EVT_ON_RSI_SWAP_ITEM_END					# None; ���׽���(�رմ���)
EVT_ON_RSI_DST_ITEM_CHANGED					# order, itemInfo; �Է�ĳ��λ�õ���Ʒ��Ϣ�ı�
EVT_ON_RSI_DST_MONEY_CHANGED				# order, quantity; �Է���Ǯ�ı�
EVT_ON_RSI_SELF_ITEM_CHANGED				# order, itemInfo; �Լ�ĳ��λ�õ���Ʒ��Ϣ�ı�
EVT_ON_RSI_SELF_MONEY_CHANGED				# order, quantity; �Լ���Ǯ�ı�
EVT_ON_RSI_DST_SWAP_STATE_CHANGED			# accept1State, accept2State; ��һ��ȷ��״̬���ڶ���ȷ��״̬��TrueΪȷ�ϣ�FalseΪû��ȷ��
EVT_ON_RSI_SELF_SWAP_STATE_CHANGED			# accept1State, accept2State; ��һ��ȷ��״̬���ڶ���ȷ��״̬��TrueΪȷ�ϣ�FalseΪû��ȷ��

# login( by hyw )
EVT_ON_SHOW_LOGIN_DIALOG					# ��ʾ��¼���档defAccount : Ĭ���˺ţ� defPassword : Ĭ������
EVT_ON_HIDE_LOGIN_DIALOG					# ���ص�¼����
EVT_ON_LOGIN_SUCCEED						# ��¼�ɹ���None
EVT_ON_LOGIN_FAIL							# ��¼ʧ�ܡ�None
EVT_ON_CANCEL_LOGIN							# ȡ����¼��None
EVT_ON_SHOW_SERVER_LIST						# ��ʾ�������б�
EVT_ON_PREVIEW_ROLE_ENTERWOLD				# ������һ�� PreviewRole

# role selector( by hyw )
EVT_ON_SHOW_ROLE_SELECTOR					# ��ʾ��ɫѡ����档
EVT_ON_HIDE_ROLE_SELECTOR					# ���ؽ�ɫѡ����档

EVT_ON_ROLE_SELECTED						# ѡ���¼��ɫ��id, name, level, raceClass
EVT_ON_ROLE_DESELECTED						# ȡ��ѡ��
EVT_ON_ROLE_DELETED							# ɾ��һ����ɫ��roleID: ��ɾ���Ľ�ɫ�� entity id
EVT_ON_HIDE_ROLE_SELECTOR					# ���ؽ�ɫѡ�����

# role creator( by hyw )
EVT_ON_SHOW_ROLE_CREATOR					# ��ʾ��ɫ��������
EVT_ON_ROLE_CHOICE							# ѡ��ĳ��Ҫ�����Ľ�ɫ��roleInfo : ��ɫ��Ϣ
EVT_ON_ROLE_UNCHOOSE						# ȡ��ѡ��ĳ��ѡ�еĴ�����ɫ��
EVT_ON_NAME_VERIFIED						# ����������֤�����allow : �Ƿ�����ʹ�ø�����
EVT_ON_ROLE_CREATE_FEEDBACK					# ������Һ󷵻أ�successful:�Ƿ񴴽��ɹ�

# chat( hyw )
EVT_ON_RECEIVE_STATUS_MESSAGE					# �ӵ�������״̬ʱ��������statusID��״̬ID��msg��״̬ע���ı�
EVT_ON_SHOW_CHAT_MESSAGE					# ���յ���ҷ���ʱ��������player����ң�msg����Ϣ�ı�

# floatname( hyw )
EVT_ON_ENTITY_ENTER_WORLD					# entity ��������ʱ��������entity��entityʵ��
EVT_ON_ENTITY_LEAVE_WORLD					# entity �뿪����ʱ��������entityID���뿪����� entity ʵ��
EVT_ON_ENTITY_LEVEL_CHANGED					# entity �ȼ��ı�ʱ��������oldLevel, newLevel
EVT_ON_ENTITY_HP_CHANGED					# entity �� HP �ı�ʱ��������hp, hpMax
EVT_ON_ENTITY_TITLE_CHANGED					# entity ͷ�θı�ʱ�����ã�oldTitle, newTitle

# quickbar( by hyw )
EVT_ON_QUICKBAR_UPDATE_ITEM					# ���� quickbar�� itemInfo����ݸ���Ϣ
EVT_ON_UPDATE_QBSHORTCUT					# ���¿�ݼ���shortcut����ݼ�����ĸ����ֵ����������ֵ����shortcutText����ݼ���ǩ���� "CTRL+H"
EVT_ON_LOCK_QUICKBARITEM					# ����ĳ����ݸ�index �������Ŀ�ݸ������

# targetinfo( by hyw )
EVT_ON_SHOW_TARGET_INFO						# ��ʾĿ����Ϣ���ڣ�targetInfo
EVT_ON_HIDE_TARGET_INFO						# ���Ŀ����Ϣ����

# helper( by hyw )
EVT_ON_SHOW_SYS_HELP						# ��ʾϵͳ������title���������⣬content����������
EVT_ON_NOTIFY_COURSE_HELPS					# ��ʾ���̰�����ʾ��ť��,duration : ��ť��ʾ�ĳ���ʱ�䣬sects ���Ի�ȡ�������ݵ� pyDataSection �б�
EVT_ON_SHOW_COURSE_HELP						# ��ʾ���̰�����content����������

# bankwindow( by hyw )
EVT_ON_SHOW_BANK_WINDOW						# ��ʾ��洰��
EVT_ON_HIDE_BANK_WINDOW						# ��˿�洰��
EVT_ON_UPDATE_BANKITEM						# ���¿����Ʒ��index����Ʒ������item����Ʒ��Ϣʵ������ BankFacade �ж��壩
EVT_ON_BANK_MONEY_CHANGED					# ����Ǯ�ı䣬amount��Ŀǰ��Ǯ����

# function panel( by hyw )
EVT_ON_TOGGLE_PROPERTY_WINDOW				# ��ʾ�������Դ���
EVT_ON_TOGGLE_QUEST_WINDOW					# ��ʾ�����б�
EVT_ON_TOGGLE_SKILL_WINDOW					# ��ʾ�����б�
EVT_ON_TOGGLE_FRIENDS_WINDOW				# ��ʾ���Ѵ���
EVT_ON_TOGGLE_KITBAG						# ��ʾ��Ʒװ������
EVT_ON_TOGGLE_CORPS_WINDOW					# ��ʾ������Ϣ����
EVT_ON_TOGGLE_SYSTEM_WINDOW					# ��ʾϵͳ���ô���

# decoration combiner ( hyw )
EVT_ON_SHOW_EQUIP_MERGE							# ��ʾ��Ʒ�ϳɴ���
EVT_ON_SET_EQUIP_MERGE_TYPES					# ������Ʒ���
EVT_ON_SET_EQUIP_MERGE_LEVELS					# ������Ʒ�ȼ�
EVT_ON_EQUIP_MERGE_TYPE_SELECTED				# ѡ��һ����Ʒ����
EVT_ON_EQUIP_MERGE_LEVEL_SELECTED				# ѡ��һ����Ʒ�ȼ�
EVT_ON_EQUIP_MERGE_PRECONDITION_CHANGED			# ���úϳ�����
EVT_ON_EQUIP_MERGE_PRECONDITION_STATUS_CHANGED	# ���úϳ�������״̬
EVT_ON_EQUIP_MERGE_REQUIRES_CHANGED				# ���ò�������
EVT_ON_EQUIP_MERGE_REQUIRES_STATUS_CHANGED		# ���ø����ϵ��Ƿ��㹻״̬
EVT_ON_EQUIP_MERGE_SUCCESS_CHANGED				# ���óɹ���
EVT_ON_EQUIP_MERGE_UPDATE_ITEM					# ����һ����Ʒ��
EVT_ON_EQUIP_MERGE_OVERPASSED					# �����Ƿ���ȫ���Ϻϳ�����
EVT_ON_EQUIP_MERGE_RESULT						# �ϳɽ�������


# process space loading( by hyw )
EVT_ON_SHOW_LOADING_PROGRESS				# ֪ͨ���� space, ground��������ͼ


# fly text( by hyw )
EVT_ON_SHOW_DAMAGE_VALUE					# ��ʾ�ܻ��˺�ֵ��entityID: �������� entityID, lastTime: ���ֳ���ʱ�䣬text: �˺�ֵ��color: �ı���ɫ
EVT_ON_SHOW_MISS_ATTACK						# ��ʾΪ����, entityID: �������� entityID
EVT_ON_SHOW_DEADLY_ATTACK					# ��ʾ�����˺�, entityID: �������� entityID
EVT_ON_SHOW_SKILL_NAME						# ��ʾ�ͷŵļ������� entityID: ʩ����ID lastTime���ֳ���ʱ�䣨Ĭ��3�룩

# friend
EVT_ON_FRIEND_MSG							# ������Ϣ����: state

EVT_ON_FRIEND_ADD_FRIEND_INFO				# ��Ӻ�����Ϣ: name, classes, level, position, groupID, time, online
EVT_ON_FRIEND_CHANGE_FRIEND_INFO			# �ı������Ϣ: name, classes, level, position, groupID, time, online
EVT_ON_FRIEND_REMOVE_FRIEND_INFO			# �Ƴ�������Ϣ��name

EVT_ON_FRIEND_CHANGE_PLAYER_GROUP			# �ı�����飺playerName, groupID

# װ���ֽ�
EVT_ON_EQUIP_ANALYZE_SHOW_WINDOW			# ��������
EVT_ON_EQUIP_ANALYZE_SELECT_ITEM			# itemInfo ѡ��ֽ����Ʒ
EVT_ON_EQUIP_ANALYZE_ITEMS					# equips ��ѡ�����Ʒ�б� [ItemInfo,...]
EVT_ON_EQUIP_ANALYZE_MSG					# msg, state ��ʾ��Ϣ

# ���Ϻϳ�
EVT_ON_EQUIP_COMPOSE_ITEM					# ItemInfo �����Ʒ
EVT_ON_EQUIP_COMPOSE_MSG					# msg, state ��ʾ��Ϣ
EVT_ON_EQUIP_COMPOSE_READY					# bool �Ƿ�׼���úϳ�
EVT_ON_EQUIP_COMPOSE_CONDITION				# ItemInfo, odds, needCount, existCount, money �ϳ�����

# װ��ǿ��
EVT_ON_EQUIP_INTENSIFY_ITEM					# ItemInfo  �����Ʒ
EVT_ON_EQUIP_INTENSIFY_ITEM_GRADATION		# gradation ) # ��Ʒ����һ�ײ�
EVT_ON_EQUIP_INTENSIFY_ODDS					# odds ǿ���ɹ���
EVT_ON_EQUIP_INTENSIFY_STONE				# ItemInfo, needCount, hasCount ǿ����Ҫ�Ļ���ʯ��Ϣ������ʯ�������е�����
EVT_ON_EQUIP_INTENSIFY_CRYSTAL				# ItemInfo, count ǿ����Ҫ��嫺�ˮ��
EVT_ON_EQUIP_INTENSIFY_MSG					# msg, state ��ʾ��Ϣ
EVT_ON_EQUIP_INTENSIFY_READY				# bool ��ʾ��Ϣ

#���Ϻϳ�
EVT_ON_SET_STUFF_MERGE_TYPES				# ���ò������
EVT_ON_SHOW_STUFF_MERGE						# ��ʾ���Ϻϳɴ���

#pk system
EVT_ON_ENTITY_PK_STATE_CHANGED				#PK״̬�ı�
"""


"""
����
	ʹ���¼�ǰ����Ϊ����ȷ�����¼�����һ������Ϣ�ꡱ��������Ϣ������д����ģ��Ŀ�ͷ��

������
class test:
	def __init__( self ):
		registerEvent( "EVENT_STRING", self )	# �ڳ�ʼ����ʱ�����Ҫ��ʱ��ע��ĳ���¼�

	def __del__( self ):
		unregisterEvent( "EVENT_STRING", self )	# ��ʵ����ɾ����ʱ�������Ҫ��ʱ��ȡ����ĳ���¼���ע��

	def onEvent( self, name, *args ):			# ����ע��ʵ������������������������ڱ���������Ϣ����ʱ�Զ�����ע��ʵ����onEvent()����
		if name == "EVENT_STRING":
			do some thing in here
		else:
			do other
"""

"""
2006.02.24: writen by penghuawei
2009.02.26: tidy up by huangyongwei
ע�⣺
	��ע�����ʵ������������������onEvent
	����Ϣ����ʱ��onEvent ���ᱻ������onEvent �ĵ�һ���������������������Ϣ�꣬������ſ��������ɸ���������ͬ����Ϣ���������һ����
"""

import sys
import weakref
from bwdebug import *


g_events = {}				# key����Ϣ�꣬����Ϊ str��value���� _Event ��ʵ��


# --------------------------------------------------------------------
# ʵ���¼���ͻ���ȫ���¼���( ÿ����Ϣ���Ӧһ���¼�ʵ�� )
# --------------------------------------------------------------------
class _Event:									# ��Ϊģ��˽�У�hyw--2009.02.26��
	def __init__( self, name ):
		self._name = name						# �¼�����
		self._receivers = []					# �¼������ߣ�ע��ÿ����Ϣ�����ж��������( renamed from 'handlers' to 'receiver' by hyw--2009.02.26 )

	def fire( self, *argv ):
		"""
		�����¼�
		"""
		for index in xrange( len( self._receivers ) - 1, -1, -1 ):
			receiver = self._receivers[index]()
			if receiver:
				try:
					receiver.onEvent( self._name, *argv )
				except Exception, errstr:
					err = "error take place when event '%s' received by %s:\n" % ( self._name, str( receiver ) )
					EXCEHOOK_MSG( err )
			else:
				self._receivers.pop( index )

	def addReceiver( self, receiver ):
		"""
		�����Ϣ������
		"""
		wr = weakref.ref( receiver )
		if wr not in self._receivers :
			self._receivers.append( wr )

	def removeHandler( self, receiver ):
		"""
		ɾ����Ϣ������
		"""
		receive = weakref.ref( receiver )
		if receive in self._receivers :
			self._receivers.remove( receive )

	def clearReceivers( self ):
		"""
		��������¼�������
		"""
		self._receivers=[]



# --------------------------------------------------------------------
# ʵ���¼�ע��͵����ӿ�
# --------------------------------------------------------------------
def registerEvent( eventKey, receiver ):
	"""
	ע��һ���¼�
	@type			eventKey : str
	@param			eventKey : ��Ϣ��
	@type			reveiver : class instance
	@param			reveiver : ��Ϣ�����ߣ�ע�⣺���¼������߱������������onEvent��
	"""
	try:
		event = g_events[eventKey]
	except KeyError:
		event = _Event( eventKey )
		g_events[eventKey] = event
	event.addReceiver( receiver )

def unregisterEvent( eventKey, receiver ):
	"""
	ɾ��һ����Ϣ������
	@type			eventKey : str
	@param			eventKey : ��Ϣ��
	@type			reveiver : class instance
	@param			reveiver : Ҫɾ������Ϣ������
	"""
	try:
		g_events[eventKey].removeHandler( receiver )
	except KeyError:
		err = "receiver is not in list of enevt '%s''" % eventKey

def fireEvent( eventKey, *args ):
	"""
	����ָ���¼�
	@type			eventKey : str
	@param			eventKey : Ҫ��������Ϣ����
	@type			*args	 : all types
	@param			*args	 : ��Ϣ����
	"""
	try:
		g_events[eventKey].fire( *args )
	except KeyError:
		pass

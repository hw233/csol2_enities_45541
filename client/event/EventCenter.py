# -*- coding: gb18030 -*-

"""
事件标记

EVT_OPEN_QUEST_WINDOW
EVT_OPEN_QUEST_LOG_WINDOW
EVT_ON_NPC_QUEST_STATE_CHANGED				# 显示 NPC 的任务状态,

EVT_OPEN_GOSSIP_WINDOW						# None; fire while a gossip is receive.
EVT_END_GOSSIP								# None; 关闭对话窗口
EVT_QUEST_SHOW_DETAIL_TEXT					# None; 显示任务对话详细内容(接任务时).
EVT_QUEST_SHOW_INCOMPLETE_TEXT				# None; 显示任务目标还没有完成时的对话
EVT_QUEST_SHOW_PRECOMPLETE_TEXT				# None; 显示任务目标已完成时的对话
EVT_QUEST_SHOW_COMPLETE_TEXT				# None; 显示完成任务后的对话
EVT_QUEST_SHOW_PREBEGIN_TEXT				# None; 显示接任务之前的废话(过渡)对白
EVT_ON_QUEST_TASK_STATE_CHANGED				# questID; 通知有一个任务的目标状态被改变
EVT_ON_QUEST_LOG_ADD						# questID; fire while a quest log is add.
EVT_ON_QUEST_LOG_REMOVED					# questID; fire while a quest log is abandon.
EVT_ON_QUEST_LOG_SELECTED					# questID; fire while a quest log is selected.
EVT_ON_QUEST_REWARDS_CHANGED				# questID; fire while a quest log is receive reward list.
EVT_ON_RECEIVE_CHAT_COMMON_MESSAGE			# 在聊天中显示普通信息，channelID, msg;
EVT_ON_RECEIVE_CHAT_SYSTEM_MESSAGE			# 在聊天中显示系统信息，channelID, msg;
EVT_ON_SHOW_LEARN_SKILL_WINDOW				# None; show learn skill window
EVT_ON_SKILL_LEARNT							# None; fire while player learnt a skill

# team message
EVT_ON_INVITE_JOIN_TEAM						# inviterName; someone invite player join in team
EVT_ON_INVITE_FOLLOW						# entityid 邀请者的id, 邀请玩家跟随
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
EVT_ON_TEAM_DISBANDED						# 队伍解散通知
EVT_ON_TEAM_MEMBER_REJOIN					# oldEntityID, newEntityID, 玩家重新上线，重新加入队伍

# corps about
EVENT_CORPS_ADDMEMBER_INFO					# PlayerName,职位,等级,位置,职业,贡献,功勋,状态,上次离线时间;
EVENT_CORPS_CHANGEMEMBER_INFO				# PlayerName,职位,等级,位置,职业,贡献,功勋,状态,上次离线时间;
EVENT_CORPS_DELMEMBER_INFO 					# PlayerName;
EVENT_CORPS_UPDATEMEMBERCOUNT_INFO			# MemberMaxCount

# merchant message
EVT_ON_BUYBAG_INFO_CHANGE					# order, itemInfo; 通知购物车中某个位置的物品信息改变，物品不存在了则itemInfo=None; itemInfo is instance of ItemInfo
EVT_ON_BUYBAG_PRICE_TOTAL_CHANGED			# price; 欲购买的商品总价值
EVT_ON_TRADE_WITH_NPC						# chapmanEntity; 与某个NPC进行交易

EVT_ON_INVOICES_BAG_SPACE_CHANGED			# space; 商人的商品数量
EVT_ON_INVOICES_BAG_INFO_CHANGED			# order, itemInfo; 有一个商品内容被改变，物品不存在了则itemInfo=None; itemInfo is instance of ItemInfo

EVT_ON_SELLBAG_INFO_CHANGE					# order, itemInfo; 通知购物车中某个位置的物品信息改变，物品不存在了则itemInfo=None; itemInfo is instance of ItemInfo
EVT_ON_SELLBAG_PRICE_TOTAL_CHANGED			# price; 欲购买的商品总价值
EVT_ON_PLAYER_INVOICES_BAG_SPACE_CHANGED	# space; 玩家的可出售物品数量
EVT_ON_PLAYER_INVOICES_BAG_INFO_CHANGED		# order, itemInfo; 有一个商品内容被改变，物品不存在了则itemInfo=None; itemInfo is instance of ItemInfo

# ItemsBag
EVT_ON_KITBAG_ITEM_LOCK_CHANGED				# kitbagOrder, itemOrder, isLocked; 某个格子的锁定状态改变
EVT_ON_KITBAG_ITEM_INFO_CHANGED				# kitbagOrder, itemOrder, itemInfo; 某个位置的物品信息改变，物品不存在了则itemInfo=None；

# player role about
EVT_ON_ROLE_MONEY_CHANGED					# old, new; 玩家金钱改变
EVT_ON_ROLE_EXP_CHANGED						# exp, maxExp; 当前经验,下一级升级经验
EVT_ON_ROLE_HP_CHANGED						# hp, hpMax; 当前hp,最大hp
EVT_ON_ROLE_MP_CHANGED						# mp, mpMax; 当前mp,最大mp
EVT_ON_ROLE_EN_CHANGED						# en, enMax; 当前enerey,最大enerey
EVT_ON_ROLE_LEVEL_CHANGED					# level; 等级
EVT_ON_ROLE_POTENTIAL_CHANGED				# value; 潜能
EVT_ON_ROLE_PHYSICS_DAMAGE_CHANGED			# value; 物理攻击
EVT_ON_ROLE_ELEMENT_DAMAGE_CHANGED			# value; 自然攻击
EVT_ON_ROLE_POISON_DAMAGE_CHANGED			# value; 毒素攻击
EVT_ON_ROLE_SPIRIT_DAMAGE_CHANGED			# value; 精神攻击
EVT_ON_ROLE_ELEMENT_RESIST_CHANGED			# value; 自然防卸
EVT_ON_ROLE_POISON_RESIST_CHANGED			# value; 毒素防卸
EVT_ON_ROLE_SPIRIT_RESIST_CHANGED			# value; 精神防卸
EVT_ON_ROLE_HITTED_CHANGED					# value; 命中
EVT_ON_ROLE_DODGE_CHANGED					# value; 闪避
EVT_ON_ROLE_DOUBLE_DAMAGE_CHANCE_CHANGED	# value; 致命一击机率
EVT_ON_ROLE_MOVED							# isMoving; 移动状态改变
EVT_ON_ROLE_BEGIN_COOLDOWN					# cooldownType, overTime; 触发一个cooldown
EVT_ON_ROLE_ENTER_WORLD						# 玩家进入游戏世界, player: 玩家
EVT_ON_ROLE_LEAVE_WORLD						# 玩家离开游戏世界, player: 玩家

# offline ( by hyw )
EVT_ON_ROLE_QUIT							# 退出角色。None
EVT_ON_GAME_LOGOFF							# 失去与服务器的连接。None
EVT_ON_GAME_QUIT							# 退出游戏客户端。None
EVT_ON_GAME_RECONNECT						# 断开服务器，重新连接

# about skill of player role( by hyw )
EVT_ON_PLAYERROLE_ADD_SKILL					# 玩家技能增加，skillID：增加的技能 ID
EVT_ON_PLAYERROLE_REMOVE_SKILL				# 玩家技能被删除，skillID: 被删除的技能 ID
EVT_ON_PLAYERROLE_UPDATE_SKILL				# 玩家技能更新，oldSkillID: 旧技能 ID, newSkillID: 新技能 ID

EVT_ON_ROLE_ADD_SKILL						# 添加一项技能，skillInfo : SkillItem 实例（位于 GUIFacade.SkillListFacade 中）
EVT_ON_ROLE_REMOVE_SKILL					# 删除一项技能，skillID	  : skillID
EVT_ON_ROLE_UPDATE_SKILL						# 更新一个技能，oldSkillID, newSkillID

# about buff ( by hyw )
EVT_ON_ROLE_ADD_BUFF						# 添加 buffer。buffData ：buff 信息数据
EVT_ON_ROLE_ADD_DUFF						# 添加 buffer。buffData ：duff 信息数据
EVT_ON_ROLE_REMOVE_BUFF						# 删除一个 buff。index ：buff 索引
EVT_ON_ROLE_REMOVE_DUFF						# 删除一个 duff。index ：duff 索引

# swap item
EVT_ON_RSI_INVITE_SWAP_ITEM					# name; 邀请玩家间交易
EVT_ON_RSI_SWAP_ITEM_BEGIN					# name; 开始进行交易(显示窗口)
EVT_ON_RSI_SWAP_ITEM_END					# None; 交易结束(关闭窗口)
EVT_ON_RSI_DST_ITEM_CHANGED					# order, itemInfo; 对方某个位置的物品信息改变
EVT_ON_RSI_DST_MONEY_CHANGED				# order, quantity; 对方金钱改变
EVT_ON_RSI_SELF_ITEM_CHANGED				# order, itemInfo; 自己某个位置的物品信息改变
EVT_ON_RSI_SELF_MONEY_CHANGED				# order, quantity; 自己金钱改变
EVT_ON_RSI_DST_SWAP_STATE_CHANGED			# accept1State, accept2State; 第一次确认状态，第二次确认状态；True为确认，False为没有确认
EVT_ON_RSI_SELF_SWAP_STATE_CHANGED			# accept1State, accept2State; 第一次确认状态，第二次确认状态；True为确认，False为没有确认

# login( by hyw )
EVT_ON_SHOW_LOGIN_DIALOG					# 显示登录界面。defAccount : 默认账号， defPassword : 默认密码
EVT_ON_HIDE_LOGIN_DIALOG					# 隐藏登录界面
EVT_ON_LOGIN_SUCCEED						# 登录成功。None
EVT_ON_LOGIN_FAIL							# 登录失败。None
EVT_ON_CANCEL_LOGIN							# 取消登录。None
EVT_ON_SHOW_SERVER_LIST						# 显示服务器列表
EVT_ON_PREVIEW_ROLE_ENTERWOLD				# 创建了一个 PreviewRole

# role selector( by hyw )
EVT_ON_SHOW_ROLE_SELECTOR					# 显示角色选择界面。
EVT_ON_HIDE_ROLE_SELECTOR					# 隐藏角色选择界面。

EVT_ON_ROLE_SELECTED						# 选择登录角色。id, name, level, raceClass
EVT_ON_ROLE_DESELECTED						# 取消选择。
EVT_ON_ROLE_DELETED							# 删除一个角色。roleID: 被删除的角色的 entity id
EVT_ON_HIDE_ROLE_SELECTOR					# 隐藏角色选择界面

# role creator( by hyw )
EVT_ON_SHOW_ROLE_CREATOR					# 显示角色创建窗口
EVT_ON_ROLE_CHOICE							# 选择某个要创建的角色。roleInfo : 角色信息
EVT_ON_ROLE_UNCHOOSE						# 取消选择某个选中的创建角色。
EVT_ON_NAME_VERIFIED						# 返回名字验证结果。allow : 是否允许使用该名字
EVT_ON_ROLE_CREATE_FEEDBACK					# 创建玩家后返回，successful:是否创建成功

# chat( hyw )
EVT_ON_RECEIVE_STATUS_MESSAGE					# 接到服务器状态时被触发，statusID：状态ID，msg：状态注释文本
EVT_ON_SHOW_CHAT_MESSAGE					# 接收到玩家发言时被触发，player：玩家，msg：信息文本

# floatname( hyw )
EVT_ON_ENTITY_ENTER_WORLD					# entity 进入世界时被触发，entity：entity实体
EVT_ON_ENTITY_LEAVE_WORLD					# entity 离开世界时被触发，entityID：离开世界的 entity 实体
EVT_ON_ENTITY_LEVEL_CHANGED					# entity 等级改变时被触发，oldLevel, newLevel
EVT_ON_ENTITY_HP_CHANGED					# entity 的 HP 改变时被触发，hp, hpMax
EVT_ON_ENTITY_TITLE_CHANGED					# entity 头衔改变时被调用，oldTitle, newTitle

# quickbar( by hyw )
EVT_ON_QUICKBAR_UPDATE_ITEM					# 更新 quickbar， itemInfo：快捷格信息
EVT_ON_UPDATE_QBSHORTCUT					# 更新快捷键，shortcut：快捷键（字母键键值，辅助键键值），shortcutText：快捷键标签，如 "CTRL+H"
EVT_ON_LOCK_QUICKBARITEM					# 锁定某个快捷格，index 被锁定的快捷格的索引

# targetinfo( by hyw )
EVT_ON_SHOW_TARGET_INFO						# 显示目标信息窗口，targetInfo
EVT_ON_HIDE_TARGET_INFO						# 因此目标信息窗口

# helper( by hyw )
EVT_ON_SHOW_SYS_HELP						# 显示系统帮助，title：帮助主题，content：帮助内容
EVT_ON_NOTIFY_COURSE_HELPS					# 显示过程帮助提示按钮）,duration : 按钮显示的持续时间，sects 可以获取帮助内容的 pyDataSection 列表
EVT_ON_SHOW_COURSE_HELP						# 显示过程帮助，content：帮助内容

# bankwindow( by hyw )
EVT_ON_SHOW_BANK_WINDOW						# 显示库存窗口
EVT_ON_HIDE_BANK_WINDOW						# 因此库存窗口
EVT_ON_UPDATE_BANKITEM						# 更新库存物品，index：物品索引，item：物品信息实例（在 BankFacade 中定义）
EVT_ON_BANK_MONEY_CHANGED					# 库存金钱改变，amount：目前金钱数量

# function panel( by hyw )
EVT_ON_TOGGLE_PROPERTY_WINDOW				# 显示人物属性窗口
EVT_ON_TOGGLE_QUEST_WINDOW					# 显示任务列表
EVT_ON_TOGGLE_SKILL_WINDOW					# 显示技能列表
EVT_ON_TOGGLE_FRIENDS_WINDOW				# 显示好友窗口
EVT_ON_TOGGLE_KITBAG						# 显示物品装备窗口
EVT_ON_TOGGLE_CORPS_WINDOW					# 显示军团信息窗口
EVT_ON_TOGGLE_SYSTEM_WINDOW					# 显示系统设置窗口

# decoration combiner ( hyw )
EVT_ON_SHOW_EQUIP_MERGE							# 显示饰品合成窗口
EVT_ON_SET_EQUIP_MERGE_TYPES					# 设置饰品类别
EVT_ON_SET_EQUIP_MERGE_LEVELS					# 设置饰品等级
EVT_ON_EQUIP_MERGE_TYPE_SELECTED				# 选择一个饰品类型
EVT_ON_EQUIP_MERGE_LEVEL_SELECTED				# 选择一个饰品等级
EVT_ON_EQUIP_MERGE_PRECONDITION_CHANGED			# 设置合成条件
EVT_ON_EQUIP_MERGE_PRECONDITION_STATUS_CHANGED	# 设置合成条件的状态
EVT_ON_EQUIP_MERGE_REQUIRES_CHANGED				# 设置材料需求
EVT_ON_EQUIP_MERGE_REQUIRES_STATUS_CHANGED		# 设置各材料的是否足够状态
EVT_ON_EQUIP_MERGE_SUCCESS_CHANGED				# 设置成功率
EVT_ON_EQUIP_MERGE_UPDATE_ITEM					# 更新一个物品格
EVT_ON_EQUIP_MERGE_OVERPASSED					# 设置是否完全符合合成条件
EVT_ON_EQUIP_MERGE_RESULT						# 合成结束返回


# process space loading( by hyw )
EVT_ON_SHOW_LOADING_PROGRESS				# 通知加载 space, ground：背景贴图


# fly text( by hyw )
EVT_ON_SHOW_DAMAGE_VALUE					# 显示受击伤害值，entityID: 被攻击的 entityID, lastTime: 文字持续时间，text: 伤害值，color: 文本颜色
EVT_ON_SHOW_MISS_ATTACK						# 显示为命中, entityID: 被攻击的 entityID
EVT_ON_SHOW_DEADLY_ATTACK					# 显示致命伤害, entityID: 被攻击的 entityID
EVT_ON_SHOW_SKILL_NAME						# 显示释放的技能名称 entityID: 施法者ID lastTime文字持续时间（默认3秒）

# friend
EVT_ON_FRIEND_MSG							# 操作信息回馈: state

EVT_ON_FRIEND_ADD_FRIEND_INFO				# 添加好友信息: name, classes, level, position, groupID, time, online
EVT_ON_FRIEND_CHANGE_FRIEND_INFO			# 改变好友信息: name, classes, level, position, groupID, time, online
EVT_ON_FRIEND_REMOVE_FRIEND_INFO			# 移除好友信息：name

EVT_ON_FRIEND_CHANGE_PLAYER_GROUP			# 改变玩家组：playerName, groupID

# 装备分解
EVT_ON_EQUIP_ANALYZE_SHOW_WINDOW			# 开启窗口
EVT_ON_EQUIP_ANALYZE_SELECT_ITEM			# itemInfo 选择分解的物品
EVT_ON_EQUIP_ANALYZE_ITEMS					# equips 可选择的物品列表 [ItemInfo,...]
EVT_ON_EQUIP_ANALYZE_MSG					# msg, state 提示信息

# 材料合成
EVT_ON_EQUIP_COMPOSE_ITEM					# ItemInfo 添加物品
EVT_ON_EQUIP_COMPOSE_MSG					# msg, state 提示信息
EVT_ON_EQUIP_COMPOSE_READY					# bool 是否准备好合成
EVT_ON_EQUIP_COMPOSE_CONDITION				# ItemInfo, odds, needCount, existCount, money 合成条件

# 装备强化
EVT_ON_EQUIP_INTENSIFY_ITEM					# ItemInfo  添加物品
EVT_ON_EQUIP_INTENSIFY_ITEM_GRADATION		# gradation ) # 物品的下一阶层
EVT_ON_EQUIP_INTENSIFY_ODDS					# odds 强化成功率
EVT_ON_EQUIP_INTENSIFY_STONE				# ItemInfo, needCount, hasCount 强化需要的火云石信息，火云石数量和有的数量
EVT_ON_EQUIP_INTENSIFY_CRYSTAL				# ItemInfo, count 强化需要的瀚海水晶
EVT_ON_EQUIP_INTENSIFY_MSG					# msg, state 提示信息
EVT_ON_EQUIP_INTENSIFY_READY				# bool 提示信息

#材料合成
EVT_ON_SET_STUFF_MERGE_TYPES				# 设置材料类别
EVT_ON_SHOW_STUFF_MERGE						# 显示材料合成窗口

#pk system
EVT_ON_ENTITY_PK_STATE_CHANGED				#PK状态改变
"""


"""
规则：
	使用事件前必须为你所确立的事件定义一个“消息宏”，并将消息宏归类地写到本模块的开头处

样例：
class test:
	def __init__( self ):
		registerEvent( "EVENT_STRING", self )	# 在初始化的时候或需要的时候注册某个事件

	def __del__( self ):
		unregisterEvent( "EVENT_STRING", self )	# 在实例被删除的时候或不再需要的时候取消对某个事件的注册

	def onEvent( self, name, *args ):			# 所有注册实例都必须有这个方法，它会在被触发的消息产生时自动调用注册实例的onEvent()方法
		if name == "EVENT_STRING":
			do some thing in here
		else:
			do other
"""

"""
2006.02.24: writen by penghuawei
2009.02.26: tidy up by huangyongwei
注意：
	被注册的类实例或类必须包含方法：onEvent
	当消息发出时，onEvent 将会被触发，onEvent 的第一个参数是上面所定义的消息宏，后面接着可以有若干个参数（不同的消息，其参数不一样）
"""

import sys
import weakref
from bwdebug import *


g_events = {}				# key：消息宏，类型为 str，value：是 _Event 类实例


# --------------------------------------------------------------------
# 实现事件类客户端全局事件类( 每个消息宏对应一个事件实例 )
# --------------------------------------------------------------------
class _Event:									# 改为模块私有（hyw--2009.02.26）
	def __init__( self, name ):
		self._name = name						# 事件名称
		self._receivers = []					# 事件接收者，注意每条消息可以有多个接收者( renamed from 'handlers' to 'receiver' by hyw--2009.02.26 )

	def fire( self, *argv ):
		"""
		触发事件
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
		添加消息接收者
		"""
		wr = weakref.ref( receiver )
		if wr not in self._receivers :
			self._receivers.append( wr )

	def removeHandler( self, receiver ):
		"""
		删除消息接收者
		"""
		receive = weakref.ref( receiver )
		if receive in self._receivers :
			self._receivers.remove( receive )

	def clearReceivers( self ):
		"""
		清除所有事件接收者
		"""
		self._receivers=[]



# --------------------------------------------------------------------
# 实现事件注册和吊销接口
# --------------------------------------------------------------------
def registerEvent( eventKey, receiver ):
	"""
	注册一个事件
	@type			eventKey : str
	@param			eventKey : 消息宏
	@type			reveiver : class instance
	@param			reveiver : 消息接收者（注意：该事件接收者必须包含方法：onEvent）
	"""
	try:
		event = g_events[eventKey]
	except KeyError:
		event = _Event( eventKey )
		g_events[eventKey] = event
	event.addReceiver( receiver )

def unregisterEvent( eventKey, receiver ):
	"""
	删除一个消息接收者
	@type			eventKey : str
	@param			eventKey : 消息宏
	@type			reveiver : class instance
	@param			reveiver : 要删除的消息接收者
	"""
	try:
		g_events[eventKey].removeHandler( receiver )
	except KeyError:
		err = "receiver is not in list of enevt '%s''" % eventKey

def fireEvent( eventKey, *args ):
	"""
	触发指定事件
	@type			eventKey : str
	@param			eventKey : 要触发的消息类型
	@type			*args	 : all types
	@param			*args	 : 消息参数
	"""
	try:
		g_events[eventKey].fire( *args )
	except KeyError:
		pass

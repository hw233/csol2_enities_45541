# -*- coding: gb18030 -*-
#
# $Id: message_logger.py

"""
日志写入模块
注：
下面的接口之所以没有使用动态的参数个数 原因是如果使用动态参数个数 那么某些调用如果参数数量错误 那么也不会表现出来
在数据库中出现参数不够的数据，也很难追踪，所以采用固定参数个数，以便在参数不够时可以知道调用的地方，虽然这样不是非
常美观。

使用规则：
把这些信息写道日志中，在日志工具那边自然有工具去处理这些行为。
主要包括提取这些数据，和分析这些数据两步。
bwdebug.DATABASE_LOG_MSG 这个方法的第一个参数是一个 数据表索引，说明这些数据会被记录到哪个表中。
每一个索引对应一个表，所以，如果需要新加入一个索引的时候，那就需要在
svn://172.16.0.234/home/svnroot/love3/trunk/bigworld/tools/server/message_logger.dbinfo.xml 中定义一个表。
否则日志信息将不会被存储。

"""

import Language
import sys
import bwdebug
import csdefine

"""
下面是action对照表 根据action可以获得该条数据的作用
deleteRole  				#删除角色
register					#注册账号
set_grade   				#设置权限
set_attr    				#设置玩家属性
set							#设置某人的persistentMapping属性中的值
set_temp					#设置某人的tempMapping属性中的值
goto						#进入一个场景
clone						#在entity当前位置创建一个npc entity
drop_item					#在当前位置扔一个物品
add_item					#给物品栏中增加一个物品
add_equip					#给物品栏中增加一个可以指定品质,前缀,孔数的装备
add_skill					#给某人增加一个技能
remove_skill				#删除某人的一个技能
set_level   				#设置玩家的等级
set_adult					#设置玩家是否成年
set_anti					#设置是否开启防沉迷系统
set_money					#设置玩家金钱
set_exp     				#设置玩家经验
set_potential 				#设置玩家潜能
set_speed   				#设置玩家的速度
family_create				#创建家族
family_addPrestige			#增加家族声望
family_quit					#设置家族相关 接受或拒绝加入家族
tong_create					#创建帮会
tong_quit					#设置家族相关 接受或拒绝加入家族
specialShop_open			#道具商城开业
specialShop_close			#道具商城关闭
specialShop_update			#道具商城更新
destroy_NPC					#摧毁指定NPC
accept_quest				#给实体添加指定的任务
set_quest_flag				#设置/清除实体身上某个任务的完成标记
tong_addMoney				#帮会增加金钱
tong_addActionVal			#增加帮会行动力
tong_addPrestige			#增加帮会声望
tong_addBuildVal			#增加帮会建设度
tong_addLevel				#增加帮会等级
tong_degrade				#降低帮会等级
tong_addhouqinVal			#增加帮会后勤度
tong_addResearchVal			#增加帮会研究度
tong_cancelDismiss  		#取消帮会解散指令
activity_control			#打开/关闭 一个活动
set_silver					#给某人设置银元宝
set_gold					#给某人设置金元宝
add_pet_calcaneus			#增加宠物根骨
set_pet_nimbus				#设置宠物灵性值
set_pet_life 				#设置宠物寿命
set_pet_joyancy				#设置宠物快乐度
set_pet_propagate_finish	#宠物繁殖完成
set_pet_storage_time		#设置宠物仓库剩余时间
wizCommand_set_pet_ability	#设置宠物成长度
dismiss_tong				#立刻解散帮会
set_xinglong_prestige		#设置兴隆镖局声望
set_changping_prestige		#设置昌平镖局声望
add_teachCredit				#增加功勋值
set_pk_value				#增加PK值
clean_behoof_record			#立刻解散帮会
add_treasure_map			#获得指定等级的藏宝图
add_title					#增加称号
remove_title				#清除称号
clean_activity_record		#清除活动标记
catch						#抓人
cometo						#到达他身边
kick						#踢人
block_account				#封锁帐号
unBlock_account				#解封账号
set_respawn_rate			#更新刷怪速度
set_loginAttemper			#设置登录排队调度状态
set_stone					#设置魂魄石
set_tong_contribute			#设置帮会贡献度
set_fabao_naijiu			#调整法宝耐久
set_fabao_max_naijiu		#调整法宝最大耐久上限
set_fabao_lim_naijiu		#调整法宝当前耐久度上限
set_fabao_level				#调整法宝等级
set_fabao_skill_level		#调整法宝技能等级
role_addQuest				#接受任务
role_completeQuest			#完成任务
role_abandonQuest			#放弃任务
use_Item					#使用物品
buy_specialItem				#购买收费物品
delete_item					#删除物品
add_item					#增加物品
buy_item					#购买物品
add_pet						#增加一个宠物
roleswap_item				#玩家交易物品
roleswap_money				#玩家交易金钱
roleswap_pet				#玩家交易宠物
pick_item					#拾取物品
vend_buyItem				#摆摊购买物品
handin_questitem			#上交任务物品
store_item					#银行存入物品
family_roleManage			#家族人员管理
create_delete_family		#创建和解散帮会
create_delete_tong			#创建和解散帮会
remove_pet					#删除宠物
drop_pet					#遗弃宠物
vend_pet					#摆摊出售宠物
store_pet					#存入宠物
takeout_pet					#取出宠物
login_out_game				#登入和登出游戏
consume_buy_specialItem  	#购买商城物品
consume_buy_roleExp 		#充代练宝石
consume_buy_petExp			#充宠物代练宝石
consume_quiz_usegold		#使用元宝答题
consume_pst_hire			#租用宠物仓库
consume_changeGoldToItem	#元宝票兑换
statisticPlayerNum			#服务器等待队列长度、登录队列长度、在线角色数量统计
role_updateLevel			#玩家升级
use_item					#使用物品
role_learn_skill			#玩家学习技能
role_update_skill			#玩家升级技能
pet_update_skill			#宠物升级技能
pet_learn_skill				#宠物学习技能
role_update_tongskill		#玩家升级帮会技能
role_learn_tongskill		#玩家学习帮会技能
vehicle_update_skill		#骑宠升级技能
vehicle_learn_skill			#骑宠学习技能
killed_by_role				#被玩家杀死
killed_by_monster			#被NPC杀死
messy_action				#杂乱行为
potential_change			#潜能变更
extend_storage				#扩充仓库
pet_reproduction			#宠物繁殖
tong_add_member				#帮会新加成员
tong_reduce_member			#帮会减少
tong_add_league				#帮户增加同盟
tong_reduce_league			#帮户减少同盟

"""

# 加入日志过滤，凡是在列表中的reason都不输出日志。
__LOG_DELETE_ITEM_REASONS_FILTER = set()			# csdefine.DELETE_ITEM_*
__LOG_ADD_ITEM_REASONS_FILTER = set()				# csdefine.ADD_ITEM_*
__LOG_ROLE_MONEYCHANGE_REASONS_FILTER = set()		# csdefine.CHANGE_MONEY_*
__LOG_ROLE_EXP_CHANGE_REASONS_FILTER = set()		# csdefine.CHANGE_EXP_*

if Language.LANG == Language.LANG_BIG5:
	# 繁体版专用过滤，以下数值列表中各值的意义请查看上面备注中相关前缀的定义。
	__LOG_DELETE_ITEM_REASONS_FILTER.update( [4,5,6,7,8,9,10,11,12,15,16,17,18,19,21,34,35,36,37,38,39,40,43,44,45,46,47,48,49,55,56,57,63,64,65,66,67,68,69,70,71,79,80,81,89,90,91,92] )
	__LOG_ADD_ITEM_REASONS_FILTER.update( [2,9,16,17,18,19,20,21,22,24,25,26,27,30,31,35,36,37,38,39,40,41,42,43,44,45,46,48,49,51,52,53,54,55,56,60,61,63,64,65,66,67,68,69,70,71,72,73,76,79,81,92,93,94,95,96,97,98,99,100,101,102,103,104,105] )
	__LOG_ROLE_MONEYCHANGE_REASONS_FILTER.update( [1,4,7,8,9,10,14,17,18,19,24,44,46,47,70,71,81,91] )
	__LOG_ROLE_EXP_CHANGE_REASONS_FILTER.update( [1,2,5,6,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,26,27,28,29,30,31,32,33,34,35] )



def LOG_ROLE_DELETE( action, account, roleDBID ):
	"""
	删除角色
	type = 000100200200 , action = deleteRole parameter1 = 删除的角色的DBID parameter2 = 账号的名称和DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 6,"||%s||%s||%s",action, roleDBID,  account )

def LOG_USE_GMCMMAND( action,command,paramStr,srcEntityDBID, dstEntityDBID,srcEntityGrade,extend = None ):
	"""
	GM命令日志:
	type = 000100900300 , action = GM命令本身 如: set_level parameter1 = 使用者的名字和DBID parameter2 = GM命令本身 如: set_level
	parameter3 = 参数，空格分开 parameter4 = 使用对象的名字和DBID（只针对玩家） parameter5 = 使用者的权限 parameter6 = 补充说明(如 set_level修改前等级)
	"""
	bwdebug.DATABASE_LOG_MSG( 7,"||%s||%s||%s||%s||%s||%s||%s",action, srcEntityDBID, command, paramStr, dstEntityDBID, srcEntityGrade, extend  )


def LOG_EXCEPTION(action,Type,message):
	"""
	异常信息:  将游戏里的重要调试信息写入数据库。
	type = 000100300100 , action = 自定义的错误日志分类(如 log写入出错的action 为log) parameter1 = 错误的类型(error warning)
	parameter2 = 错误信息的描述
	"""
	bwdebug.DATABASE_LOG_MSG( 8,"||%s||%s||%s",action,Type,message )

def LOG_BUY_SPECIALITEM(action,uid,item_name,num,gold,silver,OperatorName):
	"""
	购买收费道具记录：
	type = 000400150200, action = buy_specialItem parameter1 = 购买的玩家的名字和DBID parameter2 = 购买的物品唯一ID parameter3 = 购买物品的名称
	parameter4= 购买物品的数量 parameter5 = 花费的金元宝数 parameter6 = 花费的银元宝数
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,OperatorName,uid,item_name,num,gold,silver )

def LOG_DELETE_ITEM( uid,item_name,num,OperatorName,reason ):
	"""
	删除物品（暂时无此GM命令或者外部功能）:
	type = 000200400100, action = delete_item parameter1 = 操作的玩家的名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量  parameter5 = 删除原因
	"""
	if reason in __LOG_DELETE_ITEM_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 27,"||delete_item||%s||%s||%s||%s||%s",OperatorName,uid,item_name,num,reason )

def LOG_ADD_ITEM(uid,item_name,num,OperatorName, reason ,playerLevel = ""):
	"""
	添加物品：
	type = 000200400110 action = add_item parameter1 = 操作者名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量  parameter5 = 增加的原因 parameter6 = 玩家等级
	"""
	if reason in __LOG_ADD_ITEM_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 27,"||add_item||%s||%s||%s||%s||%s||%s",OperatorName,uid,item_name,num,reason,playerLevel )


def LOG_BUY_ITEM( action,uid,item_name,num,operatorName,user_grade,chapmanID):
	"""
	购买道具（普通道具和收费道具分开记录，便于查找和统计）:
	type = 000200400310, action = buy_item parameter1 = 购买者名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量 parameter5 = 操作者权限 parameter6 = 商人的ID
	"""
	pass
	#bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,operatorName,uid,item_name,num,user_grade,chapmanID)

def LOG_GET_PET( action,petID,petName,playerName, reason ):
	"""
	获得宠物：
	type = 000200952400, action = add_pet  parameter1 = 玩家名字和DBID parameter2 = 宠物DBID  parameter3 = 宠物名字
	parameter5 = 添加的原因
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action,playerName,petID,petName, reason )


def LOG_REMOVE_PET(  action, petID,petName, user_name, reason ):
	"""
	删除宠物:
	type = 000200952420,action = remove_pet parameter1 = 操作的玩家的名字和DBID parameter2 = 宠物ID  parameter3 = 宠物名字
	parameter5 = 删除的原因
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action,user_name, petID,petName, reason )


def LOG_ROLE_TRADE( action,trade_uid,uid,itemName,itemAmount,traderName1,traderName2 ):
	"""
	用户交易:
	type = 000200400610, action = roleswap_item  parameter1 = 自己的名字和DBID  parameter2 = 自己交易的物品唯一ID
	parameter4 = 此次交易的唯一ID parameter5 = 自己交易的物品名称 parameter6 = 物品数量 parameter7 = 出售对象名字和DBID

	用户交易金钱
	type = 000200400610, action = roleswap_money parameter1 = 自己的名字和DBID parameter2 = NULL  parameter4 = 此次交易的唯一ID
	parameter5 = cschannel_msgs.ROLERELATION_INFO_7 parameter6 = 自己给出的创世币数量 parameter7 = 给与对象名字和DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,traderName1,uid,trade_uid,itemName,itemAmount,traderName2 )

def LOG_PET_TRADE(  action, trade_uid, petID, traderName1,traderName2 ):
	"""
	交易宠物：
	type = 000200952600, action = roleswap_pet  parameter1 = 出售方名字和DBID parameter2 = 宠物ID
	parameter4 = 此次交易的唯一ID  parameter5 = 购买对象名字和DBID
 	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action, traderName1,petID,trade_uid, traderName2 )

def LOG_VEND(  action, uid, itemName, itemAmount, traderName1,traderName2 ):
	"""
	摆摊交易：
	type = 000200400630, action = vend_buyItem  parameter1 = 出售方的名字和DBID parameter2 = 物品唯一ID
	parameter4 = 物品的名称  parameter5 = 物品的数量 parameter6 = 购买方的名称和DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action,traderName2, uid, itemName, itemAmount,traderName1 )

def LOG_VEND_PET( action, petDBID, traderName1,traderName2 ):
	"""
	摆摊出售宠物:
	type = 000200952710, action = vend_pet parameter1 = 出售方的名字和DBID parameter2 = 宠物的DBID
	parameter4 = 购买方的名称和DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s",action,traderName2, petDBID, traderName1 )

def LOG_GET_STORE_PET( action, petDBID, pet_name, roleName, event ):
	"""
	仓库存取宠物:
	type = 000200952720, action = store_pet parameter1 = 玩家的名字和DBID  parameter2 = 宠物的DBID parameter3 = 宠物的名字
	parameter5 = 存入宠物
	type = 000200952720, action = takeout_pet parameter1 = 玩家的名字和DBID parameter2 = 宠物的DBID parameter3 = 宠物的名字
	parameter5 = 取出宠物
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action, roleName, petDBID, pet_name, event )


def LOG_GET_STORE_ITEM( action, uid, item_name, num, roleName, event ):
	"""
	仓库存取:
	action = store_item parameter1 = 玩家的名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量   parameter6 = 事件说明(存入或则取出)
	type = 000200400810, action = takeout_item  parameter1 = 玩家的名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	 parameter4 = 物品数量  parameter6 = 事件说明(存入或则取出)
	type = 000200400810, action = bank_destroyItem parameter1 = 玩家的名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量  parameter6 = 事件说明(存入或则取出)
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action, roleName, uid, item_name, num, event )

def LOG_CHAT_MESSAGE( action, speaker , message ):
	"""
	频道信息:
	action = cryptonym_talk  parameter1 = 发言者的名字和DBID   parameter2 = 发言的内容
	"""
	bwdebug.DATABASE_LOG_MSG( 10,"||%s||%s||%s",action, speaker , message )


def LOG_CHARGE_SUCCESSFUL( action, transactionID, Account, ChargeType, GoldCoins, SilverCoins ):
	"""
	成功充值日志查询：
	type = 000400100100 , action = charge_successful parameter1 = 订单号 parameter2 = 账号 parameter3 = 充值类型
	parameter4 = 金元宝数 parameter5 = 银元宝数
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s||%s",action, transactionID, Account, ChargeType, GoldCoins, SilverCoins)

def LOG_RECEIVE_PRESENT( action, transactionID, giftPackage, expiredTime, parentDBID ):
	"""
	物品奖励领取日志(带订单和不带订单):
	action = take_present  parameter1 = 订单号(可能没有) parameter2 = 奖品包ID parameter3 = 领奖截止日期
	parameter4 = 账号
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, transactionID, giftPackage, expiredTime, parentDBID)

def LOG_RECEIVE_SILVERCOINS( action, transactionID, silverCoins, parentDBID ):
	"""
	银元宝领取日志:
	type = 000400100810 , action = take_silverCoins  parameter1 = 订单号 parameter2 = 银元宝数 parameter3 = 账号
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s",action, transactionID, silverCoins, parentDBID )

def LOG_RECEIVE_TESTACTIVITYGIFT( action, itemID, playerNameAndID, playerLevel, giftLevel ):
	"""
	封测奖励的领取:
	type = 000400100820 , action = take_testactivitygift parameter1 = 玩家的名字和ID  parameter2 = 奖品的ID parameter3 = 玩家的等级
	parameter5 = 封测奖品包的级别
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, playerNameAndID, itemID,  playerLevel, giftLevel )

def LOG_RECEIVE_TESTWEEKGIFT( action, playerNameAndID, playerLevel, silvercoins, week ):
	"""
	封测周奖励的领取:
	type = 000400100830 , action = take_testweekgift  parameter1 = 玩家的名字和ID parameter2 = 玩家的等级
	parameter4 = 银元宝的数量 parameter5 = 领取的周数
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, playerNameAndID, playerLevel, silvercoins, week )

def LOG_RECEIVE_SPREADERGIFT( action, itemID, playerNameAndID, playerLevel ):
	"""
	推广员奖励的领取:
	type = 000400100840 , action = take_spreadergift parameter1 = 玩家的名字和ID parameter2 = 奖品的ID  parameter3 = 玩家的等级
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s",action, playerNameAndID, itemID, playerLevel )

def LOG_CREATE_DELETE_TONG( action,tongName,creatorND,event,reason ):
	"""
	创建和删除帮会:
	type = 000500800100, action = create_tong  parameter1 = 创建的玩家名字和DBID parameter2 = 帮会名称  parameter3 = 创建帮会
	parameter4 = 创建原因

	type = 000500800100, action = delete_tong  parameter1 = None parameter2 = 帮会名称和DBID parameter3 = 解散帮会
	parameter4 = 解散原因
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s",action,creatorND,tongName,event,reason )

def LOG_TONG_FAMILYMANAGE( action, tongDBID, familyDBID, event ):
	"""
	删除和加入家族：

	type = 000500800200 action = tong_addfamily parameter1 = 帮会的名字和DBID parameter2 = 家族的名字和DBID
	parameter3= '加入帮会'

	type = 000500800200 action = tong_deletefamily parameter1 = 帮会的名字和DBID parameter2 = 家族的DBID
	parameter3 =  退出帮会以及原因和退出的原因的值 如 "退出家族:家族正常退出 reason = 0
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, tongDBID, familyDBID, event )

def LOG_TONG_MONEY_CHANGE( action, tongDBID, oldValue, newValue, value, reason ):
	"""
	帮会金钱改变
	type = 000500800300 action = tong_money_change parameter1 = 帮会名称和DBID parameter2 = 原来的创世币 parameter3 =现在的创世币
	parameter4 = 改变的值(+为增加-为减少) parameter5 = 创世币改变的原因
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action, tongDBID, oldValue, newValue, value, reason )

def LOG_TONG_BUILDING_CHANGE( tongDBID, tongName, buildingType, oldValue, newValue ):
	"""
	帮会建筑等级改变
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||building_change_level||%s||%s||%s||%s||%s", tongDBID, tongName, buildingType, oldValue, newValue )

def LOG_CREATE_DELETE_FAMILY( action, familyName, operatorDBID, event ):
	"""
	家族的创建和删除：
	type = 000500800300 action = create_family parameter1 = 创建者名字和DBID parameter2 = 家族名字
	parameter3 = 创建家族

	type = 000500800300 action = delete_family parameter2 = None parameter1 = 家族名字
	parameter3 = 解散家族
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, operatorDBID, familyName,  event )

def LOG_FAMILY_ROLEMANAGE( action, familyDBID, operatorDBID, roleDBID, event):
	"""
	家族删除和加入玩家：
	type = 000500800320 ,action = family_addrole parameter1 = 家族名称和DBID parameter2 = 操作者DBID  parameter3 = 加入的玩家的名字和DBID
	parameter4 = 加入家族

	type = 000500800320 ,action = family_deleterole parameter1 = 家族名称和DBID parameter2 = 退出玩家的名字和DBID  parameter3 = 退出玩家的家族权限
	parameter4 = 退出家族:操作者自己

	type = 000500800320 ,action = family_deleterole parameter1 = 家族名称和DBID parameter2 = 退出玩家的名字和DBID  parameter3 = 退出玩家的家族权限
	parameter4 = 踢出家族:操作者的名字和DBID 如 踢出家族:操作者 = 花花(10321)
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s", action, familyDBID, operatorDBID, roleDBID, event )

def LOG_ACCOUNT_LOGIN_LOGOUT( action, IP, account, event ):
	"""
	玩家账号登陆或则登出游戏
	type = 000100500100 , action = account_login parameter1 = 账号名称 parameter2 = IP
	parameter3 = 事件的解释	账号上线
	type = 000100500100 , action = account_logout parameter1 = 账号名称 parameter2 = IP
	parameter3 = 事件的解释	账号下线
	"""
	bwdebug.DATABASE_LOG_MSG( 15,"||%s||%s||%s||%s", action, account, IP,  event )

def LOG_ROLE_LOGON_LOGOFF( action, IP, account, roleName, lifetime, event ):
	"""
	玩家角色登陆或则登出游戏
	type = 000100500600 , action = role_logon parameter1 = 玩家的名字和DBID  parameter2 = 账号名称 parameter3 = IP
	parameter4 = 总在线时间 parameter5 = event	玩家上线
	type = 000100500600 , action = role_logoff parameter1 = 玩家的名字和DBID parameter2 = 账号名称 parameter3 = IP
	parameter4 = 总在线时间 parameter5 = event	玩家下线
	"""
	bwdebug.DATABASE_LOG_MSG( 15,"||%s||%s||%s||%s||%s||%s", action, roleName,account,IP, lifetime, event )

def LOG_PLAYER_CONSUME( action,account,gold,silver,event ):
	"""
	玩家的消费日志
	type = 000400150700 , action = consume_buy_specialItem  parameter1 = 账号名称 parameter2 = 消费的金元宝  parameter3 = 消费的银元宝
	parameter4 = 事件的解释															购买商城物品
	type = 000400150700 , action = consume_buy_roleExp ...... 后面的参数同上		充代练宝石
	type = 000400150700 , action = consume_buy_petExp								充宠物代练宝石
	type = 000400150700 , action = consume_quiz_usegold								使用元宝答题
	type = 000400150700 , action = consume_pst_hire									租用宠物仓库
	type = 000400150700 , action = consume_changeGoldToItem							元宝票兑换
	"""
	bwdebug.DATABASE_LOG_MSG( 16,"||%s||%s||%s||%s||%s", action, account, gold, silver, event )

def LOG_QUEST( action, playerName, playerGrade, questName, questID ):
	"""
	玩家任务相关的日志
	type = 000300670100 , action = role_abandonQuest  parameter1 = 玩家的名字和DBID  parameter2 = 玩家的权限
	parameter3 = 任务名称 parameter4 = 任务ID 放弃任务

	type = 000300670100 , action = role_completeQuest parameter1 = 玩家的名字和DBID  parameter2 = 玩家的权限
	parameter3 = 任务名称 parameter4 = 任务ID  完成任务

	type = 000300670100 , action = role_addQuest parameter1 = 玩家的名字和DBID   parameter2 = 玩家的权限
	parameter3 = 任务名称 parameter4 = 任务ID 接受任务
	"""
	pass		# 暂时不使用任务相关的日志,如果以后出现某种与之相关的BUG,再打开
	#bwdebug.DATABASE_LOG_MSG( 17,"||000300670100||%s||%s||%s||%s||%s", action, playerName, playerGrade, questName, questID )

def LOG_ROLE_SET_LEVEL( action, playerName, oldLevel, level, lifeTime ):
	"""
	玩家升级
	type = 000300670220 , action = role_updateLevel  parameter1 = 玩家的名字和DBID
	parameter3 = 原来的等级 parameter4 = 现在的等级 parameter5 = 角色总在线时间
	"""
	bwdebug.DATABASE_LOG_MSG( 24,"||%s||%s||%s||%s||%s", action, playerName, oldLevel, level, lifeTime  )

def LOG_SVRSTATUS( action, waitAccountNum, loginAccountNum, summation  ):
	"""
	type = 000600700800 , action = statisticPlayerNum parameter1 = 等待队列中的玩家数量 parameter2 = 登陆队列中的玩家数量
	parameter3 = 在线玩家的数量
	"""
	bwdebug.DATABASE_LOG_MSG( 18,"||%s||%s||%s||%s", action, waitAccountNum, loginAccountNum, summation )

def LOG_ROLE_ACTION( *arg ):
	"""
	玩家在游戏中的操作，由于数量众多不好统一且格式各异，所以采用动态参数个数..
	action = equipStiletto  parameter1 = 操作玩家名称和DBID parameter2 = 被打孔物品UID parameter3 = 打孔后物品的UID
	parameter4 = 物品名称 parameter5 = 物品原孔数 parameter6 = 物品现在的孔数

	action = equipSplit parameter1 = 操作玩家名称和DBID parameter2 = 被拆分装备UID parameter3 = 装备的名称


	action = equipStudded parameter1 = 操作玩家名称和DBID parameter2 = 被镶嵌物品UID parameter3 = 镶嵌后物品的UID
	parameter4 = 物品名称 parameter5 = 物品原孔使用数 parameter6 = 物品现在的孔使用数 parameter7 = 镶嵌增加的属性

	action = equipIntensify parameter1 = 操作玩家名称和DBID parameter2 = 被强化物品UID parameter3 = 强化后物品的UID  parameter4 = 物品名称
	parameter5 = 物品原强化数 parameter6 = 物品现在的强化数

	action = equipRebuild parameter1 = 操作玩家名称和DBID parameter2 = 被改造物品UID parameter3 = 改造后物品的UID  parameter4 = 物品名称
	parameter5 = 物品原品质 parameter6 = 物品现在的品质  parameter7 = 物品原前缀 parameter8 = 物品现在的前缀


	action = equipBind parameter1 = 操作玩家名称和DBID parameter2 = 被绑定物品UID parameter3 = 绑定后物品的UID  parameter4 = 物品名称
	parameter6 =‘装备绑定’

	type = 000300670230 action = specialCompose parameter1 = 操作玩家名称和DBID parameter2 = 合成物品的UID parameter3 = 物品名称


	action = equipMake parameter1 = 操作玩家名称和DBID parameter2 = 制造的装备UID parameter3 = 物品名称
	parameter4 = 装备原品质 parameter5 = 装备现品质 parameter6 = 装备原前缀 parameter7 = 装备现前缀

	action = stuffCompose parameter1 = 操作玩家名称和DBID parameter2 = 合成后的材料UID parameter3= 合成后的材料名称
	parameter4= 合成后的材料数量

	action = addTalismanLife  parameter1 = 操作玩家名称和DBID parameter2 = 法宝UID parameter3 = 法宝的名称
	parameter4 = 法宝原来的生存时间 parameter5 = 法宝现在的生存时间

	发送邮件
	action = send_mail  parameter1 = 发送者名字  parameter2 = 接受者名字, parameter3 = 邮件标题 parameter4 = 物品数量  parameter5 = 金币数量

	主动退信
	action = return_mail parameter1 = 发送者名字 parameter2 = 接受者名字, parameter3 = 邮件标题 parameter4 =  邮件ID

	系统退信
	action = return_mail_sys  parameter1 = 发送者名字 parameter2 = 接受者名字, parameter3 = 邮件标题 parameter4 =  邮件ID

	删除邮件 无论是系统删除还是手动删除
	action = delete_mail parameter1 = 发送者名字 parameter2 = 接受者名字, parameter3 = 邮件标题 parameter4 =  邮件ID

	阅读邮件
	action = read_mail parameter1 = 发送者名字 parameter2 = 接受者名字, parameter3 = 邮件标题 parameter4 =  邮件ID
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 17, message, *arg)


def LOG_SKILL( *arg ):
	"""
	type = 000300955231 action = role_update_skill parameter1 = 操作玩家名称和DBID parameter2 = 技能ID parameter3 = 原技能ID
	parameter4 = 消耗的潜能点 parameter5 = 消耗的金钱		玩家升级技能

	type = 000300955231 action = role_learn_skill parameter1 = 操作玩家名称和DBID parameter2 = 技能ID
	parameter3 = 消耗的潜能点 parameter4 = 消耗的金钱 		玩家学习技能

	type = 000300955231 action = pet_update_skill parameter1 = 操作玩家名称和DBID parameter2 = 宠物的名字和DBID  parameter3 = 技能ID
	parameter4 = 原技能ID 		宠物升级技能

	type = 000300955231 action = pet_learn_skill parameter1 = 操作玩家名称和DBID parameter2 = 宠物的名字和DBID  parameter3 = 技能ID
	宠物学习技能

	type = 000300955231 action = role_update_tongskill parameter1 = 操作玩家名称和DBID parameter2 = 技能ID parameter3 = 原技能ID
	parameter4 = 消耗的潜能点 parameter5 = 消耗的金钱 	玩家升级帮会技能

	type = 000300955231 action = role_learn_tongskill parameter1 = 操作玩家名称和DBID parameter2 = 技能ID
	parameter3 = 消耗的潜能点 parameter4 = 消耗的金钱		玩家学习帮会技能

	type = 000300955231 action = vehicle_update_skill parameter1 = 操作玩家名称和DBID parameter2 = 骑宠的DBID  parameter3 = 技能ID
	parameter4 = 原技能ID  parameter5 = 消耗的技能点 parameter6 = 消耗的金币		骑宠升级技能

	type = 000300955231 action = vehicle_learn_skill parameter1 = 操作玩家名称和DBID parameter2 = 骑宠的DBID  parameter3 = 技能ID
	parameter4 = 消耗的技能点 parameter5 = 消耗的金币	骑宠学习技能

	type = 000300955231 action = learn_new_skill parameter1 = 操作玩家名称和DBID parameter2 = 玩家等级 parameter3 = 技能ID

	type = 000300955231 action = oblive_skill parameter1 = 操作玩家名称和DBID parameter2 = 玩家等级  parameter3 = 技能ID

	type = 000300955231 action = level_up_skill parameter1 = 操作玩家名称和DBID parameter2 = 玩家等级  parameter3 = 技能ID
	parameter4 = 技能熟练度 paramter5 = 技能等级
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 25, message, *arg)


def LOG_ROLE_DEAD( *arg ):
	"""
	action = killed_by_role parameter1 = 操作玩家名称和DBID parameter2 = 凶手的名称和DBID  # 被玩家杀死

	action = killed_by_monster parameter1 = 操作玩家名称和DBID parameter2 = NPC的名称 	# 被NPC杀死
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 26, message, *arg)

def LOG_ROLE_MONEYCHANGE( *arg ):
	"""
	action = money_change parameter1 = 操作玩家名称和DBID parameter2 = 原来的创世币 parameter3 =现在的创世币
	parameter4 =改变的数量(正为增加 负为减少) parameter5 = 创世币改变的原因
	"""
	if arg[-1] in __LOG_ROLE_MONEYCHANGE_REASONS_FILTER:
		return
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 23, message, *arg)


def LOG_GAME_RANKING( *arg ):
	"""
	统计游戏中的数据

	type = 000600600100 action = wealth_ranking  parameter1 = 玩家的DBID  parameter2 = 玩家名字  parameter3 = 玩家的金钱
	parameter4 = 写日志的唯一时间(排名要求写入排名靠前的若干角色,该时间用于作为判断是否为同一次的统计数据)

	type = 000600600101 action = classlevel_ranking  parameter1 = 玩家的等级  parameter2 = 玩家的职业分布(如 剑客:10 战士 20)
	parameter3 = 写日志的唯一时间(排名要求写入排名靠前的若干角色,该时间用于作为判断是否为同一次的统计数据)

	统计帮会的信息
	type = 000600600102 action = tong_info_ranking  parameter1 = 帮会的DBID  parameter2 = 帮会的名字
	parameter3 = 帮会等级， parameter4 = 帮会财富 parameter5 = 成员数量   parameter6 = 成员平均等级
	parameter7 = 成员最高等级 parameter8 = 成员最低等级
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 19, message, *arg)

def FAMILY_CHANGE_SHAIKH( action,familyInfo,newShaikhDBID,oldShaikhDBID ):
	"""
	家族族长变更
	type = 000500800321 action = family_shaikh_abdication  parameter1 = 家族的名字和DBID  parameter2 = 新族长的DBID
	parameter3 = 原族长的DBID		# 族长退位
	type = 000500800321 action = family_reinstate_shaikh  parameter1 = 家族的名字和DBID  parameter2 = 新族长的DBID	# 族长丢失（删号，封号）重新任命
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, familyInfo,newShaikhDBID,oldShaikhDBID )

def FAMILY_SET_GRADE( action,familyInfo,operater,target,oldgrade,newgrade ):
	"""
	设置成员的权限(任免官职)
	type = 000500800322 action = family_set_memberGrade  parameter1 = 家族的名字和DBID  parameter2 = 操作者的DBID
	parameter3 = 目标的DBID， parameter4 = 	目标原来的权限  parameter5 = 目标现在的权限		# 设置成员权限
	"""
	pass
	#bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action,familyInfo,operater,target,oldgrade,newgrade )

def TONG_CHANGE_LEADER( action,tongInfo,newLeaderDBID,oldLeaderDBID,reason ):
	"""
	帮会会长变更
	type = 000500800324 action = tong_leader_abdication  parameter1 = 帮会的名字和DBID  parameter2 = 新帮主的DBID
	parameter3 = 原帮主的DBID	parameter4 = 变更原因
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s",action,tongInfo,newLeaderDBID,oldLeaderDBID,reason )

def TONG_SET_GRADE( action,tongInfo,operater,target,oldgrade,newgrade ):
	"""
	设置成员的权限(任免官职)
	type = 000500800325 action = tong_set_memberGrade  parameter1 = 帮会的名字和DBID  parameter2 = 操作者的DBID
	parameter3 = 目标的DBID， parameter4 = 	目标原来的权限  parameter5 = 目标现在的权限		# 设置成员权限
	"""
	pass  # 暂时不写该日志，感觉没有必要
	#bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action,tongInfo,operater,target,oldgrade,newgrade )

def TONG_STORE_QUERY_ITEMS( action,tongInfo,operater,itemuid,itemid,itemamount,bagID):
	"""
	存取帮会仓库的物品
	type = 000500800326 action = tong_store_items  parameter1 = 帮会的名字和DBID  parameter2 = 操作者的DBID
	parameter3 = 物品UID， parameter4 = 物品ID  parameter5 = 物品的数量	 parameter6 = 仓库的包裹id	# 存储物品到帮会仓库

	type = 000500800326 action = tong_query_items  parameter1 = 帮会的名字和DBID  parameter2 = 操作者的DBID
	parameter3 = 物品UID， parameter4 = 物品ID  parameter5 = 物品的数量	 parameter6 = 仓库的包裹id	# 从帮会仓库取出物品
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s||%s", action,tongInfo,operater,itemuid,itemid,itemamount,bagID )

def TONG_PRESTIGE_CHANGE( action,tongInfo,value,reason ):
	"""
	帮会声望改变
	action = tong_addPrestige tongInfo = 帮会的名字和DBID value = 增加的声望值 reson = 增加原因
	action = tong_reducePrestige tongInfo = 帮会的名字和DBID value = 减少的声望值 reson = 减少原因
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action,tongInfo,value,reason )
	
def TONG_LEVEL_CHANGE( action,tongInfo,oldLevel,newLevel,reason ):
	"""
	帮会等级改变
	action = tong_addLevel tongInfo = 帮会的名字和DBID oldLevel = 改变前等级 newLevel = 改变后等级 reason = 改变原因
	action = tong_reduceLevel tongInfo = 帮会的名字和DBID oldLevel = 改变前等级 newLevel = 改变后等级 reason = 改变原因
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s", action,tongInfo,oldLevel,newLevel,reason )
	
def TONG_ADD_DELETE_MEMBER( action,tongInfo,playerDBID,tongMemberNum ):
	"""
	帮会增删成员
	action = tong_add_member tongInfo = 帮会的名字和DBID playerDBID = 玩家dbid tongMemberNum = 加入后帮会人数
	#
	action = tong_reduce_member tongInfo = 帮会的名字和DBID playerDBID = 玩家dbid tongMemberNum = 删除后帮会人数
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action,tongInfo,playerDBID,tongMemberNum )
	
def TONG_ADD_DELETE_LEAGUE( action,tongInfo,leaguesNum ):
	"""
	帮户增减同盟
	action = tong_add_member tongInfo = 帮会的名字和DBID leagusNum = 新的同盟数量
	#
	action = tong_reduce_member tongInfo = 帮会的名字和DBID leagusNum = 新的同盟数量
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s", action,tongInfo,leaguesNum )

def ROLE_EXP_CHANGE( action, NameAndID, oldExp, oldLevel, nowExp, nowLevel, changeValue, changeReason):
	"""
	玩家经验改变日志
	type = 000300950001 action = role_exp_change  parameter1 = 玩家的名字和DBID  parameter2 = 玩家原来的经验
	parameter3 = 玩家原来的等级， parameter4 = 玩家现在的经验  parameter5 = 玩家现在的等级	 parameter6 = 经验改变的值
	parameter7 = 改变的原因
	"""
	if changeReason in __LOG_ROLE_EXP_CHANGE_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 20,"||%s||%s||%s||%s||%s||%s||%s||%s",action, NameAndID, oldExp, oldLevel, nowExp, nowLevel, changeValue, changeReason )

def APEX_KILL_ROLE( action, NameAndID, reason, actiontype ):
	"""
	反外挂对玩家的操作 如踢下线
	action = apex_killrole  parameter1 = 玩家的名字和DBID  parameter2 = 操作的原因
	parameter3 = 操作的类型 如封号 踢下线
	"""
	bwdebug.DATABASE_LOG_MSG( 21,"||%s||%s||%s||%s",action, NameAndID, reason, actiontype)

def LOG_GM_WORKING( *arg ):
	"""
	删除物品
	action = gm_delete_item  parameter1 = 操作的GM的名字和DBID parameter2 = 物品唯一ID parameter3 = 物品名称
	parameter4 = 物品数量  parameter6 = GM权限 parameter5 = 删除原因
	金钱改变
	action = gm_money_change parameter1 = 操作GM名称和DBID parameter2 = 原来的创世币 parameter3 =现在的创世币
	parameter4 =改变的数量(正为增加 负为减少) parameter5 = GM权限 parameter6 = 创世币改变的原因
	GM杀人
	action = gm_kill_role parameter1 = 操作玩家名称和DBID parameter2 = 凶手的名称和DBID  parameter3 = 凶手的权限
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 11, message, *arg)

def LOG_POINTCARD_TRADE( action, cardNumber, cardPrice, buyerName, buyerAccount ,sellerName ):
	"""
	点卡交易
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action, cardNumber, cardPrice, buyerName, buyerAccount ,sellerName)

def LOG_GOLD_SILVER_CHANGE( action, playerNameAndID, value, oldvalue, reason, account ):
	"""
	玩家金银元宝改变
	"""
	bwdebug.DATABASE_LOG_MSG( 28,"||%s||%s||%s||%s||%s||%s",action, playerNameAndID, value, oldvalue, reason, account)

def LOG_GAME_ACTIONS( *arg ):
	"""
	帮会掠夺战
	action = tong_robwar parameter1 = 帮会A的dbid parameter2 = 帮会A的名字 parameter3 = 帮会B的dbid parameter4 = 帮会B的名字
	武道大会
	action = wudao_war   parameter1 = 等级段      parameter2 = 参与人数
	家族挑战赛
	action = family_challenge parameter1 = 家族A的dbid parameter2 = 家族A的名字 parameter3 = 家族B的dbid parameter4 = 家族B的名字
	组队竞技
	action = team_pk   parameter1 = 等级段 parameter2 = 参与人数
	个人竞技
	action = role_pk   parameter1 = 等级段 parameter2 = 参与人数
	副本类活动统计
	action = game_copy parameter1 = 副本名称
	赛马
	action = race_horse   parameter1 = 参与人数
	魔物来袭
	action = startCampaignMonsterRaid parameter1 = 帮会的DBID
	车轮战
	action = tong_turn_war parameter1 = 城市名字 parameter2 = 胜利帮会的DBID， parameter3 =队伍成员(dbid, playerName)， parameter4 = 失败帮会的DBID， parameter5 = 队伍成员(dbid, playerName), 
	峰火连天
	action = tong_feng_huo_lian_tian parameter1 = 城市名字 parameter2 = 胜利帮会DBID， parameter3 = 失败帮会DBID, parameter4 = 第几轮
	帮会夺城战
	action = tong_city_war parameter1 = 城市名字 parameter2 = 胜利帮会DBID， parameter3 = 失败帮会DBID, parameter4 = 第几轮
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 29, message, *arg)

def LOG_CITY_EARNING( *arg ):
	"""
	补给点修理收入
	action = city_repair_earning  parameter1 = 地图名称  parameter2 = NPC的ID  parameter3 = 修理获得的金钱
	补给点出售物品收入
	action = city_sell_earning  parameter1 = 地图名称  parameter2 = NPC的ID  parameter3 = 出售获得的金钱
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 30, message, *arg)

def LOG_Activity( activityType, action, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
	"""
	活动竞技日志
	"""
	bwdebug.DATABASE_LOG_MSG( 31,"||%s||%s||%s||%s||%s||%s||%s||%s",activityType, action, param1, param2, param3, param4, param5, param6)


def LOG_Messy_Action( action, messyID, playerDBID, param1, param2, param3 ):
	"""
	杂乱行为日志
	"""
	bwdebug.DATABASE_LOG_MSG( 33,"||%s||%s||%s||%s||%s||%s", action, str(messyID), str(playerDBID), param1, param2, param3 )

def LOG_POTENTIAL_CHANGE( action, playerNameAndID, orgPotential, newPotential, reason):
	"""
	潜能变更的日志记录
	action = potential_change
	orgPotential	改变前潜能值
	newPotential	改变后潜能值
	reason			原因
	"""
	bwdebug.DATABASE_LOG_MSG( 34,"||%s||%s||%s||%s||%s", action, playerNameAndID, orgPotential, newPotential, reason )

def LOG_EXTEND_STORAGE( action, playerNameAndID, extend_num, storage_num ):
	"""
	扩充仓库日志记录
	action = extend_storage
	extend_num	擴充的次數
	storage_num	玩家目前倉庫格數
	"""
	bwdebug.DATABASE_LOG_MSG( 35,"||%s||%s||%s||%s", action, playerNameAndID, extend_num, storage_num )

def LOG_PET_REPRODUCTION( action, playerNameAndID1, petData1, playerNameAndID2, petData2 ):
	"""
	宠物繁殖日志
	action = pet_reproduction
	petData1 = 宠物数据
	petData2 = 宠物数据
	"""
	bwdebug.DATABASE_LOG_MSG( 36,"||%s||%s||%s||%s||%s", action, playerNameAndID1, petData1, playerNameAndID2, petData2 )

def LOG_AWARDS_ITEM( account, roele, orderform, itemId, amount, transactionID, remark ):
	"""
	物品奖励领取日志(带订单和不带订单):
	action = Item_Awards  parameter1 = 账号名称 parameter2 = 角色名称 parameter3 = 活动标识
	parameter4 = 物品ID parameter5 = 物品数量, parameter6 = 单号 parameter7 = 备注
	"""
	bwdebug.DATABASE_LOG_MSG( 37,"||%s||%s||%s||%s||%s||%s||%s||%s","Item_Awards", account, roele, orderform, itemId, amount, transactionID, remark )

def LOG_Relation(action , parameter1 , parameter2 ):
	"""
	人物关系日志（师徒、恋人、夫妻等）
	action=产生关系或解除关系行为	parameter1=玩家ID	parameter2=玩家ID	
	若为结拜关系，则parameter1为所有玩家的姓名，parameter2为所有玩家的ID
	"""
	bwdebug.DATABASE_LOG_MSG( 38,"||%s||%s||%s" , action , parameter1 , parameter2 )

def LOG_Collection( action , parameter1 , parameter2 , parameter3 ):
	"""
	采集点采集信息记录日志
	action="caiji"	parameter1=地图名	parameter2=资源点类别	parameter3=玩家DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 39,"||%s||%s||%s||%s" , action , parameter1 , parameter2 , parameter3 )

def LOG_ROLE_ADD_DAOHENG( roleDBID, point, reason ):
	"""
	道行的增长
	"""
	bwdebug.DATABASE_LOG_MSG( 40,"||add||%s||%s||%s", roleDBID, point, reason )

def LOG_ROLE_SET_DAOHENG( roleDBID, point, reason ):
	"""
	道行的设置
	"""
	bwdebug.DATABASE_LOG_MSG( 40,"||set||%s||%s||%s", roleDBID, point, reason )

def ERROR_MESSAGE():
	"""
	获取上一次的错误信息
	该接口只有在except中调用才有意义
	"""
	message = ""
	f = sys.exc_info()[2].tb_frame
	message += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :"
	funcName = f.f_code.co_name
	className = bwdebug._getClassName( f, funcName )
	message += "%s: %s: %s" % ( className,sys.exc_info()[0], sys.exc_info()[1] )

	return message

# -*- coding: gb18030 -*-
#
# $Id: message_logger.py

"""
��־д��ģ��
ע��
����Ľӿ�֮����û��ʹ�ö�̬�Ĳ������� ԭ�������ʹ�ö�̬�������� ��ôĳЩ������������������� ��ôҲ������ֳ���
�����ݿ��г��ֲ������������ݣ�Ҳ����׷�٣����Բ��ù̶������������Ա��ڲ�������ʱ����֪�����õĵط�����Ȼ�������Ƿ�
�����ۡ�

ʹ�ù���
����Щ��Ϣд����־�У�����־�����Ǳ���Ȼ�й���ȥ������Щ��Ϊ��
��Ҫ������ȡ��Щ���ݣ��ͷ�����Щ����������
bwdebug.DATABASE_LOG_MSG ��������ĵ�һ��������һ�� ���ݱ�������˵����Щ���ݻᱻ��¼���ĸ����С�
ÿһ��������Ӧһ�������ԣ������Ҫ�¼���һ��������ʱ���Ǿ���Ҫ��
svn://172.16.0.234/home/svnroot/love3/trunk/bigworld/tools/server/message_logger.dbinfo.xml �ж���һ����
������־��Ϣ�����ᱻ�洢��

"""

import Language
import sys
import bwdebug
import csdefine

"""
������action���ձ� ����action���Ի�ø������ݵ�����
deleteRole  				#ɾ����ɫ
register					#ע���˺�
set_grade   				#����Ȩ��
set_attr    				#�����������
set							#����ĳ�˵�persistentMapping�����е�ֵ
set_temp					#����ĳ�˵�tempMapping�����е�ֵ
goto						#����һ������
clone						#��entity��ǰλ�ô���һ��npc entity
drop_item					#�ڵ�ǰλ����һ����Ʒ
add_item					#����Ʒ��������һ����Ʒ
add_equip					#����Ʒ��������һ������ָ��Ʒ��,ǰ׺,������װ��
add_skill					#��ĳ������һ������
remove_skill				#ɾ��ĳ�˵�һ������
set_level   				#������ҵĵȼ�
set_adult					#��������Ƿ����
set_anti					#�����Ƿ���������ϵͳ
set_money					#������ҽ�Ǯ
set_exp     				#������Ҿ���
set_potential 				#�������Ǳ��
set_speed   				#������ҵ��ٶ�
family_create				#��������
family_addPrestige			#���Ӽ�������
family_quit					#���ü������ ���ܻ�ܾ��������
tong_create					#�������
tong_quit					#���ü������ ���ܻ�ܾ��������
specialShop_open			#�����̳ǿ�ҵ
specialShop_close			#�����̳ǹر�
specialShop_update			#�����̳Ǹ���
destroy_NPC					#�ݻ�ָ��NPC
accept_quest				#��ʵ�����ָ��������
set_quest_flag				#����/���ʵ������ĳ���������ɱ��
tong_addMoney				#������ӽ�Ǯ
tong_addActionVal			#���Ӱ���ж���
tong_addPrestige			#���Ӱ������
tong_addBuildVal			#���Ӱ�Ὠ���
tong_addLevel				#���Ӱ��ȼ�
tong_degrade				#���Ͱ��ȼ�
tong_addhouqinVal			#���Ӱ����ڶ�
tong_addResearchVal			#���Ӱ���о���
tong_cancelDismiss  		#ȡ������ɢָ��
activity_control			#��/�ر� һ���
set_silver					#��ĳ��������Ԫ��
set_gold					#��ĳ�����ý�Ԫ��
add_pet_calcaneus			#���ӳ������
set_pet_nimbus				#���ó�������ֵ
set_pet_life 				#���ó�������
set_pet_joyancy				#���ó�����ֶ�
set_pet_propagate_finish	#���ﷱֳ���
set_pet_storage_time		#���ó���ֿ�ʣ��ʱ��
wizCommand_set_pet_ability	#���ó���ɳ���
dismiss_tong				#���̽�ɢ���
set_xinglong_prestige		#������¡�ھ�����
set_changping_prestige		#���ò�ƽ�ھ�����
add_teachCredit				#���ӹ�ѫֵ
set_pk_value				#����PKֵ
clean_behoof_record			#���̽�ɢ���
add_treasure_map			#���ָ���ȼ��Ĳر�ͼ
add_title					#���ӳƺ�
remove_title				#����ƺ�
clean_activity_record		#�������
catch						#ץ��
cometo						#���������
kick						#����
block_account				#�����ʺ�
unBlock_account				#����˺�
set_respawn_rate			#����ˢ���ٶ�
set_loginAttemper			#���õ�¼�Ŷӵ���״̬
set_stone					#���û���ʯ
set_tong_contribute			#���ð�ṱ�׶�
set_fabao_naijiu			#���������;�
set_fabao_max_naijiu		#������������;�����
set_fabao_lim_naijiu		#����������ǰ�;ö�����
set_fabao_level				#���������ȼ�
set_fabao_skill_level		#�����������ܵȼ�
role_addQuest				#��������
role_completeQuest			#�������
role_abandonQuest			#��������
use_Item					#ʹ����Ʒ
buy_specialItem				#�����շ���Ʒ
delete_item					#ɾ����Ʒ
add_item					#������Ʒ
buy_item					#������Ʒ
add_pet						#����һ������
roleswap_item				#��ҽ�����Ʒ
roleswap_money				#��ҽ��׽�Ǯ
roleswap_pet				#��ҽ��׳���
pick_item					#ʰȡ��Ʒ
vend_buyItem				#��̯������Ʒ
handin_questitem			#�Ͻ�������Ʒ
store_item					#���д�����Ʒ
family_roleManage			#������Ա����
create_delete_family		#�����ͽ�ɢ���
create_delete_tong			#�����ͽ�ɢ���
remove_pet					#ɾ������
drop_pet					#��������
vend_pet					#��̯���۳���
store_pet					#�������
takeout_pet					#ȡ������
login_out_game				#����͵ǳ���Ϸ
consume_buy_specialItem  	#�����̳���Ʒ
consume_buy_roleExp 		#�������ʯ
consume_buy_petExp			#����������ʯ
consume_quiz_usegold		#ʹ��Ԫ������
consume_pst_hire			#���ó���ֿ�
consume_changeGoldToItem	#Ԫ��Ʊ�һ�
statisticPlayerNum			#�������ȴ����г��ȡ���¼���г��ȡ����߽�ɫ����ͳ��
role_updateLevel			#�������
use_item					#ʹ����Ʒ
role_learn_skill			#���ѧϰ����
role_update_skill			#�����������
pet_update_skill			#������������
pet_learn_skill				#����ѧϰ����
role_update_tongskill		#���������Ἴ��
role_learn_tongskill		#���ѧϰ��Ἴ��
vehicle_update_skill		#�����������
vehicle_learn_skill			#���ѧϰ����
killed_by_role				#�����ɱ��
killed_by_monster			#��NPCɱ��
messy_action				#������Ϊ
potential_change			#Ǳ�ܱ��
extend_storage				#����ֿ�
pet_reproduction			#���ﷱֳ
tong_add_member				#����¼ӳ�Ա
tong_reduce_member			#������
tong_add_league				#�ﻧ����ͬ��
tong_reduce_league			#�ﻧ����ͬ��

"""

# ������־���ˣ��������б��е�reason���������־��
__LOG_DELETE_ITEM_REASONS_FILTER = set()			# csdefine.DELETE_ITEM_*
__LOG_ADD_ITEM_REASONS_FILTER = set()				# csdefine.ADD_ITEM_*
__LOG_ROLE_MONEYCHANGE_REASONS_FILTER = set()		# csdefine.CHANGE_MONEY_*
__LOG_ROLE_EXP_CHANGE_REASONS_FILTER = set()		# csdefine.CHANGE_EXP_*

if Language.LANG == Language.LANG_BIG5:
	# �����ר�ù��ˣ�������ֵ�б��и�ֵ��������鿴���汸ע�����ǰ׺�Ķ��塣
	__LOG_DELETE_ITEM_REASONS_FILTER.update( [4,5,6,7,8,9,10,11,12,15,16,17,18,19,21,34,35,36,37,38,39,40,43,44,45,46,47,48,49,55,56,57,63,64,65,66,67,68,69,70,71,79,80,81,89,90,91,92] )
	__LOG_ADD_ITEM_REASONS_FILTER.update( [2,9,16,17,18,19,20,21,22,24,25,26,27,30,31,35,36,37,38,39,40,41,42,43,44,45,46,48,49,51,52,53,54,55,56,60,61,63,64,65,66,67,68,69,70,71,72,73,76,79,81,92,93,94,95,96,97,98,99,100,101,102,103,104,105] )
	__LOG_ROLE_MONEYCHANGE_REASONS_FILTER.update( [1,4,7,8,9,10,14,17,18,19,24,44,46,47,70,71,81,91] )
	__LOG_ROLE_EXP_CHANGE_REASONS_FILTER.update( [1,2,5,6,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,26,27,28,29,30,31,32,33,34,35] )



def LOG_ROLE_DELETE( action, account, roleDBID ):
	"""
	ɾ����ɫ
	type = 000100200200 , action = deleteRole parameter1 = ɾ���Ľ�ɫ��DBID parameter2 = �˺ŵ����ƺ�DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 6,"||%s||%s||%s",action, roleDBID,  account )

def LOG_USE_GMCMMAND( action,command,paramStr,srcEntityDBID, dstEntityDBID,srcEntityGrade,extend = None ):
	"""
	GM������־:
	type = 000100900300 , action = GM����� ��: set_level parameter1 = ʹ���ߵ����ֺ�DBID parameter2 = GM����� ��: set_level
	parameter3 = �������ո�ֿ� parameter4 = ʹ�ö�������ֺ�DBID��ֻ�����ң� parameter5 = ʹ���ߵ�Ȩ�� parameter6 = ����˵��(�� set_level�޸�ǰ�ȼ�)
	"""
	bwdebug.DATABASE_LOG_MSG( 7,"||%s||%s||%s||%s||%s||%s||%s",action, srcEntityDBID, command, paramStr, dstEntityDBID, srcEntityGrade, extend  )


def LOG_EXCEPTION(action,Type,message):
	"""
	�쳣��Ϣ:  ����Ϸ�����Ҫ������Ϣд�����ݿ⡣
	type = 000100300100 , action = �Զ���Ĵ�����־����(�� logд������action Ϊlog) parameter1 = ���������(error warning)
	parameter2 = ������Ϣ������
	"""
	bwdebug.DATABASE_LOG_MSG( 8,"||%s||%s||%s",action,Type,message )

def LOG_BUY_SPECIALITEM(action,uid,item_name,num,gold,silver,OperatorName):
	"""
	�����շѵ��߼�¼��
	type = 000400150200, action = buy_specialItem parameter1 = �������ҵ����ֺ�DBID parameter2 = �������ƷΨһID parameter3 = ������Ʒ������
	parameter4= ������Ʒ������ parameter5 = ���ѵĽ�Ԫ���� parameter6 = ���ѵ���Ԫ����
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,OperatorName,uid,item_name,num,gold,silver )

def LOG_DELETE_ITEM( uid,item_name,num,OperatorName,reason ):
	"""
	ɾ����Ʒ����ʱ�޴�GM��������ⲿ���ܣ�:
	type = 000200400100, action = delete_item parameter1 = ��������ҵ����ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ����  parameter5 = ɾ��ԭ��
	"""
	if reason in __LOG_DELETE_ITEM_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 27,"||delete_item||%s||%s||%s||%s||%s",OperatorName,uid,item_name,num,reason )

def LOG_ADD_ITEM(uid,item_name,num,OperatorName, reason ,playerLevel = ""):
	"""
	�����Ʒ��
	type = 000200400110 action = add_item parameter1 = ���������ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ����  parameter5 = ���ӵ�ԭ�� parameter6 = ��ҵȼ�
	"""
	if reason in __LOG_ADD_ITEM_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 27,"||add_item||%s||%s||%s||%s||%s||%s",OperatorName,uid,item_name,num,reason,playerLevel )


def LOG_BUY_ITEM( action,uid,item_name,num,operatorName,user_grade,chapmanID):
	"""
	������ߣ���ͨ���ߺ��շѵ��߷ֿ���¼�����ڲ��Һ�ͳ�ƣ�:
	type = 000200400310, action = buy_item parameter1 = ���������ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ���� parameter5 = ������Ȩ�� parameter6 = ���˵�ID
	"""
	pass
	#bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,operatorName,uid,item_name,num,user_grade,chapmanID)

def LOG_GET_PET( action,petID,petName,playerName, reason ):
	"""
	��ó��
	type = 000200952400, action = add_pet  parameter1 = ������ֺ�DBID parameter2 = ����DBID  parameter3 = ��������
	parameter5 = ��ӵ�ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action,playerName,petID,petName, reason )


def LOG_REMOVE_PET(  action, petID,petName, user_name, reason ):
	"""
	ɾ������:
	type = 000200952420,action = remove_pet parameter1 = ��������ҵ����ֺ�DBID parameter2 = ����ID  parameter3 = ��������
	parameter5 = ɾ����ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action,user_name, petID,petName, reason )


def LOG_ROLE_TRADE( action,trade_uid,uid,itemName,itemAmount,traderName1,traderName2 ):
	"""
	�û�����:
	type = 000200400610, action = roleswap_item  parameter1 = �Լ������ֺ�DBID  parameter2 = �Լ����׵���ƷΨһID
	parameter4 = �˴ν��׵�ΨһID parameter5 = �Լ����׵���Ʒ���� parameter6 = ��Ʒ���� parameter7 = ���۶������ֺ�DBID

	�û����׽�Ǯ
	type = 000200400610, action = roleswap_money parameter1 = �Լ������ֺ�DBID parameter2 = NULL  parameter4 = �˴ν��׵�ΨһID
	parameter5 = cschannel_msgs.ROLERELATION_INFO_7 parameter6 = �Լ������Ĵ��������� parameter7 = ����������ֺ�DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s||%s",action,traderName1,uid,trade_uid,itemName,itemAmount,traderName2 )

def LOG_PET_TRADE(  action, trade_uid, petID, traderName1,traderName2 ):
	"""
	���׳��
	type = 000200952600, action = roleswap_pet  parameter1 = ���۷����ֺ�DBID parameter2 = ����ID
	parameter4 = �˴ν��׵�ΨһID  parameter5 = ����������ֺ�DBID
 	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action, traderName1,petID,trade_uid, traderName2 )

def LOG_VEND(  action, uid, itemName, itemAmount, traderName1,traderName2 ):
	"""
	��̯���ף�
	type = 000200400630, action = vend_buyItem  parameter1 = ���۷������ֺ�DBID parameter2 = ��ƷΨһID
	parameter4 = ��Ʒ������  parameter5 = ��Ʒ������ parameter6 = ���򷽵����ƺ�DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action,traderName2, uid, itemName, itemAmount,traderName1 )

def LOG_VEND_PET( action, petDBID, traderName1,traderName2 ):
	"""
	��̯���۳���:
	type = 000200952710, action = vend_pet parameter1 = ���۷������ֺ�DBID parameter2 = �����DBID
	parameter4 = ���򷽵����ƺ�DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s",action,traderName2, petDBID, traderName1 )

def LOG_GET_STORE_PET( action, petDBID, pet_name, roleName, event ):
	"""
	�ֿ��ȡ����:
	type = 000200952720, action = store_pet parameter1 = ��ҵ����ֺ�DBID  parameter2 = �����DBID parameter3 = ���������
	parameter5 = �������
	type = 000200952720, action = takeout_pet parameter1 = ��ҵ����ֺ�DBID parameter2 = �����DBID parameter3 = ���������
	parameter5 = ȡ������
	"""
	bwdebug.DATABASE_LOG_MSG( 22,"||%s||%s||%s||%s||%s",action, roleName, petDBID, pet_name, event )


def LOG_GET_STORE_ITEM( action, uid, item_name, num, roleName, event ):
	"""
	�ֿ��ȡ:
	action = store_item parameter1 = ��ҵ����ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ����   parameter6 = �¼�˵��(�������ȡ��)
	type = 000200400810, action = takeout_item  parameter1 = ��ҵ����ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	 parameter4 = ��Ʒ����  parameter6 = �¼�˵��(�������ȡ��)
	type = 000200400810, action = bank_destroyItem parameter1 = ��ҵ����ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ����  parameter6 = �¼�˵��(�������ȡ��)
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action, roleName, uid, item_name, num, event )

def LOG_CHAT_MESSAGE( action, speaker , message ):
	"""
	Ƶ����Ϣ:
	action = cryptonym_talk  parameter1 = �����ߵ����ֺ�DBID   parameter2 = ���Ե�����
	"""
	bwdebug.DATABASE_LOG_MSG( 10,"||%s||%s||%s",action, speaker , message )


def LOG_CHARGE_SUCCESSFUL( action, transactionID, Account, ChargeType, GoldCoins, SilverCoins ):
	"""
	�ɹ���ֵ��־��ѯ��
	type = 000400100100 , action = charge_successful parameter1 = ������ parameter2 = �˺� parameter3 = ��ֵ����
	parameter4 = ��Ԫ���� parameter5 = ��Ԫ����
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s||%s",action, transactionID, Account, ChargeType, GoldCoins, SilverCoins)

def LOG_RECEIVE_PRESENT( action, transactionID, giftPackage, expiredTime, parentDBID ):
	"""
	��Ʒ������ȡ��־(�������Ͳ�������):
	action = take_present  parameter1 = ������(����û��) parameter2 = ��Ʒ��ID parameter3 = �콱��ֹ����
	parameter4 = �˺�
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, transactionID, giftPackage, expiredTime, parentDBID)

def LOG_RECEIVE_SILVERCOINS( action, transactionID, silverCoins, parentDBID ):
	"""
	��Ԫ����ȡ��־:
	type = 000400100810 , action = take_silverCoins  parameter1 = ������ parameter2 = ��Ԫ���� parameter3 = �˺�
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s",action, transactionID, silverCoins, parentDBID )

def LOG_RECEIVE_TESTACTIVITYGIFT( action, itemID, playerNameAndID, playerLevel, giftLevel ):
	"""
	��⽱������ȡ:
	type = 000400100820 , action = take_testactivitygift parameter1 = ��ҵ����ֺ�ID  parameter2 = ��Ʒ��ID parameter3 = ��ҵĵȼ�
	parameter5 = ��⽱Ʒ���ļ���
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, playerNameAndID, itemID,  playerLevel, giftLevel )

def LOG_RECEIVE_TESTWEEKGIFT( action, playerNameAndID, playerLevel, silvercoins, week ):
	"""
	����ܽ�������ȡ:
	type = 000400100830 , action = take_testweekgift  parameter1 = ��ҵ����ֺ�ID parameter2 = ��ҵĵȼ�
	parameter4 = ��Ԫ�������� parameter5 = ��ȡ������
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s||%s",action, playerNameAndID, playerLevel, silvercoins, week )

def LOG_RECEIVE_SPREADERGIFT( action, itemID, playerNameAndID, playerLevel ):
	"""
	�ƹ�Ա��������ȡ:
	type = 000400100840 , action = take_spreadergift parameter1 = ��ҵ����ֺ�ID parameter2 = ��Ʒ��ID  parameter3 = ��ҵĵȼ�
	"""
	bwdebug.DATABASE_LOG_MSG( 13,"||%s||%s||%s||%s",action, playerNameAndID, itemID, playerLevel )

def LOG_CREATE_DELETE_TONG( action,tongName,creatorND,event,reason ):
	"""
	������ɾ�����:
	type = 000500800100, action = create_tong  parameter1 = ������������ֺ�DBID parameter2 = �������  parameter3 = �������
	parameter4 = ����ԭ��

	type = 000500800100, action = delete_tong  parameter1 = None parameter2 = ������ƺ�DBID parameter3 = ��ɢ���
	parameter4 = ��ɢԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s",action,creatorND,tongName,event,reason )

def LOG_TONG_FAMILYMANAGE( action, tongDBID, familyDBID, event ):
	"""
	ɾ���ͼ�����壺

	type = 000500800200 action = tong_addfamily parameter1 = �������ֺ�DBID parameter2 = ��������ֺ�DBID
	parameter3= '������'

	type = 000500800200 action = tong_deletefamily parameter1 = �������ֺ�DBID parameter2 = �����DBID
	parameter3 =  �˳�����Լ�ԭ����˳���ԭ���ֵ �� "�˳�����:���������˳� reason = 0
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, tongDBID, familyDBID, event )

def LOG_TONG_MONEY_CHANGE( action, tongDBID, oldValue, newValue, value, reason ):
	"""
	����Ǯ�ı�
	type = 000500800300 action = tong_money_change parameter1 = ������ƺ�DBID parameter2 = ԭ���Ĵ����� parameter3 =���ڵĴ�����
	parameter4 = �ı��ֵ(+Ϊ����-Ϊ����) parameter5 = �����Ҹı��ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action, tongDBID, oldValue, newValue, value, reason )

def LOG_TONG_BUILDING_CHANGE( tongDBID, tongName, buildingType, oldValue, newValue ):
	"""
	��Ὠ���ȼ��ı�
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||building_change_level||%s||%s||%s||%s||%s", tongDBID, tongName, buildingType, oldValue, newValue )

def LOG_CREATE_DELETE_FAMILY( action, familyName, operatorDBID, event ):
	"""
	����Ĵ�����ɾ����
	type = 000500800300 action = create_family parameter1 = ���������ֺ�DBID parameter2 = ��������
	parameter3 = ��������

	type = 000500800300 action = delete_family parameter2 = None parameter1 = ��������
	parameter3 = ��ɢ����
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, operatorDBID, familyName,  event )

def LOG_FAMILY_ROLEMANAGE( action, familyDBID, operatorDBID, roleDBID, event):
	"""
	����ɾ���ͼ�����ң�
	type = 000500800320 ,action = family_addrole parameter1 = �������ƺ�DBID parameter2 = ������DBID  parameter3 = �������ҵ����ֺ�DBID
	parameter4 = �������

	type = 000500800320 ,action = family_deleterole parameter1 = �������ƺ�DBID parameter2 = �˳���ҵ����ֺ�DBID  parameter3 = �˳���ҵļ���Ȩ��
	parameter4 = �˳�����:�������Լ�

	type = 000500800320 ,action = family_deleterole parameter1 = �������ƺ�DBID parameter2 = �˳���ҵ����ֺ�DBID  parameter3 = �˳���ҵļ���Ȩ��
	parameter4 = �߳�����:�����ߵ����ֺ�DBID �� �߳�����:������ = ����(10321)
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s", action, familyDBID, operatorDBID, roleDBID, event )

def LOG_ACCOUNT_LOGIN_LOGOUT( action, IP, account, event ):
	"""
	����˺ŵ�½����ǳ���Ϸ
	type = 000100500100 , action = account_login parameter1 = �˺����� parameter2 = IP
	parameter3 = �¼��Ľ���	�˺�����
	type = 000100500100 , action = account_logout parameter1 = �˺����� parameter2 = IP
	parameter3 = �¼��Ľ���	�˺�����
	"""
	bwdebug.DATABASE_LOG_MSG( 15,"||%s||%s||%s||%s", action, account, IP,  event )

def LOG_ROLE_LOGON_LOGOFF( action, IP, account, roleName, lifetime, event ):
	"""
	��ҽ�ɫ��½����ǳ���Ϸ
	type = 000100500600 , action = role_logon parameter1 = ��ҵ����ֺ�DBID  parameter2 = �˺����� parameter3 = IP
	parameter4 = ������ʱ�� parameter5 = event	�������
	type = 000100500600 , action = role_logoff parameter1 = ��ҵ����ֺ�DBID parameter2 = �˺����� parameter3 = IP
	parameter4 = ������ʱ�� parameter5 = event	�������
	"""
	bwdebug.DATABASE_LOG_MSG( 15,"||%s||%s||%s||%s||%s||%s", action, roleName,account,IP, lifetime, event )

def LOG_PLAYER_CONSUME( action,account,gold,silver,event ):
	"""
	��ҵ�������־
	type = 000400150700 , action = consume_buy_specialItem  parameter1 = �˺����� parameter2 = ���ѵĽ�Ԫ��  parameter3 = ���ѵ���Ԫ��
	parameter4 = �¼��Ľ���															�����̳���Ʒ
	type = 000400150700 , action = consume_buy_roleExp ...... ����Ĳ���ͬ��		�������ʯ
	type = 000400150700 , action = consume_buy_petExp								����������ʯ
	type = 000400150700 , action = consume_quiz_usegold								ʹ��Ԫ������
	type = 000400150700 , action = consume_pst_hire									���ó���ֿ�
	type = 000400150700 , action = consume_changeGoldToItem							Ԫ��Ʊ�һ�
	"""
	bwdebug.DATABASE_LOG_MSG( 16,"||%s||%s||%s||%s||%s", action, account, gold, silver, event )

def LOG_QUEST( action, playerName, playerGrade, questName, questID ):
	"""
	���������ص���־
	type = 000300670100 , action = role_abandonQuest  parameter1 = ��ҵ����ֺ�DBID  parameter2 = ��ҵ�Ȩ��
	parameter3 = �������� parameter4 = ����ID ��������

	type = 000300670100 , action = role_completeQuest parameter1 = ��ҵ����ֺ�DBID  parameter2 = ��ҵ�Ȩ��
	parameter3 = �������� parameter4 = ����ID  �������

	type = 000300670100 , action = role_addQuest parameter1 = ��ҵ����ֺ�DBID   parameter2 = ��ҵ�Ȩ��
	parameter3 = �������� parameter4 = ����ID ��������
	"""
	pass		# ��ʱ��ʹ��������ص���־,����Ժ����ĳ����֮��ص�BUG,�ٴ�
	#bwdebug.DATABASE_LOG_MSG( 17,"||000300670100||%s||%s||%s||%s||%s", action, playerName, playerGrade, questName, questID )

def LOG_ROLE_SET_LEVEL( action, playerName, oldLevel, level, lifeTime ):
	"""
	�������
	type = 000300670220 , action = role_updateLevel  parameter1 = ��ҵ����ֺ�DBID
	parameter3 = ԭ���ĵȼ� parameter4 = ���ڵĵȼ� parameter5 = ��ɫ������ʱ��
	"""
	bwdebug.DATABASE_LOG_MSG( 24,"||%s||%s||%s||%s||%s", action, playerName, oldLevel, level, lifeTime  )

def LOG_SVRSTATUS( action, waitAccountNum, loginAccountNum, summation  ):
	"""
	type = 000600700800 , action = statisticPlayerNum parameter1 = �ȴ������е�������� parameter2 = ��½�����е��������
	parameter3 = ������ҵ�����
	"""
	bwdebug.DATABASE_LOG_MSG( 18,"||%s||%s||%s||%s", action, waitAccountNum, loginAccountNum, summation )

def LOG_ROLE_ACTION( *arg ):
	"""
	�������Ϸ�еĲ��������������ڶ಻��ͳһ�Ҹ�ʽ���죬���Բ��ö�̬��������..
	action = equipStiletto  parameter1 = ����������ƺ�DBID parameter2 = �������ƷUID parameter3 = ��׺���Ʒ��UID
	parameter4 = ��Ʒ���� parameter5 = ��Ʒԭ���� parameter6 = ��Ʒ���ڵĿ���

	action = equipSplit parameter1 = ����������ƺ�DBID parameter2 = �����װ��UID parameter3 = װ��������


	action = equipStudded parameter1 = ����������ƺ�DBID parameter2 = ����Ƕ��ƷUID parameter3 = ��Ƕ����Ʒ��UID
	parameter4 = ��Ʒ���� parameter5 = ��Ʒԭ��ʹ���� parameter6 = ��Ʒ���ڵĿ�ʹ���� parameter7 = ��Ƕ���ӵ�����

	action = equipIntensify parameter1 = ����������ƺ�DBID parameter2 = ��ǿ����ƷUID parameter3 = ǿ������Ʒ��UID  parameter4 = ��Ʒ����
	parameter5 = ��Ʒԭǿ���� parameter6 = ��Ʒ���ڵ�ǿ����

	action = equipRebuild parameter1 = ����������ƺ�DBID parameter2 = ��������ƷUID parameter3 = �������Ʒ��UID  parameter4 = ��Ʒ����
	parameter5 = ��ƷԭƷ�� parameter6 = ��Ʒ���ڵ�Ʒ��  parameter7 = ��Ʒԭǰ׺ parameter8 = ��Ʒ���ڵ�ǰ׺


	action = equipBind parameter1 = ����������ƺ�DBID parameter2 = ������ƷUID parameter3 = �󶨺���Ʒ��UID  parameter4 = ��Ʒ����
	parameter6 =��װ���󶨡�

	type = 000300670230 action = specialCompose parameter1 = ����������ƺ�DBID parameter2 = �ϳ���Ʒ��UID parameter3 = ��Ʒ����


	action = equipMake parameter1 = ����������ƺ�DBID parameter2 = �����װ��UID parameter3 = ��Ʒ����
	parameter4 = װ��ԭƷ�� parameter5 = װ����Ʒ�� parameter6 = װ��ԭǰ׺ parameter7 = װ����ǰ׺

	action = stuffCompose parameter1 = ����������ƺ�DBID parameter2 = �ϳɺ�Ĳ���UID parameter3= �ϳɺ�Ĳ�������
	parameter4= �ϳɺ�Ĳ�������

	action = addTalismanLife  parameter1 = ����������ƺ�DBID parameter2 = ����UID parameter3 = ����������
	parameter4 = ����ԭ��������ʱ�� parameter5 = �������ڵ�����ʱ��

	�����ʼ�
	action = send_mail  parameter1 = ����������  parameter2 = ����������, parameter3 = �ʼ����� parameter4 = ��Ʒ����  parameter5 = �������

	��������
	action = return_mail parameter1 = ���������� parameter2 = ����������, parameter3 = �ʼ����� parameter4 =  �ʼ�ID

	ϵͳ����
	action = return_mail_sys  parameter1 = ���������� parameter2 = ����������, parameter3 = �ʼ����� parameter4 =  �ʼ�ID

	ɾ���ʼ� ������ϵͳɾ�������ֶ�ɾ��
	action = delete_mail parameter1 = ���������� parameter2 = ����������, parameter3 = �ʼ����� parameter4 =  �ʼ�ID

	�Ķ��ʼ�
	action = read_mail parameter1 = ���������� parameter2 = ����������, parameter3 = �ʼ����� parameter4 =  �ʼ�ID
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 17, message, *arg)


def LOG_SKILL( *arg ):
	"""
	type = 000300955231 action = role_update_skill parameter1 = ����������ƺ�DBID parameter2 = ����ID parameter3 = ԭ����ID
	parameter4 = ���ĵ�Ǳ�ܵ� parameter5 = ���ĵĽ�Ǯ		�����������

	type = 000300955231 action = role_learn_skill parameter1 = ����������ƺ�DBID parameter2 = ����ID
	parameter3 = ���ĵ�Ǳ�ܵ� parameter4 = ���ĵĽ�Ǯ 		���ѧϰ����

	type = 000300955231 action = pet_update_skill parameter1 = ����������ƺ�DBID parameter2 = ��������ֺ�DBID  parameter3 = ����ID
	parameter4 = ԭ����ID 		������������

	type = 000300955231 action = pet_learn_skill parameter1 = ����������ƺ�DBID parameter2 = ��������ֺ�DBID  parameter3 = ����ID
	����ѧϰ����

	type = 000300955231 action = role_update_tongskill parameter1 = ����������ƺ�DBID parameter2 = ����ID parameter3 = ԭ����ID
	parameter4 = ���ĵ�Ǳ�ܵ� parameter5 = ���ĵĽ�Ǯ 	���������Ἴ��

	type = 000300955231 action = role_learn_tongskill parameter1 = ����������ƺ�DBID parameter2 = ����ID
	parameter3 = ���ĵ�Ǳ�ܵ� parameter4 = ���ĵĽ�Ǯ		���ѧϰ��Ἴ��

	type = 000300955231 action = vehicle_update_skill parameter1 = ����������ƺ�DBID parameter2 = ����DBID  parameter3 = ����ID
	parameter4 = ԭ����ID  parameter5 = ���ĵļ��ܵ� parameter6 = ���ĵĽ��		�����������

	type = 000300955231 action = vehicle_learn_skill parameter1 = ����������ƺ�DBID parameter2 = ����DBID  parameter3 = ����ID
	parameter4 = ���ĵļ��ܵ� parameter5 = ���ĵĽ��	���ѧϰ����

	type = 000300955231 action = learn_new_skill parameter1 = ����������ƺ�DBID parameter2 = ��ҵȼ� parameter3 = ����ID

	type = 000300955231 action = oblive_skill parameter1 = ����������ƺ�DBID parameter2 = ��ҵȼ�  parameter3 = ����ID

	type = 000300955231 action = level_up_skill parameter1 = ����������ƺ�DBID parameter2 = ��ҵȼ�  parameter3 = ����ID
	parameter4 = ���������� paramter5 = ���ܵȼ�
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 25, message, *arg)


def LOG_ROLE_DEAD( *arg ):
	"""
	action = killed_by_role parameter1 = ����������ƺ�DBID parameter2 = ���ֵ����ƺ�DBID  # �����ɱ��

	action = killed_by_monster parameter1 = ����������ƺ�DBID parameter2 = NPC������ 	# ��NPCɱ��
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 26, message, *arg)

def LOG_ROLE_MONEYCHANGE( *arg ):
	"""
	action = money_change parameter1 = ����������ƺ�DBID parameter2 = ԭ���Ĵ����� parameter3 =���ڵĴ�����
	parameter4 =�ı������(��Ϊ���� ��Ϊ����) parameter5 = �����Ҹı��ԭ��
	"""
	if arg[-1] in __LOG_ROLE_MONEYCHANGE_REASONS_FILTER:
		return
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 23, message, *arg)


def LOG_GAME_RANKING( *arg ):
	"""
	ͳ����Ϸ�е�����

	type = 000600600100 action = wealth_ranking  parameter1 = ��ҵ�DBID  parameter2 = �������  parameter3 = ��ҵĽ�Ǯ
	parameter4 = д��־��Ψһʱ��(����Ҫ��д��������ǰ�����ɽ�ɫ,��ʱ��������Ϊ�ж��Ƿ�Ϊͬһ�ε�ͳ������)

	type = 000600600101 action = classlevel_ranking  parameter1 = ��ҵĵȼ�  parameter2 = ��ҵ�ְҵ�ֲ�(�� ����:10 սʿ 20)
	parameter3 = д��־��Ψһʱ��(����Ҫ��д��������ǰ�����ɽ�ɫ,��ʱ��������Ϊ�ж��Ƿ�Ϊͬһ�ε�ͳ������)

	ͳ�ư�����Ϣ
	type = 000600600102 action = tong_info_ranking  parameter1 = ����DBID  parameter2 = ��������
	parameter3 = ���ȼ��� parameter4 = ���Ƹ� parameter5 = ��Ա����   parameter6 = ��Աƽ���ȼ�
	parameter7 = ��Ա��ߵȼ� parameter8 = ��Ա��͵ȼ�
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 19, message, *arg)

def FAMILY_CHANGE_SHAIKH( action,familyInfo,newShaikhDBID,oldShaikhDBID ):
	"""
	�����峤���
	type = 000500800321 action = family_shaikh_abdication  parameter1 = ��������ֺ�DBID  parameter2 = ���峤��DBID
	parameter3 = ԭ�峤��DBID		# �峤��λ
	type = 000500800321 action = family_reinstate_shaikh  parameter1 = ��������ֺ�DBID  parameter2 = ���峤��DBID	# �峤��ʧ��ɾ�ţ���ţ���������
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action, familyInfo,newShaikhDBID,oldShaikhDBID )

def FAMILY_SET_GRADE( action,familyInfo,operater,target,oldgrade,newgrade ):
	"""
	���ó�Ա��Ȩ��(�����ְ)
	type = 000500800322 action = family_set_memberGrade  parameter1 = ��������ֺ�DBID  parameter2 = �����ߵ�DBID
	parameter3 = Ŀ���DBID�� parameter4 = 	Ŀ��ԭ����Ȩ��  parameter5 = Ŀ�����ڵ�Ȩ��		# ���ó�ԱȨ��
	"""
	pass
	#bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action,familyInfo,operater,target,oldgrade,newgrade )

def TONG_CHANGE_LEADER( action,tongInfo,newLeaderDBID,oldLeaderDBID,reason ):
	"""
	���᳤���
	type = 000500800324 action = tong_leader_abdication  parameter1 = �������ֺ�DBID  parameter2 = �°�����DBID
	parameter3 = ԭ������DBID	parameter4 = ���ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s",action,tongInfo,newLeaderDBID,oldLeaderDBID,reason )

def TONG_SET_GRADE( action,tongInfo,operater,target,oldgrade,newgrade ):
	"""
	���ó�Ա��Ȩ��(�����ְ)
	type = 000500800325 action = tong_set_memberGrade  parameter1 = �������ֺ�DBID  parameter2 = �����ߵ�DBID
	parameter3 = Ŀ���DBID�� parameter4 = 	Ŀ��ԭ����Ȩ��  parameter5 = Ŀ�����ڵ�Ȩ��		# ���ó�ԱȨ��
	"""
	pass  # ��ʱ��д����־���о�û�б�Ҫ
	#bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s", action,tongInfo,operater,target,oldgrade,newgrade )

def TONG_STORE_QUERY_ITEMS( action,tongInfo,operater,itemuid,itemid,itemamount,bagID):
	"""
	��ȡ���ֿ����Ʒ
	type = 000500800326 action = tong_store_items  parameter1 = �������ֺ�DBID  parameter2 = �����ߵ�DBID
	parameter3 = ��ƷUID�� parameter4 = ��ƷID  parameter5 = ��Ʒ������	 parameter6 = �ֿ�İ���id	# �洢��Ʒ�����ֿ�

	type = 000500800326 action = tong_query_items  parameter1 = �������ֺ�DBID  parameter2 = �����ߵ�DBID
	parameter3 = ��ƷUID�� parameter4 = ��ƷID  parameter5 = ��Ʒ������	 parameter6 = �ֿ�İ���id	# �Ӱ��ֿ�ȡ����Ʒ
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s||%s||%s", action,tongInfo,operater,itemuid,itemid,itemamount,bagID )

def TONG_PRESTIGE_CHANGE( action,tongInfo,value,reason ):
	"""
	��������ı�
	action = tong_addPrestige tongInfo = �������ֺ�DBID value = ���ӵ�����ֵ reson = ����ԭ��
	action = tong_reducePrestige tongInfo = �������ֺ�DBID value = ���ٵ�����ֵ reson = ����ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action,tongInfo,value,reason )
	
def TONG_LEVEL_CHANGE( action,tongInfo,oldLevel,newLevel,reason ):
	"""
	���ȼ��ı�
	action = tong_addLevel tongInfo = �������ֺ�DBID oldLevel = �ı�ǰ�ȼ� newLevel = �ı��ȼ� reason = �ı�ԭ��
	action = tong_reduceLevel tongInfo = �������ֺ�DBID oldLevel = �ı�ǰ�ȼ� newLevel = �ı��ȼ� reason = �ı�ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s||%s", action,tongInfo,oldLevel,newLevel,reason )
	
def TONG_ADD_DELETE_MEMBER( action,tongInfo,playerDBID,tongMemberNum ):
	"""
	�����ɾ��Ա
	action = tong_add_member tongInfo = �������ֺ�DBID playerDBID = ���dbid tongMemberNum = �����������
	#
	action = tong_reduce_member tongInfo = �������ֺ�DBID playerDBID = ���dbid tongMemberNum = ɾ����������
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s||%s", action,tongInfo,playerDBID,tongMemberNum )
	
def TONG_ADD_DELETE_LEAGUE( action,tongInfo,leaguesNum ):
	"""
	�ﻧ����ͬ��
	action = tong_add_member tongInfo = �������ֺ�DBID leagusNum = �µ�ͬ������
	#
	action = tong_reduce_member tongInfo = �������ֺ�DBID leagusNum = �µ�ͬ������
	"""
	bwdebug.DATABASE_LOG_MSG( 14,"||%s||%s||%s", action,tongInfo,leaguesNum )

def ROLE_EXP_CHANGE( action, NameAndID, oldExp, oldLevel, nowExp, nowLevel, changeValue, changeReason):
	"""
	��Ҿ���ı���־
	type = 000300950001 action = role_exp_change  parameter1 = ��ҵ����ֺ�DBID  parameter2 = ���ԭ���ľ���
	parameter3 = ���ԭ���ĵȼ��� parameter4 = ������ڵľ���  parameter5 = ������ڵĵȼ�	 parameter6 = ����ı��ֵ
	parameter7 = �ı��ԭ��
	"""
	if changeReason in __LOG_ROLE_EXP_CHANGE_REASONS_FILTER:
		return
	bwdebug.DATABASE_LOG_MSG( 20,"||%s||%s||%s||%s||%s||%s||%s||%s",action, NameAndID, oldExp, oldLevel, nowExp, nowLevel, changeValue, changeReason )

def APEX_KILL_ROLE( action, NameAndID, reason, actiontype ):
	"""
	����Ҷ���ҵĲ��� ��������
	action = apex_killrole  parameter1 = ��ҵ����ֺ�DBID  parameter2 = ������ԭ��
	parameter3 = ���������� ���� ������
	"""
	bwdebug.DATABASE_LOG_MSG( 21,"||%s||%s||%s||%s",action, NameAndID, reason, actiontype)

def LOG_GM_WORKING( *arg ):
	"""
	ɾ����Ʒ
	action = gm_delete_item  parameter1 = ������GM�����ֺ�DBID parameter2 = ��ƷΨһID parameter3 = ��Ʒ����
	parameter4 = ��Ʒ����  parameter6 = GMȨ�� parameter5 = ɾ��ԭ��
	��Ǯ�ı�
	action = gm_money_change parameter1 = ����GM���ƺ�DBID parameter2 = ԭ���Ĵ����� parameter3 =���ڵĴ�����
	parameter4 =�ı������(��Ϊ���� ��Ϊ����) parameter5 = GMȨ�� parameter6 = �����Ҹı��ԭ��
	GMɱ��
	action = gm_kill_role parameter1 = ����������ƺ�DBID parameter2 = ���ֵ����ƺ�DBID  parameter3 = ���ֵ�Ȩ��
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 11, message, *arg)

def LOG_POINTCARD_TRADE( action, cardNumber, cardPrice, buyerName, buyerAccount ,sellerName ):
	"""
	�㿨����
	"""
	bwdebug.DATABASE_LOG_MSG( 9,"||%s||%s||%s||%s||%s||%s",action, cardNumber, cardPrice, buyerName, buyerAccount ,sellerName)

def LOG_GOLD_SILVER_CHANGE( action, playerNameAndID, value, oldvalue, reason, account ):
	"""
	��ҽ���Ԫ���ı�
	"""
	bwdebug.DATABASE_LOG_MSG( 28,"||%s||%s||%s||%s||%s||%s",action, playerNameAndID, value, oldvalue, reason, account)

def LOG_GAME_ACTIONS( *arg ):
	"""
	����Ӷ�ս
	action = tong_robwar parameter1 = ���A��dbid parameter2 = ���A������ parameter3 = ���B��dbid parameter4 = ���B������
	������
	action = wudao_war   parameter1 = �ȼ���      parameter2 = ��������
	������ս��
	action = family_challenge parameter1 = ����A��dbid parameter2 = ����A������ parameter3 = ����B��dbid parameter4 = ����B������
	��Ӿ���
	action = team_pk   parameter1 = �ȼ��� parameter2 = ��������
	���˾���
	action = role_pk   parameter1 = �ȼ��� parameter2 = ��������
	������ͳ��
	action = game_copy parameter1 = ��������
	����
	action = race_horse   parameter1 = ��������
	ħ����Ϯ
	action = startCampaignMonsterRaid parameter1 = ����DBID
	����ս
	action = tong_turn_war parameter1 = �������� parameter2 = ʤ������DBID�� parameter3 =�����Ա(dbid, playerName)�� parameter4 = ʧ�ܰ���DBID�� parameter5 = �����Ա(dbid, playerName), 
	�������
	action = tong_feng_huo_lian_tian parameter1 = �������� parameter2 = ʤ�����DBID�� parameter3 = ʧ�ܰ��DBID, parameter4 = �ڼ���
	�����ս
	action = tong_city_war parameter1 = �������� parameter2 = ʤ�����DBID�� parameter3 = ʧ�ܰ��DBID, parameter4 = �ڼ���
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 29, message, *arg)

def LOG_CITY_EARNING( *arg ):
	"""
	��������������
	action = city_repair_earning  parameter1 = ��ͼ����  parameter2 = NPC��ID  parameter3 = �����õĽ�Ǯ
	�����������Ʒ����
	action = city_sell_earning  parameter1 = ��ͼ����  parameter2 = NPC��ID  parameter3 = ���ۻ�õĽ�Ǯ
	"""
	paramNum = len( arg )
	message = "||%s" * paramNum
	bwdebug.DATABASE_LOG_MSG( 30, message, *arg)

def LOG_Activity( activityType, action, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
	"""
	�������־
	"""
	bwdebug.DATABASE_LOG_MSG( 31,"||%s||%s||%s||%s||%s||%s||%s||%s",activityType, action, param1, param2, param3, param4, param5, param6)


def LOG_Messy_Action( action, messyID, playerDBID, param1, param2, param3 ):
	"""
	������Ϊ��־
	"""
	bwdebug.DATABASE_LOG_MSG( 33,"||%s||%s||%s||%s||%s||%s", action, str(messyID), str(playerDBID), param1, param2, param3 )

def LOG_POTENTIAL_CHANGE( action, playerNameAndID, orgPotential, newPotential, reason):
	"""
	Ǳ�ܱ������־��¼
	action = potential_change
	orgPotential	�ı�ǰǱ��ֵ
	newPotential	�ı��Ǳ��ֵ
	reason			ԭ��
	"""
	bwdebug.DATABASE_LOG_MSG( 34,"||%s||%s||%s||%s||%s", action, playerNameAndID, orgPotential, newPotential, reason )

def LOG_EXTEND_STORAGE( action, playerNameAndID, extend_num, storage_num ):
	"""
	����ֿ���־��¼
	action = extend_storage
	extend_num	�U��ĴΔ�
	storage_num	���Ŀǰ�}���
	"""
	bwdebug.DATABASE_LOG_MSG( 35,"||%s||%s||%s||%s", action, playerNameAndID, extend_num, storage_num )

def LOG_PET_REPRODUCTION( action, playerNameAndID1, petData1, playerNameAndID2, petData2 ):
	"""
	���ﷱֳ��־
	action = pet_reproduction
	petData1 = ��������
	petData2 = ��������
	"""
	bwdebug.DATABASE_LOG_MSG( 36,"||%s||%s||%s||%s||%s", action, playerNameAndID1, petData1, playerNameAndID2, petData2 )

def LOG_AWARDS_ITEM( account, roele, orderform, itemId, amount, transactionID, remark ):
	"""
	��Ʒ������ȡ��־(�������Ͳ�������):
	action = Item_Awards  parameter1 = �˺����� parameter2 = ��ɫ���� parameter3 = ���ʶ
	parameter4 = ��ƷID parameter5 = ��Ʒ����, parameter6 = ���� parameter7 = ��ע
	"""
	bwdebug.DATABASE_LOG_MSG( 37,"||%s||%s||%s||%s||%s||%s||%s||%s","Item_Awards", account, roele, orderform, itemId, amount, transactionID, remark )

def LOG_Relation(action , parameter1 , parameter2 ):
	"""
	�����ϵ��־��ʦͽ�����ˡ����޵ȣ�
	action=������ϵ������ϵ��Ϊ	parameter1=���ID	parameter2=���ID	
	��Ϊ��ݹ�ϵ����parameter1Ϊ������ҵ�������parameter2Ϊ������ҵ�ID
	"""
	bwdebug.DATABASE_LOG_MSG( 38,"||%s||%s||%s" , action , parameter1 , parameter2 )

def LOG_Collection( action , parameter1 , parameter2 , parameter3 ):
	"""
	�ɼ���ɼ���Ϣ��¼��־
	action="caiji"	parameter1=��ͼ��	parameter2=��Դ�����	parameter3=���DBID
	"""
	bwdebug.DATABASE_LOG_MSG( 39,"||%s||%s||%s||%s" , action , parameter1 , parameter2 , parameter3 )

def LOG_ROLE_ADD_DAOHENG( roleDBID, point, reason ):
	"""
	���е�����
	"""
	bwdebug.DATABASE_LOG_MSG( 40,"||add||%s||%s||%s", roleDBID, point, reason )

def LOG_ROLE_SET_DAOHENG( roleDBID, point, reason ):
	"""
	���е�����
	"""
	bwdebug.DATABASE_LOG_MSG( 40,"||set||%s||%s||%s", roleDBID, point, reason )

def ERROR_MESSAGE():
	"""
	��ȡ��һ�εĴ�����Ϣ
	�ýӿ�ֻ����except�е��ò�������
	"""
	message = ""
	f = sys.exc_info()[2].tb_frame
	message += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :"
	funcName = f.f_code.co_name
	className = bwdebug._getClassName( f, funcName )
	message += "%s: %s: %s" % ( className,sys.exc_info()[0], sys.exc_info()[1] )

	return message

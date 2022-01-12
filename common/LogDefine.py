# -*- coding: gb18030 -*-
import csdefine

LOG_TYPE_QUEST		= 1		# ����
LOG_TYPE_ACT_COPY 	= 2		# �&����
LOG_TYPE_SKILL	 	= 3		# ����
LOG_TYPE_ORG		= 4		# ��֯��������ᣬ��������ݵȣ�
LOG_TYPE_FUNC		= 5		# ϵͳ����
LOG_TYPE_COUNT		= 6 	# ͳ��
LOG_TYPE_PRO		= 7		# ����

LOG_TYPE_ITEM		= 8 	# ��Ʒ
LOG_TYPE_MONEY		= 9 	# ��Ǯ
LOG_TYPE_SILVER		= 10	# ��Ԫ��
LOG_TYPE_GOLD		= 11	# ��Ԫ��

LOG_TYPE_EXCEPT		= 12	# �쳣
LOG_TYPE_GM			= 13	# GM���߲���

# --------------------------
# ����2������
# --------------------------
LT_QUEST_ACCEPT					= 1		#��������
LT_QUEST_COMPLETE				= 2		#�������
LT_QUEST_ABANDON				= 3		#��������

# --------------------------
# �&����2������
# --------------------------
LT_AC_START						= 1		#���ʼ
LT_AC_STOP						= 2		#�����
LT_AC_KILL_MONSTER				= 3		#��ɱ�����
LT_AC_JOIN						= 4		#�����
LT_AC_RESULT					= 5		#����
LT_AC_ANSWER					= 6		#�����
LT_AT_DISTRIBUTION				= 7		#�����
LT_AT_COPY_OPEN					= 8		#��������

# --------------------------
# ����2������
# --------------------------
LT_SKILL_LEARN					= 1 	#ѧϰ����
LT_SKILL_UPGRADE				= 2		#��������
LT_SKILL_REMOVE					= 3		#�������ܣ���ǰֻ������ܣ�

LT_SKILL_PG_LEARN				= 4		#ѧϰ�̹ż���
LT_SKILL_PG_UPGRADE				= 5		#�����̹ż���

LT_SKILL_TONG_LEARN				= 6		#ѧϰ��Ἴ��
LT_SKILL_TONG_UPGRADE			= 7		#������Ἴ��

LT_SKILL_PET_LEARN				= 8 	#����ѧϰ����
LT_SKILL_PET_UPGRADE			= 9		#������������

LT_SKILL_VEHICLE_LEARN			= 10	#���ѧϰ����
LT_SKILL_VEHICLE_UPGRADE		= 11	#�����������

# --------------------------
# ��֯2������
# --------------------------
# ���ڰ��
LT_ORG_TONG						= 0		# ���
LT_ORG_TONG_CREATE 				= 1		#��ᴴ��
LT_ORG_TONG_DISMISS				= 2		#����ɢ
LT_ORG_TONG_MONEY_CHANGE		= 3		#����Ǯ�仯
LT_ORG_TONG_BUILDING_CHANGE 	= 4		#��Ὠ���ȱ���
LT_ORG_TONG_ITEMBAGS_ADD		= 5		#���ֿ����Ʒ
LT_ORG_TONG_ITEMBAGS_REMOVE		= 6		#���ֿ�ȡ��Ʒ
LT_ORG_TONG_UPLEVEL				= 7		#�������
LT_ORG_TONG_DEMOTION			= 8		#��ή��
LT_ORG_TONG_PRESTIGE_CHANGE		= 9		#��������ı�
LT_ORG_TONG_MEMBER_ADD			= 10	#�������Ա
LT_ORG_TONG_MEMBER_REMOVE		= 11	#���ɾ����Ա
LT_ORG_TONG_LEADER_CHANGE		= 12	#�����ı�
LT_ORG_TONG_SET_GRADE			= 13	#����ԱȨ������
LT_ORG_TONG_WAGE				= 14	#��Ṥ��
LT_ORG_TONG_CITY_WAR_SET_MASTER	= 15	#���ó���
LT_ORG_TONG_CITY_G_REVENUE		= 16	#������ȡ˰��
LT_ORG_TONG_CITY_R_REVENUE		= 17	#��ȡ˰��
LT_ORG_TONG_EXP_CHANGE			= 18	#��ᾭ��仯

# ����
LT_ORG_MARRY_SWEETIE			= 100	#����
LT_ORG_MARRY_SWEETIE_BUILD		= 101	#���˹�ϵ����
LT_ORG_MARRY_SWEETIE_REMOVE		= 102	#���˹�ϵ���
LT_ORG_MARRY_COUPLE_BUILD		= 103	#���޹�ϵ����
LT_ORG_MARRY_COUPLE_REMOVE		= 104	#���޹�ϵ���

# ʦͽ
LT_ORG_TEACH					= 200	#ʦͽ
LT_ORG_TEACH_BUILD				= 201	#����ʦͽ��ϵ
LT_ORG_TEACH_REMOVE				= 202	#���ʦͽ��ϵ
LT_ORG_TEACH_COMPLETE			= 203	#��ʦ

# ���
LT_ORG_ALLY						= 300	#���
LT_ORG_ALLY_CHANGE				= 301	#����б�ĸ�

# --------------------------
# ����2������
# --------------------------
# GM����
LT_FUNC_GM						= 0		#GM����
LT_FUNC_GM_COMMAND				= 1		#ʹ��GMָ��

# �ʼ�ϵͳ
LT_FUNC_MAIL					= 100	#�ʼ�ϵͳ
LT_FUNC_MAIL_SEND				= 101	#�����ʼ�
LT_FUNC_MAIL_READ				= 102	#�Ķ��ʼ�
LT_FUNC_MAIL_RETURN				= 103	#��������
LT_FUNC_MAIL_REMOVE				= 104	#ɾ���ʼ�
LT_FUNC_MAIL_SYS_RETURN			= 105	#ϵͳ����
LT_FUNC_MAIL_UP_TIME			= 106	#�����ʼ�ʱ��

# �˺�
LT_FUNC_ACCOUNT					= 200	#�˺�
LT_FUNC_ACCOUNT_REGISTER		= 201	#�˺�ע��
LT_FUNC_ACCOUNT_LOGON			= 202	#�˺ŵ�½
LT_FUNC_ACCOUNT_LOGOUT			= 203	#�˺�����

# ��ɫ
LT_FUNC_ROLE					= 300	#��ɫ
LT_FUNC_ROLE_LOGON				= 301	#��ɫ����
LT_FUNC_ROLE_LOGOUT				= 302	#��ɫ���ؽ�ɫѡ��
LT_FUNC_ROLE_UPGRADE			= 303	#��ɫ����
LT_FUNC_ROLE_START_TRAININGS	= 304	#��ɫ�������
LT_FUNC_ROLE_BEKILL				= 305	#��ɫ����ɱ
LT_FUNC_ROLE_ONLINE				= 306	#��ɫ�������
LT_FUNC_ROLE_ADD				= 307	#��ɫ���
LT_FUNC_ROLE_DELETE				= 308	#��ɫɾ�� 
LT_FUNC_ROLE_LOGOFF				= 309	#��ɫ�����˺ŵ�½
LT_FUNC_ROLE_SEND_RUMOR			= 310	#��ɫ��ҥ��


# ��̯
LT_FUNC_VEND					= 400	#��Ұ�̯

# װ��
LT_FUNC_EQUIP					= 500	#װ��
LT_FUNC_EQUIP_STILETTO			= 501	#װ�����
LT_FUNC_EQUIP_INTENSIFY			= 502	#װ��ǿ��
LT_FUNC_EQUIP_REBUILD			= 503	#װ������
LT_FUNC_EQUIP_BIND				= 504	#װ������
LT_FUNC_EQUIP_SPECIAL_COMPOSE	= 505	#װ������ϳ�
LT_FUNC_EQUIP_IMPROVE_QUALITY	= 506	#��װ��Ʒ
LT_FUNC_EQUIP_REFINE_GODWEAPON	= 507	#��������
LT_FUNC_EQUIP_STUFF_COMPOSE		= 508	#���Ϻϳ�
LT_FUNC_EQUIP_SPLIT				= 509	#װ���ֲ�
LT_FUNC_EQUIP_STUDDED			= 510	#װ����Ƕ
LT_FUNC_EQUIP_CHANGE_PROPERTY	= 511	#��װϴǰ׺
LT_FUNC_EQUIP_MAKE				= 512	#װ������
LT_FUNC_EQUIP_REPAIR_NORMAL		= 513	#װ����ͨ����

# ˮ��
LT_FUNC_CRYSTAL					= 600	#ˮ��
LT_FUNC_CRYSTAL_REMOVE			= 601	#ˮ��ժ��

# ����
LT_FUNC_TALISMAN				= 700	#����
LT_FUNC_TALISMAN_ADD_LIFE		= 701	#������ֵ
LT_FUNC_TALISMAN_SPLIT			= 702	#�����ֽ�
LT_FUNC_TALISMAN_INTENSIFY		= 703	#����ǿ��

#����
LT_FUNC_PET						= 800	#����
LT_FUNC_PET_ADD					= 801	#��ó���
LT_FUNC_PET_DEL					= 802	#ʧȥ����
LT_FUNC_PET_BREED				= 803 	#���ﷱֵ
LT_FUNC_PET_START_TRAININGS		= 804	#���ﾭ�����

#����
LT_FUNC_TRADE					= 900	#����
LT_FUNC_TRADE_NPC_BUY			= 901	#��NPC������
LT_FUNC_TRADE_NPC_SELL			= 902	#�Ѷ�������NPC
LT_FUNC_TRADE_SWAP_MONEY		= 903	#��ҽ��׽�Ǯ
LT_FUNC_TRADE_SWAP_ITEM			= 904	#��ҽ�����Ʒ
LT_FUNC_TRADE_SWAP_PET			= 905	#��ҽ��׳���

#�������
LT_FUNC_TI_SHOU					= 1000	#�������
LT_FUNC_TI_SHOU_BUY_PET			= 1001	#�������Ϲ������
LT_FUNC_TI_SHOU_BUY_ITEM		= 1002	#�������Ϲ�����Ʒ

#�ɼ�
LT_FUNC_COLLECT					= 1100	#�ɼ�

#�㿨
LT_FUNC_PC						= 1200	#�㿨
LT_FUNC_PC_RECHARGE				= 1201	#�㿨��ֵ

#�����
LT_FUNC_AP						= 1300	#�����
LT_FUNC_AP_KICK_ROLE			= 1301	#��������������

#����ֿ�
LT_FUNC_PET_STORAGE				= 1400	#����ֿ�
LT_FUNC_PET_STORAGE_ADD			= 1401	#������ֿ�����
LT_FUNC_PET_STORAGE_TAKE		= 1402	#�ӳ���ֿ�ȡ����

#�����̳�
LT_FUNC_SPECIAL_STOP			= 1500	#�����̳�
LT_FUNC_SPECIAL_STOP_BUY		= 1501	#���̳������

#�ֿ�
LT_FUNC_BANK					= 1600	#�ֿ�
LT_FUNC_BANK_STORE				= 1601	#����Ʒ
LT_FUNC_BANK_TAKE				= 1602	#ȡ��Ʒ
LT_FUNC_BANK_DES				= 1603	#������Ʒ
LT_FUNC_BANK_EXTEND				= 1604	#�س�ֿ�

#������ȡ
LT_FUNC_PRESENT					= 1700	#����
LT_FUNC_PRESENT_PACKAGE			= 1701	#��Ʒ��
LT_FUNC_PRESENT_SILVER			= 1702	#��Ԫ������
LT_FUNC_PRESENT_CHARGE			= 1703	#��ֵ��ȡ

# ͳ��
LT_COUNT_ROLE_WEALTH			= 1		#��ɫ��Ǯͳ��
LT_COUNT_ROLE_LEVEL				= 2		#��ɫ�ȼ�&ְҵͳ��
LT_COUNT_ROLE_COUNT				= 3		#��ǰ���߽�ɫ
LT_COUNT_TONG_INFO				= 4		#�����Ϣͳ��
LT_COUNT_TONG_COUNT				= 5		#������ͳ��
LT_COUNT_ONLINE_ACCOUNT			= 6		#�����˺���

# --------------------------
# �������2������
# --------------------------
LT_PRO_EXP_CHANGE				= 1		#����ı�
LT_PRO_POTENTIAL_CHANGE			= 2		#Ǳ�ܸı�

# ����
LT_PRO_DAOHENG					= 100	#����
LT_PRO_DAOHENG_ADD				= 101	#��ɫ������������
LT_PRO_DAOHENG_SET				= 102	#���ý�ɫ��������

#����
LT_PRO_SCORE_HONOR				= 200	#����
LT_PRO_SCORE_HONOR_ADD			= 201	#������������
LT_PRO_SCORE_HONOR_SUB			= 202	#������������

LT_PRO_SCORE_PERSONAL_ADD		= 203	#���Ӹ��˾�������
LT_PRO_SCORE_PERSONAL_SUB		= 204	#���ٸ��˾�������

LT_PRO_SCORE_TONG_SCORE_ADD		= 205	#���Ӱ�Ὰ������
LT_PRO_SCORE_TONG_SCORE_SUB		= 206	#���ٰ�Ὰ������

LT_FUNC_TEAM_COMPETITION_ADD	= 207	#�����Ӿ�������
LT_FUNC_TEAM_COMPETITION_SUB	= 208	#������Ӿ�������

# --------------------------
# ��Ʒ2������
# --------------------------
LT_ITEM_ADD						= 1		#�����Ʒ
LT_ITEM_DEL						= 2		#ɾ����Ʒ
LT_ITEM_SET_AMOUNT				= 3		#������Ʒ����

# --------------------------
# ��Ǯ2������
# --------------------------
LT_MONEY_CHANGE					= 1		#��ɫ��Ǯ�ı�

# --------------------------
# ��Ԫ��2������
# --------------------------
LT_SILVER_CHANGE				= 1		#��Ԫ���ı�

# --------------------------
# ��Ԫ��2������
# --------------------------
LT_GOLD_CHANGE					= 1		#��Ԫ���ı�

# --------------------------
# �쳣����
# --------------------------
LT_EXCEPT_LOG					= 1		#��־�쳣
LT_EXCEPT_LOTTERY				= 2		#���Ҵ���
LT_EXCEPT_ITEM_DROP				= 3		#��Ʒ�������ô���
LT_EXCEPT_CHARGE_PRESENT		= 4		#��ȡ��������

#---------------------------
# GM���߲���
#---------------------------
LOG_GM_RESET_BANK_PW		= 1		#����ֿ�����
LOG_GM_CHANGE_POS			= 2		#���Ľ�ɫ����
LOG_GM_RESUME_ROLE			= 3		#��ɫ�ָ�
LOG_GM_ACCOUNT_HOSTING		= 4		#�ʺ��й�
LOG_GM_MODIFY_BULLETIN		= 5		#�޸Ĺ���
LOG_GM_BATCH_LOCK_ACC		= 6		#�������
LOG_GM_BLOCK_ACC			= 7		#����˺�
LOG_GM_FREE_ACC				= 8		#�����˺�
LOG_GM_MODIFY_MONEY			= 9		#�޸Ľ�ɫ������
LOG_GM_MODIFY_PK_VALUE		= 10	#�޸�PKֵ
LOG_GM_MODIFY_PET_STRORAGE	= 11	#�����޸�
LOG_GM_MODIFY_GOLD_SILVER	= 12	#�޸��ʺ�Ԫ��
LOG_GM_MODIFY_RELATION		= 13	#�޸Ľ�ɫ��ϵ
LOG_GM_ADD_BULLETIN			= 14	#��ӹ���
LOG_GM_MODIFY_WEB_PRESENTID	= 15	#����web����ID
LOG_GM_CONFIG_ITEMAWARDS	= 16	#��������
LOG_GM_DELETE_ITEM			= 17	#ɾ�������Ʒ
LOG_GM_DELETE_MAIL			= 18	#ɾ������ʼ�
LOG_GM_DELETE_BUFF			= 19	#ɾ�����buff
LOG_GM_DELETE_PET_ITEM		= 20	#ɾ������buff

# WebServer����
LOG_GM_UPDATE_PASSWORD		= 21	#�޸��˺�����
LOG_GM_WEB_SUSPEND_ACC		= 22	#WebServer����˺�
LOG_GM_WEB_RESUME_ACC		= 23	#WebServer����˺�
LOG_GM_SET_ADULT			= 24	#����û�Ϊ������
LOG_GM_GIVE_PRESENTS		= 25	#Ϊָ���˺��ͳ�����
LOG_GM_CHECK_PRESENTS_RE	= 26	#��鶩���ŵķ���Ʒ(�ط�)
LOG_GM_CHECK_PRESENTS		= 27	#��鶩���ŵķ���Ʒ
LOG_GM_USE_JACKAROO_CARD	= 28	#����ʹ�����ֿ��û�
LOG_GM_GIFT_SILVER_COINS_RE	= 29	#������Ԫ�����ط���
LOG_GM_GIFT_SILVER_COINS	= 30	#������Ԫ��
LOG_GM_CHARGE_RE			= 31	#�һ�Ԫ�����ط���
LOG_GM_CHARGE				= 32	#�һ�Ԫ��



#�������ͻ
COPYSPACE_ACTIVITYS = {
	csdefine.SPACE_TYPE_CITY_WAR				:	csdefine.ACTIVITY_TONG_DUO_CHENG,
	csdefine.SPACE_TYPE_TONG_ABA				:	csdefine.ACTIVITY_BANG_HUI_LEI_TAI,
	csdefine.SPACE_TYPE_TIAN_GUAN				:	csdefine.ACTIVITY_CHUANG_TIAN_GUAN,
	csdefine.SPACE_TYPE_RACE_HORSE				:	csdefine.ACTIVITY_SAI_MA,
	csdefine.SPACE_TYPE_POTENTIAL				:	csdefine.ACTIVITY_POTENTIAL,
	csdefine.SPACE_TYPE_WU_DAO					:	csdefine.ACTIVITY_WU_DAO_DA_HUI,
	csdefine.SPACE_TYPE_SHEN_GUI_MI_JING		:	csdefine.ACTIVITY_SHEN_GUI_MI_JING,
	csdefine.SPACE_TYPE_WU_YAO_QIAN_SHAO		:	csdefine.ACTIVITY_WU_YAO_QIAN_SHAO,
	csdefine.SPACE_TYPE_WU_YAO_WANG_BAO_ZANG	:	csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG,
	csdefine.SPACE_TYPE_SHUIJING				:	csdefine.ACTIVITY_SHUI_JING,
	csdefine.SPACE_TYPE_HUNDUN					:	csdefine.ACTIVITY_HUN_DUN_RU_QIN,
	csdefine.SPACE_TYPE_TEAM_COMPETITION		:	csdefine.ACTIVITY_TEAM_COMPETITION,
	csdefine.SPACE_TYPE_DRAGON					:	csdefine.ACTIVITY_DRAGON,
	csdefine.SPACE_TYPE_PROTECT_TONG			:	csdefine.ACTIVITY_TONG_PROTECT,
	csdefine.SPACE_TYPE_POTENTIAL_MELEE			:	csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU,
	csdefine.SPACE_TYPE_EXP_MELEE				:	csdefine.ACTIVITY_JING_YAN_LUAN_DOU,
	csdefine.SPACE_TYPE_PIG						:	csdefine.ACTIVITY_DU_DU_ZHU,
	csdefine.SPACE_TYPE_YAYU					:	csdefine.ACTIVITY_ZHENG_JIU_YA_YU,
	csdefine.SPACE_TYPE_XIE_LONG_DONG_XUE		:	csdefine.ACTIVITY_XIE_LONG,
	csdefine.SPACE_TYPE_FJSG					:	csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG,
	csdefine.SPACE_TYPE_TONG_COMPETITION		:	csdefine.ACTIVITY_BANG_HUI_JING_JI,
	csdefine.SPACE_TYPE_ROLE_COMPETITION		:	csdefine.ACTIVITY_GE_REN_JING_JI,
	csdefine.SPACE_TYPE_SHE_HUN_MI_ZHEN			:	csdefine.ACTIVITY_SHE_HUN_MI_ZHEN,
	csdefine.SPACE_TYPE_TEACH_KILL_MONSTER		:	csdefine.ACTIVITY_SHI_TU,
	csdefine.SPACE_TYPE_KUAFU_REMAINS			:	csdefine.ACTIVITY_KUA_FU,
	csdefine.SPACE_TYPE_RABBIT_RUN				:	csdefine.ACTIVITY_RUN_RABBIT,
	csdefine.SPACE_TYPE_BEFORE_NIRVANA			:	csdefine.ACTIVITY_BEFORE_NIRVANA,
	csdefine.SPACE_TYPE_CHALLENGE				:	csdefine.ACTIVITY_CHALLENGE_FUBEN,
	csdefine.SPACE_TYPE_TEAM_CHALLENGE			:	csdefine.ACTIVITY_TEAM_CHALLENGE,
	csdefine.SPACE_TYPE_PLOT_LV40				:	csdefine.ACTIVITY_PLOT_LV40,
	csdefine.SPACE_TYPE_PLOT_LV60				:	csdefine.ACTIVITY_PLOT_LV60,
	csdefine.SPACE_TYPE_TOWER_DEFENSE			:	csdefine.ACTIVITY_TOWER_DEFENSE,
	csdefine.SPACE_TYPE_YXLM					:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG,
	csdefine.SPACE_TYPE_YE_ZHAN_FENG_QI			:	csdefine.ACTIVITY_YE_ZHAN_FENG_QI,
	csdefine.SPACE_TYPE_TONG_TURN_WAR			:	csdefine.ACTIVITY_TONG_TURN_WAR,
	csdefine.SPACE_TYPE_YXLM_PVP				:	csdefine.ACTIVITY_YING_XIONG_LIAN_MENG_PVP,
	csdefine.SPACE_TYPE_FENG_HUO_LIAN_TIAN		:	csdefine.ACTIVITY_TONG_FENG_HUO_LIAN_TIAN,
	csdefine.SPACE_TYPE_TIAO_WU					:	csdefine.ACTIVITY_TIAO_WU,
	}



MONSTER_DIED_ABOUT_ACTIVITYS =	{
	csdefine.ACTIVITY_CHUANG_TIAN_GUAN			:	[ 20611156,20621156,20631156,20641156,20651156 ],	#�����
	csdefine.ACTIVITY_BIN_LIN_CHENG_XIA			:	[ 20614002,20624003,20634002,20644001,20654002,20614004,20624005,20624008 ],	#���ٳ���
	csdefine.ACTIVITY_DU_DU_ZHU					:	[ 20354002 ],
	csdefine.ACTIVITY_FENG_JIAN_SHEN_GONG		:	[ 20742031 ],	#�⽣��
	csdefine.ACTIVITY_HUN_DUN_RU_QIN			:	[ 20124001,20134001,20144001 ],		#��������
	csdefine.ACTIVITY_NIU_MO_WANG				:	[ 20714003 ],						#ţħ��
	csdefine.ACTIVITY_QIAN_NIAN_DU_WA			:	[ 20334003 ],						#ǧ�궾��
	csdefine.ACTIVITY_JING_YAN_LUAN_DOU			:	[ 20654003 ],						#�����Ҷ�
	csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU		:	[ 20754009 ],						#Ǳ���Ҷ�
	csdefine.ACTIVITY_SHE_HUN_MI_ZHEN			:	[ 20714004 ],						#�������
	csdefine.ACTIVITY_SHUI_JING					:	[ 20724002 ],						#ˮ������
	csdefine.ACTIVITY_TIAN_JIANG_QI_SHOU		:	[ 20314006 ],						#�콵����
	csdefine.ACTIVITY_ZHENG_JIU_YA_YU			:	[ 20754011 ],						#���Ȫm؅
	csdefine.ACTIVITY_DUO_LUO_LIE_REN			:	[ 20134003 ],						#��������55
	csdefine.ACTIVITY_BAI_SHE_YAO				:	[ 20724004 ],						#������56
	csdefine.ACTIVITY_JU_LING_MO				:	[ 20714002 ],						#����ħ57
	csdefine.ACTIVITY_XIAO_TIAN_DA_JIANG		:	[ 20724005 ],						#Х���58
	csdefine.ACTIVITY_FENG_KUANG_JI_SHI			:	[ 20144003 ],						#����ʦ59
	csdefine.ACTIVITY_HAN_DI_DA_JIANG			:	[ 20754012 ],						#���ش�60
	csdefine.ACTIVITY_SHENG_LIN_ZHI_WANG		:	[],									#ɭ��֮��
	csdefine.ACTIVITY_NU_MU_LUO_SHA				:	[],									#ŭĿ��ɲ
	csdefine.ACTIVITY_YE_WAI_BOSS				:	[ 20324001,20354001,20314001,20324002,20344001,20344002,20314002,20324003,20334001,20314003,20344003,20654001,20254001,20624001,20444001,20344004,20714001,20614001,20314004,20334002,20624002,20744001,20754001,20754002,20344005,20634001,20744002,20744003,20324004,20614003,20434001,20454001,20324005,20724001,20624004,20214001,20624007,20644003,20334004,20624006,20644004,20654004 ],
	csdefine.ACTIVITY_TONG_PROTECT				:	[20114002,20124002,20134002,20144002],
}


# -*- coding: gb18030 -*-
import Language
import sys
import bwdebug
from LogDefine import *

	
class MsgLogger( object ):
	_instance = None
	def __init__( self ):
		object.__init__( self )
	
	@staticmethod
	def instance():
		if MsgLogger._instance is None:
			MsgLogger._instance = MsgLogger()
		return MsgLogger._instance
	
	def getErrorMsg( self ):
		message = ""
		f = sys.exc_info()[2].tb_frame
		message += f.f_code.co_filename + "(" + str( f.f_lineno ) + ") :"
		funcName = f.f_code.co_name
		className = bwdebug._getClassName( f, funcName )
		message += "%s: %s: %s" % ( className,sys.exc_info()[0], sys.exc_info()[1] )

		return message
	
	#-----------------------------------
	# ����
	#-----------------------------------
	def questLog( self, action, roleDBID, roleName, questID, param1 = "", param2 = "",  param3 = "", param4 = "" ):
		"""
		���������־
		action:������Ϊ
		questID:����ID
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_QUEST,"||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, questID, param1, param2, param3, param4 )
	
	def acceptQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade ):
		""" 
		��������
		"""
		self.questLog( LT_QUEST_ACCEPT, roleDBID, roleName, questID, playerLevel, playerGrade )
	
	def completeQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade, useTime ):
		"""
		��������
		useTime:ʹ�ö���ʱ��
		"""
		self.questLog( LT_QUEST_COMPLETE, roleDBID, roleName, questID, playerLevel, playerGrade, useTime )
	
	def abandonQuestLog( self, roleDBID, roleName, questID, playerLevel, playerGrade):
		"""
		��������
		"""
		self.questLog( LT_QUEST_ABANDON, roleDBID, roleName, questID, playerLevel, playerGrade )
	
	#-----------------------------------
	# �&����
	#-----------------------------------
	def actCopyLog( self, action, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = "" ):
		"""
		��ӻ&������־
		activityType: �����
		action:��Ϊ
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ACT_COPY,"||%s||%s||%s||%s||%s||%s||%s||%s||%s", action, activityType, param1, param2 , param3, param4, param5, param6, param7 )
	
	def actStartLog( self, activityType ):
		"""
		���ʼ
		"""
		self.actCopyLog( LT_AC_START, activityType )
	
	def actStopLog( self, activityType ):
		"""
		�����
		"""
		self.actCopyLog( LT_AC_STOP, activityType )
	
	def actKillMonsterLog( self, activityType, killDBID, killName, monsterClassName ):
		"""
		����ﱻ��ɱ
		"""
		self.actCopyLog( LT_AC_KILL_MONSTER, activityType, killDBID, killName, monsterClassName )
	
	def actMonsterDieLog( self, killDBID, killName, className ):
		"""
		���������
		"""
		activityType = 0
		for k,v in MONSTER_DIED_ABOUT_ACTIVITYS.iteritems():
			if className in v:
				activityType = k
				break
				
		if activityType:
			self.actKillMonsterLog( activityType, killDBID, killName, className )
	
	def actJoinLog( self, activityType, joinType, joinDBID, joinLevel, joinName ):
		"""
		�����
		joinDBID:Ҫ��joinType����,�����ǰ��DBID,�����Ǹ���DBID
		"""
		self.actCopyLog( LT_AC_JOIN, activityType, joinType, joinDBID, joinLevel, joinName )
		
	def actJoinEnterSpaceLog( self, spaceType, joinType, joinDBID, joinLevel, joinName ):
		"""
		���븱����,ת�������
		"""
		if COPYSPACE_ACTIVITYS.has_key( spaceType ): # ���������б���,��ʾ����Ҫ��¼
			self.actJoinLog( COPYSPACE_ACTIVITYS[ spaceType ], joinType, joinDBID, joinLevel, joinName )
	
	def actResultLog( self, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		����
		��ᳵ��ս�� param1����������, param2��ʤ�����, param3��ʤ�������Ա, param4��ʧ�ܰ��, param5��ʧ�ܰ���Ա ��
		������죨 param1����������, param2��ʤ�����, param3:ʧ�ܰ��, param4���ڼ��ֱ��� ��
		"""
		self.actCopyLog( LT_AC_RESULT, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" )
	
	
	def actAnswerLog( self, activityType, roleDBID, roleName, result, param1 = "", param2 = "" ):
		"""
		�����
		activityType�������
		roleDBID����ɫDBID
		result��������
		"""
		self.actCopyLog( LT_AC_ANSWER, activityType, roleDBID, roleName, result, param1, param2 )
	
	def actDistributionLog( self, activityType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = ""  ):
		"""
		�����
		����Ӷ�ս��param1��A���DBID,param2��A�������,param3��B���DBID,param4��B������� ��
		"""
		self.actCopyLog( LT_AT_DISTRIBUTION, activityType, param1, param2, param3, param4, param5 )
	
	def actCopyOpenLog( self, className ):
		"""
		��������ͳ��
		"""
		self.actCopyLog( LT_AT_COPY_OPEN, className )
	#-----------------------------------
	# ����
	#-----------------------------------
	def skillLog( self, action, roleDBID, roleName, skillID, param1 = "", param2 = "", param3 = "", param4 = "" ):
		"""
		��Ӽ�����־
		action:ѧ��,��������
		reason:��÷�ʽ
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_SKILL,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, skillID, reason, param1, param2, param3, param4 )
	
	def skillLearnLog( self, roleDBID, roleName, skillID, usePotential, useMoney ):
		"""
		��ɫѧϰ�¼���
		"""
		self.skillLog( LT_SKILL_LEARN, roleDBID, roleName, skillID, usePotential, useMoney )
	
	def skillUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney ):
		"""
		��ɫ��������
		"""
		self.skillLog( LT_SKILL_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	def skillRemoveLog( self, roleDBID, roleName, skillID ):
		"""
		��ɫ�������ܣ�Ŀǰֻ������ܣ�
		"""
		self.skillLog( LT_SKILL_REMOVE, roleDBID, roleName, skillID )
	
	def skillPGLearnLog( self, roleDBID, roleName, skillID ):
		"""
		��ɫѧϰ�̹ż���
		"""
		self.skillLog( LT_SKILL_PG_LEARN, roleDBID, roleName, skillID )
	
	def skillPGUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID ):
		"""
		��ɫ�����̹ż���
		"""
		self.skillLog( LT_SKILL_PG_UPGRADE, roleDBID, roleName, skillID, oldSkillID )
	
	def skillTongLearnLog( self, roleDBID, roleName, skillID, usePotential, useMoney ):
		"""
		��ɫѧϰ��Ἴ��
		"""
		self.skillLog( LT_SKILL_TONG_LEARN, roleDBID, roleName, skillID, usePotential, useMoney )
	
	def skillTongUpgradeLog( self, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney ):
		"""
		��ɫ������Ἴ��
		"""
		self.skillLog( LT_SKILL_TONG_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	def skillPetLearnLog( self, roleDBID, roleName, petDBID, skillID ):
		"""
		����ѧϰ����
		"""
		self.skillLog( LT_SKILL_PET_LEARN, roleDBID, roleName, petDBID, skillID )
	
	def skillPetUpgradeLog( self, roleDBID, roleName, petDBID, skillID, oldSkillID ):
		"""
		������������
		"""
		self.skillLog( LT_SKILL_PET_UPGRADE, roleDBID, roleName, petDBID, skillID, oldSkillID )
	
	def skillVehicleLearnLog( self, roleDBID, roleName, vehicleID, skillID, usePotential, useMoney ):
		"""
		���ѧϰ����
		"""
		self.skillLog( LT_SKILL_VEHICLE_LEARN, roleDBID, roleName, vehicleID, skillID, usePotential, useMoney )
	
	def skillVehicleUpgradeLog( self, roleDBID, roleName, vehicleID, skillID, oldSkillID, usePotential, useMoney ):
		"""
		�����������
		"""
		self.skillLog( LT_SKILL_VEHICLE_UPGRADE, roleDBID, roleName, skillID, oldSkillID, usePotential, useMoney )
	
	#-----------------------------------
	# ��֯
	#-----------------------------------
	def orgLog( self, orgType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = "", param8 = "", param9 = ""):
		"""
		�����֯��־
		orgType:���,����,ʦͽ
		ԭ��:�˰��,������,���,��顭��
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ORG,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s",orgType, param1, param2, param3, param4, param5, param6, param7, param8, param9 )
		
	# ���
	def tongCreateLog( self, tongDBID, tongName, creatorDBID, creatorName  ):
		"""
		��ᴴ��
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CREATE, tongName, creatorDBID, creatorName )
	
	def tongDismissLog( self, tongDBID, tongName, reason ):
		"""
		����ɢ
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_DISMISS, tongDBID, tongName, reason )

	def tongMoneyChangeLog( self, tongDBID, tongName, oldValue, newValue, reason ):
		"""
		����Ǯ�ı�
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MONEY_CHANGE, tongDBID, tongName, oldValue, newValue, reason )
	
	def tongBuildingChangeLog( self, tongDBID, tongName, buildingType, oldValue, newValue ):
		"""
		��Ὠ���ȸı�
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_BUILDING_CHANGE, tongDBID, tongName, buildingType, oldValue, newValue  )
	
	def tongItemAddLog( self, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID  ):
		"""
		���ֿ���Ʒ���
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_ITEMBAGS_ADD, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID )
	
	def tongItemRemoveLog( self, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID  ):
		"""
		���ֿ���Ʒɾ��
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_ITEMBAGS_REMOVE, tongDBID, tongName, roleDBID, roleName, itemUID, itemID, itemNum, itembagID )
	
	def tongUpgradeLog( self, tongDBID, tongName, tongLevel, reason ):
		"""
		�������
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_UPLEVEL, tongDBID, tongName, tongLevel, reason )
	
	def tongDemotionLog( self, tongDBID, tongName, tongLevel, reason ):
		"""
		��ή��
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_DEMOTION, tongDBID, tongName, tongLevel, reason )
	
	def tongPrestigeChangeLog( self, tongDBID, tongName, oldPrestige, nowPrestige, reason ):
		"""
		��������ı�
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_PRESTIGE_CHANGE, tongDBID, tongName, oldPrestige, nowPrestige, reason )
	
	def tongMemberAddLog( self, tongDBID, tongName, roleDBID, roleName, count ):
		"""
		�������³�Ա
		count:��ǰ���������
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MEMBER_ADD, tongDBID, tongName, roleDBID, roleName, count  )
	
	def tongMemberRemoveLog( self, tongDBID, tongName, roleDBID, roleName, count ):
		"""
		���ɾ����Ա
		count:��ǰ���������
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_MEMBER_REMOVE, tongDBID, tongName, roleDBID, roleName, count )
	
	def tongLeaderChangeLog( self, tongDBID, tongName, roleDBID, roleName, reason = 0 ):
		"""
		���᳤�ı�
		memNums:��ǰ���������
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_LEADER_CHANGE, tongDBID, tongName, roleDBID, roleName, reason  )
	
	def tongSetGradeLog( self, tongDBID, tongName, doRoleDBID, doRoleName, setRoleDBID, setRoleName, oldGrade, nowGrade ):
		"""
		������ó�ԱȨ��
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_SET_GRADE, tongDBID, tongName, doRoleDBID, doRoleName, setRoleDBID, setRoleName, oldGrade, nowGrade  )
		
	def tongWageLog( self, tongDBID, tongName, roleName, roleGrade, money ):
		"""
		��Ṥ�ʷ���
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_WAGE, tongDBID, tongName, roleName, roleGrade, money  )
	
	def tongCityWarSetMasterLog( self, tongDBID, tongName, cityName ):
		"""
		���ó���
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_WAR_SET_MASTER, tongDBID, tongName, cityName )
	
	def tongGetRevenueLog( self, tongDBID, tongName, memberDBID, money ):
		"""
		��ȡ˰��
		memberDBID:��ȡ�˵�DBID
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_G_REVENUE,tongDBID, tongName, memberDBID, money )
	
	def tongReceiveRevenueLog( self, tongDBID, tongName, cityName, money ):
		"""
		��˰
		tongDBID:ռ�����
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_CITY_R_REVENUE, tongDBID, tongName, cityName, money )
	
	def tongExpChangeLog(  self, tongDBID, tongName, oldValue, newValue, reason ):
		"""
		��ᾭ��ı�
		"""
		self.orgLog( LT_ORG_TONG, LT_ORG_TONG_EXP_CHANGE, tongDBID, tongName, oldValue, newValue, reason )

	#����
	def sweeticBuildLog( self, roleDBID, roleName, tRoleDBID, tRoleName ):
		"""
		���˹�ϵ�Ľ���
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_SWEETIE_BUILD, roleDBID, roleName, tRoleDBID, tRoleName )
	
	def sweeticRemoveLog( self, roleDBID, roleName, tRoleDBID ):
		"""
		���˹�ϵ�Ľ��
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_SWEETIE_REMOVE, roleDBID, roleName, tRoleDBID )
	
	def coupleBuildLog( self, roleDBID, roleName, tRoleDBID, troleName ):
		"""
		�������޹�ϵ
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_COUPLE_BUILD, roleDBID, roleName, tRoleDBID, troleName )
	
	def coupleRemoveLog( self, roleDBID, roleName, tRoleDBID ):
		"""
		������޹�ϵ
		"""
		self.orgLog( LT_ORG_MARRY_SWEETIE, LT_ORG_MARRY_COUPLE_REMOVE, roleDBID, roleName, tRoleDBID )
	
	# ʦͽ
	def teachBuildLog( self, shifuDBID, shifuName, tudiDBID, tudiName ):
		"""
		����ʦͽ��ϵ
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_BUILD, shifuDBID, shifuName, tudiDBID, tudiName )
		
	def teachRemoveLog( self, shifuDBID, shifuName, tudiDBID, tudiName ):
		"""
		���ʦͽ��ϵ
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_REMOVE,  shifuDBID, shifuName, tudiDBID, tudiName )
		
	def teachCompleteLog( self, shifuDBID, shifuName, tudiDBID ):
		"""
		��ʦ
		"""
		self.orgLog( LT_ORG_TEACH, LT_ORG_TEACH_COMPLETE, shifuDBID, shifuName, tudiDBID )
	
	#���
	def allyListChangeLog( self, nameList, DBIDList ):
		"""
		����б�ı�
		"""
		self.orgLog( LT_ORG_ALLY, LT_ORG_ALLY_CHANGE, str( DBIDList ), str( nameList ) )
	
	#-----------------------------------
	# ���ܣ�������GM,�ʼ���)
	#-----------------------------------
	def funcLog( self, funcType, param1 = "", param2 = "", param3 = "", param4 = "", param5  = "", param6 = "", param7 = "", param8 = "", param9 = "" ):
		"""
		����
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_FUNC,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s", funcType, param1, param2, param3, param4, param5, param6, param7,param8,param9 )
	
	def gmCommonLog( self, command, args, srcEntityDBID, dstEntityDBID, srcEntityGrade, extend = None ):
		"""
		ʹ��GMָ��
		"""
		self.funcLog( LT_FUNC_GM, LT_FUNC_GM_COMMAND, command, args, srcEntityDBID, dstEntityDBID, srcEntityGrade, extend )
	
	# ���书��
	def mailSendLog( self, senderName, receiverName, title, itemNum, money ):
		"""
		�����ʼ�
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_SEND, senderName, receiverName, title, itemNum, money )

	def mailReadLog( self, senderName, receiverName, title, mailID ):
		"""
		�Ķ��ʼ�
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_READ, senderName, receiverName, title, mailID )
	
	def mailReturnLog( self, senderName, receiverName, title, mailID ):
		"""
		��������
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_RETURN, senderName, receiverName, title, mailID )
		
	def mailRemoveLog( self, senderName, receiverName, title, mailID ):
		"""
		ɾ���ʼ�
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_REMOVE, senderName, receiverName, title, mailID )
	
	def mailSysReturnLog( self, senderName, receiverName, title, mailID ):
		"""
		��������
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_SYS_RETURN, senderName, receiverName, title, mailID )
	
	def mailUpTimeLog( self, readedTime, readedHintTime, title, mailID ):
		"""
		�����ʼ�ʱ��
		readedHintTime:��ʾʱ��
		"""
		self.funcLog( LT_FUNC_MAIL, LT_FUNC_MAIL_UP_TIME, senderName, receiverName, title, mailID )
	
	#�˺�
	def accountLogonLog( self, account, ip, intro ):
		"""
		�˺ŵ�½
		intro���ַ�����
		"""
		self.funcLog( LT_FUNC_ACCOUNT, LT_FUNC_ACCOUNT_LOGON, account, ip, intro )
	
	def accountLogoutLog( self, account, ip, intro ):
		"""
		�˺�����
		intro���ַ�����
		"""
		self.funcLog( LT_FUNC_ACCOUNT, LT_FUNC_ACCOUNT_LOGOUT, account, ip, intro )
		
	# ��ɫ
	def roleLogonLog( self, roleDBID, roleName, account, onlineTime, ip, intro ):
		"""
		��ɫ����
		intro���ַ�����
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGON, roleDBID, roleName, account, onlineTime, ip, intro  )
	
	def roleLogoutLog( self, roleDBID, roleName, account, onlineTime, ip, intro ):
		"""
		��ɫ���ؽ�ɫѡ��
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGOUT, roleDBID, roleName, account, onlineTime, ip, intro )
	
	def roleLogoffLog( self, ip, accountName, nameAndID, onlineTime, intro ):
		"""
		��ɫ�����˺ŵ�½
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_LOGOFF, ip, accountName, nameAndID, onlineTime, intro )
	
	def roleUpgradeLog( self, roleDBID, roleName, oldLevel, nowLevel, lifeTime ):
		"""
		��ɫ����
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_UPGRADE, roleDBID, roleName, oldLevel, nowLevel, lifeTime )
	
	def roleTrainingsLog( self, roleDBID, roleName, type ):
		"""
		��ɫ�������
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_START_TRAININGS, roleDBID, roleName, type )
	
	def roleBeKillLog( self, killDBID, beKillDBID, killGrade ):
		"""
		��ɫ��ɱ����¼
		killDBID = 0ʱ,killer�ǹ���
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_BEKILL, killDBID, beKillDBID, killGrade )
	
	def roleOnLineLog( self, roleDBID, roleName, roleLevel, tongDBID, tongGrade ):
		"""
		��ɫ�������
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_ONLINE, roleDBID, roleName, roleLevel, tongDBID, tongGrade )
	
	def accountRoleAddLog( self, account, roleDBID, roleName ):
		"""
		������ɫ
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_ADD, account, roleDBID, roleName )
	
	def accountRoleDelLog( self, account, roleDBID, roleName ):
		"""
		ɾ���˺��ϵĽ�ɫ
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_DELETE, account, roleDBID, roleName )
		
	def sendRumorLog( self, roleDBID, roleName, msg ):
		"""
		��ɫ��ҥ��
		"""
		self.funcLog( LT_FUNC_ROLE, LT_FUNC_ROLE_SEND_RUMOR, roleDBID, roleName, "\"%s\""%msg )
		
	# ��̯
	def roleVendLog( self, roleDBID, roleName ):
		"""
		��Ұ�̯
		"""
		self.funcLog( LT_FUNC_VEND, LT_FUNC_VEND, roleDBID, roleName )
	
	# װ��
	def equipStilettoLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newSlot ):
		"""
		װ�����
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STILETTO, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newSlot )
			
	def equipIntensifyLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, newIntensifyLevel ):
		"""
		װ��ǿ��
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_INTENSIFY, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, newIntensifyLevel )
	
	def equipBindLog( self, roleDBID, roleName, itemUID, newItemUID, itemName ):
		"""
		װ������
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_BIND, roleDBID, roleName, itemUID, newItemUID, itemName )
	
	def equipReBuildLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemInfos, newItemInfos ):
		"""
		װ������
		itemInfos:[Ʒ��,ǰ׺]
		newItemInfos:[Ʒ��,ǰ׺]
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REBUILD, roleDBID, roleName, itemUID, newItemUID, itemName, itemInfos, newItemInfos )
	
	def equipSpecialComposeLog( self, roleDBID, roleName, newItemUID, itemName ):
		"""
		װ��������ϳ�
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_SPECIAL_COMPOSE, roleDBID, roleName, newItemUID, itemName )
	
	def equipImproveLog( self, roleDBID, roleName, itemUID, newItemUID, itemName ):
		"""
		��װ��Ʒ
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_IMPROVE_QUALITY, roleDBID, roleName, itemUID, newItemUID, itemName )
	
	def equipGodLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, skillID ):
		"""
		��������
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REFINE_GODWEAPON, roleDBID, roleName, itemUID, newItemUID, itemName, intensifyLevel, skillID )
	
	def equipStuffComposeLog( self, roleDBID, roleName, newItemUID, newItemName, newItemNum ):
		"""
		���Ϻϳ�
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STUFF_COMPOSE, roleDBID, roleName, newItemUID, newItemName, newItemAmount )
	
	def equipSplitLog( self, roleDBID, roleName, itemUID, itemName ):
		"""
		װ���ֲ�
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_SPLIT, roleDBID, roleName, itemUID, itemName )
	
	def equipStuddedLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newItemSlot, effectAttr ):
		"""
		װ����Ƕ
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_STUDDED, roleDBID, roleName, itemUID, newItemUID, itemName, itemSlot, newItemSlot, effectAttr )
	
	def equipChangePropertyLog( self, roleDBID, roleName, itemUID, newItemUID, itemName, prefix, newPrefix ):
		"""
		��װϴǰ׺
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_CHANGE_PROPERTY, roleDBID, roleName, itemUID, newItemUID, itemName, prefix, newPrefix )
	
	def equipMakeLog( self, roleDBID, roleName, itemUID, itemName, oldQuality, quality, oldPrefix, prefix ):
		"""
		װ������
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_MAKE, roleDBID, roleName, itemUID, itemName, oldQuality, quality, oldPrefix, prefix )
	
	def equipRepairNormalLog( self, roleDBID, roleName, itemUID, itemName, oldHardinessMax, newHardinessMax, repairMoney, spaceLabel,npcID ):
		"""
		װ����ͨ����
		"""
		self.funcLog( LT_FUNC_EQUIP, LT_FUNC_EQUIP_REPAIR_NORMAL, roleDBID, roleName, itemUID, itemName, oldHardinessMax, newHardinessMax, repairMoney, spaceLabel, npcID )
	
	# ˮ��
	def crystalRemoveLog( self, roleDBID, roleName, itemUID, itemName, itemLevel ):
		"""
		ˮ��ժ��
		"""
		self.funcLog( LT_FUNC_CRYSTAL, LT_FUNC_CRYSTAL_REMOVE, roleDBID, roleName, itemUID, itemName, itemLevel )
	
	# ����
	def talismanAddLifeLog( self, roleDBID, roleName, itemUID, itemName, itemLife ):
		"""
		������ֵ
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_ADD_LIFE, roleDBID, roleName, itemUID, itemName, itemLife )
	
	def talismanSplitLog( self, roleDBID, roleName, itemUID, itemName ):
		"""
		�����ֽ�
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_SPLIT, roleDBID, roleName, itemUID, itemName )
	
	def talismanIntensifyLog( self, roleDBID, roleName, itemUID, itemName, intensifyLevel):
		"""
		����ǿ��
		intensifyLevel:ǿ���ȼ�
		"""
		self.funcLog( LT_FUNC_TALISMAN, LT_FUNC_TALISMAN_INTENSIFY, roleDBID, roleName, itemUID, oldItemName, itemName, itemLevel, intensifyLevel )
	
	#����
	def petAddLog( self, roleDBID, roleName, petDBID, petName, reason ):
		"""
		��ó���
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_ADD, roleDBID, roleName, petDBID, petName, reason )
	
	def petDelLog( self, roleDBID, roleName, petDBID, petName, reason ):
		"""
		ʧȥ����
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_DEL, roleDBID, roleName, petDBID, petName, reason )

	def petBreedLog( self, aRoleDBID, aPetData, bRoleDBID, bPetData ):
		"""
		���ﷱֳ
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_BREED, aRoleDBID, aPetData, bRoleDBID, bPetData )
	
	def petStartTrainingsLog( self, roleDBID, roleName, petDBID, trainType ):
		"""
		���ﾭ�����
		"""
		self.funcLog( LT_FUNC_PET, LT_FUNC_PET_START_TRAININGS, roleDBID, roleName, petDBID, trainType )
	
	# ����
	def tradeNpcBuyLog( self, roleDBID, roleName, itemUID, itemName, amount, payMoney, grade, chapman, spaceLabel ):
		"""
		��NPC���˴�����
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_NPC_BUY, roleDBID, roleName, itemUID, itemName, amount, payMoney, grade, chapman, spaceLabel )
	
	def tradeNpcSellLog( self, roleDBID, roleName, itemUID, itemName, amount, getMoney, grade, chapman ):
		"""
		��������NPC����
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_NPC_SELL, roleDBID, roleName, itemUID, itemName, amount, getMoney, grade, chapman)
	
	def tradeRoleMoneyLog( self, roleDBID, roleName, tRoleDBID, tRolName, money, tradeID ):
		"""
		����ҽ��׽�Ǯ
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_MONEY, roleDBID, roleName, tRoleDBID, tRolName, money, tradeID)
	
	def tradeRoleItemLog( self, roleDBID, roleName, tRoleDBID, tRolName, itemUID, itemName, amount, tradeID ):
		"""
		����ҽ�����Ʒ
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_ITEM, roleDBID, roleName, tRoleDBID, tRolName, itemUID, itemName, amount, tradeID  )
	
	def tradeRolePetLog( self, roleDBID, roleName, tRoleDBID, tRolName, petDBID, tradeID ):
		"""
		����ҽ��׳���
		"""
		self.funcLog( LT_FUNC_TRADE, LT_FUNC_TRADE_SWAP_PET, roleDBID, roleName, tRoleDBID, tRolName, petDBID, tradeID)
	
	# �������
	def tiShouBuyPetLog( self, roleDBID, roleName, ownerDBID, ownerName, petDBID, price ):
		"""
		�������Ϲ������
		ownerDBID����������
		"""
		self.funcLog( LT_FUNC_TI_SHOU, LT_FUNC_TI_SHOU_BUY_PET, roleDBID, roleName, ownerDBID, ownerName, petDBID, price )
	
	def tiShouBuyItemLog( self, roleDBID, roleName, ownerDBID, ownerName, itemUID, itemName, itemAmount, price ):
		"""
		�������Ϲ�����Ʒ
		ownerDBID����������
		"""
		self.funcLog( LT_FUNC_TI_SHOU, LT_FUNC_TI_SHOU_BUY_ITEM, roleDBID, roleName, ownerDBID, ownerName, itemUID, itemName, itemAmount, price )
	
	#�ɼ�
	def collectLog( self, roleDBID, roleName, spaceLabel, collectPoint ):
		"""
		�ɼ�
		"""
		self.funcLog( LT_FUNC_COLLECT, LT_FUNC_COLLECT, roleDBID, roleName, spaceLabel, collectPoint)
	
	#�㿨
	def pointCardRechargeLog( self, cardNo, price, buyerName, buyerAccount, salesName ):
		"""
		�㿨��ֵ
		"""
		self.funcLog( LT_FUNC_PC, LT_FUNC_PC_RECHARGE, cardNo, price, buyerName, buyerAccount, salesName )
	
	#�����
	def apexKickRoleLog( self, roleDBID, roleName, hiByte, lowByte ):
		"""
		��������������
		hiByte:����ԭ��
		lowByte������������ ���� ������
		"""
		self.funcLog( LT_FUNC_AP, LT_FUNC_AP_KICK_ROLE, roleDBID, roleName, hiByte, lowByte )
	
	#����ֿ�
	def petStorageAddLog( self, roleDBID, roleName, petDBID, petName ):
		"""
		������ֿ�ų���
		"""
		self.funcLog( LT_FUNC_PET_STORAGE, LT_FUNC_PET_STORAGE_ADD, roleDBID, roleName, petDBID, petName )
	
	def petStorageTakeLog( self, roleDBID, roleName, petDBID, petName ):
		"""
		������ֿ�ȡ�߳���
		"""
		self.funcLog( LT_FUNC_PET_STORAGE, LT_FUNC_PET_STORAGE_TAKE, roleDBID, roleName, petDBID, petName )
	
	#�����̳�
	def specialShopBuyLog( self, account, gold, silver, itemID, amount ):
		"""
		�ӵ����̳�����Ʒ
		"""
		self.funcLog( LT_FUNC_SPECIAL_STOP, LT_FUNC_SPECIAL_STOP_BUY, account, gold, silver, itemID, amount )
	
	#�ֿ�
	def bankStoreLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		��������ֿ�
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_STORE, roleDBID, roleName, itemUID, itemName, ItemAmount )
		
	def bankTakeLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		�Ӳֿ�ȡ����
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_TAKE, roleDBID, roleName, itemUID, itemName, ItemAmount )
		
	def bankDestroyLog( self, roleDBID, roleName, itemUID, itemName, ItemAmount ):
		"""
		������Ʒ
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_DES, roleDBID, roleName, itemUID, itemName, ItemAmount )
	
	def bankExtendLog( self, roleDBID, roleName, extNum, extGridNum ):
		"""
		�ֿ��س�
		extNum���س����
		extGridNum���س���ٸ�����
		"""
		self.funcLog( LT_FUNC_BANK, LT_FUNC_BANK_EXTEND, roleDBID, roleName, itemUID, itemName, ItemAmount )
	
	#������ȡ
	def presentBackageLog( self, account, transactionID, packageID, expiredTime ):
		"""
		��Ʒ��
		account���˺�, transactionID��������, packageID�����ID,expiredTime������ʱ��
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_PACKAGE, account, transactionID, packageID, expiredTime )
		
	def presentSilverLog( self, account, transactionID, silver ):
		"""
		����Ԫ��
		account���˺�, transactionID��������, packageID�����ID,expiredTime������ʱ��
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_SILVER, account, transactionID, silver )
	
	def presentChargeLog( self, account, transactionID , ChargeType, GoldCoins, SilverCoins ):
		"""
		��ֵ
		ChargeType����ֵ����
		GoldCoins����Ԫ��
		SilverCoins����Ԫ��
		"""
		self.funcLog( LT_FUNC_PRESENT, LT_FUNC_PRESENT_CHARGE, account, transactionID , ChargeType, GoldCoins, SilverCoins )
	
	#-----------------------------------
	# ͳ��
	#-----------------------------------
	def countLog( self, countType, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "", param7 = ""  ):
		"""
		ͳ��
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_COUNT,"||%s||%s||%s||%s||%s||%s||%s||%s",countType, param1, param2, param3, param4, param5, param6, param7 )
	
	def countWealthLog( self, roleDBID, roleName, roleMoney, countTime ):
		"""
		��ҲƸ�ͳ��
		"""
		self.countLog( LT_COUNT_ROLE_WEALTH, roleDBID, roleName, roleMoney, countTime )
	
	def countLevelLog( self, level, rcmaskClass, countTime ):
		"""
		��ɫ�ȼ�&ְҵͳ��
		"""
		self.countLog( LT_COUNT_ROLE_LEVEL, level, rcmaskClass, countTime )
		
	def countRoleLog( self, waitAccountNum, loginAccountNum, summation ):
		"""
		ͳ����ҵ���������
		waitAccountNum:�ȴ������е��������, 
		loginAccountNum:��½�����е��������, 
		summation:������ҵ�����
		"""
		self.countLog( LT_COUNT_ROLE_COUNT, waitAccountNum, loginAccountNum, summation )
		
	def countTongInfoLog( self, tongName, tongLevel, tongMoney, tongMembers, averageLevel, maxLevel, minLevel ):
		"""
		�����Ϣͳ��
		"""
		self.countLog( LT_COUNT_TONG_INFO, tongName, tongLevel, tongMoney, tongMembers, averageLevel, maxLevel, minLevel )
	
	def countTongNumLog( self, count ):
		"""
		�������ͳ��
		"""
		self.countLog( LT_COUNT_TONG_COUNT, count )
	
	def countOnlineAccountLog( self, accountNum,param1, param2, param3, param4, param5 ):
		"""
		�����˺�
		"""
		self.countLog( LT_COUNT_ONLINE_ACCOUNT, accountNum, param1, param2, param3, param4, param5 )
		
	#-----------------------------------
	# ����
	#-----------------------------------
	def proLog( self, type, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
		"""
		��ӽ�ɫ��־
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_PRO,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",type, roleDBID, roleName, param1, param2, param3, param4, param5, param6 )
	
	def expChangeLog( self, roleDBID, roleName, oldExp, oldLevel, nowExp, nowLevel, reason ):
		"""
		��ɫ����ı�
		"""
		self.proLog( LT_PRO_EXP_CHANGE, roleDBID, roleName, oldExp, oldLevel, nowExp, nowLevel, reason )
	
	def potentialChangeLog( self, roleDBID, roleName, oldPotential, nowPotential, reason ):
		"""
		Ǳ�ܸı�
		"""
		self.proLog( LT_PRO_POTENTIAL_CHANGE, roleDBID, roleName, oldPotential, nowPotential, reason )
			
	# ����
	def daohengAddLog( self, roleDBID, roleName, curDaoheng, value, reason = 0 ):
		"""
		��������
		"""
		self.proLog( LT_PRO_DAOHENG_ADD, roleDBID, roleName, curDaoheng, value, reason)
	
	def daohengSetLog( self, roleDBID, roleName, value ):
		"""
		GM���õ��е�ֵ
		"""
		self.proLog( LT_PRO_DAOHENG_SET, roleDBID, roleName, value )
	
	# ����
	def scoreHonorAddLog( self, roleDBID, roleName, score, reason ):
		"""
		������������
		"""
		self.proLog( LT_PRO_SCORE_HONOR_ADD, roleDBID, roleName, score, reason)
	
	def scoreHonorSubLog( self, roleDBID, roleName, score, reason ):
		"""
		������������
		"""
		self.proLog( LT_PRO_SCORE_HONOR_SUB, roleDBID, roleName, score, reason)
	
	def scorePersonalAddLog( self, roleDBID, roleName, score, reason ):
		"""
		���Ӹ��˾�������
		"""
		self.proLog( LT_PRO_SCORE_PERSONAL_ADD, roleDBID, roleName, score, reason)
	
	def scorePersonalSubLog( self, roleDBID, roleName, score, reason ):
		"""
		���ٸ��˾�������
		"""
		self.proLog( LT_PRO_SCORE_PERSONAL_SUB, roleDBID, roleName, score, reason)
	
	def scoreTongAddLog( self, roleDBID, roleName, score, reason ):
		"""
		���Ӱ�Ὰ������
		"""
		self.proLog( LT_PRO_SCORE_TONG_SCORE_ADD, roleDBID, roleName, score, reason)
	
	def scoreTongSubLog( self, roleDBID, roleName, score, reason ):
		"""
		���ٰ�Ὰ������
		"""
		self.proLog( LT_PRO_SCORE_TONG_SCORE_SUB, roleDBID, roleName, score, reason)
	
	def scoreTeamCompetitionAddLog( self, roleDBID, roleName, score, reason ):
		"""
		������Ӿ�������
		"""
		self.proLog( LT_FUNC_TEAM_COMPETITION_ADD, roleDBID, roleName, score, reason)
	
	def scoreTeamCompetitionSubLog( self, roleDBID, roleName, score, reason ):
		"""
		������Ӿ�������
		"""
		self.proLog( LT_FUNC_TEAM_COMPETITION_SUB, roleDBID, roleName, score, reason)
		
	
	#-----------------------------------
	# ��Ʒ
	#-----------------------------------
	def itemLog( self, action, roleDBID, roleName, grade, reason, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "", param6 = "" ):
		"""
		��Ʒ��־
		action:��Ʒ�Ĳ���,���,����ʧȥ
		reason:ԭ��
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_ITEM,"||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, grade, reason, param1, param2, param3, param4,param5, param6 )
	
	def itemAddLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum, playerLevel ):
		"""
		�����Ʒ��־
		"""
		self.itemLog( LT_ITEM_ADD, roleDBID, roleName, grade, reason, uid, itemName, itemNum, playerLevel )
	
	def itemDelLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum ):
		"""
		ɾ����Ʒ��־
		"""
		self.itemLog( LT_ITEM_DEL, roleDBID, roleName, grade, reason, uid, itemName, itemNum )
	
	def itemSetAmountLog( self, roleDBID, roleName, grade, reason, uid, itemName, itemNum, setNum ):
		"""
		������Ʒ����
		itemNum:ԭ��Ʒ����
		setNum:������Ʒ����
		"""
		self.itemLog( LT_ITEM_SET_AMOUNT, roleDBID, roleName, grade, reason, uid, itemName, itemNum, setNum )
	
	#-----------------------------------
	# ��Ǯ
	#-----------------------------------
	def moneyLog( self, action, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5  = "" ):
		"""
		��ӽ�Ǯ��־
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_MONEY,"||%s||%s||%s||%s||%s||%s||%s||%s",action, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def moneyChangeLog( self, roleDBID, roleName, oldMoney, nowMoney, reason, grade ):
		"""
		��ҽ�Ǯ�ı�
		"""
		self.moneyLog( LT_MONEY_CHANGE, roleDBID, roleName, oldMoney, nowMoney, reason, grade )
		
	#-----------------------------------
	# ��Ԫ��
	#-----------------------------------
	def silverLog( self, action, account, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		��Ԫ����־
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_SILVER,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, account, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def silverChangeLog( self, account, roleDBID, roleName, velue, silver, reason ):
		"""
		�����Ԫ��
		silver:��ǰ��Ԫ��
		"""
		self.silverLog( LT_SILVER_CHANGE, account, roleDBID, roleName, velue, silver, reason )
	
	#-----------------------------------
	# ��Ԫ��
	#-----------------------------------
	def goldLog( self, action, account, roleDBID, roleName, param1 = "", param2 = "", param3 = "", param4 = "", param5 = "" ):
		"""
		��Ԫ����־
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_GOLD,"||%s||%s||%s||%s||%s||%s||%s||%s||%s",action, account, roleDBID, roleName, param1, param2, param3, param4, param5 )
	
	def goldChangeLog( self, account, roleDBID, roleName, value, gold, reason ):
		"""
		��ӽ�Ԫ��
		gold����ǰ��Ԫ��
		"""
		self.goldLog( LT_GOLD_CHANGE, account, roleDBID, roleName, value, gold, reason )
	
	#-----------------------------------
	# �쳣
	#-----------------------------------
	def excepLog( self, type, message = "" ):
		"""
		�쳣��Ϣ:  ����Ϸ�����Ҫ������Ϣд�����ݿ⡣
		"""
		bwdebug.DATABASE_LOG_MSG( LOG_TYPE_EXCEPT,"||%s||%s", type, message )
	
	def logExceptLog( self, message = "" ):
		"""
		�����־����
		"""
		self.excepLog( LT_EXCEPT_LOG, message )
	
	def lotteryExceptLog( self, message = "" ):
		"""
		���Ҵ���
		"""
		self.excepLog( LT_EXCEPT_LOTTERY, message )
	
	def itemDropExceptLog( self, message = "" ):
		"""
		��Ʒ�������ô���
		"""
		self.excepLog( LT_EXCEPT_ITEM_DROP, message )
	
	def itemDropExceptLog( self, message = "" ):
		"""
		��Ʒ�������ô���
		"""
		self.excepLog( LT_EXCEPT_ITEM_DROP, message )
		
	def chargePresentExceptLog( self, message ):
		self.excepLog( LT_EXCEPT_CHARGE_PRESENT, message )
	
g_logger = MsgLogger.instance()
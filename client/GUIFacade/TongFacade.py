# -*- coding: gb18030 -*-
#
# $Id: TongFacade.py,v 1.9 2008-08-19 01:47:55 kebiao Exp $
"""
���ѵġ�Facade
"""
from bwdebug import *
from event.EventCenter import *
import BigWorld
import time
import csstatus
import csdefine
import csconst
import Const
from guis import *
from config.client.msgboxtexts import Datas as mbmsgs
from guis.general.tongabout.TongMoney import TongMoneyGUI
from guis.general.tongabout.SararyDrawing import SararyDrawing
from guis.tooluis.richtext_plugins.PL_Link import PL_Link

class TongFacade:
	@staticmethod
	def reset():
		TongFacade.tong_memberInfos = {}
		TongFacade.tongTrainer = None			# entity of trainer
		TongFacade.tongChapman = None			# entity of trainer

def tong_getMemberInfos():
	return TongFacade.tong_memberInfos

def tong_hasSetMemberInfo():
	return len( TongFacade.tong_memberInfos ) > 0

def tong_setMemberInfo( info ):
	"""
	���ó�Ա�������Ϣ
	"""
	TongFacade.tong_memberInfos = info

def tong_onSetMemberInfo( familyDBID, familyGrade, memberDBID ):
	"""
	define method.
	���ó�Ա�������Ϣ
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_MEMBERINFO", familyDBID, familyGrade, memberDBID )

def tong_onMemberGradeChanged( memberDBID, memberGrade ):
	"""
	define method.
	ĳ��Ա��Ȩ�޸ı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_GRADE", memberDBID, memberGrade )


def tong_onMemberScholiumChanged( memberDBID, scholium ):
	"""
	ĳ��Ա����ע�ı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_SCHOLIUM", memberDBID, scholium )

def tong_onMemberContributeChanged( memberDBID, contribute, totalContribute ):
	"""
	ĳ��Ա��ṱ�׶ȸı�
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_CONTRIBUTE", memberDBID, contribute )
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_TCONTRIBUTE", memberDBID, totalContribute )

def tong_onDutyGradeChanged( gradeKey, dutys ):
	"""
	�յ����ְ��Ȩ�޵ĸı�֪ͨ
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_DUTYGRADE",gradeKey, dutys )

def tong_initDutyName( duty, dutyName ):
	"""
	��ʼ��ְλ
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_INIT_DUTY_NAME", duty, dutyName )

def tong_onMemberOnlineStateChanged( memberDBID, onlineState ):
	"""
	define method.
	ĳ��Ա������״̬�ı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_ONLINE_STATE", memberDBID, onlineState )

def tong_onMemberLevelChanged( memberDBID, level ):
	"""
	define method.
	ĳ��Ա�ļ���ı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_LEVEL", memberDBID, level )

def tong_onMemberNameChanged( memberDBID, name ):
	"""
	define method.
	ĳ��Ա�����ָı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_NAME", memberDBID, name )

def tong_updateMemberMapInfo( memberDBID, spaceType, position, lineNumber ):
	"""
	��ҵ����ı�
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_AREA", memberDBID, spaceType, position, lineNumber )

def tong_onDutyNameChanged( duty, newName ):
	"""
	ĳ��ְ������Ƹı�
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_DUTY_NAME", duty, newName )


def tong_onRemoveMember( memberDBID ):
	"""
	ɾ��ĳ��Ա
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_REMOVE_MEMBER", memberDBID )

def onSetTongDismissRemainTime( dismissTime ):
	"""
	��ʾ����ɢ����ʱ
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_DISSMISS_REMAINTIME", dismissTime )

def tong_reset():
	fireEvent( "EVT_ON_TOGGLE_TONG_CLEAR_ALL" )
	
def tong_onInitFund( lastWeekInfo, thisWeekInfo ):
	"""
	����ʽ�
	"""
	fireEvent( "EVT_ON_TOGGLE_INIT_TONG_FUND", lastWeekInfo, thisWeekInfo )
	
def tong_onUpdateNextWeekChangeRate( rate ):
	"""
	���ܶһ���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_NEXTWEEKRATE", rate )
	
def tong_receiveSalaryInfo( sararyInfo ):
	"""
	��ȡٺ»
	"""
	SararyDrawing.instance().instanceShow( sararyInfo )
	
#---------------------------------------------------------------------------------------------------------

def tong_onReceiveRequestJoin( requestEntityName, tongDBID, tongName, chiefName,tongLevel,memberCount ):
	"""
	define method.
	�յ��������tong
	@param requestEntityName: ����������
	@oaram familyDBID		: �����dbid, ����������ʱ����Ҫ�õ�
	"""
	arr = ["EVT_ON_SHOW_TONGDETAILS",tongName,chiefName,tongLevel,memberCount]
	mark = "log:" + str( arr )
	tongName = PL_Link.getSource( tongName, mark , cfc = "c4", hfc = "c3", ul = 1 )
	def query( rs_id ):
		BigWorld.player().tong_answerRequestJoin( rs_id == RS_OK, tongDBID )
		if rs_id == RS_CANCEL:
			BigWorld.player().statusMessage( csstatus.TONG_JOIN_REFUSE_INVITOR, requestEntityName )
	# "��xxx���������������᡾yyy��һͬ����ٵأ�������ħ�����Ƿ�Ը�⣿"
	showMessage( mbmsgs[0x01c1] % ( requestEntityName, tongName ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )
	
def tong_onReceiveRequestJoinMessage( requestEntityName, tongName, chiefName, tongLevel, memberCount ):
	"""
	��ʽ�ַ����� ����ҷ��������������Ϣ
	"""
	arr = ["EVT_ON_SHOW_TONGDETAILS",tongName,chiefName,tongLevel,memberCount]
	mark = "log:" + str( arr )
	tongName = PL_Link.getSource( tongName, mark , cfc = "c4", hfc = "c3", ul = 1 )
	tongName = "��" + tongName + "��"
	BigWorld.player().statusMessage( csstatus.TONG_REQUEST_JOIN, requestEntityName, tongName )

#---------------------------------------------------------------------------------------------------------

def tong_onSetTongName( role, oldName, tongName ):
	"""
	define method.
	���������ÿͻ��˰������
	@param tongName: �������
	@type  tongName: string
	"""
	fireEvent( "EVT_ON_ROLE_CORPS_NAME_CHANGED", role, oldName, tongName )

def tong_onSetTongGrade( role, oldName, tongGrade ):
	"""
	define method.
	���������ÿͻ��˰��ְ��
	@param tongGrade: ���ְ��
	@type  tongGrade: string
	"""
	fireEvent( "EVT_ON_ROLE_CORPS_GRADE_CHANGED", role, oldName, tongGrade )

def tong_onSetAffiche( affiche ):
	"""
	define method.
	�յ����������ÿͻ���tong����
	@param affiche: ����
	@type  affiche: string
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_AFFICHE", affiche )

def tong_onSetTongPrestige( prestige ):
	"""
	define method.
	���������ÿͻ��˼�������
	@param prestige: ��������
	@type  prestige: int32
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_SET_PRESTIGE", prestige )
	#BigWorld.player().chat_say( "������� :%i" % prestige )

def tong_onSetTongLevel( level ):
	fireEvent( "EVT_ON_TOGGLE_TONG_LEVEL_CHANGE", level )

def tong_onSetTongMoney( money ):
	fireEvent( "EVT_ON_TOGGLE_TONG_MONEY_CHANGE", money )

def onGetBuildingSpendMoney( spendingMoney ):
	#fireEvent( "EVT_OPEN_TONG_MONEY_WINDOW", spendingMoney )
	TongMoneyGUI.instance().instanceShow(spendingMoney)

def tong_onRequestTongLeague( requestByTongName, requestByTongDBID ):
	def query( rs_id ):
		BigWorld.player().tong_answerRequestTongLeague( rs_id == RS_OK, requestByTongDBID )
	# "%s���������İ���Ϊͬ��, �Ƿ����?"
	showMessage( mbmsgs[0x01c2] % ( requestByTongName ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def tong_receiveBattleLeagueInvitation(  inviterTongName, inviterTongDBID, msg ):
	def query( rs_id ):
		BigWorld.player().tong_replyBattleLeagueInvitation( inviterTongDBID , rs_id == RS_OK )
	# "%s����������Ϊ�����ս�е�ս�����ѣ�һ�𲢼�ս���ɾʹ�ҵ��%s"
	showAutoHideMessage( 60, mbmsgs[0x01c4] % ( inviterTongName, msg ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def tong_onChiefConjure():
	"""
	define method.
	�յ��ӳ������� ���ȷ����ʹ��tong_onAnswerConjure��Ӧ��û��ȷ�������κ�����
	"""
	def query( rs_id ):
		if rs_id == RS_OK:
			BigWorld.player().cell.tong_onAnswerConjure()
	# "����ʹ���˼�����.��Ը����������?"
	showMessage( 0x01c3, "", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def onSetHoldCity( role, city ):
	fireEvent( "EVT_OPEN_TONG_SET_HOLD_CITY", role, city )

#-----------------------------------------------�����о�ѧϰ��---------------------------------------------

def tong_showSkillResearchWindow( tongTrainer, buildingLevel, currentResearchVal, currentResearchSkill, skills ):
	"""
	�򿪼����о�����
	@param currentResearchVal: ��ǰ�о���
	"""
	if BigWorld.player().tong_grade&( csdefine.TONG_GRADES &~ csdefine.TONG_GRADE_CREATE_SKILL ) < 0:return
	TongFacade.tongTrainer = tongTrainer
	fireEvent( "EVT_ON_TOGGLE_TONG_SKILLS_RESEARCH", buildingLevel, skills )
#		BigWorld.player().chat_say( "�о�Ժ�ȼ�:%i, ���з��ļ���: %i, �ȼ�: %i" % ( buildingLevel, item["id"], item["level"] ) )
	if currentResearchSkill:
		fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_RESEARCH_SKILL", currentResearchSkill, currentResearchVal )
#		BigWorld.player().chat_say( "�����з�%i ����%i---��ǰ�Ѿ��з�:%i" % ( currentResearchSkill["id"], currentResearchSkill["level"], currentResearchVal ) )

def tong_researchSkill( skillID ):
	"""
	�����з��ü���
	"""
	TongFacade.tongTrainer.researchSkill( skillID )

def tong_onChangeResearchSkill( currentResearchSkill ):
	"""
	��ǰ�����з��ļ��ܸı���
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_SKILL_CHANGE", currentResearchSkill )
#	BigWorld.player().chat_say( "�����з�%i ����%i" % ( currentResearchSkill["id"], currentResearchSkill["level"] ) )

def tong_onShowTongSkillClearWindow( clearSkillIDs ):
	"""
	�յ������������ļ���������
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CLEAR_SKILLS", clearSkillIDs )
#	BigWorld.player().chat_say( "�������ļ���:%s" % clearSkillIDs )

def tong_clearTongSkill( skillID ):
	"""
	ѡ��������ĳ����
	"""
	TongFacade.tongTrainer.clearTongSkill( skillID )

def tong_onSetTongActionVal( actionVal ):
	"""
	����ж����ı�
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_ACTIONVAL_CHANGE", actionVal )

#-----------------------------------------------�����Ʒ�о������---------------------------------------------

def tong_onShowTongMakeItemWindow( tongChapman, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs ):
	"""
	�յ�BASE�����İ���������Ʒ�б�
	@param buildingLevel		:�����ļ��� �̵�
	@param currentMakeHouqinVal	:��ǰ�о���Ʒ���о��ĺ��ڶ�
	@param currentMakeItem		:��ǰ������������Ʒ
	@param canMakeItemIDs		:����������Ʒ�б�
	"""
	TongFacade.tongChapman = tongChapman
	fireEvent( "EVT_ON_TOGGLE_TONG_ITEMS_RESEARCH", buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs )
#	BigWorld.player().chat_say( "�̵꼶��:%i" % buildingLevel )
#	BigWorld.player().chat_say( "��ǰ�����о���Ʒ���ڶ�:%i" % currHouqinVal )
#	BigWorld.player().chat_say( "��ǰ�����о���Ʒ%i:%i" % ( currMakeItemData["itemID"],currMakeItemData["amount"]) )
#	BigWorld.player().chat_say( "��������Ʒ�б�:%s" % canMakeItemIDs )

def tong_makeItems( makeItemID ):
	"""
	��������������������Ʒ
	@param makeItemID	:��ƷID
	"""
	TongFacade.tongChapman.makeItems( makeItemID )

def tong_onChangeMakeItem( makeItemID, makeAmount ):
	"""
	��ǰ�з���Ʒ���ı�
	@param makeItemID	:��ƷID
	@param makeAmount	:Ҫ����������
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_ITEM_CHANGE", makeItemID, makeAmount )
#	BigWorld.player().chat_say( "��ǰ�����о���Ʒ�ı�Ϊ%i:%i" % ( makeItemID, makeAmount ) )

def tong_updatePlayerWarReport( playerID, playerName, playerTongDBID, killCount, dieCount ): #�������ᱨ��
	fireEvent( "EVT_ON_TOGGLE_TONGWAR_REPORT_CHANGE", playerID, playerName, playerTongDBID, killCount, dieCount )
	
def tong_onLeaveWarSpace():
	fireEvent( "EVT_ON_TOGGLE_TONG_LEAVE_WAR" )
	fireEvent( "EVT_ON_TOGGLE_FAMILY_LEAVE_WAR" )

def tong_onInitRemainWarTime( warOvertime ):
	fireEvent( "EVT_ON_ROLE_ENTER_NPC_CHALLENGE", warOvertime )

def tong_onWarMarkChanged( enemyTongName, enemyTongMark, selfTongMark ):
	fireEvent( "EVT_ON_TOGGLE_TONGWAR_MARK_CHANGE", enemyTongName, enemyTongMark, selfTongMark )

def tong_onAbaMarkChanged( enemyTongName, enemyTongMark, selfTongMark, isSelfMark ):
	fireEvent( "EVT_ON_TOGGLE_TONGABA_MARK_CHANGE", enemyTongName, enemyTongMark, selfTongMark, isSelfMark )

def tong_onTongAbaDie( ):
	fireEvent( "EVT_ON_TOGGLE_TONG_ABA_RELIVE_BOX" ) #����ڰ����̨�������������ѡ�����
#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/08/12 08:51:26  kebiao
# ��Ӱ����������
#
# Revision 1.7  2008/07/01 01:59:34  fangpengjun
# ����tong_updateMemberMapInfo����
#
# Revision 1.6  2008/06/30 10:24:11  fangpengjun
# �޸Ĳ�����Ϣ
#
# Revision 1.5  2008/06/29 08:53:56  fangpengjun
# ����˽�����Ҫ����Ϣ
#
# Revision 1.4  2008/06/21 03:41:46  kebiao
# �����ṱ�׶�
#
# Revision 1.3  2008/06/16 09:15:26  kebiao
# base �ϲ��ֱ�¶�ӿ�ת�Ƶ�cell �ı���÷�ʽ
#
# Revision 1.2  2008/06/14 09:15:37  kebiao
# ������Ṧ��
#
# Revision 1.1  2008/06/09 09:24:00  kebiao
# ���������
#
#
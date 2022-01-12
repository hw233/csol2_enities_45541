# -*- coding: gb18030 -*-
#
# $Id: TongFacade.py,v 1.9 2008-08-19 01:47:55 kebiao Exp $
"""
好友的　Facade
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
	设置成员的相关信息
	"""
	TongFacade.tong_memberInfos = info

def tong_onSetMemberInfo( familyDBID, familyGrade, memberDBID ):
	"""
	define method.
	设置成员的相关信息
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_MEMBERINFO", familyDBID, familyGrade, memberDBID )

def tong_onMemberGradeChanged( memberDBID, memberGrade ):
	"""
	define method.
	某成员的权限改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_GRADE", memberDBID, memberGrade )


def tong_onMemberScholiumChanged( memberDBID, scholium ):
	"""
	某成员的批注改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_SCHOLIUM", memberDBID, scholium )

def tong_onMemberContributeChanged( memberDBID, contribute, totalContribute ):
	"""
	某成员帮会贡献度改变
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_CONTRIBUTE", memberDBID, contribute )
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_TCONTRIBUTE", memberDBID, totalContribute )

def tong_onDutyGradeChanged( gradeKey, dutys ):
	"""
	收到帮会职务权限的改变通知
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_DUTYGRADE",gradeKey, dutys )

def tong_initDutyName( duty, dutyName ):
	"""
	初始化职位
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_INIT_DUTY_NAME", duty, dutyName )

def tong_onMemberOnlineStateChanged( memberDBID, onlineState ):
	"""
	define method.
	某成员的在线状态改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_ONLINE_STATE", memberDBID, onlineState )

def tong_onMemberLevelChanged( memberDBID, level ):
	"""
	define method.
	某成员的级别改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_LEVEL", memberDBID, level )

def tong_onMemberNameChanged( memberDBID, name ):
	"""
	define method.
	某成员的名字改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_NAME", memberDBID, name )

def tong_updateMemberMapInfo( memberDBID, spaceType, position, lineNumber ):
	"""
	玩家地区改变
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_AREA", memberDBID, spaceType, position, lineNumber )

def tong_onDutyNameChanged( duty, newName ):
	"""
	某个职务的名称改变
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_DUTY_NAME", duty, newName )


def tong_onRemoveMember( memberDBID ):
	"""
	删除某成员
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_REMOVE_MEMBER", memberDBID )

def onSetTongDismissRemainTime( dismissTime ):
	"""
	显示帮会解散倒计时
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_DISSMISS_REMAINTIME", dismissTime )

def tong_reset():
	fireEvent( "EVT_ON_TOGGLE_TONG_CLEAR_ALL" )
	
def tong_onInitFund( lastWeekInfo, thisWeekInfo ):
	"""
	帮会资金
	"""
	fireEvent( "EVT_ON_TOGGLE_INIT_TONG_FUND", lastWeekInfo, thisWeekInfo )
	
def tong_onUpdateNextWeekChangeRate( rate ):
	"""
	下周兑换额
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_NEXTWEEKRATE", rate )
	
def tong_receiveSalaryInfo( sararyInfo ):
	"""
	领取俸禄
	"""
	SararyDrawing.instance().instanceShow( sararyInfo )
	
#---------------------------------------------------------------------------------------------------------

def tong_onReceiveRequestJoin( requestEntityName, tongDBID, tongName, chiefName,tongLevel,memberCount ):
	"""
	define method.
	收到邀请加入tong
	@param requestEntityName: 邀请者名称
	@oaram familyDBID		: 家族的dbid, 后面答复邀请的时候需要用到
	"""
	arr = ["EVT_ON_SHOW_TONGDETAILS",tongName,chiefName,tongLevel,memberCount]
	mark = "log:" + str( arr )
	tongName = PL_Link.getSource( tongName, mark , cfc = "c4", hfc = "c3", ul = 1 )
	def query( rs_id ):
		BigWorld.player().tong_answerRequestJoin( rs_id == RS_OK, tongDBID )
		if rs_id == RS_CANCEL:
			BigWorld.player().statusMessage( csstatus.TONG_JOIN_REFUSE_INVITOR, requestEntityName )
	# "【xxx】邀请您加入其帮会【yyy】一同开天辟地，降妖除魔。您是否愿意？"
	showMessage( mbmsgs[0x01c1] % ( requestEntityName, tongName ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )
	
def tong_onReceiveRequestJoinMessage( requestEntityName, tongName, chiefName, tongLevel, memberCount ):
	"""
	格式字符串后 给玩家发送邀请加入帮会信息
	"""
	arr = ["EVT_ON_SHOW_TONGDETAILS",tongName,chiefName,tongLevel,memberCount]
	mark = "log:" + str( arr )
	tongName = PL_Link.getSource( tongName, mark , cfc = "c4", hfc = "c3", ul = 1 )
	tongName = "【" + tongName + "】"
	BigWorld.player().statusMessage( csstatus.TONG_REQUEST_JOIN, requestEntityName, tongName )

#---------------------------------------------------------------------------------------------------------

def tong_onSetTongName( role, oldName, tongName ):
	"""
	define method.
	服务器设置客户端帮会名称
	@param tongName: 帮会名称
	@type  tongName: string
	"""
	fireEvent( "EVT_ON_ROLE_CORPS_NAME_CHANGED", role, oldName, tongName )

def tong_onSetTongGrade( role, oldName, tongGrade ):
	"""
	define method.
	服务器设置客户端帮会职务
	@param tongGrade: 帮会职务
	@type  tongGrade: string
	"""
	fireEvent( "EVT_ON_ROLE_CORPS_GRADE_CHANGED", role, oldName, tongGrade )

def tong_onSetAffiche( affiche ):
	"""
	define method.
	收到服务器设置客户端tong公告
	@param affiche: 公告
	@type  affiche: string
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_UPDATE_AFFICHE", affiche )

def tong_onSetTongPrestige( prestige ):
	"""
	define method.
	服务器设置客户端家族声望
	@param prestige: 家族声望
	@type  prestige: int32
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_SET_PRESTIGE", prestige )
	#BigWorld.player().chat_say( "帮会声望 :%i" % prestige )

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
	# "%s帮会邀请你的帮会结为同盟, 是否接受?"
	showMessage( mbmsgs[0x01c2] % ( requestByTongName ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def tong_receiveBattleLeagueInvitation(  inviterTongName, inviterTongDBID, msg ):
	def query( rs_id ):
		BigWorld.player().tong_replyBattleLeagueInvitation( inviterTongDBID , rs_id == RS_OK )
	# "%s帮会邀请贵帮成为帮会夺城战中的战斗盟友，一起并肩战斗成就大业！%s"
	showAutoHideMessage( 60, mbmsgs[0x01c4] % ( inviterTongName, msg ) ,"", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def tong_onChiefConjure():
	"""
	define method.
	收到队长集结令 点击确定后使用tong_onAnswerConjure回应，没点确定不做任何事情
	"""
	def query( rs_id ):
		if rs_id == RS_OK:
			BigWorld.player().cell.tong_onAnswerConjure()
	# "帮主使用了集结令.你愿意跟随帮主吗?"
	showMessage( 0x01c3, "", MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )

def onSetHoldCity( role, city ):
	fireEvent( "EVT_OPEN_TONG_SET_HOLD_CITY", role, city )

#-----------------------------------------------技能研究学习等---------------------------------------------

def tong_showSkillResearchWindow( tongTrainer, buildingLevel, currentResearchVal, currentResearchSkill, skills ):
	"""
	打开技能研究窗口
	@param currentResearchVal: 当前研究度
	"""
	if BigWorld.player().tong_grade&( csdefine.TONG_GRADES &~ csdefine.TONG_GRADE_CREATE_SKILL ) < 0:return
	TongFacade.tongTrainer = tongTrainer
	fireEvent( "EVT_ON_TOGGLE_TONG_SKILLS_RESEARCH", buildingLevel, skills )
#		BigWorld.player().chat_say( "研究院等级:%i, 可研发的技能: %i, 等级: %i" % ( buildingLevel, item["id"], item["level"] ) )
	if currentResearchSkill:
		fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_RESEARCH_SKILL", currentResearchSkill, currentResearchVal )
#		BigWorld.player().chat_say( "正在研发%i 级别%i---当前已经研发:%i" % ( currentResearchSkill["id"], currentResearchSkill["level"], currentResearchVal ) )

def tong_researchSkill( skillID ):
	"""
	决定研发该技能
	"""
	TongFacade.tongTrainer.researchSkill( skillID )

def tong_onChangeResearchSkill( currentResearchSkill ):
	"""
	当前正在研发的技能改变了
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_SKILL_CHANGE", currentResearchSkill )
#	BigWorld.player().chat_say( "正在研发%i 级别%i" % ( currentResearchSkill["id"], currentResearchSkill["level"] ) )

def tong_onShowTongSkillClearWindow( clearSkillIDs ):
	"""
	收到服务器传来的技能遗忘表
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CLEAR_SKILLS", clearSkillIDs )
#	BigWorld.player().chat_say( "可遗忘的技能:%s" % clearSkillIDs )

def tong_clearTongSkill( skillID ):
	"""
	选择了遗忘某技能
	"""
	TongFacade.tongTrainer.clearTongSkill( skillID )

def tong_onSetTongActionVal( actionVal ):
	"""
	帮会行动力改变
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_ACTIONVAL_CHANGE", actionVal )

#-----------------------------------------------帮会物品研究购买等---------------------------------------------

def tong_onShowTongMakeItemWindow( tongChapman, buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs ):
	"""
	收到BASE传来的帮会可生产物品列表
	@param buildingLevel		:建筑的级别 商店
	@param currentMakeHouqinVal	:当前研究物品所研究的后勤度
	@param currentMakeItem		:当前正在生产的物品
	@param canMakeItemIDs		:可生产的物品列表
	"""
	TongFacade.tongChapman = tongChapman
	fireEvent( "EVT_ON_TOGGLE_TONG_ITEMS_RESEARCH", buildingLevel, currHouqinVal, currMakeItemData, canMakeItemIDs )
#	BigWorld.player().chat_say( "商店级别:%i" % buildingLevel )
#	BigWorld.player().chat_say( "当前正在研究物品后勤度:%i" % currHouqinVal )
#	BigWorld.player().chat_say( "当前正在研究物品%i:%i" % ( currMakeItemData["itemID"],currMakeItemData["amount"]) )
#	BigWorld.player().chat_say( "可生产物品列表:%s" % canMakeItemIDs )

def tong_makeItems( makeItemID ):
	"""
	向服务器请求生产这个物品
	@param makeItemID	:物品ID
	"""
	TongFacade.tongChapman.makeItems( makeItemID )

def tong_onChangeMakeItem( makeItemID, makeAmount ):
	"""
	当前研发物品被改变
	@param makeItemID	:物品ID
	@param makeAmount	:要生产的数量
	"""
	fireEvent( "EVT_ON_TOGGLE_TONG_CURRENT_ITEM_CHANGE", makeItemID, makeAmount )
#	BigWorld.player().chat_say( "当前正在研究物品改变为%i:%i" % ( makeItemID, makeAmount ) )

def tong_updatePlayerWarReport( playerID, playerName, playerTongDBID, killCount, dieCount ): #更新争夺报表
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
	fireEvent( "EVT_ON_TOGGLE_TONG_ABA_RELIVE_BOX" ) #玩家在帮会擂台死亡弹出复活点选择界面
#
# $Log: not supported by cvs2svn $
# Revision 1.8  2008/08/12 08:51:26  kebiao
# 添加帮主集结令功能
#
# Revision 1.7  2008/07/01 01:59:34  fangpengjun
# 修正tong_updateMemberMapInfo参数
#
# Revision 1.6  2008/06/30 10:24:11  fangpengjun
# 修改部分消息
#
# Revision 1.5  2008/06/29 08:53:56  fangpengjun
# 添加了界面需要的信息
#
# Revision 1.4  2008/06/21 03:41:46  kebiao
# 加入帮会贡献度
#
# Revision 1.3  2008/06/16 09:15:26  kebiao
# base 上部分暴露接口转移到cell 改变调用方式
#
# Revision 1.2  2008/06/14 09:15:37  kebiao
# 新增帮会功能
#
# Revision 1.1  2008/06/09 09:24:00  kebiao
# 加入帮会相关
#
#
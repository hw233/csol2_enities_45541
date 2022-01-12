# -*- coding: gb18030 -*-
#
# $Id: TeamFacade.py,v 1.16 2008-08-13 09:07:57 huangdong Exp $

from bwdebug import *
import BigWorld
from event.EventCenter import *

class TeamFacade:
	@staticmethod
	def reset():
		pass



# ------------------------------->
# 用于让底层调用
# ------------------------------->
def onAskJoinTeam( inviterName, isInvite ):
	"""
	某个人想要邀请你(向你申请)加入队伍

	@param inviterName: 邀请（申请）者名称
	@type  inviterName: STRING
	@param isInvite: 1 == 邀请加入队伍，0 == 申请加入队伍
	@type  isInvite: INT8
	@return:         无
	"""
	if isInvite:
		fireEvent( "EVT_ON_INVITE_JOIN_TEAM", inviterName )
	else:
		fireEvent( "EVT_ON_REQUEST_JOIN_TEAM", inviterName )


def onAskFollow( entityid ):
	"""
	队长邀请你跟随他
	@param entityid : 队长的entityid
	@param entityid : INT
	@return			: NONE
	"""
	fireEvent( "EVT_ON_INVITE_FOLLOW", entityid )

def onTeamMemberAdded( member ):
	"""
	有新的成员加入队伍

	@param member: instance of TeamMember; see also Team.py
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_ADDED", member )

def onTeamMemberLeft( entityID ):
	"""
	队员离开
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_LEFT", entityID )

def onTeamMemberChangeHP( entityID, hp, hpMax ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_HP_CHANGED", entityID, hp, hpMax )

def onTeamMemberChangeMP( entityID, mp, mpMax ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_MP_CHANGED", entityID, mp, mpMax )

def onTeamMemberChangeLevel( entityID, value ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_LEVEL_CHANGED", entityID, value )

def onTeamMemberChangeSpace( entityID, value ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_SPACE_CHANGED", entityID, value )

def onTeamMemberChangeName( entityID, name ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_NAME_CHANGED", entityID, name )

def onTeamMemberChangeIcon( entityID, iconFileName ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_HEADER_CHANGED", entityID, iconFileName )

def onTeamMemberLogOut( entityID ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_LOG_OUT", entityID )

def onTeamMemberChangePosition( entityID, position ):
	"""
	@param position: VECTOR3 or tuple of float that include 3 element like as (0.0, 0.0, 0.0)
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_POSITION_CHANGED", entityID, position )

def onTeamCaptainChanged( entityID ):
	"""
	"""
	fireEvent( "EVT_ON_TEAM_CAPTAIN_CHANGED", entityID )

def onTeamDisbanded() :
	fireEvent( "EVT_ON_TEAM_DISBANDED" )

def onTeamMemberRejoin( oldEntityID, newEntityID ):
	fireEvent( "EVT_ON_TEAM_MEMBER_REJOIN", oldEntityID, newEntityID )

# ------------------------------->
# team about
# ------------------------------->
def inviteToTeam( targetEntity ):
	"""
	邀请目标加入队伍

	@param targetEntity: 要邀请的目标entity实例
	@return: BOOL；如果能邀请且数据正常发送则返回True，否则返回False
	"""
	return BigWorld.player().inviteJoinTeamNear( targetEntity )

def revertInviteJoinTeam( accept = True ):
	"""
	回复对方的邀请，玩家同意(拒绝)加入对方的队伍

	@param accept: BOOL；是否接受邀请
	"""
	BigWorld.player().revertInviteJoinTeam( accept )

def revertRequestJoinTeam( accept = True ):
	"""
	回复对方申请加入自己队伍的要求
	"""
	BigWorld.player().acceptJoinTeam()

def leaveTeam():
	"""
	玩家请求离开队伍
	"""
	BigWorld.player().leaveTeam()

def disbandTeam():
	"""
	解散队伍
	"""
	BigWorld.player().disbandTeam()

def kickoutTeam( objectID ):
	"""
	开除出队伍
	"""
	BigWorld.player().teamDisemploy( objectID )

def inviteAllfollow():
	"""
	队长发起组队跟随
	"""
	BigWorld.player().team_leadTeam()


#
# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/09 10:03:19  huangdong
# 加入了抛出邀请跟随消息的函数
#
# Revision 1.14  2008/02/29 06:40:34  zhangyuxing
# no message
#
# Revision 1.13  2007/11/16 03:56:09  zhangyuxing
# 修改BUG：fireEvent( "EVT_ON_TEAM_MEMBER_REJOIN" )
# to
# 	fireEvent( "EVT_ON_TEAM_MEMBER_REJOIN", oldEntityID, newEntityID )
# 原本的调用少写了两个参数
#
# Revision 1.12  2007/10/09 07:57:17  phw
# 队伍代码调整，删除了一些不用的接口
#
# Revision 1.11  2007/06/14 10:36:37  huangyongwei
# 整理了全局定义
#
# Revision 1.10  2007/06/14 03:22:56  panguankong
# 修改client只使用objectID
#
# Revision 1.9  2007/02/03 06:09:18  fangpengjun
# 将fireEvent( "EVT_ON_TEAM_CAPTAIN_CHANGED", entityDBID )中的entityDBID 改为
#  fireEvent( "EVT_ON_TEAM_CAPTAIN_CHANGED", entityID )中的entityID
#
# Revision 1.8  2006/12/21 03:16:35  panguankong
# 添加取队伍成员接口
#
# Revision 1.7  2006/12/20 09:39:18  huangyongwei
# 添加了队伍解散函数： onTeamDisbanded
#
# Revision 1.6  2006/12/19 10:27:37  huangyongwei
# EVT_ON_TEAM_MEMBER_CHANGE_HP				# entityID, hp, hpMax;
# EVT_ON_TEAM_MEMBER_CHANGE_MP				# entityID, mp, mpMax;
# EVT_ON_TEAM_MEMBER_CHANGE_LEVEL				# entityID, level;
# EVT_ON_TEAM_MEMBER_CHANGE_SPACE				# entityID, spaceID;
# EVT_ON_TEAM_MEMBER_CHANGE_NAME				# entityID, name;
# EVT_ON_TEAM_MEMBER_CHANGE_ICON				# entityID, iconFileName;
# EVT_ON_TEAM_MEMBER_CHANGE_POSITION			# entityID, position;
#
# --->
# EVT_ON_TEAM_MEMBER_HP_CHANGED				# entityID, hp, hpMax;
# EVT_ON_TEAM_MEMBER_MP_CHANGED				# entityID, mp, mpMax;
# EVT_ON_TEAM_MEMBER_LEVEL_CHANGED			# entityID, level;
# EVT_ON_TEAM_MEMBER_SPACE_CHANGED			# entityID, spaceID;
# EVT_ON_TEAM_MEMBER_NAME_CHANGED				# entityID, name;
# EVT_ON_TEAM_MEMBER_HEADER_CHANGED				# entityID, iconFileName;
# EVT_ON_TEAM_MEMBER_POSITION_CHANGED			# entityID, position;
#
# Revision 1.5  2006/11/29 09:50:14  panguankong
# no message
#
# Revision 1.4  2006/07/15 08:01:13  phw
# 出现了两个onTeamMemberChangeIcon()的情况,修改其中一个成为onTeamMemberChangePosition()
#
# Revision 1.3  2006/07/15 05:14:02  phw
# 删除了两行误输入的字符串
#
# Revision 1.2  2006/07/15 05:11:10  phw
# 删除onTeamMemberChangeMPMax()
# 删除onTeamMemberChangeHPMax()
# 修改了onTeamMemberChangeHP()
# 修改了onTeamMemberChangeMP()
#
# Revision 1.1  2006/07/13 10:14:10  phw
# 队伍相关的接口
#
#
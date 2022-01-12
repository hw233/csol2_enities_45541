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
# �����õײ����
# ------------------------------->
def onAskJoinTeam( inviterName, isInvite ):
	"""
	ĳ������Ҫ������(��������)�������

	@param inviterName: ���루���룩������
	@type  inviterName: STRING
	@param isInvite: 1 == ���������飬0 == ����������
	@type  isInvite: INT8
	@return:         ��
	"""
	if isInvite:
		fireEvent( "EVT_ON_INVITE_JOIN_TEAM", inviterName )
	else:
		fireEvent( "EVT_ON_REQUEST_JOIN_TEAM", inviterName )


def onAskFollow( entityid ):
	"""
	�ӳ������������
	@param entityid : �ӳ���entityid
	@param entityid : INT
	@return			: NONE
	"""
	fireEvent( "EVT_ON_INVITE_FOLLOW", entityid )

def onTeamMemberAdded( member ):
	"""
	���µĳ�Ա�������

	@param member: instance of TeamMember; see also Team.py
	"""
	fireEvent( "EVT_ON_TEAM_MEMBER_ADDED", member )

def onTeamMemberLeft( entityID ):
	"""
	��Ա�뿪
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
	����Ŀ��������

	@param targetEntity: Ҫ�����Ŀ��entityʵ��
	@return: BOOL��������������������������򷵻�True�����򷵻�False
	"""
	return BigWorld.player().inviteJoinTeamNear( targetEntity )

def revertInviteJoinTeam( accept = True ):
	"""
	�ظ��Է������룬���ͬ��(�ܾ�)����Է��Ķ���

	@param accept: BOOL���Ƿ��������
	"""
	BigWorld.player().revertInviteJoinTeam( accept )

def revertRequestJoinTeam( accept = True ):
	"""
	�ظ��Է���������Լ������Ҫ��
	"""
	BigWorld.player().acceptJoinTeam()

def leaveTeam():
	"""
	��������뿪����
	"""
	BigWorld.player().leaveTeam()

def disbandTeam():
	"""
	��ɢ����
	"""
	BigWorld.player().disbandTeam()

def kickoutTeam( objectID ):
	"""
	����������
	"""
	BigWorld.player().teamDisemploy( objectID )

def inviteAllfollow():
	"""
	�ӳ�������Ӹ���
	"""
	BigWorld.player().team_leadTeam()


#
# $Log: not supported by cvs2svn $
# Revision 1.15  2008/08/09 10:03:19  huangdong
# �������׳����������Ϣ�ĺ���
#
# Revision 1.14  2008/02/29 06:40:34  zhangyuxing
# no message
#
# Revision 1.13  2007/11/16 03:56:09  zhangyuxing
# �޸�BUG��fireEvent( "EVT_ON_TEAM_MEMBER_REJOIN" )
# to
# 	fireEvent( "EVT_ON_TEAM_MEMBER_REJOIN", oldEntityID, newEntityID )
# ԭ���ĵ�����д����������
#
# Revision 1.12  2007/10/09 07:57:17  phw
# ������������ɾ����һЩ���õĽӿ�
#
# Revision 1.11  2007/06/14 10:36:37  huangyongwei
# ������ȫ�ֶ���
#
# Revision 1.10  2007/06/14 03:22:56  panguankong
# �޸�clientֻʹ��objectID
#
# Revision 1.9  2007/02/03 06:09:18  fangpengjun
# ��fireEvent( "EVT_ON_TEAM_CAPTAIN_CHANGED", entityDBID )�е�entityDBID ��Ϊ
#  fireEvent( "EVT_ON_TEAM_CAPTAIN_CHANGED", entityID )�е�entityID
#
# Revision 1.8  2006/12/21 03:16:35  panguankong
# ���ȡ�����Ա�ӿ�
#
# Revision 1.7  2006/12/20 09:39:18  huangyongwei
# ����˶����ɢ������ onTeamDisbanded
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
# ����������onTeamMemberChangeIcon()�����,�޸�����һ����ΪonTeamMemberChangePosition()
#
# Revision 1.3  2006/07/15 05:14:02  phw
# ɾ����������������ַ���
#
# Revision 1.2  2006/07/15 05:11:10  phw
# ɾ��onTeamMemberChangeMPMax()
# ɾ��onTeamMemberChangeHPMax()
# �޸���onTeamMemberChangeHP()
# �޸���onTeamMemberChangeMP()
#
# Revision 1.1  2006/07/13 10:14:10  phw
# ������صĽӿ�
#
#
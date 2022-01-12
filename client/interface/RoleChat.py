# -*- coding: gb18030 -*-

# $Id: RoleChat.py,v 1.39 2008-08-30 09:15:54 huangyongwei Exp $
"""
implement chatting system

09/05/2005 : created by phw
11/28/2006 : modified by huangyongwei
"""

import csdefine
import csstatus
import csstatus_msgs
import event.EventCenter as ECenter
from bwdebug import *
from gbref import rds
from MapMgr import mapMgr
import Const
from ChatFacade import chatFacade
from config.client.labels import RoleChat as lbs_RoleChat
from config.client.SkillAutoConfig import Datas as skill_auto_datas  #add by wuxo 2011-11-17
# --------------------------------------------------------------------
# ʵ������ӿ�
# --------------------------------------------------------------------
class RoleChat :
	def __init__( self ) :
		self.chat_commands = {}			# ���п��� GM ָ�{ ָ������ : ָ��ȼ� }

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache�������
		"""
		pass


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStatusMessage_( self, statusID, *args ) :
		"""
		�յ�״̬��Ϣʱ�����ã��� Role �е� onStatusMessage def �����յ���Ϣ�󣬽���������Ͳ������˷�����
		״̬��Ϣ��Ҫת��ΪƵ����Ϣ
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		"""
		chatFacade.rcvStatusMsg( statusID, *args )

	def _onDirectMessage( self, chids, spkName, msg ) :
		"""
		�յ�Ƶ����Ϣʱ�����ã��� Role �е� onDirectMessage def �����յ���Ϣ�󴥷��˷�����
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		"""
		chatFacade.rcvMsgDirect( chids, spkName, msg )

	# ----------------------------------------------------------------
	# attribute setting methods
	# ----------------------------------------------------------------
	def set_grade( self, old ) :
		"""
		����ȼ��ı�ʱ������
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		hyw--2009.03.16
		"""
		pass


	# ----------------------------------------------------------------
	# defined methods
	# ----------------------------------------------------------------
	def chat_onChannelMessage( self, chid, spkID, spkName, msg, blobArgs ) :
		"""
		defined method
		�յ�Ƶ����Ϣʱ������
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		@type		chid	: INT8
		@param 		chid	: speaking channel
		@type		spkID	: OBJECT_ID
		@param		spkID	: ������ entity id
		@type		spkName : STRING
		@param 		spkName : spokesman's name
		@type		msg		: STRING
		@param 		msg		: speech
		@type		blobArgs: BLOB
		@param		blobArgs: ��Ϣ����
		@return				: None
		"""
		if spkName in self.blackList : return						# ���Լ��ĺ������Ͳ�������Ϣ
		chatFacade.rcvChannelMsg( chid, spkID, spkName, msg, blobArgs )

	def chat_onRcvOflMessage( self, chid, spkID, spkName, msg, blobArgs, sendTime ) :
		"""
		defined method
		����������Ϣ
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		@type		chid	: INT8
		@param 		chid	: speaking channel
		@type		spkID	: OBJECT_ID
		@param		spkID	: ������ entity id
		@type		spkName : STRING
		@param 		spkName : spokesman's name
		@type		msg		: STRING
		@param 		msg		: speech
		@type		blobArgs: BLOB
		@param		blobArgs: ��Ϣ����
		@type		sendTime: STRING
		@param		sendTime: ��Ϣ����ʱ��
		@return				: None
		"""
		if spkName in self.blackList : return						# ���Լ��ĺ������Ͳ�������Ϣ
		chatFacade.rcvChannelMsg( chid, spkID, spkName, msg, blobArgs, sendTime )

	# ---------------------------------------
	def chat_systemInfo( self, msg ) :
		"""
		defined method
		����һ���򵥵�Ƶ�������Ϣ����������Ӧ�þ����� statusMessage ����˷�����
		ע�⣺�� ����Ϣ���ĸ�Ƶ����ʾ���� msg ��ǰ׺����
			  �� Ƶ��ǰ׺˵���뿴��common/csstatus_msgs.py
			  �� ����Ƶ��ǰ׺����ϢĬ���ڡ����ˡ�Ƶ����ʾ
		"""
		msgInfo = csstatus_msgs.getMSGInfo( msg )
		for chid in msgInfo.chids :
			chatFacade.rcvChannelMsg( chid, 0, msgInfo.spkName, msgInfo.msg, [] )

	# -------------------------------------------------
	def chat_onReceiveRoleInfo( self, roleInfo ) :
		"""
		defined method
		�յ���ɫ��Ϣ
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		"""
		if roleInfo["name"] == "" :
			self.statusMessage( csstatus.TARGET_IS_NONE_OR_NOT_ONLINE )
		else :
			msg = "%s, " % roleInfo["name"]
			msg += lbs_RoleChat.level % roleInfo["level"]
			if roleInfo["tong"] != "" :
				msg += lbs_RoleChat.tong % roleInfo["tong"]
			spaceLabel = roleInfo["spaceLabel"]
			wholeArea = mapMgr.getWholeArea( spaceLabel )
			if wholeArea :
				msg += lbs_RoleChat.area % wholeArea.name
			else :
				ERROR_MSG( "spaceLabel: '%s' is not exist!" % spaceLabel )						# Ӧ�ò��᲻ִ�е�������Ǹó������� bigmap.xml ������
			ECenter.fireEvent( "EVT_ON_CHAT_RECEIVE_ROLE_INFO", msg )

	def chat_onScenarioMsg( self, msg, visible ) :
		"""
		define method
		���������͵ľ�����ʾ
		@param		msg : �����ı�
		@type		msg : STRING
		@param 		visible: �Ƿ�������ҽ���,False��ʾ������
		@param		visible: Bool
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_SCENARIO_TIPS", msg, visible )


	# ----------------------------------------------------------------
	# public( called by client )
	# ----------------------------------------------------------------
	def statusMessage( self, statusID, *args ) :
		"""
		send status message
		ע�⣺�÷���ֻ�� PlayerRole ʹ�ã���Ҫ��ͼͨ��������ɫ���ø÷�������˽�ɫ����һ����Ϣ��
		@type			statusID : INT16
		@param			statusID : defined in common/scdefine.py
		@type			args	 : int/float/str/double
		@param			args	 : it must match the message defined in csstatus_msgs.py
		@return					 : None
		"""
		# �Զ�ս��״̬��������ʾ��Ϣ
		if hasattr( self, "attackState" ) and self.attackState == Const.ATTACK_STATE_AUTO_FIGHT:return
		chatFacade.rcvStatusMsg( statusID, *args )
		#������Ӧ��Чadd by wuxo 2012-5-15
		if skill_auto_datas.has_key( statusID ):
			career_gender = self.getClass() + self.getGender()
			if skill_auto_datas[ statusID ].has_key( career_gender ):
				rds.soundMgr.play2DSound( skill_auto_datas[ statusID ][ career_gender ] )

	# -------------------------------------------------
	def chat_requireRoleInfo( self, roleName ) :
		"""
		�����ɫ��Ϣ
		ע�⣺�÷���ֻ�� PlayerRole ʹ��
		hyw -- 2008.08.29
		@type				roleName : str
		@param				roleName : ��ɫ����
		"""
		self.base.chat_requireRoleInfo( roleName )

	def chat_switchFengQi( self, unLocked ):
		"""
		GM����/����ҹս�������������
		"""
		self.cell.chat_switchFengQi( unLocked )
	
	def chat_onSwitchFengQi( self, unLocked ):
		"""
		define method
		����/����ҹս���������ص�
		"""
		ECenter.fireEvent( "EVT_ON_PLAYER_SWITCH_FENGQI", unLocked )

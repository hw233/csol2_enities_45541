# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter

class RoleYiJieZhanChangInterface:
	"""
	���ս��
	"""
	def __init__( self ):
		self.yiJieReviveTime = 0
		self.yiJieKiller = ""
	
	def yiJieOnTeleportReady( self ):
		"""
		define method
		������ɣ���ͼ�������֪ͨ�ͻ���
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_WINDOW_SHOW" )
		ECenter.fireEvent( "EVT_ON_YI_JIE_BATTLE_INFOS_SHOW" )
	
	def yiJieOnExit( self ):
		"""
		<define method>
		�˳�ս��
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_WINDOW_HIDE" )
		ECenter.fireEvent( "EVT_ON_YI_JIE_BATTLE_INFOS_HIDE" )
	
	def yiJieSetReviveInfo( self, reviveTime, killerName ) :
		"""
		<define method>
		���ø�������ʱ��
		"""
		self.yiJieReviveTime = reviveTime
		self.yiJieKiller = killerName
	
	def yiJieShowSignUp( self ):
		"""
		define method
		�򿪱�������
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_JIJIE_SIGNUP_WINDOW" )
	
	def yiJieCancelSignUp( self ):
		"""
		define method
		�رձ�������
		"""
		ECenter.fireEvent( "EVT_ON_CANCEL_JIJIE_SIGNUP_WINDOW" )
	
	def onAngerPointChanged( self, angerPoint ):
		"""
		define method
		ŭ��ֵ�ı�ص�
		@type			angerPoint : ŭ��ֵ
		@param			angerPoint : INT8
		"""
		ECenter.fireEvent( "EVT_ON_ANGER_POINT_CHANGED", angerPoint )
	
	def requestEnterYiJie( self ):
		"""
		����������ս��
		"""
		self.cell.yiJieRequestEnter()
		
	def yiJieReceiveDatas( self, roleInfos ):
		"""
		define method
		�������������Ϣ��������������Ҳ������roleInfos�У�
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_YIJIE_SCORES_DATAS", roleInfos )
		
	def yiJieOnKillDataChanged( self, killNum, keepNum, maxKeepNum ) :
		"""
		< define method >
		ɱ��������ն���������ն�������ݸı�ص�
		@type			killNum 	: ɱ����
		@param			killNum 	: INT32
		@type			keepNum 	: ��ն��
		@param			keepNum		: INT32
		@type			maxKeepNum 	: �����ն��
		@param			maxKeepNum 	: INT32
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_YIJIE_PLAYER_INFOS", killNum, keepNum, maxKeepNum )
	
	def canPk( self, entity ) :
		"""
		�ܷ��� entity ���� pk
		"""
		if self.yiJieFaction == entity.yiJieFaction or self.yiJieAlliance == entity.yiJieFaction :
			return False
		else :
			return True
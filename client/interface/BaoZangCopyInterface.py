# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import Define
import event.EventCenter as ECenter
from MessageBox import *
from config.client.msgboxtexts import Datas as mbmsgs


class BaoZangCopyInterface:
	#���ظ����ӿ�( Ӣ������ )
	def __init__( self ):
		self.baoZangRobotInfos = {}
		self.isRequestCampYingXiongCopy = False

	# ------------------------
	#  PVE
	# ------------------------
	def baoZangReqRobotInfos( self ):
		"""
		�����������Ϣ
		"""
		if len( self.baoZangRobotInfos ) <= 0:
			self.cell.baoZangReqRobotInfos()
	
	def baoZangOnReqRobotInfos( self, robotInfos ):
		"""
		define method
		������������˵���Ϣ
		"""
		for robotInfo in robotInfos:
			className = robotInfo["className"]
			self.baoZangRobotInfos[className] = robotInfo
	

	def baoZangPVESetRobot( self, rbtCls ):
		"""
		����Ѹ��»�������Ϣ
		"""
		self.cell.baoZangPVESetRobot( rbtCls )
		
	def baoZangPVEonSetRobot( self, rbtCls ):
		"""
		define method
		�ӳ�ѡ�������
		@ param rbtCls: className list
		"""
		ECenter.fireEvent( "EVT_ON_SET_PVE_ROBOTS", rbtCls )
		
	
	def baoZangOnReqPVE( self, selectRobots ):
		"""
		ѡ������˵Ȳ�����ɣ�������븱��
		selectRobots: className list
		"""
		self.cell.baoZangOnReqPVE( selectRobots )
	
	def baoZangReqPVE( self, robotsInfos, rbtCls ):
		"""
		define method
		�򿪻�����ѡ�����
		"""
		self.baoZangOnReqRobotInfos( robotsInfos )
		ECenter.fireEvent( "EVT_ON_TOGGLE_ROBOT_CHOICE_WND", rbtCls )
	
	# ------------------------
	#  PVP
	# ------------------------
	def baoZangPVPonReq( self, reqTime ):
		"""
		define method
		�������뱦�ظ���PVP�Ŷ�
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_REQ, "" )
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_REQ_TIME", reqTime )
		
	
	def baoZangPVPonCancel( self, isMatch ):
		"""
		define method.
		ȡ������PVP���Ŷ�
		"""
		if not isMatch: # ƥ��ɹ�����ʾ
			self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
		
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_CANCEL_QUEUE", False )
		
	def baoZangReqSucceed( self, teamID ):
		"""
		define method
		ƥ��ɹ�
		"""
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.baoZangGotoNPC()
				
		showMessage( mbmsgs[0x1000], "", MB_YES_NO, result )
	
	def baoZangOpenPVPTeamInfos( self, memberIds, countDown, isReady ):
		"""
		define method
		�Կ�����׼������
		@param1 :countDown ����ʱ
		������Ա��ID
		"""
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_TOGGLE_WND", memberIds, countDown, isReady )
	
	def baoZangReReq( self ):
		"""
		define method
		���ڶԷ�û��ȷ��ƥ�䣬����ƥ��ʧ��
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
	
	def baoZangClosePVPTeamInfos( self ):
		"""
		define method
		�رս���
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_NOT_READY, "" )
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_CLOSE_WND" )
	
	# ------------------------
	#  ��ӪӢ������
	# ------------------------
	def yingXiongCampOnReq( self, reqTime ):
		"""
		define method
		�������뱦�ظ���PVP�Ŷ�
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_REQ, "" )
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_REQ_TIME", reqTime )
		self.isRequestCampYingXiongCopy = True
	
	def yingXiongCampOnCancel( self, isMatch ):
		"""
		define method.
		ȡ������PVP���Ŷ�
		"""
		self.isRequestCampYingXiongCopy = False
		if not isMatch: # ƥ��ɹ�����ʾ
			self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
		
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_CANCEL_QUEUE", False )

	def yingXiongCampReqSucceed( self, teamID ):
		"""
		define method
		ƥ��ɹ�
		"""
		self.isRequestCampYingXiongCopy = False
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.yingXiongCampGotoNPC()
				
		showMessage( mbmsgs[0x1000], "", MB_YES_NO, result )
	
	def yingXiongCampOpenTeamInfos( self, memberIds, countDown, isReady ):
		"""
		define method
		�Կ�����׼������
		@param1 :countDown ����ʱ
		������Ա��ID
		"""
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_TOGGLE_WND", memberIds, countDown, isReady )
	
	def yingXiongCampReReq( self ):
		"""
		define method
		���ڶԷ�û��ȷ��ƥ�䣬����ƥ��ʧ��
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
	
	def yingXiongCampCloseTeamInfos( self ):
		"""
		define method
		�رս���
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_NOT_READY, "" )
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_CLOSE_WND" )
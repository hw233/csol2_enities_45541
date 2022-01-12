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
	#宝藏副本接口( 英雄联盟 )
	def __init__( self ):
		self.baoZangRobotInfos = {}
		self.isRequestCampYingXiongCopy = False

	# ------------------------
	#  PVE
	# ------------------------
	def baoZangReqRobotInfos( self ):
		"""
		请求机器人信息
		"""
		if len( self.baoZangRobotInfos ) <= 0:
			self.cell.baoZangReqRobotInfos()
	
	def baoZangOnReqRobotInfos( self, robotInfos ):
		"""
		define method
		返回请求机器人的信息
		"""
		for robotInfo in robotInfos:
			className = robotInfo["className"]
			self.baoZangRobotInfos[className] = robotInfo
	

	def baoZangPVESetRobot( self, rbtCls ):
		"""
		向队友更新机器人信息
		"""
		self.cell.baoZangPVESetRobot( rbtCls )
		
	def baoZangPVEonSetRobot( self, rbtCls ):
		"""
		define method
		队长选择机器人
		@ param rbtCls: className list
		"""
		ECenter.fireEvent( "EVT_ON_SET_PVE_ROBOTS", rbtCls )
		
	
	def baoZangOnReqPVE( self, selectRobots ):
		"""
		选择机器人等操作完成，请求进入副本
		selectRobots: className list
		"""
		self.cell.baoZangOnReqPVE( selectRobots )
	
	def baoZangReqPVE( self, robotsInfos, rbtCls ):
		"""
		define method
		打开机器人选择界面
		"""
		self.baoZangOnReqRobotInfos( robotsInfos )
		ECenter.fireEvent( "EVT_ON_TOGGLE_ROBOT_CHOICE_WND", rbtCls )
	
	# ------------------------
	#  PVP
	# ------------------------
	def baoZangPVPonReq( self, reqTime ):
		"""
		define method
		队伍申请宝藏副本PVP排队
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_REQ, "" )
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_REQ_TIME", reqTime )
		
	
	def baoZangPVPonCancel( self, isMatch ):
		"""
		define method.
		取消副本PVP的排队
		"""
		if not isMatch: # 匹配成功不提示
			self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
		
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_CANCEL_QUEUE", False )
		
	def baoZangReqSucceed( self, teamID ):
		"""
		define method
		匹配成功
		"""
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.baoZangGotoNPC()
				
		showMessage( mbmsgs[0x1000], "", MB_YES_NO, result )
	
	def baoZangOpenPVPTeamInfos( self, memberIds, countDown, isReady ):
		"""
		define method
		对开进入准备界面
		@param1 :countDown 倒计时
		进入人员的ID
		"""
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_TOGGLE_WND", memberIds, countDown, isReady )
	
	def baoZangReReq( self ):
		"""
		define method
		由于对方没有确认匹配，本次匹配失败
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
	
	def baoZangClosePVPTeamInfos( self ):
		"""
		define method
		关闭界面
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_NOT_READY, "" )
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_CLOSE_WND" )
	
	# ------------------------
	#  阵营英雄联盟
	# ------------------------
	def yingXiongCampOnReq( self, reqTime ):
		"""
		define method
		队伍申请宝藏副本PVP排队
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_REQ, "" )
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_REQ_TIME", reqTime )
		self.isRequestCampYingXiongCopy = True
	
	def yingXiongCampOnCancel( self, isMatch ):
		"""
		define method.
		取消副本PVP的排队
		"""
		self.isRequestCampYingXiongCopy = False
		if not isMatch: # 匹配成功不提示
			self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
		
		ECenter.fireEvent( "EVT_ON_BAOZANG_PVP_CANCEL_QUEUE", False )

	def yingXiongCampReqSucceed( self, teamID ):
		"""
		define method
		匹配成功
		"""
		self.isRequestCampYingXiongCopy = False
		def result( rs_id ):
			if rs_id == RS_YES:
				self.cell.yingXiongCampGotoNPC()
				
		showMessage( mbmsgs[0x1000], "", MB_YES_NO, result )
	
	def yingXiongCampOpenTeamInfos( self, memberIds, countDown, isReady ):
		"""
		define method
		对开进入准备界面
		@param1 :countDown 倒计时
		进入人员的ID
		"""
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_TOGGLE_WND", memberIds, countDown, isReady )
	
	def yingXiongCampReReq( self ):
		"""
		define method
		由于对方没有确认匹配，本次匹配失败
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_RE_REQ, "" )
	
	def yingXiongCampCloseTeamInfos( self ):
		"""
		define method
		关闭界面
		"""
		self.onStatusMessage( csstatus.YING_XIONG_LIAN_MENG_PVP_NOT_READY, "" )
		ECenter.fireEvent( "EVT_ON_PVP_TEAM_CLOSE_WND" )
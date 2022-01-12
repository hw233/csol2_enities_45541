# -*- coding: gb18030 -*-
import BigWorld

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter

class RoleYeZhanFengQiInterface:
	def __init__( self ):
		self.fengQiIntegrals = {}
		self.fengQiReviveTime = 0
	
	def fengQiOnEnter( self ):
		"""
		define method
		进入凤栖战场
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_ON_ENTER", self )
	
	def fengQiOnExit( self ):
		"""
		define method
		退出战场
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_ON_EXIT", self )
	
	def fengQiReqExit( self ):
		"""
		请求退出副本
		"""
		self.cell.fengQiReqExit()
	
	def fengQiCountDown( self ):
		"""
		define method
		结束倒计时
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_COUNT_DOWN" )
	
	def fengQiCloseActivity( self ):
		"""
		define method
		活动时间到
		"""
		pass
	
	def fengQiUpIntegral( self, mId, mIntegral ):
		"""
		define method.
		设置积分
		"""
		self.fengQiIntegrals[mId] = mIntegral
		ECenter.fireEvent( "EVT_ON_FENGQI_SET_INTERGRAL", mId, mIntegral )
	
	def fengQiUpReport( self, mId, mName, mKill, mBeKill ):
		"""
		define method
		更新战报
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_UP_REPORT", mId, mName, mKill, mBeKill )
	
	def fengQiUpBox( self, mId, boxNum ):
		"""
		define method
		更新玩家拾取箱子数
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_UP_BOXNUM", mId, boxNum )
	
	def fengQiExitMember( self, mId ):
		"""
		define method
		有玩家退出
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_MEMBER_EXIT", mId )
		
	def fengQiReviveClew( self, reviveTime ):
		"""
		define method.
		凤栖副本复活提示
		"""
		self.fengQiReviveTime = reviveTime
		ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )
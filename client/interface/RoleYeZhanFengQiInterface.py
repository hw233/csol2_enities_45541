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
		�������ս��
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_ON_ENTER", self )
	
	def fengQiOnExit( self ):
		"""
		define method
		�˳�ս��
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_ON_EXIT", self )
	
	def fengQiReqExit( self ):
		"""
		�����˳�����
		"""
		self.cell.fengQiReqExit()
	
	def fengQiCountDown( self ):
		"""
		define method
		��������ʱ
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_COUNT_DOWN" )
	
	def fengQiCloseActivity( self ):
		"""
		define method
		�ʱ�䵽
		"""
		pass
	
	def fengQiUpIntegral( self, mId, mIntegral ):
		"""
		define method.
		���û���
		"""
		self.fengQiIntegrals[mId] = mIntegral
		ECenter.fireEvent( "EVT_ON_FENGQI_SET_INTERGRAL", mId, mIntegral )
	
	def fengQiUpReport( self, mId, mName, mKill, mBeKill ):
		"""
		define method
		����ս��
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_UP_REPORT", mId, mName, mKill, mBeKill )
	
	def fengQiUpBox( self, mId, boxNum ):
		"""
		define method
		�������ʰȡ������
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_UP_BOXNUM", mId, boxNum )
	
	def fengQiExitMember( self, mId ):
		"""
		define method
		������˳�
		"""
		ECenter.fireEvent( "EVT_ON_FENGQI_MEMBER_EXIT", mId )
		
	def fengQiReviveClew( self, reviveTime ):
		"""
		define method.
		���ܸ���������ʾ
		"""
		self.fengQiReviveTime = reviveTime
		ECenter.fireEvent( "EVT_ON_SHOW_REVIVE_BOX" )
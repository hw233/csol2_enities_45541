# -*- coding: gb18030 -*-

import BigWorld

from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import csstatus

FENG_QI_SPACE_CLASS_NAME = "fu_ben_ye_zhan_feng_qi"

class RoleYeZhanFengQiInterface:
	def __init__( self ):
		self.onFengQi = False  # �Ƿ��ڷ���ս��
	
	def fengQiAddPlayerIntegral( self, integral ):
		"""
		define method
		��ӻ���
		"""
		self.getCurrentSpaceBase().cell.addPlayerIntegral( self.id, integral )
		self.statusMessage( csstatus.YE_ZHAN_FENG_QI_GET_INTEGRAL, integral )
	
	def fengQiOnEnter( self, isAction ):
		"""
		define method
		�������ս��
		"""
		self.onFengQi = True
		self.addActivityCount( csdefine.ACTIVITY_YE_ZHAN_FENG_QI )
		if isAction:
			self.fengQiAction()
		else:
			self.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )
			self.statusMessage( csstatus.YE_ZHAN_FENG_QI_READY )
			
		self.client.fengQiOnEnter()
	
	def fengQiAction( self ):
		"""
		define method.
		ս����ʼ
		"""
		self.statusMessage( csstatus.YE_ZHAN_FENG_QI_ACTION )
		self.setSysPKMode( csdefine.PK_CONTROL_PROTECT_NONE )
	
	def fengQiCloseActivity( self ):
		"""
		define method
		�����
		"""
		self.unLockPkMode()
		self.setPkMode( self.id, csdefine.PK_CONTROL_PROTECT_RIGHTFUL )
		self.setSysPKMode( 0 )
		self.lockPkMode()
		self.statusMessage( csstatus.YE_ZHAN_FENG_QI_END )
		self.client.fengQiCloseActivity()
	
	def fengQiOnExit( self ):
		"""
		define method
		�˳�ս��
		"""
		self.onFengQi = False
		self.unLockPkMode()
		self.setSysPKMode( 0 )
		self.end_body_changing( self.id, "" )
		self.client.fengQiOnExit()
	
	def fengQiReqExit( self, exposed ):
		"""
		define method
		�����˳�ս��
		"""
		self.gotoForetime()
	
	def afterDie( self, killerID ):
		"""
		virtual method.
		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		objScript = g_objFactory.getObject( FENG_QI_SPACE_CLASS_NAME )
		self.systemCastSpell( objScript.gainSkillID )
		self.client.fengQiReviveClew( objScript.reviveTime )
	
	def onDestroy( self ):
		"""
		��Ϸ����
		"""
		self.getCurrentSpaceBase.cell.playerExit( self.base )
	
	def fengQiGetRevivePosition( self ):
		"""
		ȡ�ø���λ��
		"""
		objScript = g_objFactory.getObject( FENG_QI_SPACE_CLASS_NAME )
		pos = objScript.getRandomEnterPos()[0]
		return  pos
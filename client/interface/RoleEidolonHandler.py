# -*- coding:gb18030 -*-

from bwdebug import *
import csdefine
import csconst
import event.EventCenter as ECenter
import BigWorld
from Sound import soundMgr


class RoleEidolonHandler:
	"""
	���С��������ӿ�
	"""
	def __init__( self ):
		"""
		"""
		pass

	def conjureEidolon( self ):
		"""
		�ٻ�С����
		"""
		self.cell.conjureEidolon()

	def withdrawEidolon( self ) :
		"""
		�ջ�С����
		"""
		self.cell.withdrawEidolon()

	def vipShareSwitch( self ) :
		"""
		С����VIP���ܹ���
		"""
		self.cell.vipShareSwitch()

	def eidolonDirect( self, objectID ):
		"""
		����ָ��
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_SHOW_COURSE_HELP" )

	def eidolonQueryHelp( self, objectID ):
		"""
		ָ����ѯ
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_HELP_SEARCH", "" )

	def eidolonLevelHelp( self, objectID ):
		"""
		�ȼ�����
		"""
		try:
			entity = BigWorld.entities[objectID]
		except KeyError:
			ERROR_MSG( "The NPC %s has not exist " % objectID )
			return
		ECenter.fireEvent( "EVT_ON_TOGGLE_HELP_WINDOW" )

	def set_vip( self, oldValue ):
		"""
		"""
		pass

	def onEidolonLeaveWorld( self ) :
		"""
		��ҵ�С������ʧʱ֪ͨ���ˣ��Ƕ��巽����
		"""
		pass
		
	def onWithdrawEidolon( self ) :
		"""
		�ջ�С���飬��������
		"""
		soundMgr.play2DSound( "xitongyuyin/xt_xiaojingling01" )

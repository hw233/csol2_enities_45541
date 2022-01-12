# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import Const

NEXT_CONTENT			= 999				#��һ�����ݵ�timerArg

WAIT 					= 10				#�ȴ�һ��ˢ��
END_WAIT 				= 60				#1���Ӻ��뿪����
"""
�� CopyContent�� �������Ǹ�����һ�����ݡ�

����Ѹ�����ɷֳɶ������ݡ�

��Щ���ݣ�����˳��һ������ִ�У��򸱱���ɡ�

"""

class CopyContent:
	"""
	��������
	"""
	def __init__( self ):
		"""
		"""
		self.key = ""												#һ�����ݹ����� ��ʱ ���Ե� "key"
		self.val = 0												#��ʱ������Ҫ�ﵽ val ��ֵ��������ݲŽ�����
	
	def beginContent( self, spaceEntity ):
		"""
		���ݿ�ʼ
		"""
		pass
	
	def onContent( self, spaceEntity ):
		"""
		����ִ��
		"""
		pass
	
	def doContent( self, spaceEntity ):
		"""
		"""
		self.beginContent( spaceEntity )
		self.onContent( spaceEntity )
	
	def onConditionChange( self, spaceEntity, params ):
		"""
		һ�����������仯��֪ͨ����
		"""
		if not self.doConditionChange( spaceEntity, params ):
			return
		keyVal = spaceEntity.queryTemp( self.key, 0 )
		keyVal += 1
		spaceEntity.setTemp( self.key, keyVal )
		if keyVal >= self.val:
			self.endContent( spaceEntity )
	
	def doConditionChange(  self, spaceEntity, params ):
		"""
		���������д���
		"""
		return True

	def endContent( self, spaceEntity ):
		"""
		���ݽ���
		"""
		spaceEntity.getScript().doNextContent( spaceEntity )
	
	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ����
		"""
		pass
	
	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		�����ڼ䣬��ɫ�뿪
		"""
		pass
	
	def onTeleportReady( self, spaceEntity, baseMailbox ):
		"""
		�����ڼ䣬��ɫ�������client��ͼ�������,���Կ�ʼ��Ϸ���ݷ������������
		"""
		pass


	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == NEXT_CONTENT:
			spaceEntity.getScript().onConditionChange( spaceEntity, { "reason": "timeOver" } )
		
		
		elif userArg == Const.SPACE_TIMER_ARG_CLOSE:
			spaceEntity.base.closeSpace( True )
			
		elif userArg == Const.SPACE_TIMER_ARG_KICK:
			spaceEntity.getScript().kickAllPlayer( spaceEntity )



class CCKickPlayersProcess( CopyContent ):
	"""
	#�����и�������߳�ȥ,��������
	"""
	def __init__( self ):
		"""
		"""
		self.key = "closeProcess"
		self.val = 0
	
	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.gotoForetime()
				
		spaceEntity.addTimer( 10, 0, Const.SPACE_TIMER_ARG_CLOSE )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		���������д���
		"""
		return False


class CCWait( CopyContent ):
	"""
	#�ȴ�
	"""
	def __init__( self ):
		"""
		"""
		self.key = "wait"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		"""
		spaceEntity.addTimer( WAIT, 0, NEXT_CONTENT )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		���������д���
		"""
		return "reason" in params and params["reason"] == "timeOver"


class CCEndWait( CopyContent ):
	"""
	#�ȴ�
	"""
	def __init__( self ):
		"""
		"""
		self.key = "endWait"
		self.val = 1
	
	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_WILL_BE_CLOSED, "" )
		spaceEntity.addTimer( END_WAIT, 0, NEXT_CONTENT )

	def doConditionChange(  self, spaceEntity, params ):
		"""
		���������д���
		"""
		return "reason" in params and params["reason"] == "timeOver"
# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus
import Const

class SpaceCopyExpMelee( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.addTimer( 2400, 0, 2400 )		# �����Ҷ�������40min���Զ��ر�

	def onOverMelee( self ):
		"""
		define method.
		֪ͨ�����
		"""
		self.getScript().onOverMelee( self, False )

	def onMeleeMsg( self, timeVal ):
		"""
		define method.
		֪ͨ�����
		"""
		if timeVal == 300: # 5����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 5 )
		elif timeVal == 240: # 4����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 4 )
		elif timeVal == 180: # 3����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 3 )
		elif timeVal == 120: # 2����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 2 )
		elif timeVal == 60: # 1����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE1, 1 )
		elif timeVal < 60: # 30���Ժ�
			self.getScript().statusMessageAllPlayer( self, 	csstatus.EXP_MELEE_ALERT_CLOSE2, timeVal )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if cbID == 2400:
			self.addTimer( 60, 0, 4*60 )
		elif cbID == 4*60:
			self.onMeleeMsg( 4*60 )
			self.addTimer( 60, 0, 3*60 )
			return
		elif cbID == 3*60:
			self.onMeleeMsg( 3*60 )
			self.addTimer( 60, 0, 2*60 )
			return
		elif cbID == 2*60:
			self.onMeleeMsg( 2*60 )
			self.addTimer( 60, 0, 1*60 )
			return
		elif cbID == 1*60:
			self.onMeleeMsg( 60 )
			self.addTimer( 30, 0, 30 )
			return
		elif cbID == 30:
			self.onMeleeMsg( 30 )
			self.addTimer( 10, 0, 10 )
			return
		elif cbID <= 0:
			self.onOverMelee()
			return
		elif cbID <= 10:
			self.onMeleeMsg( cbID )
			self.addTimer( 1, 0, cbID - 1 )
			return
		# �ű���onTimer
		SpaceCopy.onTimer( self, timerID, cbID )

	def setLeaveTeamPlayerMB( self, baseMailbox ):
		"""
		define method
		"""
		self.setTemp( 'leavePMB', baseMailbox )
	
	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
		]
		"""
		# ��ʾʣ�����Σ�ʣ��BOSS��ʣ��ʱ�䡣
		return [ 0, 2, 3 ]
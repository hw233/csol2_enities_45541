# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus

class SpaceCopyProtectTong( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		
	def onProtectTongEnd( self ):
		"""
		define method.
		֪ͨ�����
		"""
		self.getScript().onProtectTongEnd( self, False )
	
	def onTeamDismiss( self ):
		"""
		define method.
		���鱻��ɢ
		"""
		self.setTemp( "destroyTimer", self.addTimer( 10, 0, 0  ) )
		self.getScript().statusMessageAllPlayer( self, csstatus.PROTECT_TONG_OVER1 )
		
	def onProtectTongMsg( self, timeVal ):
		"""
		define method.
		֪ͨ�����
		"""
		if timeVal == 300: # 5����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 5 )
		elif timeVal == 240: # 4����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 4 )
		elif timeVal == 180: # 3����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 3 )
		elif timeVal == 120: # 2����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 2 )
		elif timeVal == 60: # 1����
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE1, 1 )	
		elif timeVal < 60: # 30���Ժ�
			self.getScript().statusMessageAllPlayer( self, 	csstatus.POTENTIAL_MELEE_ALERT_CLOSE2, timeVal )

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
		# ��ʾʣ��С�֣�ʣ��BOSS�� 
		return [ 1, 3 ]
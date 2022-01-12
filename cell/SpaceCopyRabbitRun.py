# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10.0						#���ȫ���뿪�����󣬸���ø�����ɾ��

class SpaceCopyRabbitRun( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
	
	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method
		"""
		if not self.queryTemp( "firstEnter", False ):
			self.setTemp( "firstEnter", True )
		SpaceCopy.onEnterCommon( self, baseMailbox, params )

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
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
			8: �m؅Ѫ���ٷֱ�
		]
		"""
		# ��ʾʣ��С�֣�ʣ��BOSS�� 
		return [ 1, 3 ]

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )


	def onTimer( self, id, userArg ):
		"""
		���ǵײ��onTimer()�������
		"""
		SpaceCopy.onTimer( self, id, userArg )



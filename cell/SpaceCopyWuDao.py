# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus

IS_ENTER_TIME			= 1   # ��ǽ����ж��Ƿ���ڶ���
CLOSE_WUDAO_TIME		= 2   # ��ǹر�������
CLOSE_COPY				= 3	  # ��ǹرո���
CLOSE_WUDAO				= 4   # �ر�������

class SpaceCopyWuDao( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )
		
		self.hasClearNoFight = False		# ����Ƿ��Ѿ��������ɫ����սЧ��
		self.addTimer( csconst.WUDAO_TIME_PREPARE * 60, 0, IS_ENTER_TIME )
		self.addTimer( csconst.WUDAO_TIME_SPACE_LIVING * 60, 0, CLOSE_WUDAO_TIME )
		
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == IS_ENTER_TIME: # ׼��ʱ����󣬲鿴�Ƿ��ж���	
			if len( self.databaseIDList ) == 1 and len( self._players ) == 1: # ���û�ж��ֲ����ڸ����У�ֱ�ӻ�ʤ
				self._players[0].client.onStatusMessage( csstatus.WU_DAO_ENEMY_NOT_ENTER, "" )
				self._players[0].onWuDaoOver( self._players[0], 1 ) # ֪ͨ���������������ʤ��
				self.getScript().closeWuDao( self ) # �ر�������
				return
				
			self.getScript().clearNoFight( self )

		elif userArg == CLOSE_WUDAO_TIME: # �ر�������
			if len(self._players) == 1:
				self._players[0].client.onStatusMessage( csstatus.WU_DAO_WIN, "" )
				self._players[0].onWuDaoOver( self._players[0], 1 ) # ֪ͨ���������������ʤ��
			else:
				for e in self._players:
					e.client.onStatusMessage( csstatus.WU_DAO_DRAW, "" )
					e.onWuDaoOver( e, 0 ) # ֪ͨ�������������ʧ�ܷ�
			self.getScript().closeWuDao( self )
			return

		elif userArg == CLOSE_COPY:
			self.base.closeSpace( True )

		elif userArg == CLOSE_WUDAO:
			self.getScript().closeWuDao( self )
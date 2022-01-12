# -*- coding: gb18030 -*-
#
# ���ǳ������ 2009-01-16 SongPeifang

from QuestBox import QuestBox


class QuestShellBox( QuestBox ) :
	"""
	���ǳ��������
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
		if self.isShow == 0 or self.isShow == None:
			self.addFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
			self.setTemp( "quest_box_destroyed", 1 )
		
	def spawnShell( self ):
		"""
		Define method.
		�ñ���ˢ����
		"""
		self.removeFlag( 0 )	# ����ר�ã����ܻ���FLAG_*��ͻ�������û������ԭ��Ӧ��û������
		self.removeFlag( 1 )	# ����ڲ����صĳ��������Ϊ��ʹ�ͻ����ܵõ�����
		self.removeTemp( "quest_box_destroyed" )


	def isMoving( self ):
		"""
		�ж�entity��ǰ�Ƿ������ƶ���

		@return: BOOL
		@rtype:  BOOL
		"""
		return False

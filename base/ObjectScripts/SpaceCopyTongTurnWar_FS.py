# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyTongTurnWar_FS( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.left_watchPoint = None
		self.left_fightPoint = None
		self.right_watchPoint = None
		self.ritht_fightPoint = None

	def load( self, section ):
		"""
		�������м�������

		@type section : PyDataSection
		@param section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		
		spaceData = section[ "Space" ]
		
		# ����1����λ��
		self.left_watchPoint = eval( spaceData[ "leftTeam_watchPoint" ].asString )
		self.left_fightPoint = eval( spaceData[ "leftTeam_fightPoint" ].asString )
		
		# ����2����λ��
		self.right_watchPoint = eval( spaceData[ "rightTeam_watchPoint" ].asString )
		self.right_fightPoint = eval( spaceData[ "rightTeam_fightPoint" ].asString )
		
		# ս�ܹ�ս��
		self.loser_watchPoint = eval( spaceData[ "loser_watchPoint" ].asString )
		self.centerPoint = eval( spaceData[ "centerPoint" ].asString )
	
	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'databaseID' : entity.databaseID, "teamID": entity.teamID, "spaceKey":entity.teamID }

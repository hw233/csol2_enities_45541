# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyTongTurnWar( SpaceCopy ):
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
		self.left_watchPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_watchPoint" ].asString.split() ] )
		self.left_fightPoint = tuple( [ float(x) for x in spaceData[ "leftTeam_fightPoint" ].asString.split() ] )
		
		# ����2����λ��
		self.right_watchPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_watchPoint" ].asString.split() ] )
		self.right_fightPoint = tuple( [ float(x) for x in spaceData[ "rightTeam_fightPoint" ].asString.split() ] )
		self.loser_watchPoint = tuple( [ float(x) for x in spaceData[ "loser_watchPoint" ].asString.split() ] )
	
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

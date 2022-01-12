# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy

class SpaceCopyYXLMPVP( SpaceCopy ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
	
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
		d = { 'dbID' : entity.databaseID }
		d["teamID"] = entity.teamID		# ȡ������ʱ�Ķ���ID���������ֵ��Ϊ0��
		d["spaceKey"] = entity.teamID
		# ע�������Ժ���ܻ���Ҫȡ���ѵ�dbid�������ڻ�û����Ҫ��ô���������ʱ����ע��
		return d
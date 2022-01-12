# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps

class SpaceCopyMapsTeam( SpaceCopyMaps ):
	"""
	���ͼ��Ӹ����ű�
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopyMaps.__init__( self )

	def packedDomainData( self, entity ):
		"""
		virtual method.
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		d = SpaceCopyMaps.packedDomainData( self, entity )
		d["teamID"] = entity.teamID
		return d
# -*-coding: gb18030 -*-
#
#
"""
14:38 2008-9-12,by wangshufeng
"""
"""
2010.11
������̨��ֲΪ�����̨ by cxm
"""
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy


class SpaceCopyTongAba( SpaceCopy ):
	"""
	��̨�������ռ�ȫ��ʵ���ű�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		self.right_playerEnterPoint = ()	# ��̨������right�������
		self.left_playerEnterPoint = ()		# ��̨������left�������
		self.right_chapmanPoint = ()		# ( position, direction )��right�����˵�λ��
		self.left_chapmanPoint = ()			# ( position, direction )��left�����˵�λ��
		self.left_relivePoints = []			# left�������
		self.right_relivePoints = []		# right�������
		
		
	def load( self, section ):
		"""
		�������м�������
		
		@type section : PyDataSection
		@param section : python data section load from npc's config file
		"""
		SpaceCopy.load( self, section )
		
		# right�������
		data = section[ "Space" ][ "right_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.right_playerEnterPoint = ( pos, direction )
		data = section[ "Space" ][ "left_playerEnterPoint" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		self.left_playerEnterPoint = ( pos, direction )
		
		
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
		return { 'tongDBID' : entity.cellData[ "tong_dbID" ] }
		
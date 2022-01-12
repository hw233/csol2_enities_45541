# -*- coding: gb18030 -*-
#
#$Id:$

"""
14:23 2008-9-11,by wangshufeng
"""
"""
2010.11
������̨��ֲΪ�����̨ by cxm
"""
import BigWorld
from bwdebug import *
import time

import csdefine
import csconst
import csstatus

from SpaceCopy import SpaceCopy



class SpaceCopyTongAba( SpaceCopy ):
	"""
	�����̨�������ռ�
	"""
	def __init__( self ):
		"""
		"""
		SpaceCopy.__init__( self )
		
		
	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'tongDBID' : entity.tong_dbID }
		
		
	def checkDomainIntoEnable( self, entity ):
		"""
		��cell�ϼ��ÿռ���������
		"""
		return csstatus.SPACE_OK
		
	def receiveAbaData( self, round, startTime ):
		"""
		Define method.
		������̨������
		
		@param round : �����̨�����ִ�
		@param startTime : ���ֿ�ʼʱ��
		"""
		DEBUG_MSG( "--------->>>round, startTime", round, startTime )
		self.abaRound = round
		self.abaStartTime = startTime
		if self.abaRound == csdefine.ABATTOIR_EIGHTHFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_QUARTERFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_SEMIFINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 15 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		elif self.abaRound == csdefine.ABATTOIR_FINAL:
			self.setTemp( "tongAbaOverTimer", self.addTimer( 20 * 60 - self.getAbaTimeInfo(), 0, 1 ) )
		
	def getAbaTimeInfo( self ):
		"""
		return �����Ѿ���ʼ�˶೤ʱ��
		"""
		return BigWorld.time() - self.abaStartTime
	
	def getAbaRound( self ):
		return self.abaRound
		
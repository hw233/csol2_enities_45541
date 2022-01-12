# -*- coding: gb18030 -*-

# ���帱��raid��¼�Ľӿڣ�by ganjinxing
from bwdebug import INFO_MSG
from BaseSpaceCopyFormulas import spaceCopyFormulas


class SpaceCopyRaidRecordInterface :

	def __init__( self ) :
		self.bossesTotal = spaceCopyFormulas.totalBossesOf( self.className )	# boss����
		self.bossesKilled = 0						# boss�ѻ�ɱ����
		self.isRaidFinish = False					# �����Ƿ��Ѿ����

	def queryBossesKilled( self, querist, userData ) :
		"""
		<Define method>
		��ѯboss�Ļ�ɱ����
		@type	querist : BASE MAILBOX
		@param	querist : ��ѯ�ߣ�������ж��巽��onQueryBossesKilledCallback
		@type	userData : INT32
		@param	userData : ��ѯ�߻ص�������
		"""
		querist.onQueryBossesKilledCallback( userData, self.bossesKilled )

	def setBossesTotal( self, bossesTotal ) :
		"""
		"""
		self.bossesTotal = bossesTotal

	def incBossesKilled( self ) :
		"""
		<Define method>
		����boss��ɱ��¼
		"""
		self.bossesKilled = min( self.bossesKilled + 1, self.bossesTotal )

	def decBossesKilled( self ) :
		"""
		����boss��ɱ��¼
		"""
		self.bossesKilled = max( self.bossesKilled - 1, 0 )

	def setRaidFinish( self, finish ) :
		"""
		<Define method>
		���ø���Raid��ɱ��
		@type	finish : BOOL
		@param	finish : �����Ƿ��Ѵ���
		"""
		self.isRaidFinish = finish
		if finish and self.domainMB :
			self.domainMB.notifyTeamRaidFinished( self.spaceNumber )

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		��ҽ����˿ռ䣬��Ҫ���ݸ���boss�Ļ�ɱ����������
		��Ӧ����ʾ���������ѡ���Ǽ������������뿪������
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onEnterʱ��һЩ�������
		@type params: py_dict
		"""
		baseMailbox.cell.onEnterMatchedCopy( self.className, self.bossesKilled )

	def onLeave( self, baseMailbox, params ):
		"""
		define method.
		����뿪�ռ�
		@param baseMailbox: ���mailbox
		@type baseMailbox: mailbox
		@param params: ���onLeaveʱ��һЩ�������
		@type params: py_dict
		"""
		pass

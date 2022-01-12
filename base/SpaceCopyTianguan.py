# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

MIN_TEAM_MEMBER_COUNT	= 3

class SpaceCopyTianguan( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnMonstersList = {}


	def addSpawnPointTianguan( self, spawnMailBox, grade, teamcount ):
		"""
		define method
		�ռ������һ��ˢ�ֵ�
		"""
		key = str(grade) + "and" +  str(teamcount)
		if not self.spawnMonstersList.has_key( key ):
			self.spawnMonstersList[key] = [spawnMailBox]
		else:
			self.spawnMonstersList[key].append( spawnMailBox )


	def spawnMonsters( self, params ):
		"""
		define method
		"""
		tc = params["teamcount"]
		if tc < 3:
			tc = 3
		for i in xrange( MIN_TEAM_MEMBER_COUNT, tc + 1 ):
			key = str(params["grade"]) + "and" +  str(i)
			if not key in self.spawnMonstersList:
				continue
			for j in self.spawnMonstersList[key]:
				d = {}
				d[ "tianguan_level" ] = params["copyLevel"]
				d[ "current_toll_gate" ] = params["grade"]
				j.cell.createEntity( d )

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
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

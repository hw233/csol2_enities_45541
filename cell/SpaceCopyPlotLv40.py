# -*- coding: gb18030 -*-

# 40 �����鸱��
# by ganjinxing

# bigworld
import BigWorld
# common
import csdefine
from bwdebug import *
# cell
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory


class SpaceCopyPlotLv40( SpaceCopy ) :

	def __init__( self ):
		SpaceCopy.__init__( self )
		self._bt_killCommit = False								# ������������ֹ�ظ����ɱ��( ������������صı��� ) bt == ���죨 bu tian ��
		self._bt_killDict = {}									# �����ѻ�ɱ���������( ������������صı��� )
		self._bt_spawnDict = {}									# �����Ѵ������������( ������������صı��� )
		self._bt_normalTimerID = 0								# ˢ��ͨ�ֵ�TimerID( ������������صı��� )
		self._bt_specialTimerID = 0								# ˢ����ֵ�TimerID( ������������صı��� )
		self._bt_normalSpawnCounter = 20						# ��ͨ��20���ʼˢ����֮����εݼ�2��ˢ�������ʹ��һ������������¼
		self.monsterPositions = []
		self.startTime = []
		self.intervalTime = []
		self.monsterNumLists = []
		self.monsterIDLists = []
		self._bt_monsterTimerIDList = []
		self._bt_monsterDict = {}

	def onEnterCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnterCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s enter copy plot lv40." % entity.getName() )
		else :
			INFO_MSG( "Something enter copy plot lv40." )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		define method.
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		entity = BigWorld.entities.get( baseMailbox.id, None )
		if entity :
			INFO_MSG( "%s leave copy plot lv40." % entity.getName() )
		else :
			INFO_MSG( "Something leave copy plot lv40." )

	# ----------------------------------------------------------------
	# ������������صķ���
	# ----------------------------------------------------------------
	def bt_initSpawningMonsters( self ) :
		"""
		ˢ��ǰ׼��
		"""
		self._bt_killCommit = False							# ���û�ɱ��ɱ��
		self._bt_killDict.clear()								# ����ɱ�ּ���
		self._bt_spawnDict.clear()								# ����ˢ�ּ�¼
		self._bt_normalSpawnCounter = 20						# ������ͨˢ�ֵļ�����

	def bt_addNormalSpawnTimer( self, userData=0 ) :
		"""
		ˢ��ͨ���ÿ�μ���2��ˢ��ʱ��
		"""
		self._bt_normalSpawnCounter = max( 6, self._bt_normalSpawnCounter )
		self._bt_normalTimerID = self.addTimer( self._bt_normalSpawnCounter, 0.0, userData )
		self._bt_normalSpawnCounter -= 2

	def bt_addSpecialSpawnTimer( self, userData=0 ) :
		"""
		ˢ������ǰһ������20���ˢ��һ������script�п���
		"""
		self._bt_specialTimerID = self.addTimer( 20, 0.0, userData )

	def bt_stopSpawnTimer( self ) :
		"""
		ֹͣˢ�ֵ�Timer
		"""
		#self.cancel( self._bt_normalTimerID )
		#self.cancel( self._bt_specialTimerID )
		for monsterTimerID in self._bt_monsterTimerIDList:
			self.cancel( monsterTimerID )

	def bt_spawnMonsters( self, enemyID, className, pos, amount = 1 ) :
		"""
		"""
		recorder = self._bt_spawnDict.get( className )
		if recorder is None :
			recorder = []
			self._bt_spawnDict[className] = recorder
		while amount > 0 :
			amount -= 1
			monster = g_objFactory.getObject( className ).createEntity( self.spaceID,\
				pos[amount], (0,0,0), { "spawnPos" : pos[amount] } )
			monster.changeAttackTarget( enemyID )
			recorder.append( monster.id )

	def bt_getMonsterSpawned( self, className ) :
		"""
		��ȡ�����Ĺ�������
		"""
		return len( self._bt_spawnDict.get( className, [] ) )

	# -------------------------------------------------
	def bt_getMonsterKilled( self, className ) :
		"""
		��ȡĳ������ĵ�ǰ��ɱ����
		"""
		return self._bt_killDict.get( className, 0 )

	def bt_onMonsterKilled( self, className ) :
		"""
		ĳ�����ﱻɱ����֪ͨ����
		"""
		self._bt_killDict[className] = self._bt_killDict.get( className, 0 ) + 1

	def bt_isKillCommitted( self ) :
		"""
		��ɱ�Ƿ��Ѿ����
		"""
		return self._bt_killCommit

	def bt_commitKill( self ) :
		"""
		��ǵ�ǰΪ��ɱ���״̬
		"""
		self._bt_killCommit = True

	# -------------------------------------------------
	def bt_destroyMonsters( self ) :
		"""
		��������ˢ�����Ĺ���
		"""
		for monsters in self._bt_spawnDict.itervalues() :
			for m_id in monsters :
				monster = BigWorld.entities.get( m_id )
				if monster : monster.destroy()

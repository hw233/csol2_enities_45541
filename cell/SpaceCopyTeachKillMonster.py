# -*- coding:gb18030 -*-

from SpaceCopy import SpaceCopy
from bwdebug import *
import BigWorld
import Const

class SpaceCopyTeachKillMonster( SpaceCopy ):
	"""
	"""
	def bossDead( self, spawnPointBaseMB ):
		"""
		Define method.
		boss�ҵ���
		"""
		bossCount = self.queryTemp( "bossCount" )
		if bossCount > 0:
			self.setTemp( "bossCount", bossCount - 1  )
			spawnPointBaseMB.cell.createEntity()
		else:	# ���ɴ�����
			self.getScript().createDoor( self )
			#door = BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 0), {} )
			#if otherDict.has_key( 'modelScale' ) and otherDict[ 'modelScale' ] != 0.0:
			#	door.modelScale = otherDict[ 'modelScale' ]
			
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
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def showDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
		]
		"""
		return [ 0, 1 ]
		
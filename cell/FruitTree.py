# -*- coding: gb18030 -*-
#
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.NPCQuestDroppedItemLoader import NPCQuestDroppedItemLoader
from NPCObject import NPCObject
import csdefine
import csstatus
import random
import BigWorld
import items
import csconst
import ItemSystemExp
import ECBExtend
import time

from config.item.FruitItems import Datas as FruitItemsDatas
GROWING_TIME_VALUE = 600
FRUIT_TREE_TIME = 60

class FruitTree( NPCObject ):
	"""
	��������
	"""
	
	def __init__(self):
		"""
		@summary:	��ʼ��
		"""
		NPCObject.__init__( self )
		self.growingTime = GROWING_TIME_VALUE
		if self.fruitseedID in FruitItemsDatas.keys():
			self.growingTime = FruitItemsDatas.get( self.fruitseedID ).get( "time" )
		self.setEntityType( csdefine.ENTITY_TYPE_FRUITTREE )
		self.addTimer( self.growingTime, 0, ECBExtend.FRUITTREE_GROWTH_CBID )
		self.plantingTime = time.time()

	def onFruitTreeGrowth( self, timerID, cbID ):
		"""
		��������timer�ص�
		��Ȼ����
		"""
		self.ripe()
		self.planesAllClients( "onReceiveRipeNotice", ( csdefine.FRUIT_TREE_RIPE_NORMAL, ) )

	def onFruitTreeDie( self, timerID, cbID ):
		"""
		��������timer�ص�
		"""
		self.destroy()

	def onRipe( self ):
		"""
		Define Method
		��ʩ��˲�����
		"""
		self.ripe()
		self.planesAllClients( "onReceiveRipeNotice", ( csdefine.FRUIT_TREE_RIPE_FAST, ) )

	def ripe( self ):
		"""
		��������
		"""
		self.isRipe = True
		self.addTimer( FRUIT_TREE_TIME, 0, ECBExtend.FRUITTREE_DIE_CBID )

	def requestData( self, srcEntityID ):
		"""
		Exposed Method
		"""
		player = BigWorld.entities.get( srcEntityID, None )
		if player is None: return
		if self.isRipe:
			lastTime = 0
		else:
			currTime = time.time()
			lastTime = self.growingTime + self.plantingTime - currTime
			if lastTime <= 0: lastTime = 0
		player.clientEntity( self.id ).onReceiveData( self.modelNumber, self.planterName, self.fruitseedID, lastTime )

	def onPick( self, pickerDBID ):
		"""
		Define Method
		���ɼ�
		"""
		self.pickerDBID = pickerDBID
		self.destroy()

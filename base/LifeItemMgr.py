# -*- coding: gb18030 -*-

import time
import random

import BigWorld
from bwdebug import *

# ��������Ʒ���ʱ����
LIFE_ITEM_TIME_INTERVAL = 1.0

class LifeItemMgr( BigWorld.Base ):
	"""
	����������Ʒ������
	"""

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.datas = []
		self.uidMapMailBox = {}

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "LifeItemMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register LifeItemMgr Fail!" )
			# again
			self.registerGlobally( "LifeItemMgr", self._onRegisterManager )
		else:
			# ע�ᵽ���еķ�������
			BigWorld.globalData["LifeItemMgr"] = self
			INFO_MSG("LifeItemMgr Create Complete!")
			self.addTimer( 0, LIFE_ITEM_TIME_INTERVAL, 0 )

	def onTimer( self, id, userData ):
		"""
		��ʱ������
		"""
		nowTime = time.time()

		for lifeTime, uid in self.datas[:]:
			if lifeTime <= nowTime:
				self.datas.remove( ( lifeTime, uid ) )
				baseMailBox = self.uidMapMailBox.get( uid )
				if baseMailBox: baseMailBox.cell.onItemLifeOver( uid )
			else:
				break

	def addItems( self, baseMailBox, uids, lifeTimes ):
		"""
		Define method
		���һϵ����Ʒ����������
		"""
		for uid, lifeTime in zip( uids, lifeTimes ):
			index = self.getIndex( lifeTime )
			self.datas.insert( index, ( lifeTime, uid ) )
			self.uidMapMailBox[uid] = baseMailBox

	def removeItems( self, baseMailBox, uids, lifeTimes ):
		"""
		Define method
		�ӹ��������Ƴ�һϵ����Ʒ
		"""
		for uid, lifeTime in zip( uids, lifeTimes ):
			data = ( lifeTime, uid )
			if data in self.datas:
				self.datas.remove( data )
			if uid in self.uidMapMailBox:
				self.uidMapMailBox.pop( uid )

	def getIndex( self, lifeTime ):
		"""
		�����з�ԭ�����lifeTime�ٽ�����������֤�б�˳������
		"""

		count = len( self.datas )
		if count == 0: return 0

		if lifeTime <= self.datas[0][0]: return 0
		if lifeTime >= self.datas[-1][0]: return count

		startIndex = 0
		middleIndex = count/2
		endIndex = count - 1

		while 1:
			if ( endIndex - startIndex ) <= 1:
				return endIndex
			mValue = self.datas[middleIndex][0]
			if mValue == lifeTime:
				return middleIndex
			elif mValue < lifeTime:
				startIndex = middleIndex
				middleIndex = middleIndex + ( endIndex - middleIndex )/2
			else:
				endIndex = middleIndex
				middleIndex = middleIndex - ( middleIndex - startIndex )/2

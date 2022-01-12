#-*- coding:gb18030 -*-
import BigWorld
import Love3
from fishingJoy.FishRoom import FishRoom
from fishingJoy.Fisher import Fisher
from fishingJoy.FishingJoyTimerProvider import FishingJoyTimerProvider
from bwdebug import *

class FishingJoyMgr( FishingJoyTimerProvider, BigWorld.Base ):
	"""
	ȫ�ֵĲ����������
	
	1�������Ŀ�����رգ�
	2��������ά�����㷿�䣻
	3��timer�����ṩ�ߣ�
	4��ά�����벶���������ݣ�
	5������벶�㷿��֮���ͨѶ������
	"""
	def __init__( self ):
		FishingJoyTimerProvider.__init__( self )
		BigWorld.Base.__init__( self )
		self.fishRooms = {}
		self.isOpen = False
		self.fishers = {}				# ���ڲ��벶������
		BigWorld.globalData["FishingJoyMgr"] = self
		
	def start( self ):
		self.isOpen = True
	
	def close( self ):
		self.isOpen = False
		
	def isOpen( self ):
		return self.isOpen
		
	def canJoin( self, playerName ):
		"""
		��֤������Ƿ���Բ��벶��
		0�������Ƿ���
		1�����������Ƿ��Ѵ�����
		2������Ƿ��Ѿ��ڲ�����
		3�������������...
		"""
		if not self.isOpen():
			INFO_MSG( "fish has not open." )
			return False
		if self.fishers.has_key( playerName ):
			WARNNING_MSG( "player( %s ) request dumplicated." % playerName )
			return False
		return True
		
	def findFishingRoom( self, roomID ):
		if not self.fishRooms.has_key( roomID ):
			self.fishRooms[roomID] = FishRoom( self, roomID )
		return self.fishRooms[roomID]
		
	def enterRoom( self, playerName, playerBase, roomID ):
		"""
		Define method.
		���ѡ�����俪ʼ���㣬�����ǽ��벶��space��
		�����Ҫ���ḻ�ı�������Ҫ����������Ϣ������ȫ��֪ͨ����ҡ������ɹ�����һ������衱��
		
		@param roomID : SPACE_ID,���һ��space��Ӧһ��room����ô����һ��space id���������һ������Ψһ��ʶ���㷿��ı�ţ��˱�ſ��Ա����ѡ��
		"""
		if self.fishers.has_key( playerBase.id ):
			HACK_MSG( "player( %s ) had already been joined." % ( playerName ) )
			return
		
		fishRoom = self.findFishingRoom( roomID )
		fisher = Fisher( playerName, playerBase, fishRoom )
		self.fishers[playerBase.id] = fisher
		fishRoom.enter( fisher )
		
	def fisherHit( self, playerID, bulletNumber, positionTuple ):
		"""
		define mehtod.
		�����ĳ��λ�÷����ڵ�����Ҫ֪ͨ������ҿͻ��ˡ�
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		fisher = self.fishers[playerID]
		fisher.getRoom().fisherHit( playerID, bulletNumber, positionTuple )
		
	def fisherHitFish( self, playerID, bulletNumber, bulletType, magnification, fishNumbers ):
		"""
		define mehtod.
		���������һЩ�㡣
		
		@param magnification : �˴λ��еı���
		@Param fishNumbers : array of int32
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
			
		fisher = self.fishers[playerID]
		fisher.getRoom().hitFishes( fisher, bulletNumber, bulletType, magnification, fishNumbers )
		
	def leaveRoom( self, playerID ):
		"""
		Define method.
		����뿪����
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		fisher = self.fishers.pop( playerID )
		fishRoom = fisher.getRoom()
		fishRoom.leave( fisher )
		if fishRoom.isEmpty():
			self.fishRooms.pop( fishRoom.getID() ).destroy()
			
	def fisherChangeBullet( self, playerID, bulletType ):
		"""
		Define method.
		��Ҹı���ʹ�õ��ڵ�����
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].changeBullet( bulletType )
		
	def fisherUseItem( self, playerID ):
		"""
		Define method.
		���ʹ������Ʒ
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].useItem()
		
	def fisherUseItemOver( self, playerID ):
		"""
		Define method.
		���ʹ������Ʒ
		"""
		if not self.fishers.has_key( playerID ):
			HACK_MSG( "cant find player( %i )." % ( playerID ) )
			return
		self.fishers[playerID].useItemOver()
		
	def onTimer( self, timerID, useArg ):
		FishingJoyTimerProvider.onTimer( self, timerID, useArg )
		
		
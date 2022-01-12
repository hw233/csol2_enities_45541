# -*- coding:gb18030 -*-

import Love3
import random

from bwdebug import *


class FishRoom:
	def __init__( self, fisingJoyMgr, roomID ):
		self.fisingJoyMgr = fisingJoyMgr
		self.id = roomID
		self.fishers = []
		self.fishes = {}					# like as { fishNumber:fish, ... }��һ������fish�Ͳ������٣�ѭ�����ã�ֻ��������뿪ʱ��������Ӧ��Ŀ��fish
		self.currentNum = 0
		self.isCatchingSeason = False
		self.fishSpecies = Love3.g_fishingJoyLoader.generateSpecies( self )		# ��������͹���

	def getID( self ):
		return self.id

	def getFishers( self ):
		return self.fishers

	def getFisherCount( self ):
		return len( self.fishers )

	def catchingSeason( self ):
		return self.isCatchingSeason

	def getFishingJoyMgr( self ):
		return self.fisingJoyMgr

	def enter( self, newFisher ):
		"""
		�����+1����Ӧ�����������
		"""
		fishes = []
		for number, fish in self.fishes.iteritems():
			fishes.append( fish )
		newFisher.fishBorn( fishes )
		self.fishers.append( newFisher )
		for fishSpecies in self.fishSpecies:
			fishSpecies.onFisherEnter( newFisher )
		# �����˵��ڵ�����֪ͨ�½���������
		for fisher in self.fishers:
			if fisher is not newFisher:
				newFisher.otherFisherChangeBulletType(fisher.id, fisher.bulletType)

	def leave( self, fisher ):
		"""
		����뿪���䡣
		"""
		self.fishers.remove( fisher )
		fisher.leaveRoom()
		DEBUG_MSG( "fisher( %s ) have been leave." % fisher.getName() )

	def isEmpty( self ):
		return len( self.fishers ) == 0

	def destroy( self ):
		for fishSpecies in self.fishSpecies:
			fishSpecies.destroy()

	def fishBorn( self, fish ):
		number = fish.getNumber()
		self.fishes[number] = fish
		for fisher in self.fishers:
			fisher.fishBorn( [ fish ] )

	def fishBornBatch( self, fishAndPathList ):
		"""
		�������������������¸�fisher
		"""
		fishes = []
		for fish in fishAndPathList:
			self.fishes[fish.getNumber()] = fish
			fishes.append( fish )
		for fisher in self.fishers:
			fisher.fishBorn( fishes )

	def newNumber( self ):
		"""
		����һ���µ�fish���
		fish�������ǳ��죬��0x7FFFFFFF��ֵ�ռ���fish��Ų����ظ���
		"""
		self.currentNum = ( self.currentNum + 1 ) % 0x7FFFFFFF
		return self.currentNum

	def fisherHit( self, playerID, bulletNumber, position ):
		"""
		playerID����ҹ���ĳһ��λ��position
		"""
		for fisher in self.fishers:
			if fisher.getID() != playerID:
				fisher.otherFisherHit( playerID, bulletNumber, position )

	def hitFishes( self, fisher, bulletNumber, bulletType, magnification, fishNumbers ):
		"""
		�ͻ��˼���������м����㣬ʲô���͵��㣬�ͻ��˿���random.shuffle�����˳��

		�������£�
		�羭���жϺ󲶻�ɹ������㱾���������ۼ��ջ��Ƿ�С���ڵ���ֵ�������Ԫ���ڵ����ж�Ԫ����ֵ�ջ��������Ϸ���ڵ���������Ϸ�Ҽ�ֵ�ջ񣩣�
		��С���ڵ���ֵ�����������һ����Ĳ���ɹ����жϣ�����ڵ����ڵ���ֵ�����������������̣�������������㣻
		"""
		earnings = 0
		bullet = Love3.g_fishingJoyLoader.getBullet( bulletType )
		bulletValue = bullet.getValue() * magnification
		dieFishNumbers = []
		for number in fishNumbers:
			fish = self.fishes.get( number, None )
			if fish and fish.isRunning():
				fishValue = bullet.getFishValue( fish )
				# ����ɹ��� = min��0.95��0.8 * �ڵ���ֵ / ��ļ�ֵ��+ ��ʧ������
				rateAmend = bullet.getCaptureRateAmend( fisher, fish )
				if random.random()  <= min( 0.95, 0.8 * bulletValue / fishValue ) + rateAmend:
					DEBUG_MSG( "fisher(%s) use bullet( %i ) in value( %i ) catch fish( %i )." % ( fisher.getName(), bulletType, bulletValue, number ) )
					dieFishNumbers.append( number )
					self.fishes.pop( number ).die( fisher )
					if rateAmend > 0:	# �������ʱ�����ʷ��������ã���ô����fisher����ʧ��
						bullet.resetFisherLoss( fisher )
					earnings += fishValue * magnification
					if bulletValue <= earnings:
						break
			else:
				DEBUG_MSG( "fish( %i ) have been not enable." % number )
		bullet.addFisherEarnings( fisher, earnings, bulletValue )
		DEBUG_MSG( "player( %s ) hit fish result:%s." % ( fisher.getName(), str( dieFishNumbers ) ) )
		for otherFisher in self.fishers:
			otherFisher.fishBeenCaught( fisher.getID(), bulletNumber, dieFishNumbers )

	def swimAway( self, fishNumber ):
		DEBUG_MSG( "fish( %i ) swimAway" % fishNumber )
		del self.fishes[fishNumber]

	def fisherChangeBullet( self, fisherID, bulletType ):
		for fisher in self.fishers:
			if fisher.getID() != fisherID:
				fisher.otherFisherChangeBulletType( fisherID, bulletType )

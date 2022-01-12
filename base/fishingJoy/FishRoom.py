# -*- coding:gb18030 -*-

import Love3
import random

from bwdebug import *


class FishRoom:
	def __init__( self, fisingJoyMgr, roomID ):
		self.fisingJoyMgr = fisingJoyMgr
		self.id = roomID
		self.fishers = []
		self.fishes = {}					# like as { fishNumber:fish, ... }，一旦创建fish就不会销毁，循环利用，只有在玩家离开时才销毁相应数目的fish
		self.currentNum = 0
		self.isCatchingSeason = False
		self.fishSpecies = Love3.g_fishingJoyLoader.generateSpecies( self )		# 把鱼分类型管理

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
		玩家数+1，相应调整鱼的数量
		"""
		fishes = []
		for number, fish in self.fishes.iteritems():
			fishes.append( fish )
		newFisher.fishBorn( fishes )
		self.fishers.append( newFisher )
		for fishSpecies in self.fishSpecies:
			fishSpecies.onFisherEnter( newFisher )
		# 将他人的炮弹类型通知新进房间的玩家
		for fisher in self.fishers:
			if fisher is not newFisher:
				newFisher.otherFisherChangeBulletType(fisher.id, fisher.bulletType)

	def leave( self, fisher ):
		"""
		玩家离开房间。
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
		鱼批量产生，批量更新给fisher
		"""
		fishes = []
		for fish in fishAndPathList:
			self.fishes[fish.getNumber()] = fish
			fishes.append( fish )
		for fisher in self.fishers:
			fisher.fishBorn( fishes )

	def newNumber( self ):
		"""
		产生一个新的fish编号
		fish的消亡非常快，在0x7FFFFFFF数值空间中fish编号不会重复。
		"""
		self.currentNum = ( self.currentNum + 1 ) % 0x7FFFFFFF
		return self.currentNum

	def fisherHit( self, playerID, bulletNumber, position ):
		"""
		playerID的玩家攻击某一个位置position
		"""
		for fisher in self.fishers:
			if fisher.getID() != playerID:
				fisher.otherFisherHit( playerID, bulletNumber, position )

	def hitFishes( self, fisher, bulletNumber, bulletType, magnification, fishNumbers ):
		"""
		客户端计算网里该有几条鱼，什么类型的鱼，客户端可以random.shuffle捕获的顺序。

		规则如下：
		如经过判断后捕获成功，计算本次渔网的累计收获是否小于炮弹价值（如果是元宝炮弹，判断元宝价值收获；如果是游戏币炮弹，计算游戏币价值收获），
		如小于炮弹价值，继续随机下一条鱼的捕获成功率判断，如大于等于炮弹价值，结束本次渔网捕捞，放弃其他鱼计算；
		"""
		earnings = 0
		bullet = Love3.g_fishingJoyLoader.getBullet( bulletType )
		bulletValue = bullet.getValue() * magnification
		dieFishNumbers = []
		for number in fishNumbers:
			fish = self.fishes.get( number, None )
			if fish and fish.isRunning():
				fishValue = bullet.getFishValue( fish )
				# 捕获成功率 = min（0.95，0.8 * 炮弹价值 / 鱼的价值）+ 损失修正率
				rateAmend = bullet.getCaptureRateAmend( fisher, fish )
				if random.random()  <= min( 0.95, 0.8 * bulletValue / fishValue ) + rateAmend:
					DEBUG_MSG( "fisher(%s) use bullet( %i ) in value( %i ) catch fish( %i )." % ( fisher.getName(), bulletType, bulletValue, number ) )
					dieFishNumbers.append( number )
					self.fishes.pop( number ).die( fisher )
					if rateAmend > 0:	# 如果捕获时修正率发挥了作用，那么重置fisher的损失额
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

# -*- coding: gb18030 -*-
"""
藏宝图物品类。
"""
import random
import Math
import csconst
import csdefine
from CItemBase import CItemBase
from bwdebug import *
from Love3 import g_TreasurePositions

class CItemTreasureMap( CItemBase ):
	"""
	藏宝图物品类
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: 物品的原始数据
		"""
		CItemBase.__init__( self, srcData )
		self.mapInfos = {}	# 此物品所记载的地图信息

	def genTreatureMap( self, player, level = 0 ):
		"""
		根据藏宝图级别随机出宝藏可能埋藏的地图
		注意：是genTreatureMap不是getTreatureMap，是生成宝藏地点，而不是获得宝藏地点，获得宝藏地点要用query("treasure_space")
		"""
		if player == None and level == 0:
			# INFO_MSG( "生成藏宝图坐标出错，传入了数值为None的玩家" )
			return "fengming"
		return self.getSpaceByLevel( level )

	def genTreaturePosition( self, spaceName, level = 1 ):
		"""
		根据藏宝图级别随机出宝藏可能埋藏的位置坐标
		注意：是genTreaturePosition不是getTreaturePosition，是生成宝藏坐标，而不是获得宝藏坐标，获得宝藏坐标要用query("treasure_position")
		"""
		# 具体如何生成尚未确定，要与策划讨论，暂时写成这样
		x = random.randint( -3,3 )
		z = random.randint( -3,3 )
		npcPosition = (0,0,0)
		posList = g_TreasurePositions.getTreasureSpawnPointsLocationList( spaceName, level )
		if len( posList ) == 0:
			ERROR_MSG( "生成藏宝图坐标生成失败！地图名为：%s，级别为%d。" % ( spaceName, level ) )
		else:
			index = random.randint( 0,len( posList ) - 1 )
			npcPosition = posList[index] + Math.Vector3( x, 0, z )
		return npcPosition

	def generateLocation( self, player, level = 1 ):
		"""
		生成并设置此物品中所记载的宝藏地点的信息
		"""
		treasureSpace = self.genTreatureMap( player, level )				# 随机生成地图
		treasurePos = ( 0,0,0 )
		treasurePos = self.genTreaturePosition( treasureSpace, level )		# 随机生成具体坐标
		treasurePosition = str( treasurePos )
		self.set( "treasure_space", treasureSpace, player )					# 记录这个地图信息
		self.set( "treasure_position", treasurePosition, player )			# 记录这个坐标信息

	def setAmount( self, amount, owner = None, reason = csdefine.ITEM_NORMAL ):
		"""
		设置物品数量
		重写这个是因为这个函数是一定被调用的，那么当其调用时如果发现藏宝图没储存地点信息就生成之！
		"""
		CItemBase.setAmount( self, amount, owner, reason )
		spaceName = self.query( "treasure_space", "" )
		level = 1
		if self.query( level ) != 0:
			level = self.query( "level" )
		if not g_TreasurePositions._treasurePositions.has_key( spaceName ):
			# INFO_MSG( "非正常途径拾取藏宝图，可能是玩家直接add_item的，该藏宝图地图信息不在表中!地图名是%s" % spaceName )
			self.generateLocation( owner )
		elif self.query( "treasure_position", "" ) == "":
			# 如果藏宝图没有储存坐标，就生成之
			self.set( "treasure_position", str( self.genTreaturePosition( spaceName, level ) ) )

	def getSpaceByLevel( self, level ):
		"""
		根据等级确定藏宝图的宝藏地图信息
		"""
		if level >= 0 and level < 20:
			# 新凤鸣
			return "fengming"
		if level >= 20 and level <= 30:
			# 新飞来石
			return "xin_fei_lai_shi_001"
		elif level >= 31 and level <= 40:
			# 板泉
			return "zly_ban_quan_xiang"
		elif level >= 41 and level <= 50:
			# 飞云坡
			return "zly_ying_ke_cun"
		elif level >= 51 and level <= 60:
			# 避世山谷
			return "zly_bi_shi_jian"
		elif level >= 61 and level <= 70:
			# 青凤原
			return "yun_meng_ze_01"
		elif level >= 71 and level <= 80:
			# 苗人沼泽
			return "yun_meng_ze_02"
		elif level >= 81 and level <= 95:
			# 蓬莱
			return "peng_lai"
		elif level >= 96:
			# 昆仑
			return "kun_lun"
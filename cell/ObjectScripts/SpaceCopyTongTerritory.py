# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
副本场景中共有10组刷新点，每组8个坐标。
根据以下规则产生怪物，玩家数量指在副本创建时即进入副本的玩家，不包括后进入的玩家。怪物数量产生后也不再发生改变。
即：
1个玩家：随机确定其中5组，每组随机确定3个点，共产生15个怪物。
2个玩家：随机确定其中6组，每组随机确定5个点，共产生30个怪物。
3个玩家：随机确定其中9组，每组随机确定5个点，共产生45个怪物。
4个玩家：10组，每组随机确定6个点，共产生60个怪物。
5个玩家：10组，全部8个点，共产生80个怪物。
"""
import BigWorld
import csstatus
import csdefine
import random
import csconst
from bwdebug import *
from SpaceCopy import SpaceCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	注：此脚本只能用于匹配SpaceDomainCopy、SpaceCopy或继承于其的类。
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		self.tempDatas = {}
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = False

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		self.tempDatas[ "npcConfig" ] = {}
		# 议事大厅 npcID
		data = section[ "Space" ][ "ysdt_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ysdt" ] = ( ( pos, direction ), section[ "Space" ][ "ysdt_npc" ].asString )

		# 金库 npcID
		data = section[ "Space" ][ "jk_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "jk" ] = ( ( pos, direction ), section[ "Space" ][ "jk_npc" ].asString )

		# 神兽殿 npcID
		data = section[ "Space" ][ "ssd_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ssd" ] = ( ( pos, direction ), section[ "Space" ][ "ssd_npc" ].asString )

		# 仓库 npcID
		data = section[ "Space" ][ "cc_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ck" ] = ( ( pos, direction ), section[ "Space" ][ "cc_npc" ].asString )

		# 铁匠铺 npcID
		data = section[ "Space" ][ "tjp_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "tjp" ] = ( ( pos, direction ), section[ "Space" ][ "tjp_npc" ].asString	)

		# 商店 npcID
		data = section[ "Space" ][ "sd_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "sd" ] = ( ( pos, direction ), section[ "Space" ][ "sd_npc" ].asString )

		# 研究院 npcID
		data = section[ "Space" ][ "yjy_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "yjy" ] = ( ( pos, direction ), section[ "Space" ][ "yjy_npc" ].asString	)

		# 传送 npcID
		data = section[ "Space" ][ "cs_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "cs" ] = ( ( pos, direction ), section[ "Space" ][ "cs_npc" ].asString	)

		# 战场总管 npcID
		data = section[ "Space" ][ "zg_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "zg" ] = ( ( pos, direction ), section[ "Space" ][ "zg_npc" ].asString	)

		# 邮箱 npcID
		data = section[ "Space" ][ "mailbox_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "mailbox" ] = ( ( pos, direction ), section[ "Space" ][ "mailbox_npc" ].asString	)

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		用我自己的数据初始化参数 selfEntity 的数据
		"""
		npcConfig = self.tempDatas[ "npcConfig" ]
		tongDBID = selfEntity.params[ "tongDBID" ]
		"""
		for key, cnf in npcConfig.items():# 创建NPC
			if key != "zg" and key != "cs" and selfEntity.params[ key + "_level" ] <= 0:
				continue
			selfEntity.createNPCObject( cnf[1], cnf[0][0], cnf[0][1], {} )
		"""

		for key, cnf in npcConfig.iteritems():# 创建NPC
			if key == "zg" or key == "cs" or key == "mailbox":
				print "---------------------",key
				selfEntity.createNPCObject( cnf[1], cnf[0][0], cnf[0][1], {} )
				print "*&*****************"

		# 检查是否有保护帮派活动开始
		selfEntity.setTemp( "checkProtectTongStartTimer",  selfEntity.addTimer( 1.0, 0, 0 ) )

		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TONG_TERRITORY_TONGDBID, tongDBID )

	def packedDomainData( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		@param entity: 通常为玩家
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { 'tongDBID' : entity.tong_dbID, "enter_tong_territory_datas" : entity.popTemp( "enter_tong_territory_datas", {} ), "spaceKey": entity.tong_dbID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		获取entity进入时，向所在的space发送进入了该space消息的额外参数；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于在玩家上线时需要在指定的space创建cell而获取数据；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict['tongDBID'] = entity.tong_dbID
		packDict[ 'tongLevel' ] = entity.tong_level
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		获取entity离开时，向所在的space发送离开该space消息的额外参数；
		@param entity: 想要向space entity发送离开该space消息(onLeave())的entity（通常为玩家）
		@return: dict，返回要离开的space所需要的entity数据。如，有些space可能会需要比较离开的玩家名字与当前记录的玩家的名字，这里就需要返回玩家的playerName属性
		"""
		packDict = SpaceCopy.packedSpaceDataOnLeave( self, entity )
		packDict['tongDBID'] = entity.tong_dbID
		return packDict

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if id == selfEntity.queryTemp( "checkProtectTongStartTimer", 0 ):	# 检查是否有保护帮派活动开始
			selfEntity.checkProtectTongStart()
			selfEntity.popTemp( "checkProtectTongStartTimer" )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		一个entity进入到space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onEnter()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 进入此space的entity mailbox
		@param params: dict; 进入此space时需要的附加数据。此数据由当前脚本的packedDataOnEnter()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		# 设置玩家最后进入的帮会领地的DBID
		baseMailbox.cell.tong_setLastTongTerritoryDBID( selfEntity.params[ "tongDBID" ] )

		if params[ "tongDBID" ] == selfEntity.params[ "tongDBID" ]:
			nagualData = selfEntity.queryTemp( "nagualData", None )

			if nagualData:
				skillID = selfEntity.getNagualBuffID( nagualData[0], nagualData[1] )
				if skillID != None:
					if BigWorld.entities.has_key( baseMailbox.id ):
						BigWorld.entities[ baseMailbox.id ].spellTarget( skillID, baseMailbox.id )
					else:
						baseMailbox.cell.spellTarget( skillID, baseMailbox.id )
				else:
					ERROR_MSG( "skillID is None, %i, %i" % ( nagualData[0], nagualData[1] ) )

			# 帮会祭祀活动的值设置
			feteData = selfEntity.queryTemp( "feteData", None )
			if not feteData is None:
				baseMailbox.client.tong_setFeteData( feteData )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		此接口在base的ObjectScripts/Space.py中也同样存在，用于处理base收到onLeave()消息时（如果有的话）的处理。
		@param selfEntity: 与自身相匹配的Space Entity
		@param baseMailbox: 要离开此space的entity mailbox
		@param params: dict; 离开此space时需要的附加数据。此数据由当前脚本的packedDataOnLeave()接口根据当前脚本需要而获取并传输
		"""
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )
		if params[ "tongDBID" ] == selfEntity.params[ "tongDBID" ]:
			# 帮会祭祀活动的值设置
			feteData = selfEntity.queryTemp( "feteData", None )
			if not feteData is None:
				baseMailbox.client.tong_setFeteData( -1 )

	def createDoor( self, selfEntity ):
		"""
		创建Door
		"""
		pass

#
# $Log: not supported by cvs2svn $
#

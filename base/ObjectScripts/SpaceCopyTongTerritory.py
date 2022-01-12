# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyFamilyWar.py,v 1.3 2008-08-02 03:50:27 kebiao Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
from SpaceCopy import SpaceCopy

class SpaceCopyTongTerritory( SpaceCopy ):
	"""
	用于匹配SpaceDomainCopyTeam的基础类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		self.tempDatas = {}
		
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		SpaceCopy.load( self, section )
		data = section[ "Space" ][ "enterPos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.enterPoint = ( pos, direction )
		
		self.tempDatas[ "buildingConfig" ] = {}
		self.tempDatas[ "npcConfig" ] = {}
		# 议事大厅 建筑坐标和建筑ID
		data = section[ "Space" ][ "ysdt_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ysdt" ] = ( ( pos, direction ), section[ "Space" ][ "ysdt_building" ].asString )
		
		# 金库 建筑坐标和建筑ID
		data = section[ "Space" ][ "jk_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "jk" ] = ( ( pos, direction ), section[ "Space" ][ "jk_building" ].asString )
		
		# 神兽殿 建筑坐标和建筑ID
		data = section[ "Space" ][ "ssd_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ssd" ] = ( ( pos, direction ), section[ "Space" ][ "ssd_building" ].asString )
		
		# 仓库 建筑坐标和建筑ID
		data = section[ "Space" ][ "cc_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ck" ] = ( ( pos, direction ), section[ "Space" ][ "cc_building" ].asString )
		
		# 铁匠铺 建筑坐标和建筑ID
		data = section[ "Space" ][ "tjp_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "tjp" ] = ( ( pos, direction ), section[ "Space" ][ "tjp_building" ].asString	)
		
		# 商店 建筑坐标和建筑ID
		data = section[ "Space" ][ "sd_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "sd" ] = ( ( pos, direction ), section[ "Space" ][ "sd_building" ].asString )
		
		# 研究院 建筑坐标和建筑ID
		data = section[ "Space" ][ "yjy_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "yjy" ] = ( ( pos, direction ), section[ "Space" ][ "yjy_building" ].asString	)

		# 神兽 建筑坐标和建筑ID
		data = section[ "Space" ][ "ss_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "shenshou_config" ] = ( ( pos, direction ), { csdefine.TONG_SHENSHOU_TYPE_1 : section[ "Space" ][ "ss_npc1" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_2 : section[ "Space" ][ "ss_npc2" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_3 : section[ "Space" ][ "ss_npc3" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_4 : section[ "Space" ][ "ss_npc4" ].asString }	)
																	

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

		# 帮会活动 魔物来袭 怪物出现点
		data = section[ "Space" ][ "campaign_monsterRaid_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "campaign_monsterRaid_pos" ] = ( pos, direction )

		# 帮会活动 魔物来袭 小怪出现点
		data = section[ "Space" ][ "campaign_monsterRaid_poss" ]
		self.tempDatas[ "campaign_monsterRaid_poss" ] = []
		for posData in data.values():
			pos 	  = tuple( [ float(x) for x in posData[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in posData[ "direction" ].asString.split() ] )		
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "campaign_monsterRaid_poss" ].append( ( pos, direction ) )

		# 帮会活动 魔物来袭 箱子出现点
		data = section[ "Space" ][ "campaign_monsterRaid_box_pos" ]
		self.tempDatas[ "campaign_monsterRaid_box_pos" ] = []
		for item in data.values():
			pos 	  = tuple( [ float(x) for x in item[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in item[ "direction" ].asString.split() ] )			
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "campaign_monsterRaid_box_pos" ].append( ( pos, direction ) )
			
		# 帮会活动 魔物来袭 某怪物暴某箱子配置
		data = section[ "Space" ][ "campaign_monster_box_drops" ]
		self.tempDatas[ "campaign_monster_box_drops" ] = {}
		for item in data.values():
			NPCID = item[ "NPCID" ].asString
			boxIDs = []
			for boxs in item[ "boxID" ].values():
				boxIDs.append( boxs.asString )
			self.tempDatas[ "campaign_monster_box_drops" ][ NPCID ] = boxIDs

		self.tempDatas[ "feteDatas" ] = {}
		# 帮会活动 祭祀 场景物件 香谭数据
		data = section[ "Space" ][ "feteThingDatas" ]
		self.tempDatas[ "feteDatas" ][ "feteThingDatas" ] = {}
		for item in data.values():
			NPCID = item[ "id" ].asString
			pos = tuple( [ float(x) for x in item[ "pos" ][ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in item[ "pos" ][ "direction" ].asString.split() ] )
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "feteDatas" ][ "feteThingDatas" ][ NPCID ] = ( pos, direction )

		# 帮会活动 祭祀 场景物件 香谭数据
		data = section[ "Space" ][ "feteRewardNPCPos" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "feteDatas" ][ "feteRewardNPC" ] = ( section[ "Space" ][ "feteRewardNPCID" ].asString, ( pos, direction ) )

		# 保护帮派活动 NPCID
		self.tempDatas[ "protectTong" ] = {}
		self.tempDatas[ "protectTong" ][ "npcID" ] = section[ "Space" ][ "protectTongNPCID" ].asString
		self.tempDatas[ "protectTong" ][ "protectTongMidAutumnNPCID" ] = section[ "Space" ][ "protectTongMidAutumnNPCID" ].asString	# 中秋月饼怪npc
		
		# 保护帮派活动 NPC坐标
		data = section[ "Space" ][ "protectTongNPC_pos" ]
		self.tempDatas[ "protectTong" ][ "pos" ] = []
		for posData in data.values():
			pos 	  = tuple( [ float(x) for x in posData[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in posData[ "direction" ].asString.split() ] )		
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "protectTong" ][ "pos" ].append( ( pos, direction ) )
		
		self.tempDatas[ "protectTong" ][ "midAutumnPos" ] = []
		for posData in section[ "Space" ][ "protectTongMidAutumnNPC_pos" ].values():
			pos 	  = tuple( [ float(x) for x in posData[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in posData[ "direction" ].asString.split() ] )		
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "protectTong" ][ "midAutumnPos" ].append( ( pos, direction ) )
			
	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		# 返回databaseID，这样space domain能够此数据正确的记录副本的创建者，
		# 且不用担心玩家在短时间内（断）下线后重上时找回副本的问题；
		return { "tongDBID" : entity.cellData[ "lastTongTerritoryDBID" ], "spaceKey":entity.cellData["lastTongTerritoryDBID"] }
		

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/01 08:03:39  kebiao
# 增加玩家复活点规则
#
# Revision 1.1  2008/07/31 09:04:12  kebiao
# no message
#
#
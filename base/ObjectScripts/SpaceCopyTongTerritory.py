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
	����ƥ��SpaceDomainCopyTeam�Ļ�����
	"""
	def __init__( self ):
		"""
		��ʼ��
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
		# ���´��� ��������ͽ���ID
		data = section[ "Space" ][ "ysdt_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ysdt" ] = ( ( pos, direction ), section[ "Space" ][ "ysdt_building" ].asString )
		
		# ��� ��������ͽ���ID
		data = section[ "Space" ][ "jk_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "jk" ] = ( ( pos, direction ), section[ "Space" ][ "jk_building" ].asString )
		
		# ���޵� ��������ͽ���ID
		data = section[ "Space" ][ "ssd_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ssd" ] = ( ( pos, direction ), section[ "Space" ][ "ssd_building" ].asString )
		
		# �ֿ� ��������ͽ���ID
		data = section[ "Space" ][ "cc_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "ck" ] = ( ( pos, direction ), section[ "Space" ][ "cc_building" ].asString )
		
		# ������ ��������ͽ���ID
		data = section[ "Space" ][ "tjp_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "tjp" ] = ( ( pos, direction ), section[ "Space" ][ "tjp_building" ].asString	)
		
		# �̵� ��������ͽ���ID
		data = section[ "Space" ][ "sd_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "sd" ] = ( ( pos, direction ), section[ "Space" ][ "sd_building" ].asString )
		
		# �о�Ժ ��������ͽ���ID
		data = section[ "Space" ][ "yjy_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "buildingConfig" ][ "yjy" ] = ( ( pos, direction ), section[ "Space" ][ "yjy_building" ].asString	)

		# ���� ��������ͽ���ID
		data = section[ "Space" ][ "ss_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "shenshou_config" ] = ( ( pos, direction ), { csdefine.TONG_SHENSHOU_TYPE_1 : section[ "Space" ][ "ss_npc1" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_2 : section[ "Space" ][ "ss_npc2" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_3 : section[ "Space" ][ "ss_npc3" ].asString, \
																		csdefine.TONG_SHENSHOU_TYPE_4 : section[ "Space" ][ "ss_npc4" ].asString }	)
																	

		# ���´��� npcID
		data = section[ "Space" ][ "ysdt_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ysdt" ] = ( ( pos, direction ), section[ "Space" ][ "ysdt_npc" ].asString )
		
		# ��� npcID
		data = section[ "Space" ][ "jk_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "jk" ] = ( ( pos, direction ), section[ "Space" ][ "jk_npc" ].asString )
		
		# ���޵� npcID
		data = section[ "Space" ][ "ssd_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ssd" ] = ( ( pos, direction ), section[ "Space" ][ "ssd_npc" ].asString )
		
		# �ֿ� npcID
		data = section[ "Space" ][ "cc_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "ck" ] = ( ( pos, direction ), section[ "Space" ][ "cc_npc" ].asString )
		
		# ������ npcID
		data = section[ "Space" ][ "tjp_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "tjp" ] = ( ( pos, direction ), section[ "Space" ][ "tjp_npc" ].asString	)
		
		# �̵� npcID
		data = section[ "Space" ][ "sd_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "sd" ] = ( ( pos, direction ), section[ "Space" ][ "sd_npc" ].asString )
		
		# �о�Ժ npcID
		data = section[ "Space" ][ "yjy_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )		
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "yjy" ] = ( ( pos, direction ), section[ "Space" ][ "yjy_npc" ].asString	)

		# ��� ħ����Ϯ ������ֵ�
		data = section[ "Space" ][ "campaign_monsterRaid_pos" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "campaign_monsterRaid_pos" ] = ( pos, direction )

		# ��� ħ����Ϯ С�ֳ��ֵ�
		data = section[ "Space" ][ "campaign_monsterRaid_poss" ]
		self.tempDatas[ "campaign_monsterRaid_poss" ] = []
		for posData in data.values():
			pos 	  = tuple( [ float(x) for x in posData[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in posData[ "direction" ].asString.split() ] )		
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "campaign_monsterRaid_poss" ].append( ( pos, direction ) )

		# ��� ħ����Ϯ ���ӳ��ֵ�
		data = section[ "Space" ][ "campaign_monsterRaid_box_pos" ]
		self.tempDatas[ "campaign_monsterRaid_box_pos" ] = []
		for item in data.values():
			pos 	  = tuple( [ float(x) for x in item[ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in item[ "direction" ].asString.split() ] )			
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "campaign_monsterRaid_box_pos" ].append( ( pos, direction ) )
			
		# ��� ħ����Ϯ ĳ���ﱩĳ��������
		data = section[ "Space" ][ "campaign_monster_box_drops" ]
		self.tempDatas[ "campaign_monster_box_drops" ] = {}
		for item in data.values():
			NPCID = item[ "NPCID" ].asString
			boxIDs = []
			for boxs in item[ "boxID" ].values():
				boxIDs.append( boxs.asString )
			self.tempDatas[ "campaign_monster_box_drops" ][ NPCID ] = boxIDs

		self.tempDatas[ "feteDatas" ] = {}
		# ��� ���� ������� ��̷����
		data = section[ "Space" ][ "feteThingDatas" ]
		self.tempDatas[ "feteDatas" ][ "feteThingDatas" ] = {}
		for item in data.values():
			NPCID = item[ "id" ].asString
			pos = tuple( [ float(x) for x in item[ "pos" ][ "pos" ].asString.split() ] )
			direction = tuple( [ float(x) for x in item[ "pos" ][ "direction" ].asString.split() ] )
			direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
			self.tempDatas[ "feteDatas" ][ "feteThingDatas" ][ NPCID ] = ( pos, direction )

		# ��� ���� ������� ��̷����
		data = section[ "Space" ][ "feteRewardNPCPos" ]
		pos = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "feteDatas" ][ "feteRewardNPC" ] = ( section[ "Space" ][ "feteRewardNPCID" ].asString, ( pos, direction ) )

		# �������ɻ NPCID
		self.tempDatas[ "protectTong" ] = {}
		self.tempDatas[ "protectTong" ][ "npcID" ] = section[ "Space" ][ "protectTongNPCID" ].asString
		self.tempDatas[ "protectTong" ][ "protectTongMidAutumnNPCID" ] = section[ "Space" ][ "protectTongMidAutumnNPCID" ].asString	# �����±���npc
		
		# �������ɻ NPC����
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
		�������������ʱ��Ҫ��ָ����domain���������
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { "tongDBID" : entity.cellData[ "lastTongTerritoryDBID" ], "spaceKey":entity.cellData["lastTongTerritoryDBID"] }
		

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/01 08:03:39  kebiao
# ������Ҹ�������
#
# Revision 1.1  2008/07/31 09:04:12  kebiao
# no message
#
#
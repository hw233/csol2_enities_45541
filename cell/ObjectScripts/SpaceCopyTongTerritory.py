# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyPotential.py,v 1.17 2008-06-23 01:32:24 kebiao Exp $

"""
���������й���10��ˢ�µ㣬ÿ��8�����ꡣ
�������¹����������������ָ�ڸ�������ʱ�����븱������ң���������������ҡ���������������Ҳ���ٷ����ı䡣
����
1����ң����ȷ������5�飬ÿ�����ȷ��3���㣬������15�����
2����ң����ȷ������6�飬ÿ�����ȷ��5���㣬������30�����
3����ң����ȷ������9�飬ÿ�����ȷ��5���㣬������45�����
4����ң�10�飬ÿ�����ȷ��6���㣬������60�����
5����ң�10�飬ȫ��8���㣬������80�����
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
	ע���˽ű�ֻ������ƥ��SpaceDomainCopy��SpaceCopy��̳�������ࡣ
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		SpaceCopy.__init__( self )
		self.tempDatas = {}
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = False

	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
		"""
		SpaceCopy.load( self, section )
		self.tempDatas[ "npcConfig" ] = {}
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

		# ���� npcID
		data = section[ "Space" ][ "cs_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "cs" ] = ( ( pos, direction ), section[ "Space" ][ "cs_npc" ].asString	)

		# ս���ܹ� npcID
		data = section[ "Space" ][ "zg_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "zg" ] = ( ( pos, direction ), section[ "Space" ][ "zg_npc" ].asString	)

		# ���� npcID
		data = section[ "Space" ][ "mailbox_pos_npc" ]
		pos 	  = tuple( [ float(x) for x in data[ "pos" ].asString.split() ] )
		direction = tuple( [ float(x) for x in data[ "direction" ].asString.split() ] )
		direction = ( direction[0],direction[2],direction[1]*3.1415926/180 )
		self.tempDatas[ "npcConfig" ][ "mailbox" ] = ( ( pos, direction ), section[ "Space" ][ "mailbox_npc" ].asString	)

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		�����Լ������ݳ�ʼ������ selfEntity ������
		"""
		npcConfig = self.tempDatas[ "npcConfig" ]
		tongDBID = selfEntity.params[ "tongDBID" ]
		"""
		for key, cnf in npcConfig.items():# ����NPC
			if key != "zg" and key != "cs" and selfEntity.params[ key + "_level" ] <= 0:
				continue
			selfEntity.createNPCObject( cnf[1], cnf[0][0], cnf[0][1], {} )
		"""

		for key, cnf in npcConfig.iteritems():# ����NPC
			if key == "zg" or key == "cs" or key == "mailbox":
				print "---------------------",key
				selfEntity.createNPCObject( cnf[1], cnf[0][0], cnf[0][1], {} )
				print "*&*****************"

		# ����Ƿ��б������ɻ��ʼ
		selfEntity.setTemp( "checkProtectTongStartTimer",  selfEntity.addTimer( 1.0, 0, 0 ) )

		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_TONG_TERRITORY_TONGDBID, tongDBID )

	def packedDomainData( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		@param entity: ͨ��Ϊ���
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		# ����databaseID������space domain�ܹ���������ȷ�ļ�¼�����Ĵ����ߣ�
		# �Ҳ��õ�������ڶ�ʱ���ڣ��ϣ����ߺ�����ʱ�һظ��������⣻
		return { 'tongDBID' : entity.tong_dbID, "enter_tong_territory_datas" : entity.popTemp( "enter_tong_territory_datas", {} ), "spaceKey": entity.tong_dbID }

	def packedSpaceDataOnEnter( self, entity ):
		"""
		��ȡentity����ʱ�������ڵ�space���ͽ����˸�space��Ϣ�Ķ��������
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ��������������ʱ��Ҫ��ָ����space����cell����ȡ���ݣ�
		@param entity: ��Ҫ��space entity���ͽ����space��Ϣ(onEnter())��entity��ͨ��Ϊ��ң�
		@return: dict�����ر������space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ��¼��ҵ����֣��������Ҫ������ҵ�playerName����
		@note: ֻ�ܷ����ֵ����ͣ����ֵ������е�����ֻ����python���õĻ����������ͣ�����������ʵ�����Զ�������ʵ���ȡ�
		"""
		packDict = SpaceCopy.packedSpaceDataOnEnter( self, entity )
		packDict['tongDBID'] = entity.tong_dbID
		packDict[ 'tongLevel' ] = entity.tong_level
		return packDict

	def packedSpaceDataOnLeave( self, entity ):
		"""
		��ȡentity�뿪ʱ�������ڵ�space�����뿪��space��Ϣ�Ķ��������
		@param entity: ��Ҫ��space entity�����뿪��space��Ϣ(onLeave())��entity��ͨ��Ϊ��ң�
		@return: dict������Ҫ�뿪��space����Ҫ��entity���ݡ��磬��Щspace���ܻ���Ҫ�Ƚ��뿪����������뵱ǰ��¼����ҵ����֣��������Ҫ������ҵ�playerName����
		"""
		packDict = SpaceCopy.packedSpaceDataOnLeave( self, entity )
		packDict['tongDBID'] = entity.tong_dbID
		return packDict

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if id == selfEntity.queryTemp( "checkProtectTongStartTimer", 0 ):	# ����Ƿ��б������ɻ��ʼ
			selfEntity.checkProtectTongStart()
			selfEntity.popTemp( "checkProtectTongStartTimer" )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity���뵽spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onEnter()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: �����space��entity mailbox
		@param params: dict; �����spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnEnter()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		# �������������İ����ص�DBID
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

			# ��������ֵ����
			feteData = selfEntity.queryTemp( "feteData", None )
			if not feteData is None:
				baseMailbox.client.tong_setFeteData( feteData )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		һ��entity׼���뿪spaceʱ��֪ͨ��
		�˽ӿ���base��ObjectScripts/Space.py��Ҳͬ�����ڣ����ڴ���base�յ�onLeave()��Ϣʱ������еĻ����Ĵ���
		@param selfEntity: ��������ƥ���Space Entity
		@param baseMailbox: Ҫ�뿪��space��entity mailbox
		@param params: dict; �뿪��spaceʱ��Ҫ�ĸ������ݡ��������ɵ�ǰ�ű���packedDataOnLeave()�ӿڸ��ݵ�ǰ�ű���Ҫ����ȡ������
		"""
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )
		if params[ "tongDBID" ] == selfEntity.params[ "tongDBID" ]:
			# ��������ֵ����
			feteData = selfEntity.queryTemp( "feteData", None )
			if not feteData is None:
				baseMailbox.client.tong_setFeteData( -1 )

	def createDoor( self, selfEntity ):
		"""
		����Door
		"""
		pass

#
# $Log: not supported by cvs2svn $
#

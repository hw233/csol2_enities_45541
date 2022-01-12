# -*- coding: gb18030 -*-
"""
�ر�ͼ��Ʒ�ࡣ
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
	�ر�ͼ��Ʒ��
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: ��Ʒ��ԭʼ����
		"""
		CItemBase.__init__( self, srcData )
		self.mapInfos = {}	# ����Ʒ�����صĵ�ͼ��Ϣ

	def genTreatureMap( self, player, level = 0 ):
		"""
		���ݲر�ͼ������������ؿ�����صĵ�ͼ
		ע�⣺��genTreatureMap����getTreatureMap�������ɱ��صص㣬�����ǻ�ñ��صص㣬��ñ��صص�Ҫ��query("treasure_space")
		"""
		if player == None and level == 0:
			# INFO_MSG( "���ɲر�ͼ���������������ֵΪNone�����" )
			return "fengming"
		return self.getSpaceByLevel( level )

	def genTreaturePosition( self, spaceName, level = 1 ):
		"""
		���ݲر�ͼ������������ؿ�����ص�λ������
		ע�⣺��genTreaturePosition����getTreaturePosition�������ɱ������꣬�����ǻ�ñ������꣬��ñ�������Ҫ��query("treasure_position")
		"""
		# �������������δȷ����Ҫ��߻����ۣ���ʱд������
		x = random.randint( -3,3 )
		z = random.randint( -3,3 )
		npcPosition = (0,0,0)
		posList = g_TreasurePositions.getTreasureSpawnPointsLocationList( spaceName, level )
		if len( posList ) == 0:
			ERROR_MSG( "���ɲر�ͼ��������ʧ�ܣ���ͼ��Ϊ��%s������Ϊ%d��" % ( spaceName, level ) )
		else:
			index = random.randint( 0,len( posList ) - 1 )
			npcPosition = posList[index] + Math.Vector3( x, 0, z )
		return npcPosition

	def generateLocation( self, player, level = 1 ):
		"""
		���ɲ����ô���Ʒ�������صı��صص����Ϣ
		"""
		treasureSpace = self.genTreatureMap( player, level )				# ������ɵ�ͼ
		treasurePos = ( 0,0,0 )
		treasurePos = self.genTreaturePosition( treasureSpace, level )		# ������ɾ�������
		treasurePosition = str( treasurePos )
		self.set( "treasure_space", treasureSpace, player )					# ��¼�����ͼ��Ϣ
		self.set( "treasure_position", treasurePosition, player )			# ��¼���������Ϣ

	def setAmount( self, amount, owner = None, reason = csdefine.ITEM_NORMAL ):
		"""
		������Ʒ����
		��д�������Ϊ���������һ�������õģ���ô�������ʱ������ֲر�ͼû����ص���Ϣ������֮��
		"""
		CItemBase.setAmount( self, amount, owner, reason )
		spaceName = self.query( "treasure_space", "" )
		level = 1
		if self.query( level ) != 0:
			level = self.query( "level" )
		if not g_TreasurePositions._treasurePositions.has_key( spaceName ):
			# INFO_MSG( "������;��ʰȡ�ر�ͼ�����������ֱ��add_item�ģ��òر�ͼ��ͼ��Ϣ���ڱ���!��ͼ����%s" % spaceName )
			self.generateLocation( owner )
		elif self.query( "treasure_position", "" ) == "":
			# ����ر�ͼû�д������꣬������֮
			self.set( "treasure_position", str( self.genTreaturePosition( spaceName, level ) ) )

	def getSpaceByLevel( self, level ):
		"""
		���ݵȼ�ȷ���ر�ͼ�ı��ص�ͼ��Ϣ
		"""
		if level >= 0 and level < 20:
			# �·���
			return "fengming"
		if level >= 20 and level <= 30:
			# �·���ʯ
			return "xin_fei_lai_shi_001"
		elif level >= 31 and level <= 40:
			# ��Ȫ
			return "zly_ban_quan_xiang"
		elif level >= 41 and level <= 50:
			# ������
			return "zly_ying_ke_cun"
		elif level >= 51 and level <= 60:
			# ����ɽ��
			return "zly_bi_shi_jian"
		elif level >= 61 and level <= 70:
			# ���ԭ
			return "yun_meng_ze_01"
		elif level >= 71 and level <= 80:
			# ��������
			return "yun_meng_ze_02"
		elif level >= 81 and level <= 95:
			# ����
			return "peng_lai"
		elif level >= 96:
			# ����
			return "kun_lun"
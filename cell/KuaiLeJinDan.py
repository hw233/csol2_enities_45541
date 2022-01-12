# -*- coding: gb18030 -*-
#
# ���ֽ𵰻

from bwdebug import *
import csdefine
import csconst
import Language
import csstatus
import time
import sys

SKILL_ID = 780004001				# �ҵ���ϣ�����ɫһ��buff
SUPER_KLJD_ITEM = 10101002			# ���ֽ𵰳����󽱣������������Ʒ

class KuaiLeJinDan():
	"""
	���ֽ𵰻
	"""
	_instance = None

	def __init__( self ):
		assert KuaiLeJinDan._instance is None, "KuaiLeJinDan instance already exist in"
		KuaiLeJinDan._instance = self
		self.restrictLevel = 0
		self.g_rewards = None		# ��Ϊ��������ʼ��ʱ����ֱ��import Love3��g_rewards�����Ը�Ϊʹ��ʱimport

	@staticmethod
	def instance():
		if KuaiLeJinDan._instance is None:
			KuaiLeJinDan._instance = KuaiLeJinDan()
		return KuaiLeJinDan._instance

	def load( self, xmlPath = "" ):
		"""
		����xml�ļ�����
		"""
		section = Language.openConfigSection( xmlPath )
		assert section is not None,"open file( path:%s ) error:not exist!" % xmlPath

		self.restrictLevel = section.readInt( "restrictLevel" )
		self.restrictTime = section.readInt( "restrictTime" )

	def startKLJDActivity( self, player ):
		"""
		���ʼ--���ҵ�����
		"""
		if player.level < self.restrictLevel:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_LEVEL, self.restrictLevel )
			return
		if not player.kuaiLeJinDanDailyRecord.checklastTime():				# �ж��Ƿ�ͬһ��
			player.kuaiLeJinDanFlag = False									# ���ñ���Ƿ��Ѿ��ҵ�Ϊfalse
		if player.kuaiLeJinDanFlag:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_FLAG )
			return
		if player.wallow_isEffected() and player.antiIndulgenceRec.onlineCount < 60:	# ��������һСʱ����(���뿪�������ԣ��ŻῪʼ��ʱ)
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_ONLINE )
			return

		player.client.startKLJDActivity()	# ֪ͨ�ͻ��˴��ҵ�����

	def doKLJDActivity( self, player ):
		"""
		�ҵ���
		"""
		if player.level < self.restrictLevel:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_LEVEL )
			return

		if not player.kuaiLeJinDanDailyRecord.checklastTime():				# �ж��Ƿ�ͬһ��
			player.kuaiLeJinDanFlag = False									# ���ñ���Ƿ��Ѿ��ҵ�Ϊfalse
			player.kuaiLeJinDanDailyRecord.reset()							# ���ü�¼����
		if player.kuaiLeJinDanFlag:
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_FLAG )
			return
		if player.kuaiLeJinDanDailyRecord.getDegree() >= self.restrictTime:		# �ж��ҵ�����
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_TIME )
			return

		if player.wallow_isEffected() and player.antiIndulgenceRec.onlineCount < 60:	# ��������һСʱ����(���뿪�������ԣ��ŻῪʼ��ʱ)
			player.statusMessage( csstatus.KUAI_LE_JIN_DAN_RESTRICT_ONLINE )
			return

		self.doKLJDReward( player )		# �ҵ�����

	def doKLJDReward( self, player ):
		"""
		�ҵ�����
		"""
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_HAPPY_GODEN_EGG, player )
		if len( awarder.items ) <= 0:
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		item = awarder.items[0]		# �ûֻ�ά��һ������һ�Σ������ϳ�����1�������������������� by ����
		item.set( "level", player.level )

		if item.id == SUPER_KLJD_ITEM:		# ��������ǳ����󽱵ĳ齱����
			today = self.getToday()
			item.set( "createTime", today )
		elif item.id == 10101001:			# ��������Ǿ�����Ʒ
			item.set( "rewardExp", pow( player.level, 1.6 )*60 )

		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		awarder.award( player, csdefine.ADD_ITEM_DOKLJDREWARD )
		
		player.kuaiLeJinDanFlag = True					# ����Ѿ��ҹ�����
		player.client.endKLJDReward()					# ���ܿͻ�����Ҫ����������
		player.kuaiLeJinDanDailyRecord.incrDegree()		# �ҵ�������1
		if player.kuaiLeJinDanDailyRecord.getDegree() == 3:		# �����ɫ�Ѿ��ҵ�����(���ܲ������ַ�ʽ����)
			player.spellTarget( SKILL_ID, player.id )


	def startSuperKLJDActivity( self, player ):
		"""
		������--��̬Ҫ��
		"""
		player.client.startSuperKLJDActivity()	# ֪ͨ�ͻ��˴��ҵ�����

	def validStartSuperKLJDActivity( self, player ):
		"""
		�����󽱣��Ƿ���������
		"""
		item = player.findItemFromNKCK_( SUPER_KLJD_ITEM )		# ȡ�ý�ɫ���ϳ����󽱲μӣ�����Я������Ʒ
		if not item:return False
		return self.checkTodayTime( item.query( "createTime" ) )

	def doSuperKLJDActivity( self, player ):
		"""
		�����ҵ�����
		"""
		items = player.findItemsFromNKCK_( SUPER_KLJD_ITEM )		# ȡ�ý�ɫ���ϳ����󽱲μӣ�����Я������Ʒ
		if len( items ) <= 0:
			HACK_MSG( "�Ҳ����μӳ����󽱵���Ʒ" )
			return
		sorce_item = None
		for item in items:
			if self.checkTodayTime( item.query( "createTime" ) ):
				sorce_item = item
				break
		if sorce_item is None:
			HACK_MSG( "�μӳ����󽱵���Ʒ���ǵ�������ģ�û������" )
			return
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_SUPER_HAPPY_GODEN_EGG, player )
		if len( awarder.items ) <= 0:
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		rewardItem = awarder.items[0]		# �ûֻ�ά��һ������һ�Σ������ϳ�����1�������������������� by ����
		rewardItem.set( "level", player.level )
		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		player.removeItem_( sorce_item.order, 1, csdefine.DELETE_ITEM_SUPERKLJDACTIVITY )
		awarder.award( player, csdefine.ADD_ITEM_DOSUPERKLJDACTIVITY )

	def getToday( self ):
		"""
		��ʼʱ��Ϊ����
		"""
		year, month, day = time.localtime()[:3]
		lastTime = year * 10000 + month * 100 + day
		return lastTime

	def checkTodayTime( self, today ):
		"""
		��������ʱ���뵱ǰʱ���Ƿ���ͬһ��
		@return: bool
		"""
		year, month, day = time.localtime()[:3]
		curr = year * 10000 + month * 100 + day
		return curr == today

	def doKLJDExpReward( self, player ):
		"""
		���ֽ𵰣���ȡ���齱��
		"""
		item = player.findItemFromNKCK_( 10101001 )		# ���ֽ𵰣���ȡ���齱���������н�������Ʒ
		if not item:
			HACK_MSG( "�Ҳ������ֽ𵰾��齱����Ʒ" )
			return
		player.addExp( int( item.query( "rewardExp" ) ), csdefine.CHANGE_EXP_KLJDEXPREWARD )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_KLJDEXPREWARD )

	def validDoKLJDExpReward( self, player ):
		"""
		���ֽ𵰣���ȡ���齱����valid
		"""
		item = player.findItemFromNKCK_( 10101001 )		# ���ֽ𵰣���ȡ���齱���������н�������Ʒ
		if not item:
			return False
		return True

	def doKLJDZuoQiReward( self, player ):
		"""
		���ֽ𵰣���ȡ���ｱ��
		"""
		id_list = [ 10101001, 10101002, 10101003, 10101004 ]
		items = player.findItemsByIDsFromNKCK( id_list )
		for item in items:
			if item.id in id_list:
				id_list.remove( item.id )
		if len( id_list ) > 0:
			HACK_MSG( "�Ҳ������ֽ����ｱ����Ʒ" )		# ���ֽ𵰣���ȡ���齱���������н�������Ʒ
			return
		if self.g_rewards is None:
			from Love3 import g_rewards
			self.g_rewards = g_rewards
		awarder = self.g_rewards.fetch( csdefine.RCG_HAPPY_GODEN_EGG_V, player )
		if len( awarder.items ) <= 0:		# �ûֻ�ά��һ������һ�Σ������ϳ�����1�������������������� by ����
			player.statusMessage( csstatus.CIB_ITEM_CONFIG_ERROR )
			return
		if not player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_CAN_HOLD:
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		for item in items:
			if item.id in id_list:
				continue
			id_list.append( item.id )
			player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_KLJDZUOQIREWARD )
			
		awarder.award( player, csdefine.ADD_ITEM_DOKLJDZUOQIREWARD )


	def validDoKLJDZuoQiReward( self, player ):
		"""
		���ֽ𵰣���ȡ���ｱ����valid
		"""
		id_list = [ 10101001, 10101002, 10101003, 10101004 ]
		items = player.findItemsByIDsFromNKCK( id_list )
		for item in items:
			if item.id in id_list:
				id_list.remove( item.id )
		return len( id_list ) <= 0

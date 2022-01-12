# -*- coding: gb18030 -*-

# $Id: PresentChargeUnite.py  hd
# �����ȡ��Ӫ������ͳ�ֵԪ����ģ��

from bwdebug import *
from PresentChargeManage import PresentChargeManage
import csdefine
import csstatus

class PresentChargeUnite:
	"""
	�����ȡ��Ӫ������ͳ�ֵԪ����ģ��
	"""
	def __init__( self ):
		self._dataDBIDs = []			#��¼���ڴ����DBID
		self._pcu_manager = None		#�����������
		self._pcu_addSilverCoinTmp = 0	#��¼��ȡȫ������ʱ ������ȡ����Ԫ������


	def get_pcu_manager( self ):
		"""
		��ȡ�������
		ע:ͨ�����������ǲ���������������ģ�������øýӿڱ�ʾ��Ҫ����������ô���û�г�ʼ���������������ʼ��
		"""
		if not self._pcu_manager:
			self._pcu_manager = PresentChargeManage( self )
		return self._pcu_manager

	def pcu_takeThings( self, dataType, item_id ):
		"""
		@define method
		��ʼ��ȡ����
		@type  dataType : UINT8
		@param dataType : ����������
		"""
		self.get_pcu_manager().takeThings( dataType, item_id )

	def pcu_getPresentTypes( self ):
		"""
		@define method
		�����ȡ���ӵ�еĽ�������,cell��ȡ����Ծ����ÿͻ���ȥ��ʾ������ҿ���֪���Լ��Ƿ��н���������У����������ȡ����
		����äĿ��ȥ����
		"""
		self.get_pcu_manager().getPresentTypes( self )

	def pcu_check( self, dbid ):
		"""
		���Ҫ�����DBID�Ƿ���֮ǰ���ڴ���
		@type  dbid : int
		@param dbid : ���ݵ�DBID
		"""
		return dbid in self._dataDBIDs

	def pcu_removeDBID( self, dbid ):
		"""
		ɾ���Ѿ������˵�DBID
		@type  dbid : int
		@param dbid : ���ݿ��иò�����DBID
		"""
		try:
			self._dataDBIDs.remove( dbid )
			return True
		except:
			ERROR_MSG("can not find dbid %s" % dbid )
			return False

	def pcu_addDBID( self, dbid ):
		"""
		����һ��DBID�����ڴ����DBID�б��У��Ա����ڼ�������¿��ܳ����ظ����������
		@type  dbid : int
		@param dbid : ���ݿ��иò�����DBID
		"""
		self._dataDBIDs.append( dbid )

	def takeOverSuccess( self ):
		"""
		@define method
		�ɹ��콱����������
		"""
		if self._pcu_addSilverCoinTmp:
			self.gainSilver( self._pcu_addSilverCoinTmp, csdefine.CHANGE_SILVER_CHARGE )	# ֮ǰ�Ѿ������Ƿ���������Ԫ�� �������ﲻ�ټ�顣
			self._pcu_addSilverCoinTmp = 0
		self.get_pcu_manager().takeThingsSuccess()

	def takeOverFailed( self ):
		"""
		@define method
		ʧ��,�������
		"""
		self.get_pcu_manager().takeThingsFailed()

	def takeSilverCoins( self, silverCoins ):
		"""
		��ȡ��Ԫ��
		"""
		addSilverCoin = 0
		for silverCoin in silverCoins:
			addSilverCoin += silverCoin
		if not self.accountEntity.testAddSilver( addSilverCoin ):	#��ʾ����������
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return
		self.gainSilver( addSilverCoin, csdefine.CHANGE_SILVER_SILVERPRESENT )
		self.takeOverSuccess()					#֪ͨ��������

	def takeChargedMoney( self, silverCoinsList, goldList ):
		"""
		��ȡ��ֵ�˵Ľ���Ԫ��
		"""
		m_addSilverCoin   = 0
		m_addGold		  = 0
		for silverCoin in silverCoinsList:
			m_addSilverCoin += silverCoin
		if not self.accountEntity.testAddSilver( m_addSilverCoin ):	#��ʾ����������
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return
		for gold in goldList:
			m_addGold += gold
		if not self.accountEntity.testAddGold( m_addGold ):	#��ʾ����������
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_GOLD )
			return
		if m_addGold > 0:
			self.gainGold( m_addGold, csdefine.CHANGE_GOLD_CHARGE )
		if m_addSilverCoin > 0:
			self.gainSilver( m_addSilverCoin, csdefine.CHANGE_SILVER_CHARGE )
		self.takeOverSuccess()					#֪ͨ��������


	def takePresents( self, presentIDs, silverCoins ):
		"""
		��ȡ��Ԫ������Ʒ
		"""
		self._pcu_addSilverCoinTmp = 0
		for silverCoin in silverCoins:
			self._pcu_addSilverCoinTmp += silverCoin
		if not self.accountEntity.testAddSilver( self._pcu_addSilverCoinTmp ):	#�������Ƿ��ܹ�������Ԫ��
			self.takeOverFailed( )
			self.statusMessage( csstatus.PCU_CAN_NOT_ADD_SIlVERCOINS )
			return

		self.cell.takePresent( presentIDs )		# ���ﵽCELL������Ʒ
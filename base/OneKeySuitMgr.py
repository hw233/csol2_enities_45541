# -*- coding: gb18030 -*-
#

import BigWorld
import cPickle
from Function import Functor
import ItemTypeEnum
from bwdebug import *
import csstatus

"""
һ����װ���ݹ�����
"""

class OneKeySuitMgr( BigWorld.Base ):
	"""
	һ����װ���ݹ�����
	"""
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "OneKeySuitMgr", self._onRegisterManager )
		
	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register OneKeySuitMgr Fail!" )
			# again
			self.registerGlobally( "OneKeySuitMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["OneKeySuitMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("OneKeySuitMgr Create Complete!")
		
		self.oneKeySuitDatas = {}
		self._loadDatas()
		
	def _loadDatas( self ):
		"""
		�����ݿ��������
		"""
		query = "SELECT * FROM custom_oneKeySuit"
		BigWorld.executeRawDatabaseCommand( query, self._onLoadDatas )
		
	def _onLoadDatas( self, result, rows, errstr ):
		"""
		��ʼ��oneKeySuitDatas
		"""
		if errstr:
			ERROR_MSG( "load custom_oneKeySuit failed! %s"%errstr  )
			return
		# ��ͷ�����ؼס����ס����ָ�����ӡ�������
		# ���������ƣ��������������������ҽ�ָ��Ь�ӡ���
		"""
		suitPartDict = {
			ItemTypeEnum.CWT_HEAD :0, # ͷ     ���� ͷ��
			ItemTypeEnum.CWT_NECK :0, # ��     ���� ����
			ItemTypeEnum.CWT_BODY :0, # ����   ���� ���
			ItemTypeEnum.CWT_BREECH :0, # �β�   ���� ����
			ItemTypeEnum.CWT_VOLA :0, # ��     ���� ����
			ItemTypeEnum.CWT_HAUNCH :0, # ��     ���� ����
			ItemTypeEnum.CWT_CUFF :0, # ��     ���� ����
			ItemTypeEnum.CWT_LEFTHAND :0, # ����   ���� ����
			ItemTypeEnum.CWT_RIGHTHAND :0, # ����   ���� ����
			ItemTypeEnum.CWT_FEET :0, # ��     ���� Ь��
			ItemTypeEnum.CWT_LEFTFINGER :0, # ����ָ ���� ��ָ
			ItemTypeEnum.CWT_RIGHTFINGER :0, # ����ָ ���� ��ָ
			ItemTypeEnum.CWT_TALISMAN :0, # ����
			}
		"""
		for i in result:
			roleDBID = int(i[1])
			if not roleDBID in self.oneKeySuitDatas:
				self.oneKeySuitDatas[roleDBID] = {}
			suitOrder = int(i[2])
			self.oneKeySuitDatas[roleDBID][suitOrder] = {}
			self.oneKeySuitDatas[roleDBID][suitOrder]["suitName"] = str(i[3])
			self.oneKeySuitDatas[roleDBID][suitOrder]["suitList"] = [int(t) for t in i[4:]]
			
	def addSuit( self, playerDBID, suitOrder, newSuitName, newSuit, playerMB ):
		"""
		define method
		��������װ
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuitName : STRING
		@param newSuit : LIST OF UID
		@param playerMB : MAILBOX
		"""
		query = "INSERT INTO custom_oneKeySuit SET sm_roleDBID = %d,sm_suitOrder = %d,sm_suitName = \'%s\',sm_head = %d,\
					sm_neck = %d,sm_body = %d,sm_breach = %d,\
					sm_vola = %d,sm_haunch = %d,sm_cuff = %d,\
					sm_lefthand = %d,sm_righthand = %d,sm_feet = %d,\
					sm_leftfinger = %d,sm_rightfinger = %d,sm_talisman = %d"%( playerDBID, suitOrder, newSuitName, newSuit[0], \
			newSuit[1], newSuit[2], newSuit[3], newSuit[4], newSuit[5],\
			newSuit[6], newSuit[7], newSuit[8], newSuit[9], newSuit[10],\
			newSuit[11], newSuit[12] )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onAddSuit, playerDBID, suitOrder, newSuitName, newSuit, playerMB ) )
		
	def _onAddSuit( self, playerDBID, suitOrder, newSuitName, newSuit, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "add one key suit failed! %s"%errstr  )
			return
		try:
			if playerDBID not in self.oneKeySuitDatas:
				self.oneKeySuitDatas[playerDBID] = {}
			self.oneKeySuitDatas[playerDBID][suitOrder] = {}
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitName"] = newSuitName
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitList"] = newSuit
			playerMB.client.onStatusMessage( csstatus.OKS_RENAME_SUCCESSED, "" )
		except:
			ERROR_MSG( "add one key suit error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
		
	def updateSuitName( self, playerDBID, suitOrder, newSuitName, playerMB ):
		"""
		define method
		������װ����
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuitName : STRING
		@param playerMB : MAILBOX
		"""
		query = "UPDATE custom_oneKeySuit SET sm_suitName = \'%s\' WHERE sm_roleDBID = %d AND sm_suitOrder = %d"%( newSuitName, playerDBID, suitOrder )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onUpdateSuitName, playerDBID, suitOrder, newSuitName, playerMB ) )
		
	def _onUpdateSuitName( self, playerDBID, suitOrder, newSuitName, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "update one key suit name failed! %s"%errstr  )
			return
		try:
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitName"] = newSuitName
			playerMB.client.onStatusMessage( csstatus.OKS_RENAME_SUCCESSED, "" )
		except:
			ERROR_MSG( "update one key suit name error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
		
	def updateSuit( self, playerDBID, suitOrder, newSuit, playerMB ):
		"""
		define method
		������װ
		@param playerDBID : UINT32
		@param suitOrder : UINT8
		@param newSuit : LIST OF UID
		@param playerMB : MAILBOX
		"""
		query = "UPDATE custom_oneKeySuit SET sm_head = %d,\
					sm_neck = %d,sm_body = %d,sm_breach = %d,\
					sm_vola = %d,sm_haunch = %d,sm_cuff = %d,\
					sm_lefthand = %d,sm_righthand = %d,sm_feet = %d,\
					sm_leftfinger = %d,sm_rightfinger = %d,sm_talisman = %d \
			WHERE sm_roleDBID = %d AND sm_suitOrder = %d"%( newSuit[0], \
			newSuit[1], newSuit[2], newSuit[3], newSuit[4], newSuit[5],\
			newSuit[6], newSuit[7], newSuit[8], newSuit[9], newSuit[10],\
			newSuit[11], newSuit[12], playerDBID, suitOrder )
		BigWorld.executeRawDatabaseCommand( query, Functor( self._onUpdateSuit, playerDBID, suitOrder, newSuit, playerMB ) )
		
	def _onUpdateSuit( self, playerDBID, suitOrder, newSuit, playerMB, result, rows, errstr ):
		"""
		"""
		if errstr:
			ERROR_MSG( "update one key suit failed! %s"%errstr  )
			return
		try:
			self.oneKeySuitDatas[playerDBID][suitOrder]["suitList"] = newSuit
			playerMB.client.onStatusMessage( csstatus.OKS_SAVE_SUCCESSED, "" )
		except:
			ERROR_MSG( "update one key suit error. DBID(%d)Order(%d)"%(playerDBID, suitOrder) )
			
	def getSuitDatas( self, playerDBID, playerMB ):
		"""
		define method
		��һ����һ����װ����
		"""
		if not playerDBID in self.oneKeySuitDatas:
			return
		playerMB.client.onGetSuitDatas( self.oneKeySuitDatas[playerDBID] )
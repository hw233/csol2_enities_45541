# -*- coding: gb18030 -*-
#
# $Id: PresentChargeManage.py

"""
������ֵ����ģ��
"""

import BigWorld
import weakref
from bwdebug import *
from MsgLogger import g_logger
import time
from Function import Functor
import csstatus
import csconst
import re
import sys

class PresentChargeManage:
	"""
	�����ͳ�ֵ������
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		@type	entity: role
		@param	entity: ��ҵ�ʵ��
		ע��ģ�齫��ֵ����ȡ�����ֿ���ԭ���ǿ��ǵ���ֵ���ܻ�ͬʱ�ӵ�������Ϣ�����Ҷ�����Ч������(��ֵ�ɹ��Ż�ӵ�ϵͳ����)��
		��Ҫ��ʱ��������ȡ����һ��ֻ����һ�������ҽ���һ�λ�ȫ����ȡ���������������Ѿ���ǰһ������Ҳ��Ҫ��ֹ��Ҳ�ͣ����
		������Ҫһ��һ���������������ֱ������������ʵ�������������ֻ�������һ����ȡ����Ͷ�����ֵ����
		"""
		self.operations = []										# ��¼��ҵ�����Ķ���
		self.currOperation = None									# ��¼��ҵ�ǰ������
		self.entity  = weakref.proxy(entity)

	def havePresent( self ):
		"""
		�ж��Ƿ�����ȡ�����ڶ�����
		"""
		if self.currOperation and not isinstance(self.currOperation,takeTypes[csconst.PCU_TAKECHARGE]):
		#�����ǰ������ǳ�ֵ����ô��ȥ��ѯ�������Ƿ�����ȡ����
			return True
		for operation in self.operations:
			if not isinstance(operation,takeTypes[csconst.PCU_TAKECHARGE]):
				return True
		return False

	def takeThings( self, dataType, item_id ):
		"""
		��ȡ���ݿ��е�����
		@type  dataType: UINT8
		@param dataType: ����(��ֵ)����
		@type  item_id: ITEM_ID
		@param item_id: �������Ʒ���� ������Ʒ��ID
		ע:������ֻ������һ����ȡ����������Ͷ����ֵ����,��ȡ������������ҷ������������ظ�������ͬʱֻ����һ������ֵ����
		Ϊϵͳ������ÿһ����Ϊ��ֵ�󴥷�������Ϊ��Ч����ͨ������¶�����ֻ����һ������
		"""
		if dataType == csconst.PCU_TAKECHARGE or not self.havePresent():	# ����ǳ�ֵ��������б���û����ȡ����
			self.operations.append( takeTypes[dataType]( self.entity ) )	# ʵ��һ�������͵Ĳ���,���ŵ�������
			if not self.currOperation:										# �����ǰû�в���
				self.currOperation = self.operations.pop(0)					# ��ô��¼������ʵ��
				self.currOperation( item_id )								# ִ�в���
		else:
			self.entity.statusMessage( csstatus.PCU_YOU_ARE_BUSY )			# ��ʾ���ڴ�������

	def takeThingsSuccess( self ):
		"""
		�����ɹ�������������ݣ�����ȡ����������һ������
		"""
		if not self.currOperation:
			ERROR_MSG( "current has not operation" )
			return False
		self.currOperation.operationSuccess()
		self.currOperation = None
		if self.operations: 						#��������л�������,��ô����������
			self.currOperation = self.operations.pop(0)
			self.currOperation()
		return True

	def takeThingsFailed( self ):
		"""
		����ʧ�ܣ�����������ݣ���������ݿ��е����ݣ�����ȡ����������һ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.currOperation = None
			self.operations = None
			self.entity = None
			return False

		if not self.currOperation:
			ERROR_MSG( "current has not operation" )
			return False
		self.currOperation.operationFaile()
		self.currOperation = None
		if self.operations: 						#��������л�������,��ô����������
			self.currOperation = self.operations.pop(0)
			self.currOperation()
		return True

	def getPresentTypes( self ):
		"""
		��ȡ���˺�Ŀǰӵ�е���Ʒ��������. ��ֵ���ڲ�ѯ֮��,���ڵĲ��ڲ�ѯ֮��
		ע��֮��������������Ϊ�ýӿ���Ҫ���ڻ�ȡ����������е����ͣ�������ʾ�����ѡ����ȡ�����û����ô�����ṩ��ȡ����ѡ�
		���ڵ��޷���ȡ���Բ������أ���ֵ��������ϵͳ��ȡ���Բ��÷���
		"""
		sql = "SELECT sm_type FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type!= %s and ( ( sm_type !=0 and sm_type !=2 ) or  sm_expiredTime >= Now() )"\
		% ( self.entity.accountName, csconst.PCU_TAKECHARGE )
		BigWorld.executeRawDatabaseCommand( sql, self._onGetPresentTypes )

	def _onGetPresentTypes( self, results, rows, errstr ):
		"""
		��ȡ�˸��˺�ӵ�еĽ�����������
		ע������ѻ�ȡ�Ľ������cell�ϣ���Ϊһ�ֽ�������һ�λ�ȫ��ȡ��������ÿ������ֻ��ʾһ�Ρ�ʹ����setȥ���ظ����
		"""
		if errstr:
			ERROR_MSG( "get PresentTypes fail!" )
			return False
		result = results[0]  # results������0һ����ֵ ��ʹΪ�յ�list
		types  = []
		if result:
			result.sort()
			types = list( set( result ) )
		self.entity.cell.pcu_onGetPresentTypes( types )

class TakeThings:
	"""
	��ȡ��Ʒ�Ļ�����
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		self.thingsParam = []		#�洢ȡ��������
		self.entity      = entity

	def getThingsDatas( self ):
		"""
		��ȡ��Ʒ������
		"""
		return self.thingsParam

	def operationFaile( self ):
		"""
		���������ϼ�¼�ĸò�����ռ�õ�DBID
		������� �ͷ�entity
		"""
		for param in self.thingsParam:
			#����������ռ�õ�DBID,��DBID�����ڴ�������������ݿ��е�DBID,��ֹ��������»��ظ���������
			self.entity.pcu_removeDBID( param[-1] )
		self.thingsParam = []
		self.entity      = None

	def operationSuccess( self ):
		"""
		���������ϼ�¼�ĸò�����ռ�õ�DBID
		������ݿ��е�����
		д��־
		�ͷ�entity
		"""
		dbids = []
		for param in self.thingsParam:
			dbids.append( "id = %s" % param[-1] )
			#����������ռ�õ�DBID,��DBID�����ڴ�������������ݿ��е�DBID,��ֹ��������»��ظ���������
			self.entity.pcu_removeDBID( param[-1] )
		syntax = " or ".join( dbids )		#һ��ȫ��ɾ��
		sql  = "DELETE FROM custom_ChargePresentUnite WHERE %s" % syntax
		BigWorld.executeRawDatabaseCommand( sql, self._onOperationSuccess )
		self.entity   = None

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�,�˽ӿ���Ҫ�����า��
		"""
		pass

class TakePresentWithoutID( TakeThings ):
	"""
	��ȡû�ж����ŵĽ�Ʒ����
	"""
	def __init__( self,  entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		if item_id != 0:
			sql = "SELECT sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 0 and sm_expiredTime >= Now() and sm_giftPackage = %s"\
			% ( self.entity.accountName,item_id )
		else:
			sql = "SELECT sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 0 and sm_expiredTime >= Now()"\
			% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		thingsIDs   = []		#��¼��Ʒ��ID
		for result in results:	#��������
			giftPackageID = result[0]					# ��ֳ���Ʒ��ID
			expiredTime   = result[1]							# ��ȡʱ��
			accountName   = result[2]
			if self.entity.pcu_check( result[-1] ):				# ����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# �洢DBID��������ϣ����⼫��������ظ�������������ɻᱻ���
			self.thingsParam.append( ( giftPackageID, expiredTime, accountName, result[-1] ) ) # ��¼����
			thingsIDs.append( giftPackageID )					# ��¼��Ҫ���͵�CELL�ϵ�����
		if not thingsIDs:										# û�з���Ҫ���ID ֱ�ӷ��� ��Ӧ���Ǵ�����������Ϊ��Ȼ���������
																#˵������һ���ǻ��и����͵�����û�д���
			INFO_MSG("account = %s type = 0 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )		# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )
		return True

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־����������
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[2], None, params[0], params[1] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakeSilverCoins( TakeThings  ):
	"""
	�������ŵ���Ԫ�����ͽӿ�
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		sql = "SELECT sm_transactionID,sm_silverCoins,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 1" % ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas(self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take SilverCoins fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		SilverCoinsList   = []		#��¼��Ԫ��������
		transactionIDs    = []		#��¼������
		for result in results:
			transactionID  = result[0]
			silverCoins    = int( result[1])
			accountName     = result[2]
			if not transactionID or not silverCoins:
				continue
			if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )				#�洢DBID����������ɻᱻ���
			self.thingsParam.append( ( transactionID, silverCoins, accountName, result[-1] ) )
			if transactionID in transactionIDs:
				try:
					g_logger.chargePresentExceptLog( "take silver error has repetitious transactionID (%s)" %  transactionID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				continue
			transactionIDs.append(transactionID )
			SilverCoinsList.append( silverCoins )
		if not SilverCoinsList:								#û�з���Ҫ�����Ԫ���� ֱ�ӷ���
			INFO_MSG("account = %s type = 1 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		self.entity.takeSilverCoins( SilverCoinsList )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentSilverLog( params[2], params[0], params[1] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakePresent( TakeThings ):
	"""
	�������ŵĽ�Ʒ���ͽӿ�
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		if item_id != 0:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 2 and sm_expiredTime >= Now() and sm_giftPackage = %s" \
			% ( self.entity.accountName, item_id )
		else:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 2 and sm_expiredTime >= Now()" \
			% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			expiredTime   = result[2]
			accountName   = result[3]
			if not transactionID or not giftPackageID or not expiredTime:
				continue
			if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# �洢DBID��������ϣ����⼫��������ظ�������������ɻᱻ���
			self.thingsParam.append( (transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
			thingsIDs.append( giftPackageID )
		if not thingsIDs:										# û�з���Ҫ���ID ֱ�ӷ��� ��Ӧ���Ǵ�����������Ϊ��Ȼ���������
																#˵������һ���ǻ��и����͵�����û�д���
			INFO_MSG("account ID = %s type = 2 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakeCharge( TakeThings ):
	"""
	��ȡ��ֵ������
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		sql = "SELECT sm_transactionID,sm_chargeType,sm_silverCoins,sm_goldCoins,sm_account,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 3" % ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			self.entity.takeOverFailed()
			return False
		silverCoinsList = []
		goldList		= []
		transactionIDs  = []
		for result in results:
			transactionID = result[0]
			chargeType    = result[1]
			silverCoins   = int( result[2] )
			goldCoins     = int( result[3] )
			accountName   = result[4]
			if not transactionID or not chargeType:
				continue
			if silverCoins ==0 and goldCoins ==0:
				continue
			if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )	#�洢DBID����������ɻᱻ���
			self.thingsParam.append( (transactionID,chargeType,silverCoins,goldCoins, accountName, result[-1]) )
			silverCoinsList.append( silverCoins )
			if transactionID in transactionIDs:
				try:
					g_logger.chargePresentExceptLog( "charge error has repetitious transactionID (%s)" %  transactionID)
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				continue
			transactionIDs.append(transactionID)
			goldList.append(goldCoins)
		if not silverCoinsList and goldList:			#û�з���Ҫ���Ԫ���� ֱ�ӷ���
			ERROR_MSG("account = %s type = 3 has no things" % (self.entity.accountName )  )
			self.entity.takeOverFailed()
			return False
		self.entity.takeChargedMoney( silverCoinsList, goldList )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentChargeLog( params[4], params[0], params[1], params[3], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class TakeChargeUnite( TakeThings ):
	"""
	��Ʒ��ȡ�ӿ�(�������Ͳ��������ŵ�)
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		if item_id != 0:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and ( sm_type = 0 or sm_type = 2 ) and sm_expiredTime >= Now() and sm_giftPackage = %s"\
			% ( self.entity.accountName, item_id )
		else:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and ( sm_type = 0 or sm_type = 2 ) and sm_expiredTime >= Now()"\
			% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		transactionIDs = []	# ��¼������
		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			expiredTime   = result[2]
			accountName   = result[3]
			if not giftPackageID or not expiredTime:
				continue
			if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# �洢DBID��������ϣ����⼫��������ظ�������������ɻᱻ���
			self.thingsParam.append( ( transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
			if transactionID and transactionID in transactionIDs:
				try:
					g_logger.chargePresentExceptLog( "take present error has repetitious transactionID (%s)" %  transactionID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				continue
			transactionIDs.append(transactionID)
			thingsIDs.append( giftPackageID )
		if not thingsIDs:
			# û�з���Ҫ���ID,ֱ�ӷ�����Ӧ���Ǵ�������.
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			INFO_MSG("account =%s type=0 or type=2 has no things" % (self.entity.accountName ) )
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class TakePresentUnite( TakeThings ):
	"""
	����ֵ�����н�Ʒ��ȡ�ӿ�(�������Ͳ��������ŵ�)
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		"""
		sql = "SELECT sm_transactionID,sm_giftPackage,sm_silverCoins,sm_expiredTime,sm_account,sm_type,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and  sm_type in (0, 1, 2 ) and sm_expiredTime >= Now()"\
		% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		silverCoinsList = []
		transactionIDs = []	# ��¼������

		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			silverCoins   = int(result[2])
			expiredTime   = result[3]
			accountName   = result[4]
			presentType   = int(result[5])

			if presentType == 0 or presentType == 2:				#������ȡ��Ʒ
				if not giftPackageID or not expiredTime:
					continue
				if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
					continue
				self.entity.pcu_addDBID(  result[-1]  )				# �洢DBID��������ϣ����⼫��������ظ�������������ɻᱻ���
				self.thingsParam.append( ( presentType, transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
				if transactionID and transactionID in transactionIDs:
					try:
						g_logger.chargePresentExceptLog( "take present error has repetitious transactionID (%s)" %  transactionID )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					continue
				transactionIDs.append(transactionID)
				thingsIDs.append( giftPackageID )

			elif presentType == 1:									#������ȡ��Ԫ��
				if not transactionID or not silverCoins:
					continue
				if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
					continue
				self.entity.pcu_addDBID(  result[-1]  )				#�洢DBID����������ɻᱻ���
				self.thingsParam.append( ( presentType, transactionID, silverCoins, accountName, result[-1] ) )
				if transactionID in transactionIDs:
					try:
						g_logger.chargePresentExceptLog( "take silver error has repetitious transactionID (%s)" %  transactionID )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					continue
				transactionIDs.append(transactionID )
				silverCoinsList.append( silverCoins )

		if not silverCoinsList and not thingsIDs:								# û�з���Ҫ��Ľ��� ����
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		if silverCoinsList and thingsIDs:
			self.entity.takePresents( thingsIDs, silverCoinsList )
		elif silverCoinsList:
			self.entity.takeSilverCoins( silverCoinsList )
		elif thingsIDs:
			self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			if params[0] == 0 or params[0] == 2:
				try:
					g_logger.presentBackageLog( params[4], params[1], params[2], params[3] )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
			elif params[0] == 1:
				try:
					g_logger.presentSilverLog( params[3], params[1], params[2] )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )

class TakeChargeUniteSingle( TakeThings ):
	"""
	һ����ȡһ����Ʒ�ģ���/��������������
	"""
	def __init__( self, entity ):
		"""
		��ʼ��
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		�����ݿ���ȡ����Ҫ�ֶε�����
		��sm_type�У�0,2�ǻ����Ľ����洢���ͣ���ʾ�ý����������ڶ����Ŷ��ҽ�����Ʒ
		��6�������ݵķ��ʽӿڵı�ţ�ʵ���ϲ�Ӧ����Ϊ�洢���ͣ��Ǹ��������ţ���Ӧ����ʹ��
		����Ϊ������Ѿ����������ݿ��һЩ���ݵļ����ԣ��ݴ˱������6
		"""
		if item_id != 0:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and ( sm_type in ( 0, 2, 6 ) ) and sm_giftPackage = %s limit 1"\
			% ( self.entity.accountName, item_id )
		else:
			sql = "SELECT sm_transactionID,sm_giftPackage,sm_expiredTime,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and ( sm_type in ( 0, 2, 6 ) ) limit 1"\
			% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		��ȡ����Ҫ������
		"""
		# ���첽�ص�������£�entity Ϊ None�������ٵ���������п��ܷ����ģ�
		# ���������Ҫ��������������
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		transactionIDs = []	# ��¼������
		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			expiredTime   = result[2]
			accountName   = result[3]
			if not giftPackageID or not expiredTime:
				continue
			if self.entity.pcu_check( result[-1] ):				#����DBID�Ƿ��Ѿ����ڴ���
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# �洢DBID��������ϣ����⼫��������ظ�������������ɻᱻ���
			self.thingsParam.append( ( transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
			if transactionID and transactionID in transactionIDs:
				try:
					g_logger.chargePresentExceptLog( "take present error has repetitious transactionID (%s)" %  transactionID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				continue
			transactionIDs.append(transactionID)
			thingsIDs.append( giftPackageID )
		if not thingsIDs:
			# û�з���Ҫ���ID,ֱ�ӷ�����Ӧ���Ǵ�������.
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# ��ʾû���ҵ����������Ľ���
			INFO_MSG("account =%s type=0 or type=2 has no things" % (self.entity.accountName ) )
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		������Ϻ�д��־�ӿ�
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog(  params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

takeTypes = {
			csconst.PCU_TAKEPRESENTWITHOUTID	: TakePresentWithoutID,	#���������ŵĽ�Ʒ��ȡ����	0
			csconst.PCU_TAKESILVERCOINS			: TakeSilverCoins,		#��Ԫ����ȡ����				1
			csconst.PCU_TAKEPRESENT				: TakePresent,			#�������ŵĽ�Ʒ��ȡ����		2
			csconst.PCU_TAKECHARGE				: TakeCharge,			#��ֵ��ȡ����				3
			csconst.PCU_TAKECHARGEUNITE			: TakeChargeUnite,		#��Ʒ��ȡ(�������Ͳ�������)	4
			csconst.PCU_TAKEPRESENTUNITE		: TakePresentUnite,		#���н�Ʒ����ȡ(����ֵ��)	5
			csconst.PCU_TAKECHARGEUNITE_SINGLE		: TakeChargeUniteSingle,	#һ����ȡһ����Ʒ�ģ���/��������������
			}
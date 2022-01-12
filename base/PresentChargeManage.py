# -*- coding: gb18030 -*-
#
# $Id: PresentChargeManage.py

"""
奖励充值管理模块
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
	奖励和充值管理器
	"""
	def __init__( self, entity ):
		"""
		初始化
		@type	entity: role
		@param	entity: 玩家的实例
		注：模块将充值和领取奖励分开，原因是考虑到充值可能会同时接到多条消息，而且都是有效的请求(充值成功才会接到系统请求)，
		需要即时处理，而领取奖励一次只会有一条，并且奖励一次会全部领取，后面的请求可能已经被前一条处理。也需要防止玩家不停请求，
		所以需要一条一条处理。多余的请求直接摒弃。所以实际在请求队列中只会最多有一条领取请求和多条充值请求
		"""
		self.operations = []										# 记录玩家的请求的队列
		self.currOperation = None									# 记录玩家当前的请求
		self.entity  = weakref.proxy(entity)

	def havePresent( self ):
		"""
		判断是否有领取奖励在队列中
		"""
		if self.currOperation and not isinstance(self.currOperation,takeTypes[csconst.PCU_TAKECHARGE]):
		#如果当前处理的是充值，那么就去查询队列中是否有领取奖励
			return True
		for operation in self.operations:
			if not isinstance(operation,takeTypes[csconst.PCU_TAKECHARGE]):
				return True
		return False

	def takeThings( self, dataType, item_id ):
		"""
		获取数据库中的数据
		@type  dataType: UINT8
		@param dataType: 奖励(充值)类型
		@type  item_id: ITEM_ID
		@param item_id: 如果是物品奖励 就是物品的ID
		注:队列中只允许有一个领取奖励的请求和多个充值请求,领取奖励请求由玩家发出，可能有重复，所以同时只允许一个，充值请求
		为系统发出，每一个都为充值后触发，所以为有效请求。通常情况下队列中只会有一个请求。
		"""
		if dataType == csconst.PCU_TAKECHARGE or not self.havePresent():	# 如果是充值请求或者列表中没有领取请求
			self.operations.append( takeTypes[dataType]( self.entity ) )	# 实例一个该类型的操作,并放到队列中
			if not self.currOperation:										# 如果当前没有操作
				self.currOperation = self.operations.pop(0)					# 那么记录该请求实例
				self.currOperation( item_id )								# 执行操作
		else:
			self.entity.statusMessage( csstatus.PCU_YOU_ARE_BUSY )			# 提示正在处理请求

	def takeThingsSuccess( self ):
		"""
		操作成功，清除操作数据，并且取出队列中下一个请求
		"""
		if not self.currOperation:
			ERROR_MSG( "current has not operation" )
			return False
		self.currOperation.operationSuccess()
		self.currOperation = None
		if self.operations: 						#如果队列中还有请求,那么启动新请求
			self.currOperation = self.operations.pop(0)
			self.currOperation()
		return True

	def takeThingsFailed( self ):
		"""
		操作失败，清除操作数据，不清除数据库中的数据，并且取出队列中下一个请求。
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
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
		if self.operations: 						#如果队列中还有请求,那么启动新请求
			self.currOperation = self.operations.pop(0)
			self.currOperation()
		return True

	def getPresentTypes( self ):
		"""
		获取该账号目前拥有的物品奖励类型. 充值不在查询之内,过期的不在查询之内
		注：之所以这样做是因为该接口主要用于获取玩家身上已有的类型，用于显示给玩家选择领取，如果没有那么将不提供领取请求选项，
		过期的无法领取所以不作返回，充值的请求是系统领取所以不用返回
		"""
		sql = "SELECT sm_type FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type!= %s and ( ( sm_type !=0 and sm_type !=2 ) or  sm_expiredTime >= Now() )"\
		% ( self.entity.accountName, csconst.PCU_TAKECHARGE )
		BigWorld.executeRawDatabaseCommand( sql, self._onGetPresentTypes )

	def _onGetPresentTypes( self, results, rows, errstr ):
		"""
		获取了该账号拥有的奖励类型数据
		注：这里把获取的结果发到cell上，因为一种奖励类型一次会全部取出，所以每种类型只显示一次。使用了set去除重复的项。
		"""
		if errstr:
			ERROR_MSG( "get PresentTypes fail!" )
			return False
		result = results[0]  # results的索引0一定有值 即使为空的list
		types  = []
		if result:
			result.sort()
			types = list( set( result ) )
		self.entity.cell.pcu_onGetPresentTypes( types )

class TakeThings:
	"""
	领取物品的基础类
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		self.thingsParam = []		#存储取出的数据
		self.entity      = entity

	def getThingsDatas( self ):
		"""
		获取物品的数据
		"""
		return self.thingsParam

	def operationFaile( self ):
		"""
		清除玩家身上记录的该操作的占用的DBID
		清除数据 释放entity
		"""
		for param in self.thingsParam:
			#清除玩家身上占用的DBID,该DBID就是在处理的数据在数据库中的DBID,防止极端情况下会重复处理数据
			self.entity.pcu_removeDBID( param[-1] )
		self.thingsParam = []
		self.entity      = None

	def operationSuccess( self ):
		"""
		清除玩家身上记录的该操作的占用的DBID
		清除数据库中的数据
		写日志
		释放entity
		"""
		dbids = []
		for param in self.thingsParam:
			dbids.append( "id = %s" % param[-1] )
			#清除玩家身上占用的DBID,该DBID就是在处理的数据在数据库中的DBID,防止极端情况下会重复处理数据
			self.entity.pcu_removeDBID( param[-1] )
		syntax = " or ".join( dbids )		#一次全部删除
		sql  = "DELETE FROM custom_ChargePresentUnite WHERE %s" % syntax
		BigWorld.executeRawDatabaseCommand( sql, self._onOperationSuccess )
		self.entity   = None

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口,此接口需要被子类覆盖
		"""
		pass

class TakePresentWithoutID( TakeThings ):
	"""
	领取没有订单号的奖品奖励
	"""
	def __init__( self,  entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
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
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		thingsIDs   = []		#记录物品的ID
		for result in results:	#分离数据
			giftPackageID = result[0]					# 拆分出物品的ID
			expiredTime   = result[1]							# 获取时间
			accountName   = result[2]
			if self.entity.pcu_check( result[-1] ):				# 检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# 存储DBID到玩家身上，避免极端情况下重复处理，当操作完成会被清除
			self.thingsParam.append( ( giftPackageID, expiredTime, accountName, result[-1] ) ) # 记录数据
			thingsIDs.append( giftPackageID )					# 记录需要发送到CELL上的数据
		if not thingsIDs:										# 没有符合要求的ID 直接返回 这应该是错误的情况，因为既然玩家能请求
																#说明身上一定是会有该类型的数据没有处理。
			INFO_MSG("account = %s type = 0 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )		# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )
		return True

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志和清理数据
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[2], None, params[0], params[1] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakeSilverCoins( TakeThings  ):
	"""
	带订单号的银元宝发送接口
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
		"""
		sql = "SELECT sm_transactionID,sm_silverCoins,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 1" % ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas(self, results, rows, errstr ):
		"""
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take SilverCoins fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		SilverCoinsList   = []		#记录银元宝的数量
		transactionIDs    = []		#记录订单号
		for result in results:
			transactionID  = result[0]
			silverCoins    = int( result[1])
			accountName     = result[2]
			if not transactionID or not silverCoins:
				continue
			if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )				#存储DBID，当操作完成会被清除
			self.thingsParam.append( ( transactionID, silverCoins, accountName, result[-1] ) )
			if transactionID in transactionIDs:
				try:
					g_logger.chargePresentExceptLog( "take silver error has repetitious transactionID (%s)" %  transactionID )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				continue
			transactionIDs.append(transactionID )
			SilverCoinsList.append( silverCoins )
		if not SilverCoinsList:								#没有符合要求的银元宝数 直接返回
			INFO_MSG("account = %s type = 1 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		self.entity.takeSilverCoins( SilverCoinsList )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentSilverLog( params[2], params[0], params[1] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakePresent( TakeThings ):
	"""
	带订单号的奖品发送接口
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
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
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
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
			if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# 存储DBID到玩家身上，避免极端情况下重复处理，当操作完成会被清除
			self.thingsParam.append( (transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
			thingsIDs.append( giftPackageID )
		if not thingsIDs:										# 没有符合要求的ID 直接返回 这应该是错误的情况，因为既然玩家能请求
																#说明身上一定是会有该类型的数据没有处理。
			INFO_MSG("account ID = %s type = 2 has no things" % (self.entity.accountName )  )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

class TakeCharge( TakeThings ):
	"""
	获取充值的数据
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
		"""
		sql = "SELECT sm_transactionID,sm_chargeType,sm_silverCoins,sm_goldCoins,sm_account,sm_account,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and sm_type = 3" % ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
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
			if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )	#存储DBID，当操作完成会被清除
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
		if not silverCoinsList and goldList:			#没有符合要求的元宝数 直接返回
			ERROR_MSG("account = %s type = 3 has no things" % (self.entity.accountName )  )
			self.entity.takeOverFailed()
			return False
		self.entity.takeChargedMoney( silverCoinsList, goldList )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentChargeLog( params[4], params[0], params[1], params[3], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class TakeChargeUnite( TakeThings ):
	"""
	奖品领取接口(带订单和不带订单号的)
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
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
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		transactionIDs = []	# 记录订单号
		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			expiredTime   = result[2]
			accountName   = result[3]
			if not giftPackageID or not expiredTime:
				continue
			if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# 存储DBID到玩家身上，避免极端情况下重复处理，当操作完成会被清除
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
			# 没有符合要求的ID,直接返回这应该是错误的情况.
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			INFO_MSG("account =%s type=0 or type=2 has no things" % (self.entity.accountName ) )
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog( params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


class TakePresentUnite( TakeThings ):
	"""
	除充值外所有奖品领取接口(带订单和不带订单号的)
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
		"""
		sql = "SELECT sm_transactionID,sm_giftPackage,sm_silverCoins,sm_expiredTime,sm_account,sm_type,id FROM custom_ChargePresentUnite WHERE sm_account = '%s' and  sm_type in (0, 1, 2 ) and sm_expiredTime >= Now()"\
		% ( self.entity.accountName )
		BigWorld.executeRawDatabaseCommand( sql, self._onQueryDatas )

	def _onQueryDatas( self, results, rows, errstr ):
		"""
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		silverCoinsList = []
		transactionIDs = []	# 记录订单号

		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			silverCoins   = int(result[2])
			expiredTime   = result[3]
			accountName   = result[4]
			presentType   = int(result[5])

			if presentType == 0 or presentType == 2:				#处理领取物品
				if not giftPackageID or not expiredTime:
					continue
				if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
					continue
				self.entity.pcu_addDBID(  result[-1]  )				# 存储DBID到玩家身上，避免极端情况下重复处理，当操作完成会被清除
				self.thingsParam.append( ( presentType, transactionID,giftPackageID,expiredTime, accountName, result[-1] ) )
				if transactionID and transactionID in transactionIDs:
					try:
						g_logger.chargePresentExceptLog( "take present error has repetitious transactionID (%s)" %  transactionID )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					continue
				transactionIDs.append(transactionID)
				thingsIDs.append( giftPackageID )

			elif presentType == 1:									#处理领取银元宝
				if not transactionID or not silverCoins:
					continue
				if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
					continue
				self.entity.pcu_addDBID(  result[-1]  )				#存储DBID，当操作完成会被清除
				self.thingsParam.append( ( presentType, transactionID, silverCoins, accountName, result[-1] ) )
				if transactionID in transactionIDs:
					try:
						g_logger.chargePresentExceptLog( "take silver error has repetitious transactionID (%s)" %  transactionID )
					except:
						g_logger.logExceptLog( GET_ERROR_MSG() )
					continue
				transactionIDs.append(transactionID )
				silverCoinsList.append( silverCoins )

		if not silverCoinsList and not thingsIDs:								# 没有符合要求的奖励 返回
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
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
		处理完毕后写日志接口
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
	一次领取一个物品的（带/不带订单）奖励
	"""
	def __init__( self, entity ):
		"""
		初始化
		"""
		TakeThings.__init__( self, entity )

	def __call__( self, item_id ):
		"""
		到数据库中取出需要字段的数据
		在sm_type中，0,2是基本的奖励存储类型，表示该奖励不依赖于订单号而且奖励物品
		而6则是数据的访问接口的编号，实际上不应该作为存储类型，是个无意义编号，不应该再使用
		但是为了配合已经存在于数据库的一些数据的兼容性，暂此保留编号6
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
		获取了需要的数据
		"""
		# 在异步回调的情况下，entity 为 None或已销毁的情况总是有可能发生的，
		# 因此我们需要对这个情况做处理。
		if self.entity is None or self.entity.isDestroyed: 
			self.entity.takeOverFailed()
			return False

		if errstr:
			ERROR_MSG( "take Present fail!" )
			self.entity.takeOverFailed()
			return False
		if not results:
			INFO_MSG( "have no Presnet" )
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			self.entity.takeOverFailed()
			return False
		thingsIDs = []
		transactionIDs = []	# 记录订单号
		for result in results:
			transactionID = result[0]
			giftPackageID = result[1]
			expiredTime   = result[2]
			accountName   = result[3]
			if not giftPackageID or not expiredTime:
				continue
			if self.entity.pcu_check( result[-1] ):				#检查该DBID是否已经正在处理
				continue
			self.entity.pcu_addDBID(  result[-1]  )				# 存储DBID到玩家身上，避免极端情况下重复处理，当操作完成会被清除
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
			# 没有符合要求的ID,直接返回这应该是错误的情况.
			self.entity.statusMessage( csstatus.PCU_HAVE_NO_PRESENT )			# 提示没有找到符合条件的奖励
			INFO_MSG("account =%s type=0 or type=2 has no things" % (self.entity.accountName ) )
			self.entity.takeOverFailed()
			return False
		self.entity.cell.takePresent( thingsIDs )

	def _onOperationSuccess( self, results, rows, errstr ):
		"""
		处理完毕后写日志接口
		"""
		for params in self.thingsParam:
			try:
				g_logger.presentBackageLog(  params[3], params[0], params[1], params[2] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

takeTypes = {
			csconst.PCU_TAKEPRESENTWITHOUTID	: TakePresentWithoutID,	#不带订单号的奖品领取类型	0
			csconst.PCU_TAKESILVERCOINS			: TakeSilverCoins,		#银元宝领取类型				1
			csconst.PCU_TAKEPRESENT				: TakePresent,			#带订单号的奖品领取类型		2
			csconst.PCU_TAKECHARGE				: TakeCharge,			#充值领取类型				3
			csconst.PCU_TAKECHARGEUNITE			: TakeChargeUnite,		#奖品领取(带订单和不带订单)	4
			csconst.PCU_TAKEPRESENTUNITE		: TakePresentUnite,		#所有奖品的领取(除充值外)	5
			csconst.PCU_TAKECHARGEUNITE_SINGLE		: TakeChargeUniteSingle,	#一次领取一个物品的（带/不带订单）奖励
			}
# -*- coding: gb18030 -*-

"""
帮会会标管理器，负责帮会会标的存取、更新等功能 by 姜毅 8:52 2010-1-13
"""

import BigWorld
from bwdebug import *
from Function import Functor
import Const
import csstatus

class TongSignMgr:
	"""
	帮会会标管理器
	这个管理器只会创建在第一个启动的baseapp上。
	"""
	_instance = None
	def __init__( self ):
		assert TongSignMgr._instance is None		# 不允许有两个以上的实例
		INFO_MSG( "TongSignMgr create." )
		self.__datas = {}			# 对应数据库的帮会图标动态数据(运行时数据，base崩了就没戏了)
		self.__iconDatas = {}		# 对应数据库的图标数据(运行时数据，base崩了就没戏了)
		self.__dymDatas = {}		# 实时的帮会会标动态数据(运行时数据，base崩了就没戏了)
		# 其结构允许同名帮会，但DBID不能相同
		# self.__datas = { tongDBID:IconMD5, tongDBID:IconMD5, ...}
		TongSignMgr._instance = self
		
	@staticmethod
	def instance():
		"""
		通过 action id 获取action实例
		"""
		if TongSignMgr._instance is None:
			TongSignMgr._instance = TongSignMgr()
		return TongSignMgr._instance
		
	# --------------------------------------------------------------------------------------------
	def userTongSignDatas( self ):
		"""
		"""
		query = "SELECT * FROM custom_TongSignTable;"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onUserTongSignDatas ) )
		
	def tongSignDatas( self ):
		"""
		"""
		query = "SELECT id, sm_tongSignMD5 FROM tbl_TongEntity;"
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onTongSignDatas ) )
		
	def __onUserTongSignDatas( self, result, dummy, errstr ):
		"""
		组织自定义帮会图标数据
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "userTongSign: get datas failed!" )
			return
			
		if result is None or len( result ) <= 0:
			INFO_MSG( "custom_TongSignTable no datas" )
		else:
			for data in result:
				self.__datas[long(data[1])] = data[4]
				self.__iconDatas[long(data[1])] = data[3]
			
	def __onTongSignDatas( self, result, dummy, errstr ):
		"""
		组织帮会图标数据
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TongSign: get datas failed!" )
			return
			
		if result is None or len( result ) <= 0:
			INFO_MSG( "tbl_TongEntity no tong sign datas" )
		else:
			for data in result:
				if data[1] is None or data[1] == "":
					continue
				self.__dymDatas[long(data[0])] = data[1]
			
	# --------------------------------------------------------------------------------------------
	def getTongSignDatas( self ):
		"""
		"""
		return self.__datas
		
	def getDymTongSignDatas( self ):
		"""
		"""
		return self.__dymDatas
		
	def getDymTongSignMD5( self, tongDBID ):
		"""
		获得某帮会会标
		"""
		if tongDBID not in self.__dymDatas:
			return ""
		return self.__dymDatas[tongDBID]
		
	def getTongSignStrByDBID( self, tongDBID ):
		"""
		通过DBID获得帮会会标
		"""
		if not tongDBID in self.__iconDatas:
			return ""
		return self.__iconDatas[tongDBID]
		
	def hasUserTongSignDatas( self, tongDBID, iconMD5 ):
		"""
		是否有该自定义图标
		"""
		if tongDBID not in self.__datas:
			return False
		return self.__datas[tongDBID] == iconMD5
		
	def hasDymTongSignDatas( self, tongDBID ):
		"""
		该帮会是否有会标
		"""
		return tongDBID in self.__dymDatas
	# --------------------------------------------------------------------------------------------
	def submitTongSign( self, tongDBID, tongName, iconString, iconMD5, playerMB ):
		"""
		上传帮会会标
		"""
		iconBaseString = BigWorld.escape_string(iconString)
		iconBaseMD5 = BigWorld.escape_string(iconMD5)
		if self.__iconDatas.has_key( tongDBID ) and self.__iconDatas[tongDBID] == iconString:
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_HAS_NOW, "" )
			return
		if not tongDBID in self.__datas:
			query = "REPLACE INTO custom_TongSignTable ( sm_TongDBID, sm_TongName, sm_Icon, sm_IconMD5  )Value ( %d, '%s','%s','%s' )"% ( tongDBID, tongName, iconBaseString, iconBaseMD5 )
		else:
			if self.__datas[tongDBID] == iconMD5:
				return
			query = "update custom_TongSignTable set sm_Icon = '%s',sm_IconMD5 = '%s' where sm_TongDBID = %d"%( iconBaseString, iconBaseMD5, tongDBID )
			
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__onSubmitTongSign, tongDBID, iconString, iconMD5, playerMB ) )
		
	def __onSubmitTongSign( self, tongDBID, iconString, iconMD5, playerMB, result, dummy, errstr ):
		"""
		上传帮会会标回调
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TongSign: submitTongSign failed! tongDBID: %i, iconMD5: %s"%( tongDBID, iconMD5 ) )
			playerMB.client.onStatusMessage( csstatus.TONG_SIGN_SUBMIT_FAILED, "" )
			return
		self.__datas[tongDBID] = iconMD5
		self.__iconDatas[tongDBID] = iconString
		playerMB.onTong_submitSign( iconMD5 )
	# --------------------------------------------------------------------------------------------
	def changeTongSign( self, tongDBID, iconMD5 ):
		"""
		更换帮会会标
		"""
		if iconMD5 is None:
			 iconMD5 == ""
		self.__dymDatas[tongDBID] = iconMD5
	
	# --------------------------------------------------------------------------------------------
	def removeTongSign( self, tongDBID, iconMD5  ):
		"""
		define method
		移除一个帮会会标
		"""
		if not tongDBID in self.__datas:
			return
		query = "delete from custom_TongSignTable where sm_TongDBID=%i and sm_IconMD5='%s';" % (tongDBID, iconMD5)
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTongSignCB, tongDBID, iconMD5 ) )
		
	def __removeTongSignCB( self, tongDBID, iconMD5, result, dummy, errstr):
		"""
		移除一个帮会会标回调
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: delete TongSing failed! tongDBID: %I, IconMD5: %s"%( tongDBID, iconMD5 ) )
			return
		self.__datas.pop( tongDBID )

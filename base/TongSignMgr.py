# -*- coding: gb18030 -*-

"""
��������������������Ĵ�ȡ�����µȹ��� by ���� 8:52 2010-1-13
"""

import BigWorld
from bwdebug import *
from Function import Functor
import Const
import csstatus

class TongSignMgr:
	"""
	����������
	���������ֻ�ᴴ���ڵ�һ��������baseapp�ϡ�
	"""
	_instance = None
	def __init__( self ):
		assert TongSignMgr._instance is None		# ���������������ϵ�ʵ��
		INFO_MSG( "TongSignMgr create." )
		self.__datas = {}			# ��Ӧ���ݿ�İ��ͼ�궯̬����(����ʱ���ݣ�base���˾�ûϷ��)
		self.__iconDatas = {}		# ��Ӧ���ݿ��ͼ������(����ʱ���ݣ�base���˾�ûϷ��)
		self.__dymDatas = {}		# ʵʱ�İ���궯̬����(����ʱ���ݣ�base���˾�ûϷ��)
		# ��ṹ����ͬ����ᣬ��DBID������ͬ
		# self.__datas = { tongDBID:IconMD5, tongDBID:IconMD5, ...}
		TongSignMgr._instance = self
		
	@staticmethod
	def instance():
		"""
		ͨ�� action id ��ȡactionʵ��
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
		��֯�Զ�����ͼ������
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
		��֯���ͼ������
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
		���ĳ�����
		"""
		if tongDBID not in self.__dymDatas:
			return ""
		return self.__dymDatas[tongDBID]
		
	def getTongSignStrByDBID( self, tongDBID ):
		"""
		ͨ��DBID��ð����
		"""
		if not tongDBID in self.__iconDatas:
			return ""
		return self.__iconDatas[tongDBID]
		
	def hasUserTongSignDatas( self, tongDBID, iconMD5 ):
		"""
		�Ƿ��и��Զ���ͼ��
		"""
		if tongDBID not in self.__datas:
			return False
		return self.__datas[tongDBID] == iconMD5
		
	def hasDymTongSignDatas( self, tongDBID ):
		"""
		�ð���Ƿ��л��
		"""
		return tongDBID in self.__dymDatas
	# --------------------------------------------------------------------------------------------
	def submitTongSign( self, tongDBID, tongName, iconString, iconMD5, playerMB ):
		"""
		�ϴ������
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
		�ϴ������ص�
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
		���������
		"""
		if iconMD5 is None:
			 iconMD5 == ""
		self.__dymDatas[tongDBID] = iconMD5
	
	# --------------------------------------------------------------------------------------------
	def removeTongSign( self, tongDBID, iconMD5  ):
		"""
		define method
		�Ƴ�һ�������
		"""
		if not tongDBID in self.__datas:
			return
		query = "delete from custom_TongSignTable where sm_TongDBID=%i and sm_IconMD5='%s';" % (tongDBID, iconMD5)
		BigWorld.executeRawDatabaseCommand( query, Functor( self.__removeTongSignCB, tongDBID, iconMD5 ) )
		
	def __removeTongSignCB( self, tongDBID, iconMD5, result, dummy, errstr):
		"""
		�Ƴ�һ�������ص�
		"""
		if errstr:
			ERROR_MSG(errstr)
			ERROR_MSG( "TiShou: delete TongSing failed! tongDBID: %I, IconMD5: %s"%( tongDBID, iconMD5 ) )
			return
		self.__datas.pop( tongDBID )

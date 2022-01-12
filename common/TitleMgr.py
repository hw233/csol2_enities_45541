# -*- coding: gb18030 -*-

# $Id: TitleMgr.py,v 1.1 2008-07-19 01:45:48 wangshufeng Exp $

import Language
from bwdebug import *
from config.Title import Datas as g_TitleData
from config.CreditTitle import Datas as c_Titles
from config.TeachCreditTitle import Datas as teachCreditTitleData
import csstatus

class TitleMgr:
	"""
	�ƺ����ü�����
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert TitleMgr._instance is None
		TitleMgr._instance = self
		# key == ��Ӧ�ĳƺ�id
		# value == [( id, prestige ), ...]
		# like as { id : [(id, prestige), ...], ...}
		self._datas = g_TitleData #ͨ���ֵ䷽ʽ����Title.Datas������Դֻ��һ��
		self._teachCreditData = {}	# like as:{ titleID:{"preTitle":1,"titleID":2,"teachCreditRequire":3333}, ... }
		for data in teachCreditTitleData:
			self._teachCreditData[data["titleID"]] = data
			
	def getData( self, titleID ):
		"""
		����titleID�������
		
		@param factionID: ����id ���
		@return: [( id, prestige ), ...]
		"""
		try:
			return self._datas[ titleID ]
		except KeyError:
			ERROR_MSG( "Title %s has no data." % ( titleID ) )
			return None
			
	def getTeachTitleRequire( self, titleID ):
		"""
		���������titleID�������
		"""
		return self._teachCreditData[titleID]

	def getTeachPreTitle( self, titleID ):
		"""
		���ǰ�õ�ʦ���ƺ�
		"""
		return self._teachCreditData[titleID]["preTitleID"]
		
	def isTeachTitle( self, titleID ):
		"""
		�Ƿ�ʦ���ƺ�
		"""
		return titleID in self._teachCreditData

	def getTeachCreditRequire( self, titleID ):
		"""
		��óƺ����蹦ѫ
		"""
		return self._teachCreditData[titleID]["teachCreditRequire"]

	def getName( self, titleID ):
		"""
		����titleID�������
		"""
		try:
			return self._datas[ titleID ][ "name" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return ""
			
	def getOrder( self, titleID ):
		"""
		����titleID���order
		"""
		try:
			return self._datas[ titleID ][ "order" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
	def getDescription( self, titleID ):
		"""
		����titleID�������
		"""
		try:
			return self._datas[ titleID ][ "Description" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return ""
			
	def getType( self, titleID ):
		"""
		����titleID��óƺŵ�����
		"""
		try:
			return self._datas[ titleID ][ "type" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
			
	def isTimeLimit( self, titleID ):
		"""
		�ƺ��Ƿ���ʱ������
		
		rtype : BOOL
		"""
		try:
			time = self._datas[ titleID ][ "limitTime" ]
			return time > 0
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return False
			
			
	def getSkillID( self, titleID ):
		"""
		����titleID��óƺŶ�Ӧ�ļ���id
		"""
		try:
			return self._datas[ titleID ][ "skillID" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
	def getTeacherTitle( self, value ):
		"""
		���ݹ�ѫֵ�����Ӧ�ĳƺ�
		
		@param value : ��ѫֵ
		@type value : INT32
		
		29:Ǭ����ʦ�ĳƺ�id
		28:������ʦ�ĳƺ�id
		27:�ķ���ʦ�ĳƺ�id
		26:��ҵ��ʦ�ĳƺ�id
		25:�����ʦ�ĳƺ�id
		24:������ʦ�ĳƺ�id
		"""
		if value > 6000:
			return 29
		elif value > 3000:
			return 28
		elif value > 1000:
			return 27
		elif value > 500:
			return 26
		elif value > 200:
			return 25
		elif value > 1:
			return 24
		else:
			return 0
	def getTitleIDByCredit( self, creditID, value ):
		"""
		�������ʵ��ID��ö�Ӧ�����ĳƺ�ID by����
		"""
		if creditID not in c_Titles: return -1
		titleID = 0
		try:
			cTitleData = c_Titles[creditID]
			for ct in cTitleData:
				if value < ct: break
				titleID = int( cTitleData[ct][0] )
			return titleID
		except:
			return 0
			
			
	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = TitleMgr()
		return SELF._instance
		
		
#
# $Log: not supported by cvs2svn $
#
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
	称号配置加载器
	"""
	_instance = None
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert TitleMgr._instance is None
		TitleMgr._instance = self
		# key == 对应的称号id
		# value == [( id, prestige ), ...]
		# like as { id : [(id, prestige), ...], ...}
		self._datas = g_TitleData #通过字典方式引用Title.Datas，数据源只有一份
		self._teachCreditData = {}	# like as:{ titleID:{"preTitle":1,"titleID":2,"teachCreditRequire":3333}, ... }
		for data in teachCreditTitleData:
			self._teachCreditData[data["titleID"]] = data
			
	def getData( self, titleID ):
		"""
		根据titleID获得数据
		
		@param factionID: 势力id 编号
		@return: [( id, prestige ), ...]
		"""
		try:
			return self._datas[ titleID ]
		except KeyError:
			ERROR_MSG( "Title %s has no data." % ( titleID ) )
			return None
			
	def getTeachTitleRequire( self, titleID ):
		"""
		根据申请的titleID获得数据
		"""
		return self._teachCreditData[titleID]

	def getTeachPreTitle( self, titleID ):
		"""
		获得前置的师父称号
		"""
		return self._teachCreditData[titleID]["preTitleID"]
		
	def isTeachTitle( self, titleID ):
		"""
		是否师父称号
		"""
		return titleID in self._teachCreditData

	def getTeachCreditRequire( self, titleID ):
		"""
		获得称号所需功勋
		"""
		return self._teachCreditData[titleID]["teachCreditRequire"]

	def getName( self, titleID ):
		"""
		根据titleID获得名称
		"""
		try:
			return self._datas[ titleID ][ "name" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return ""
			
	def getOrder( self, titleID ):
		"""
		根据titleID获得order
		"""
		try:
			return self._datas[ titleID ][ "order" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
	def getDescription( self, titleID ):
		"""
		根据titleID获得描述
		"""
		try:
			return self._datas[ titleID ][ "Description" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return ""
			
	def getType( self, titleID ):
		"""
		根据titleID获得称号的类型
		"""
		try:
			return self._datas[ titleID ][ "type" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
			
	def isTimeLimit( self, titleID ):
		"""
		称号是否有时间限制
		
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
		根据titleID获得称号对应的技能id
		"""
		try:
			return self._datas[ titleID ][ "skillID" ]
		except KeyError:
			ERROR_MSG( "title %s is not exist." % ( titleID ) )
			return 0
			
	def getTeacherTitle( self, value ):
		"""
		根据功勋值获得相应的称号
		
		@param value : 功勋值
		@type value : INT32
		
		29:乾坤宗师的称号id
		28:九州宗师的称号id
		27:四方宗师的称号id
		26:授业宗师的称号id
		25:解惑宗师的称号id
		24:传道宗师的称号id
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
		根据玩家实例ID获得对应声望的称号ID by姜毅
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
# -*- coding: gb18030 -*-
#
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import BigWorld
import csdefine
import csstatus
import csconst
import random
from bwdebug import *
from Function import Functor
from ObjectScripts.GameObject import GameObject

class TongTerritoryManager:
	"""
	领地管理器负责调度领地的创建， 与管理所有的领地。
	我们的帮会的设计是没有成员上线则帮会ENTITY不会被创建， 而领地的规则是任何人都可以去其他帮会的领地
	所以该领地的存在不代表帮会ENTITY的存在， 而帮会ENTITY是需要知道领地MAILBOX的，所以我的做法是如果领地被创建
	帮会ENTITY已经被创建则直接注册给帮会ENTITY，否则则由帮会ENTITY被创建时，帮会ENTITY主动要求该管理器将领地注册给他,
	另外即使自己帮会的副本被创建过， 但领地没有成员进入也不会创建， 因此这么设计。
	"""
	def __init__( self ):
		self.territorys = {}	# 这里面保存着所有帮会的领地

	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		pass
		
	def onTongDismiss( self, tongDBID ):
		"""
		define method.
		某个帮会被解散了，准备销毁它的相关数据
		"""
		# 有可能帮会刚创建没有人曾经进入过领地帮会又解散了，因此需要判断
		if self.territorys.has_key( tongDBID ):
			territory = self.territorys.pop( tongDBID )
			territory.onTongDismiss()
	
	def findTerritoryByTongDBID( self, tongDBID ):
		"""
		寻找某帮会的领地
		"""
		if tongDBID in self.territorys:
			return self.territorys[ tongDBID ]
		return None
		
	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: 帮会DBID
		@param territory:领地副本的basemailbox
		"""
		self.territorys[ tongDBID ] = territory
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onRegisterTerritory( territory )
		
	def onTongEntityRequestTerritory( self, tongEntity, tongDBID ):
		"""
		define method.
		帮会被创建后向管理器要领地副本的mailbox (如果他被创建了)
		"""
		if not tongDBID in self.territorys:
			return
		tongEntity.onRegisterTerritory( self.territorys[ tongDBID ] )
		
	def onRequestCreateTongTerritory( self, spaceDomain, tongDBID ):
		"""
		define method.
		spaceDomain 向管理器请求获得 某帮会领地的信息去创建一个帮会领地副本
		@param spaceDomain: 副本领域类
		@param tongDBID	  : 请求进入领地的帮会
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onRequestCreateTongTerritory( spaceDomain )
		else:
			cmd = "select sm_level, sm_jk_level, sm_ssd_level, sm_ck_level, sm_tjp_level, sm_sd_level, sm_yjy_level, sm_shenshouType, sm_shenshouReviveTime from tbl_TongEntity where id = %i;" % tongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.onQueryDB_onCreateTongTerritoryCallBack, spaceDomain, tongDBID ) )
	
	def onQueryDB_onCreateTongTerritoryCallBack( self, spaceDomain, tongDBID, result, dummy, error ):
		"""
		删除成员信息 数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			spaceDomain.onCreateTongTerritoryError( tongDBID )
			return

		try:
			ysdt_level = int( result[0][0] )
			jk_level = int( result[0][1] )
			ssd_level = int( result[0][2] )
			ck_level = int( result[0][3] )
			tjp_level = int( result[0][4] )
			sd_level = int( result[0][5] )
			yjy_level = int( result[0][6] )
			shenshouType = int( result[0][7] )
			shenshouReviveTime = int( result[0][8] )
			spaceDomain.onCreateTongTerritory( tongDBID, ysdt_level, jk_level, ssd_level, ck_level, tjp_level, sd_level, yjy_level, shenshouType, shenshouReviveTime )
		except IndexError:
			ERROR_MSG( "onQueryDB_onCreateTongTerritoryCallBack is error!" )
			spaceDomain.onCreateTongTerritoryError( tongDBID )
			
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""	
		pass

#
# $Log: not supported by cvs2svn $
#
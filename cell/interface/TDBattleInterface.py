# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import csstatus
import VehicleHelper
import SkillTargetObjImpl
from Resource.SkillLoader import g_skills
from bwdebug import *

SKILL_ID = 123549001

class TDBattleInterface:
	"""
	仙魔论战接口
	"""
	def __init__( self ):
		pass
	
	def TDB_onClickActButton( self, srcEntityID ):
		"""
		Exposed method
		客户端点击活动图标
		"""
		BigWorld.globalData["TaoismAndDemonBattleMgr"].onClickActButton( self.base, self.getCamp() )
		
	def TDB_showTransWindow( self ):
		"""
		define method
		显示传送界面
		"""
		endTime = BigWorld.globalData["TDBattleEndTime"]
		record = self.query( "TDB_transData", None )
		if record and record[2] == int( endTime ):
			if record[3]:		# 已经回城复活了
				self.client.TDB_showTransWindow( 3 )		# 传送和传回按钮都显示
			else:
				self.client.TDB_showTransWindow( 2 )		# 显示回传按钮
		else:
			self.client.TDB_showTransWindow( 1 )		# 显示传送按钮
			if record:
				self.remove( "TDB_transData" )

	def TDB_onPlayerLogin( self, srcEntityID ):
		"""
		Exposed method
		玩家登陆
		"""
		if srcEntityID != self.id: return
		record = self.query( "TDB_transData", None )
		if record:
			if not BigWorld.globalData.has_key( "TDBattleEndTime" ) or BigWorld.globalData["TDBattleEndTime"] != record[2]:
				self.remove( "TDB_transData" )
		BigWorld.globalData["TaoismAndDemonBattleMgr"].onPlayerLogin( self.base, self.getName() )

	def addFightMonster( self, monsterID ):
		"""
		define method
		当某个怪物把自己设为当前战斗对象时，玩家记录此怪物id
		"""
		fightMonster = self.queryTemp( "TDB_fightingMonster ", [] )
		if monsterID not in fightMonster:
			fightMonster.append( monsterID )
			self.setTemp( "TDB_fightingMonster ", fightMonster )
		
		if not self.findBuffsByBuffID( 199021 ):
			try:
				spell = g_skills[ SKILL_ID ]
			except:
				ERROR_MSG( "%i: skill %i not exist." % ( self.id, SKILL_ID ) )
				return
			spell.use( self, SkillTargetObjImpl.createTargetObjEntity( self ) )			# 给玩家加Buff_199021，使玩家受到治疗时可以将治疗量通知给仙魔论战管理器

	def removeFightMonster( self, monsterID ):
		"""
		define method
		玩家删除此怪物id
		"""
		fightMonster = self.queryTemp( "TDB_fightingMonster ", [] )
		if monsterID in fightMonster:
			fightMonster.remove( monsterID )
			self.setTemp( "TDB_fightingMonster ", fightMonster )

	def TDB_transToActPos( self, srcEntityID ):
		"""
		Exposed method
		传送到活动区域
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return
		if not BigWorld.globalData.has_key( "TDBattleEndTime" ):
			return
			
		endTime = BigWorld.globalData[ "TDBattleEndTime" ]
		self.set( "TDB_transData", [ self.spaceType, tuple( self.position ), int( endTime ), False ] )
		if self.getCamp() == csdefine.ENTITY_CAMP_TAOISM:
			space = csconst.TDB_TRANSPORT_SPACE_T
			position = csconst.TDB_TRANSPORT_POSITION_T
		else:
			space =  csconst.TDB_TRANSPORT_SPACE_D
			position = csconst.TDB_TRANSPORT_POSITION_D
		self.gotoSpace( space, position, self.direction )
		
	def TDB_transportBack( self, srcEntityID ):
		"""
		Exposed method
		回到传送前位置
		"""
		if self.id != srcEntityID:
			return
		if not self.transConditionCheck():
			return
			
		record = self.query( "TDB_transData", None )
		if record:
			self.remove( "TDB_transData" )
			self.gotoSpace( record[0], record[1], self.direction )
		else:
			ERROR_MSG( "Player(ID: %s) has not record position!" % self.id )
	
	def TDB_onReviveOnCity( self ):
		"""
		回城复活了
		"""
		record = self.query( "TDB_transData", None )
		if record:
			record[3] = True
		
	def TDB_onBattleOver( self, endTime ):
		"""
		define method
		战斗结束（boss死亡或者活动结束）
		
		@param endTime : type INT32
		@param endTime : 当次活动的结束时间
		"""
		if self.getCurrentSpaceType() != csdefine.SPACE_TYPE_NORMAL:
			return
		record = self.query( "TDB_transData", None )
		if not record or record[2] != endTime:			# 说明玩家之前没有点传送或者不是本次活动点了传送
			return
		self.client.TDB_showActTip()
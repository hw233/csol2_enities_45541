# -*- coding: gb18030 -*-
#
# $Id: Space.py,v 1.8 2008-04-16 05:51:18 phw Exp $

"""
"""

import random
import Language
import Love3
import csdefine
import csstatus
from bwdebug import *
from GameObject import GameObject
import ECBExtend
import Language

class Space( GameObject ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		GameObject.__init__( self )
		self._spawnFile	=	""			 # 获取该地图的出生点配置文件
		self.isDiffCampTeam = False							# 是否允许不同阵营的玩家组队
		self.bufferCount = 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLoadEntityProperties_( self, section ) :
		"""
		virtual method. template method, called by GameObject::load() when an entity initialized.
		initialize entity's properties from PyDataSection
		note: all properties here must be defined in ".def" fine
		@type			section : PyDataSection
		@param			section : python data section load from entity's coonfig file
		@return					: None
		"""
		GameObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "dirmapping", section["dirMapping"].asString )
		self.setEntityProperty( "timeon", section["TimeOn"].asInt )

		#self.bufferCount = section.readInt("spaceItemBuffers")


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def load( self, section ) :
		"""
		virtual method.
		load properts' datas
		@type		section : PyDataSection
		@param		section : python data section load from npc's coonfig file
		"""
		GameObject.load( self, section )
		self._spawnFile = section.readString("spawnFile") 								   # 打开指定地图的配置
		self._spawnSection = Language.openConfigSection( self._spawnFile )
		if section.has_key( "DiffCampTeam" ):
			self.isDiffCampTeam = True

	def getSpaceSpawnFile( self, selfEntity ):
		"""
		获取出生点文件
		"""
		return self._spawnFile

	def getSpawnSection( self ):
		"""
		"""
		return self._spawnSection

	def onSpaceTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData ):
		"""
		domain找到相应的spaceNormal后，spaceNormal开始传送一个entity到他的space上时的通知
		"""
		baseMailbox.cell.teleportToSpace( position, direction, selfEntity.cell, selfEntity.spaceID )

	def onPlanesTeleportEntity( self, selfEntity, position, direction, baseMailbox, pickData, planesID ):
		"""
		domain找到相应的spaceNormal后，spaceNormal开始传送一个entity到他的space上时的通知
		位面传送，需要先通知传送对象的客户端
		"""
		baseMailbox.cell.teleportToPlanes( position, direction, selfEntity.cell, planesID )
	#------------------------------------------------------------------------------------------------------------------------------------

	def packedDomainData( self, entity ):
		"""
		virtual method.
		用于在玩家上线时需要在指定的domain额外参数；
		@param entity: 想要向space entity发送进入该space消息(onEnter())的entity（通常为玩家）
		@return: dict，返回被进入的space所需要的entity数据。如，有些space可能会需要记录玩家的名字，这里就需要返回玩家的playerName属性
		@note: 只能返回字典类型，且字典类型中的数据只能是python内置的基本数据类型，不允许返回类实例、自定义类型实例等。
		"""
		return None		# {}


	def onEnter( self, selfEntity, cellMailBox, params ):
		"""
		virtual method.
		玩家进入了空间
		@param cellMailBox: cell mailbox
		@type cellMailBox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		pass

	def onLeave( self, selfEntity, cellMailBox, params  ):
		"""
		virtual method.
		玩家离开空间
		@param cellMailBox: 玩家mailbox
		@type cellMailBox: mailbox
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		pass

	def onCloseSpace( self, selfEntity ):
		"""
		virtual method.
		space生命周期结束，正在删除space,这里可以做一些准备删除时要做的事情；
		此方法被Space entity调用（如SpaceNormal 实例等）。
		"""
		pass

	def checkIntoDomainEnable( self, entity ):
		"""
		virtual method.
		检查domain的进入条件
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		"""
		return csstatus.SPACE_OK

	def emplaceRoleOnLogon(self, role):
		"""
		virtual method.
		玩家登陆时设置正确的安放位置
		@param role: 玩家entity实体
		@type role : Role
		"""
		if role.cellData[ "spaceType" ] != role.cellData[ "lastSpaceType" ]:
			role.cellData[ "spaceType" ] = role.cellData[ "lastSpaceType" ]
			role.cellData[ "position" ] = role.cellData[ "lastSpacePosition" ]
			role.logonSpace()
		else:
			# 在某种情况下会产生这种错误， 即客户端登陆后客户端崩溃导致未跳转到上一次存在的场景
			# 那么此时2个场景记录就是一样的 而此场景又不让他登陆 造成无限循环.
			DEBUG_MSG( "has a error! spaceType == lastSpaceType, login failed, again select revive to login !" )
			role.cellData[ "spaceType" ] = role.cellData[ "reviveSpace" ]
			role.cellData[ "position" ] = role.cellData[ "revivePosition" ]
			role.cellData[ "direction" ] = role.cellData[ "reviveDirection" ]
			role.logonSpace()

# SpaceNormal.py

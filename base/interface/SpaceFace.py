# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 phw Exp $

"""
Player Base for Space
"""
import time

import BigWorld
from bwdebug import *
import Language
# from SpaceConst import * ( 又 import * ………………)
import csstatus
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objects = GameObjectFactory.instance()

class SpaceFace:
	"""
	Player Base
	"""
	def __init__( self ):
		pass

	def enterSpace( self, spaceType, position, direction, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@param spaceType:地图类别 "yanhuang",...
		@type spaceType : String,
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		result = g_objects.getObject( spaceType ).checkIntoDomainEnable( self ) #直接找到与该域对应的本地脚本进行domain条件判断
		if result == csstatus.SPACE_OK:
			self.spaceManager.teleportEntity( spaceType, position, direction, self, params )
		else:
			INFO_MSG( "enter domain condition different:", result )
			self.client.spaceMessage( result )

	def logonSpace( self ):
		"""
		define method.
		玩家上线
		作用：
		玩家上线时触发，通知spaceManager
		"""
		spaceType = self.cellData["spaceType"]

		space = g_objects.getObject( spaceType )
		assert space != None, "space %s not found!" % spaceType
		result = space.checkIntoDomainEnable( self ) #直接找到与该域对应的本地脚本进行domain条件判断
		assert result != None, "space %s not found!" % spaceType
		if result == csstatus.SPACE_OK:
			self.spaceManager.teleportEntityOnLogin( spaceType, self, space.packedDomainData( self ) )
		else:
			INFO_MSG( "login domain condition different:", result )
			self.client.spaceMessage( result )

	def logonSpaceInSpaceCopy( self ):
		"""
		define method.
		玩家在临时副本（过去因任务或者活动创建的临时性副本）登陆
		"""
		space = g_objects.getObject(self.cellData["spaceType"])
		assert space != None, "space %s not found!" % self.cellData["spaceType"]
		space.emplaceRoleOnLogon(self)

	def createCellFromSpace( self, spaceCell ):
		"""
		define method.
		在spaceCell上创建roleCell
		@param spaceCell:	空间cell
		@type spaceCell:	mailbox
		"""
		self.createCellEntity( spaceCell )

	def gotoSpace( self, space, position, direction = (0, 0 ,0) ):
		"""
		define method.
		传送到新的场景和位置
			@param space	:	目的场景标识
			@type space		:	string
			@param position	:	目的场景位置
			@type position	:	vector3
			@param direction:	出现时方向
			@type direction	:	vector3
		"""
		self.cell.gotoSpace( space, position, direction )

	def gotoSpaceLineNumber( self, space, lineNumber, position, direction = (0, 0 ,0) ):
		"""
		define method.
		传送到x线场景， 一些支持多线的space如果想指定传送到第几线，必须使用这个接口进行传送
		使用gotoSpace也可以， 但到底被传送到哪个线由space负载平衡来决定。
			@param space		:	目的场景标识
			@type space			:	string
			@param lineNumber	:	线的号码
			@type space			:	uint
			@param position		:	目的场景位置
			@type position		:	vector3
			@param direction	:	出现时方向
			@type direction		:	vector3
		"""
		self.cell.gotoSpaceLineNumber( space, lineNumber, position, direction )
#
# $Log: not supported by cvs2svn $
# Revision 1.9  2007/09/22 09:07:10  kebiao
# 重新调整了space设计
#
# Revision 1.7  2007/06/14 09:24:19  huangyongwei
# SpaceConst 中的宏定义被移动到 csstatus 中，因此要更改 import
#
# Revision 1.6  2007/05/21 08:27:33  panguankong
# 根据spaceDomainCondition修改代码
#
# Revision 1.5  2007/05/14 07:04:07  phw
# 删除不用的模块引用
#
# Revision 1.4  2007/05/11 07:51:11  phw
# method modified: createCellFromSpace(), param spaceBase removed
#
# Revision 1.3  2007/03/19 10:24:28  panguankong
# 修改SPACE接口
#
# Revision 1.2  2007/03/19 09:18:44  panguankong
# 修改space接口
#
# Revision 1.1  2006/11/01 08:51:37  panguankong
# 添加了空间管理系统
#
#
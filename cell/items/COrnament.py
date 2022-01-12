# -*- coding: gb18030 -*-

# $Id: COrnament.py,v 1.4 2008-09-04 07:44:43 kebiao Exp $

"""
装备类基础模块
"""
from bwdebug import *
from CEquip import *
import csconst

class COrnament( CEquip ):
	"""
	饰品，适用于戒指和项链
	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		装备道具

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		# 已装备不可能再次装备，这个是效果是否产生问题，和装备要求扯不上，因此不放在onWield里
		if not CEquip.wield( self, owner, update ):
			return False
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下装备

		@param  owner: 背包拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		if not self.isAlreadyWield(): return	# 如果没有装备效果则不用unwield
		CEquip.unWield( self, owner, update )
		return

### end of class: COrnament ###


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/02/22 01:37:59  yangkai
# 移除旧的首饰附加属性代码
#
# Revision 1.2  2007/01/23 04:16:04  kebiao
# 加入 rndBonus 支持
#
# Revision 1.1  2006/08/18 06:54:01  phw
# no message
#
#

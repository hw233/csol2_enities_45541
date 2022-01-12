# -*- coding: gb18030 -*-
#
# $Id: SpaceDomainCopy.py,v 1.5 2008-01-28 06:01:59 kebiao Exp $

"""
Space domain class
"""

import time
import Language
import BigWorld
from bwdebug import *
import Function
from SpaceDomain import SpaceDomain
from interface.DomainTeamInterface import UseDomainForTeamInter
import csdefine

# 领域类
class SpaceDomainCopy( SpaceDomain, UseDomainForTeamInter ):
	"""
	单人副本，无视队伍特性；
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		UseDomainForTeamInter.__init__(self)
		# 以玩家的dbid来映射SpaceItem实例，以提高副本同一条件的进入判断速度，
		# 玩家的dbid也标示与之相对应的SpaceItem例实的拥有者，
		# 使用玩家的dbid而不使用entityID的原因是为了防止玩家下（断）线后重上时找不到原来的所属space，
		# 也是为了防止玩家以下（断）线的方式绕过副本短时间内可进入的次数
		# 此表与self.spaceItems_对应，如果在self.spaceItems_删除一项，也应该在这里删除，创建亦然
		# key = player's dbid, value = spaceNumber
		
		# 每小时内，最大新副本进入次数，0表示不限制
		#self.maxRepeat = 0
		
		# 记录玩家进入副本的次数及实例的首次进入时间，用此参数来决定玩家是否能继续进入新的副本实例；
		# key = dbid, value = [ (enterTime, spaceNumber), ... ]
		self.__enterRecord = {}
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		
	def setEnterRepeat( self, dbid, spaceNumber ):
		"""
		检查并设置重进新副本次数
		@return: bool; 表示设置重进次数是否成功
		"""
		# 不限制创建次数，直接返回True
		if self.maxRepeat <= 0:
			return True
			
		if dbid not in self.__enterRecord:
			self.__enterRecord[dbid] = []
		
		removeList = []
		t = time.time()
		records = self.__enterRecord[dbid]
		for index, value in enumerate( records ):
			enterTime, number = value
			if spaceNumber == number:
				return True						# 要进入的副本是旧副本，直接返回True，清除过期列表的事情交由下一次再做
			if t - enterTime > 3600:			# 最后的进入时间大于1小时则放入删除列表
				removeList.insert( 0, index )	# 插入到最前面，这样删除的时候就等于从最后面删除，而不会出现bug
				
		# 清除过期列表
		for index in removeList:
			records.pop( index )
		
		if len( records ) >= self.maxRepeat:
			return False
			
		records.append( (t, spaceNumber) )		# 记录要进入的副本编号
		return True
		
	def getSpaceItemByDBID( self, dbid ):
		"""
		根据dbid查找相应的SpaceItem实例，找不到则返回None
		@return: instance of SpaceItem
		"""
		number = self.keyToSpaceNumber.get( dbid )
		if number:
			return self.getSpaceItem( number )
		return None
		
	def requestCreateSpace( self, mailbox, params ):
		"""
		define method.
		手动创建一个指定的space
		@param mailbox: MAILBOX: 如果此参数不为None，space创建完成后将调用mailbox.onRequestCell()方法以通知mailbox所指向的entity
		@type  mailbox: MAILBOX
		"""
		# 由于副本支持队伍，因此一定会记录拥有者，而此接口是无条件创建新space实例，因此我们无法实现此功能。
		raise RuntimeError, "I can't implement the function."

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
		
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/01/22 02:43:01  kebiao
# modify:createSpaceItem params to param
#
# Revision 1.2  2007/10/07 07:17:05  phw
# 结构调整，细化了SpaceItem的创建、删除，并允许继承类去实现它
#
# Revision 1.1  2007/10/03 07:35:20  phw
# no message
#
#
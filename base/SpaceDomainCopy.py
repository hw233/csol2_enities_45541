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

# ������
class SpaceDomainCopy( SpaceDomain, UseDomainForTeamInter ):
	"""
	���˸��������Ӷ������ԣ�
	"""
	def __init__( self ):
		SpaceDomain.__init__(self)
		UseDomainForTeamInter.__init__(self)
		# ����ҵ�dbid��ӳ��SpaceItemʵ��������߸���ͬһ�����Ľ����ж��ٶȣ�
		# ��ҵ�dbidҲ��ʾ��֮���Ӧ��SpaceItem��ʵ��ӵ���ߣ�
		# ʹ����ҵ�dbid����ʹ��entityID��ԭ����Ϊ�˷�ֹ����£��ϣ��ߺ�����ʱ�Ҳ���ԭ��������space��
		# Ҳ��Ϊ�˷�ֹ������£��ϣ��ߵķ�ʽ�ƹ�������ʱ���ڿɽ���Ĵ���
		# �˱���self.spaceItems_��Ӧ�������self.spaceItems_ɾ��һ�ҲӦ��������ɾ����������Ȼ
		# key = player's dbid, value = spaceNumber
		
		# ÿСʱ�ڣ�����¸������������0��ʾ������
		#self.maxRepeat = 0
		
		# ��¼��ҽ��븱���Ĵ�����ʵ�����״ν���ʱ�䣬�ô˲�������������Ƿ��ܼ��������µĸ���ʵ����
		# key = dbid, value = [ (enterTime, spaceNumber), ... ]
		self.__enterRecord = {}
		self.findSpaceItemRule = csdefine.FIND_SPACE_ITEM_FOR_COMMON_COPYS
		
	def setEnterRepeat( self, dbid, spaceNumber ):
		"""
		��鲢�����ؽ��¸�������
		@return: bool; ��ʾ�����ؽ������Ƿ�ɹ�
		"""
		# �����ƴ���������ֱ�ӷ���True
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
				return True						# Ҫ����ĸ����Ǿɸ�����ֱ�ӷ���True����������б�����齻����һ������
			if t - enterTime > 3600:			# ���Ľ���ʱ�����1Сʱ�����ɾ���б�
				removeList.insert( 0, index )	# ���뵽��ǰ�棬����ɾ����ʱ��͵��ڴ������ɾ�������������bug
				
		# ��������б�
		for index in removeList:
			records.pop( index )
		
		if len( records ) >= self.maxRepeat:
			return False
			
		records.append( (t, spaceNumber) )		# ��¼Ҫ����ĸ������
		return True
		
	def getSpaceItemByDBID( self, dbid ):
		"""
		����dbid������Ӧ��SpaceItemʵ�����Ҳ����򷵻�None
		@return: instance of SpaceItem
		"""
		number = self.keyToSpaceNumber.get( dbid )
		if number:
			return self.getSpaceItem( number )
		return None
		
	def requestCreateSpace( self, mailbox, params ):
		"""
		define method.
		�ֶ�����һ��ָ����space
		@param mailbox: MAILBOX: ����˲�����ΪNone��space������ɺ󽫵���mailbox.onRequestCell()������֪ͨmailbox��ָ���entity
		@type  mailbox: MAILBOX
		"""
		# ���ڸ���֧�ֶ��飬���һ�����¼ӵ���ߣ����˽ӿ���������������spaceʵ������������޷�ʵ�ִ˹��ܡ�
		raise RuntimeError, "I can't implement the function."

	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
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
# �ṹ������ϸ����SpaceItem�Ĵ�����ɾ����������̳���ȥʵ����
#
# Revision 1.1  2007/10/03 07:35:20  phw
# no message
#
#
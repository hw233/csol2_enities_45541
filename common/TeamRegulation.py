# -*- coding: gb18030 -*-


import BigWorld


TEAM_FREE_PICK		= 0				#����ʰȡ
TEAM_NORMAL_PICK	= 1				#����ʰȡ
TEAM_CAPTIAN_PICK	= 2				#�ӳ�ʰȡ


DISTANCE_ATTENTION = 80				#���϶���ʰȡ��Χ��С����λ����


BIG_CONDITION = 10					#ɱ�ִ�����£���Ʒ������Ȼ���ڵ�ǰֵ


class TeamRegulation:
	def __init__( self ):
		self.regulationType = 0
		self.val1 = 0
		self.val2 = 0

	def getType( self ):
		"""
		�������
		"""
		return self.regulationType


	##################################################################
	# BigWorld User Defined Type �Ľӿ�                              #
	##################################################################
	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		
		
		return { "val1":obj.val1, "val2":obj.val2, "regulationType": obj.regulationType } 
		

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		obj = g_pRMgr.createRegulaiton( dict['regulationType'] )
		
		obj.regulationType = dict['regulationType']
		obj.val1 = dict['val1']
		obj.val2 = dict['val2']

		return obj

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		if obj is None:
			return True
		return isinstance( obj, TeamRegulation )



instance = TeamRegulation()

class TeamFreePickRegulation( TeamRegulation ):
	"""
	��������ʰȡ����
	@ע:
		����ʰȡ�����Ƕ���ʵ���һ��������������ս��Ʒ�ķ��䡣
	"""
	def __init__( self ):
		self.regulationType = TEAM_FREE_PICK
		self.val1 = 0																		#�Զ������1
		self.val2 = 0																		#�Զ������2
			
	def init( self, teamEntity ):
		"""
		"""
		pass

	def bigHandle( self, id, playerEntity, itemBox ):
		"""
		�󱬴���
		"""
		dropBox = BigWorld.entities.get( id )
		if dropBox is None:
			return False
		
		if len( itemBox ) > BIG_CONDITION:
			members = playerEntity.getAllMemberInRange( DISTANCE_ATTENTION )
			for i in members:
				tempItemsIndex = [ e for e in self.getIndexs( itemBox ) if self.getIndexs( itemBox ).index(e) % len( members ) == members.index( i ) ]
				dropBox.setDropItemsQueryOwner( i.id, tempItemsIndex[:] )
				dropBox.setDropItemsPickOwner( i.id, tempItemsIndex[:] )				
			return True
		else:
			return False

	
	def setItemsOwners( self, id, playerEntity, itemBox ):
		"""
		������з���Ҫ���ʰȡ��
		"""
		if not self.bigHandle(id, playerEntity, itemBox ):
			self.setItemsOwners_( id, playerEntity, itemBox )

	def setItemsOwners_( self, id, playerEntity, itemBox ):
		"""
		������з���Ҫ���ʰȡ��
		"""
		dropBox = BigWorld.entities.get( id )
		if dropBox is None:
			return
		
		members = playerEntity.getAllMemberInRange( DISTANCE_ATTENTION )
		for i in members:
			dropBox.setDropItemsQueryOwner( i.id, self.getIndexs( itemBox )[:] )
			dropBox.setDropItemsPickOwner( i.id, self.getIndexs( itemBox )[:] )				
		return 


	def getItems( self, itemBox ):
		"""
		"""
		items = []
		for iItemDict in itemBox:
			items.append( iItemDict['item'] )
		
		return items

	def getIndexs( self, itemBox ):
		"""
		"""
		indexs = []
		for iItemDict in itemBox:
			indexs.append( iItemDict['order'] )
		
		return indexs

	def getItem( self, itemBox, index ):
		"""
		"""
		for iItemDict in itemBox:
			if iItemDict['order'] == index:
				return  iItemDict['item'] 
		return None


class TeamNormalPickRegulation( TeamFreePickRegulation ):
	"""
	��������ʰȡ����
	"""
	def __init__( self ):
		"""
		@param	val1:																	#����һ���ڼ�¼��ǰ���ֵ�˭��ȡ����
		"""
		TeamFreePickRegulation.__init__( self )
		self.regulationType = TEAM_NORMAL_PICK
		self.val2 = 0																	#��ʼ״̬�£�������Ʒ��������ROLL

	def setItemsOwners_( self, id, playerEntity, itemBox ):
		"""
		���÷���Ҫ���ʰȡ��
		"""
		dropBox = BigWorld.entities.get( id )
		if dropBox is None:
			return
		
		members = playerEntity.getAllMemberInRange( DISTANCE_ATTENTION )
		if members == []:
			dropBox.setDropItemsQueryOwner( playerEntity.id, self.getIndexs( itemBox )[:] )
			dropBox.setDropItemsPickOwner( playerEntity.id, self.getIndexs( itemBox )[:] )
			return
		member = members[ self.val1%len( members ) ]

		#���Ϸ������Ʒ
		itemIDsIndex = []
		if self.val2 != 0 and self.val2 >= 2:
			for iItemIndex in self.getIndexs( itemBox ):
				if self.getItem( itemBox, iItemIndex ).getQuality() >= self.val2:
					itemIDsIndex.append( iItemIndex )
			
			for iMember in members:
				dropBox.setDropItemsQueryOwner( iMember.id,  [ e for e in itemIDsIndex ] )
				dropBox.setDropItemsRollOwner( iMember.id,  [ e for e in itemIDsIndex ] )

		self.val1 += 1
		dropBox.setDropItemsQueryOwner( member.id, [ e for e in self.getIndexs( itemBox ) if e not in itemIDsIndex ] )
		dropBox.setDropItemsPickOwner( member.id, [ e for e in self.getIndexs( itemBox ) if e not in itemIDsIndex ] )

		for i in members:
			i.setTeamPickRegulationVal1( self.val1 )				



	
class TeamCaptainPickRegulation( TeamFreePickRegulation ):
	"""
	����ӳ�ʰȡ����
	"""
	def __init__( self ):
		"""
		@param	val1:																	#����һ���ڼ�¼��ǰ���ֵ�˭��ȡ����
		"""
		TeamFreePickRegulation.__init__( self )
		self.regulationType = TEAM_CAPTIAN_PICK
		self.val1 = 1
		self.val2 = 2

	def init( self, teamEntity ):
		"""
		@param	val2:																	#�������ڼ�¼��Ʒ��Ʒ����Ϣ																	#
		"""
		TeamFreePickRegulation.init( self, teamEntity )
		self.val1 = 1
		self.val2 = 2																	#��߼���Ʒ�ʲ������鳤���䡣-1	˵����������Ʒ�����ɷ��䡣																							



	def setItemsOwners_( self, id, playerEntity, itemBox ):
		"""
		������з���Ҫ���ʰȡ��
		"""
		dropBox = BigWorld.entities.get( id )
		if dropBox is None:
			return
		
		members = playerEntity.getAllMemberInRange( DISTANCE_ATTENTION )
		
		
		#���Ϸ������Ʒ
		itemIDsIndex = []
		for iMember in members:
			if playerEntity.captainID == iMember.id:
				for iItemIndex in self.getIndexs( itemBox ):
					if self.getItem( itemBox, iItemIndex ).getQuality() >= self.val2:
						itemIDsIndex.append( iItemIndex )
		
		dropBox.setDropItemsAssignOwner( playerEntity.captainID, [ e for e in itemIDsIndex ] )

		for iMember in members:
			dropBox.setDropItemsQueryOwner( iMember.id,  [ e for e in itemIDsIndex ] )

		member = members[self.val1%len( members )]
		
		self.val1 += 1
		dropBox.setDropItemsQueryOwner( member.id, [ e for e in self.getIndexs( itemBox ) if e not in itemIDsIndex ] )
		dropBox.setDropItemsPickOwner( member.id, [ e for e in self.getIndexs( itemBox ) if e not in itemIDsIndex ] )
		
		for i in members:
			i.setTeamPickRegulationVal1( self.val1 )				
		

	def bigHandle( self, id, playerEntity, itemBox ):
		"""
		�󱬴���
		"""
		if len( itemBox ) > BIG_CONDITION:
			dropBox = BigWorld.entities[id]
			members = playerEntity.getAllMemberInRange( DISTANCE_ATTENTION )
			for i in members:
				tempItemsIndex = [ e for e in self.getIndexs( itemBox ) if self.getIndexs( itemBox ).index(e) % len( members ) == members.index( i ) and self.getItem(itemBox, e).getQuality() < self.val2 ]
				dropBox.setDropItemsQueryOwner( i.id, tempItemsIndex[:] )
				dropBox.setDropItemsPickOwner( i.id, tempItemsIndex[:] )
				
				if playerEntity.captainID == i.id:
					dropBox.setDropItemsAssignOwner( i.id, [ e for e in self.getIndexs( itemBox ) if self.getItem(itemBox, e).getQuality() >= self.val2 ] )
				
				dropBox.setDropItemsQueryOwner( i.id, [ e for e in self.getIndexs( itemBox ) if self.getItem(itemBox, e).getQuality() >= self.val2 ] )		
			return True
		else:
			return False
	

class PickRegulaitonMgr:
	"""
	"""
	def __init__( self ):
		self.regulaitonDict = {  TEAM_FREE_PICK: TeamFreePickRegulation, \
								TEAM_NORMAL_PICK: TeamNormalPickRegulation, \
								TEAM_CAPTIAN_PICK: TeamCaptainPickRegulation,\
								}
		
	
	def createRegulaiton( self, regulaitonType ):
		"""
		"""
		return self.regulaitonDict[regulaitonType]()



g_pRMgr = PickRegulaitonMgr()
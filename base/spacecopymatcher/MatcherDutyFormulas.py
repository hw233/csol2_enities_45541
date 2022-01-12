# -*- coding: gb18030 -*-

import csdefine

class DutyAllocatee :
	"""Allocate duty to appropriate member according to the selection of team members,
	base on duties selection is complementary."""
	def __init__( self ) :
		self.__dutyMatcher = DutyMatcher()
		self.__yieldDuties = []											# 递归中需要退让的职责，防止职责重复造成死循环
		self.__allocatedDuties = {}

	def allocate( self, allocatedDuties ) :
		"""
		@param	allocatedDuties : duties to be allocated
		@type	allocatedDuties : dictionary like.
		"""
		self.__initAllocation( allocatedDuties )
		return self.__allocateCompletely()								# 如果传入了空职责，这里会检测出错误

	def dutiesAreFull( self ) :
		"""
		All duties are undertaken.
		"""
		return self.__dutyMatcher.plenary()

	def allDutiesYielded( self ) :
		"""
		Duties are yielded successfully.
		"""
		return len( self.__yieldDuties ) == 0

	def dutiesDistribution( self ) :
		"""
		"""
		return self.__dutyMatcher.matchbox()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initAllocation( self, allocatedDuties ) :
		"""Initialize this allocation."""
		self.__resetYieldDuties()
		self.__dutyMatcher.clear()
		self.__allocatedDuties.clear()
		self.__allocatedDuties.update( allocatedDuties )

	def __resetYieldDuties( self ) :
		"""Clear yield duties of undertaker.
		"""
		self.__yieldDuties = []

	def __recordYieldDuty( self, duty ) :
		"""Add duty which is yielding.
		"""
		self.__yieldDuties.append( duty )

	def __yieldDutyUnrecorded( self, duty ) :
		"""Check if duty is in yield.
		"""
		return duty not in self.__yieldDuties

	def __allocateCompletely( self ) :
		"""try to allocate appropriate duty to every undertaker."""
		for undertaker, duties in self.__allocatedDuties.iteritems() :
			if self.__allocateDutyByAllWay( undertaker, duties ) is False :
				return False
		return True

	def __allocateDutyByAllWay( self, undertaker, duties ) :
		"""allocate one of duties to undertaker.
		"""
		if len( duties ) == 0 :
			return False
		elif self.__allocateBlankDuty( undertaker, duties ) :
			return True
		elif self.__swapWithOccupant( undertaker, duties ) :
			return True
		else :
			return False

	def __allocateBlankDuty( self, undertaker, duties ) :
		"""Try to allocate one blank duty of duties to undertaker.
		"""
		for duty in duties :
			if self.__dutyMatcher.want( duty ) > 0 :
				self.__dutyMatcher.add( duty, undertaker )
				return True
		return False

	def __swapWithOccupant( self, undertaker, duties ) :
		"""Try to swap duty with current occupant.
		"""
		for duty in duties :
			if self.__occupantYield( duty ) :
				self.__dutyMatcher.add( duty, undertaker )
				return True
		return False

	def __occupantYield( self, duty ) :
		"""Try if other undertakders can yield this duty and turn to another.
		"""
		if self.__yieldDutyUnrecorded( duty ) :
			self.__recordYieldDuty( duty )
			occupants = self.__dutyMatcher.undertakersOf( duty )
			for undertaker in occupants :
				otherDuties = self.__otherDutiesOf( undertaker, duty )
				if self.__allocateDutyByAllWay( undertaker, otherDuties ) :				# 递归替换
					self.__dutyMatcher.remove( duty, undertaker )
					self.__resetYieldDuties()
					return True
		return False

	def __otherDutiesOf( self, undertaker, duty ) :
		"""Fetch other duties except the given of undertaker.
		"""
		otherDuties = list( self.__allocatedDuties[undertaker] )
		otherDuties.remove( duty )
		return otherDuties


class DutyMatcher :
	"""
	DutyMatcher manages the rule of duty to match a copy team for the players,
	like how many tanks needed in a team.
	"""
	DUTIES_WANTED = { csdefine.COPY_DUTY_MT:1, \
					csdefine.COPY_DUTY_HEALER:1, \
					csdefine.COPY_DUTY_DPS:3,\
					}														# 一个队伍所需的各职责人员个数

	def __init__( self ) :
		self.__matchbox = { csdefine.COPY_DUTY_MT:[],\
						csdefine.COPY_DUTY_DPS:[], \
						csdefine.COPY_DUTY_HEALER:[],\
						 }													# 排队成员，可能有些玩家同时选择了多个职责

	def __wantedOf( self, duty ) :
		"""Check missing amount of duty."""
		return DutyMatcher.DUTIES_WANTED[duty] - len( self.__matchbox[duty] )

	def missing( self ) :
		"""
		"""
		result = []
		for duty in DutyMatcher.DUTIES_WANTED.iterkeys() :
			if self.__wantedOf( duty ) > 0 :
				result.append( duty )
		return result

	def plenary( self ) :
		"""
		all duties are undertaken.
		"""
		return len( self.missing() ) == 0

	def want( self, duty ) :
		"""
		"""
		return self.__wantedOf( duty )

	def add( self, duty, undertaker ) :
		"""
		"""
		if self.__wantedOf( duty ) > 0 :
			self.__matchbox[duty].append( undertaker )

	def remove( self, duty, undertaker ) :
		"""
		"""
		staffs = self.__matchbox.get( duty )
		if staffs and undertaker in staffs :
			staffs.remove( undertaker )

	def members( self ) :
		"""
		"""
		result = set()
		for members in self.__matchbox.itervalues() :
			result.update( members )
		return tuple( result )

	def matchbox( self ) :
		"""
		"""
		return self.__matchbox.copy()

	def undertakersOf( self, duty ) :
		"""
		"""
		return self.__matchbox[duty][:]

	def clear( self ) :
		"""
		"""
		self.__matchbox = { csdefine.COPY_DUTY_MT:[], csdefine.COPY_DUTY_DPS:[], csdefine.COPY_DUTY_HEALER:[] }

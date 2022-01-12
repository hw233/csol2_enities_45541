# -*- coding: gb18030 -*-

import csdefine
from MatcherDutyFormulas import DutyAllocatee


class CopyTeamFormulas :

	def __init__( self ) :
		self.__dutyAllocatee = DutyAllocatee()

	def analyzeDuties( self, duties ) :
		"""
		"""
		if self.dutiesComplementary( duties ) :
			if self.__dutyAllocatee.dutiesAreFull() :
				return csdefine.COPY_TEAM_DUTIES_MATCH_PLENARILY
			else :
				return csdefine.COPY_TEAM_DUTIES_MATCH_PARTIALLY
		else :
			return csdefine.COPY_TEAM_DUTIES_CONFLICT

	def dutiesComplementary( self, duties ) :
		"""check if duties of a team is complementary."""
		#return self.allotDuties( duties )
		return duties and self.__dutyAllocatee.allocate( duties )

	def dutiesPlenary( self, duties ) :
		"""
		whether duties are full.
		"""
		return self.analyzeDuties( duties ) == csdefine.COPY_TEAM_DUTIES_MATCH_PLENARILY

	def latestAllocation( self ) :
		"""
		"""
		return self.__dutyAllocatee.dutiesDistribution()


	# ----------------------------------------------------------------
	# pass
	# ----------------------------------------------------------------
	def allotDuties( self, membersDuties ) :
		"""落实队伍中每个人的职责（这是该方法的最初版本）"""
		queuingGroup = DutyMatcher()
		def dutiesExcept( duty, undertaker ) :
			otherDuties =  list( membersDuties[undertaker] )
			otherDuties.remove( duty )
			return otherDuties

		def allot( undertaker, objDuties ) :
			for duty in objDuties :
				if queuingGroup.want( duty ) > 0 :
					queuingGroup.add( duty, undertaker )
					return True
			return False

		def tryOtherUndertakers( duty ) :
			undertakers = queuingGroup.undertakersOf( duty )
			for undertaker in undertakers :
				otherDuties = dutiesExcept( duty, undertaker )
				if allot( undertaker, otherDuties ) :
					queuingGroup.remove( duty, undertaker )
					return True
			return False

		for undertaker, objDuties in enumerate( membersDuties ) :
			if not allot( undertaker, objDuties ) :
				for duty in objDuties :
					if tryOtherUndertakers( duty ) :
						queuingGroup.add( duty, undertaker )
						break
				else :
					return False
		#print "Undertaker of mt:", queuingGroup.undertakersOf( csdefine.COPY_DUTY_MT )
		#print "Undertaker of healer:", queuingGroup.undertakersOf( csdefine.COPY_DUTY_HEALER )
		#print "Undertaker of dps:", queuingGroup.undertakersOf( csdefine.COPY_DUTY_DPS )
		return True


copyTeamFormulas = CopyTeamFormulas()

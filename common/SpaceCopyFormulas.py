# -*- coding: gb18030 -*-

import Language
from bwdebug import ERROR_MSG

class SpaceCopyFormulas :

	def __init__( self ) :
		self.__copiesSummary = {}
		self.__checkers = []

	def loadCopiesData( self, cfgPath ) :
		"""Load summary conditions of all copies."""
		sect = Language.openConfigSection( cfgPath )
		if sect is None :
			ERROR_MSG( "Can't open config of path: %s." % cfgPath )
			return
		for copySect in sect.values() :
			copyLabel = copySect.readString( "spaceClassName" )
			summary = {}
			summary["copyLabel"] = copyLabel
			summary["copyName"] = copySect.readString( "spaceName" )
			summary["copyFlag"] = copySect.readInt("copyFlag")
			summary["consumedFlag"] = copySect.readInt("consumedFlag")
			summary["mode"] = copySect.readInt("mode")
			summary["bossesTotal"] = copySect.readInt( "bossesTotal" )
			summary["minEnterLevel"] = copySect.readInt( "minEnterLevel" )
			#summary["maxCompletionPerDay"] = copySect.readInt( "maxCompletionPerDay" )
			if copySect.has_key( "amount" ):
				summary["amount"] = copySect.readInt( "amount" )
			summary["unit"] = copySect.readString( "unit" )
			if copySect.has_key( "day" ):
				summary["day"] = copySect.readInt( "day" )	
			if copySect.has_key( "time1" ):
				summary["time1"] = copySect.readString( "time1" )
			if copySect.has_key( "time2" ):
				summary["time2"] = copySect.readString( "time2" )
			if copySect.has_key( "time3" ):
				summary["time3"] = copySect.readString( "time3" )									
			self.__copiesSummary[copyLabel] = summary
		Language.purgeConfig( cfgPath )

	def setCopiesSummary( self, summaries ) :
		"""�Զ��帱������"""
		self.__copiesSummary.clear()
		self.__copiesSummary.update( summaries )

	def formatCopyLevel( self, actualLevel ) :
		"""
		ת�������ȼ�������40��49������ң�����Ӧ45���ĸ�����
		50��59������ң�����Ӧ55���ĸ���
		"""
		return int( actualLevel ) / 10 * 10 + 5

	def summaryOf( self, copyLabel ) :
		"""��ȡĳ��������summary"""
		summary = self.__copiesSummary.get( copyLabel )
		if summary :
			return summary.copy()
		return None

	def totalBossesOf( self, copyLabel ) :
		"""��ȡ������boss����"""
		summary = self.__copiesSummary.get( copyLabel )
		if summary :
			return summary["bossesTotal"]
		return 0

	def setCheckers( self, checkers ) :
		"""���ü�����"""
		self.__checkers = []
		for checker in checkers :
			assert issubclass( checker, CopyCheckerBase )
			self.__checkers.append( checker )

	def checkCopiesEnterable( self, player, copyLabels ) :
		"""�������Ƿ��ܽ���ָ������"""
		if len( copyLabels ) == 0 :
			return False
		else :
			for copyLabel in copyLabels :
				if not self.checkCopyEnterable( player, copyLabel ) :
					return False
			return True

	def checkCopyEnterable( self, player, copyLabel ) :
		"""�������Ƿ��ܽ���ָ������"""
		summary = self.__copiesSummary.get( copyLabel )
		if summary is None :
			ERROR_MSG( "Cant't find summary of copy: %s." % copyLabel )
			return False
		for checker in self.__checkers :
			if not checker.check( player, summary ) :
				return False
		return True
	
	def getCopiesSummary( self ):
		"""
		��ȡ���и���
		"""
		return self.__copiesSummary

# ----------------------------------------------------------------
# CopyCheckerBase: base class of formulas checker.
# ----------------------------------------------------------------
class CopyCheckerBase :

	@staticmethod
	def check( player, summary ) :
		"""check if obj adjust to summary."""
		return True


# ----------------------------------------------------------------
# CopyCheckerLevel: check the level of player.
# ----------------------------------------------------------------
class CopyCheckerLevel( CopyCheckerBase ) :

	@staticmethod
	def check( player, summary ) :
		""""""
		return player.level >= summary["minEnterLevel"]

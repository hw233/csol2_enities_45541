# -*- coding: gb18030 -*-
#
# ����ռ��
#

import Language
from bwdebug import *
from csarithmetic import getRandomElement

class SuanGuaZhanBuLoader:
	"""
	����Ʒ����Ʒ�ı�������
	"""
	_instance = None
	def __init__( self ):
		# ��������2����2������ʵ��
		assert SuanGuaZhanBuLoader._instance is None
		SuanGuaZhanBuLoader._instance = self

	def load( self, configPath ):
		"""
		�������ñ�
		"""
		section = Language.openConfigSection( configPath )
		assert section is not None, "open %s false." % configPath

		self._money = section.readString( "money" )	# ռ����Ǯ���ģ����ã�"30-59,60-89,90-119,120-150;1,2,5,15"
		self._skills = section.readString( "skills" )	# ռ�����ܺͻ��ʣ����ã�"ID1:����1;ID2:����2"

		self._expendKey = []	# [[30, 59], [60, 89], [90, 119], [120, 150]]
		self._expendValue = []	# [1,2,5,15]
		keyStr = self._money.split( ";" )[0]
		valStr = self._money.split( ";" )[1]
		for e in keyStr.split(","):
			self._expendKey.append( [ int(e.split( "-" )[0]), int(e.split( "-" )[1]) ] )
		for e in valStr.split(","):
			self._expendValue.append( int(e) )

		self._skillIDList = []				# ��ż��ܵ�ID
		self._skillOddsList = []			# ��ż���ID��Ӧ�Ļ�������
		for e in self._skills.split( ";" ):
			self._skillIDList.append( str( e.split( ":" )[0] ) )
			self._skillOddsList.append( float( e.split( ":" )[1] ) )

		# �������
		Language.purgeConfig( configPath )

	def getNeedMoney( self, level ):
		"""
		��ȡ��Ҫ���Ľ�Ǯ
		"""
		index = 0
		for e in self._expendKey:
			if level <= e[1] and level >= e[0]:
				index = self._expendKey.index( e )
				break
		return int( self._expendValue[index] )

	def getRandomSkill( self ):
		"""
		��ȡһ���������
		"""
		return int( getRandomElement( self._skillIDList, self._skillOddsList ) )

	@classmethod
	def instance( SELF ):
		"""
		"""
		if SELF._instance is None:
			SELF._instance = SuanGuaZhanBuLoader()
		return SELF._instance

g_SuanGuaZhanBuLoader = SuanGuaZhanBuLoader.instance()
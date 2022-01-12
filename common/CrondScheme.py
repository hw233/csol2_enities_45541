# -*- coding: gb18030 -*-


"""
first write by penghuawei.

get from: man -s 5 crontab
      The time and date fields are:

             field          allowed values
             -----          --------------
             minute         0-59
             hour           0-23
             day of month   1-31
             month          1-12
             day of week    0-7 (0 or 7 is Sun)

      A field may be an asterisk (*), which always stands for ''first-last''.

      Ranges of numbers are allowed.  Ranges are two numbers separated with a hyphen.  The specified range is inclu-
      sive.  For example, 8-11 for an ''hours'' entry specifies execution at hours 8, 9, 10 and 11.

      Lists  are  allowed.   A  list  is  a  set of numbers (or ranges) separated by commas.  Examples: ''1,2,5,9'',
      ''0-4,8-12''.

      Step values can be used in conjunction with ranges.  Following a range with ''/<number>'' specifies  skips  of
      the  number's value through the range.  For example, ''0-23/2'' can be used in the hours field to specify com-
      mand execution every other hour (the alternative in the V7  standard  is  ''0,2,4,6,8,10,12,14,16,18,20,22'').
      Steps are also permitted after an asterisk, so if you want to say ''every two hours'', just use ''*/2''.

      Note:  The  day  of  a command's execution can be specified by two fields -- day of month, and day of week.  If
      both fields are restricted (ie, aren't *), the command will be run when either field matches the current time.
      For example,
      ''30  4  1,15  *  5'' would cause a command to be run at 4:30 am on the 1st and 15th of each month, plus every
      Friday.
"""

import time
from bwdebug import *

ERROR_TIME = 0xFFFFFFFF

def calculateWeekDay( year, month, day ):
	"""
	ʹ�á���ķ����ɭ���㹫ʽ��������ĳ��ĳ��ĳ�������ڼ�
	W= (d+2*m+3*(m+1)/5+y+y/4-y/100+y/400) mod 7
	�ڹ�ʽ��d��ʾ�����е�������m��ʾ�·�����y��ʾ������
	"""
	# ע�⣺�ڴ˹�ʽ���и���������ʽ��ͬ�ĵط���
	# ��һ�ºͶ��¿�������һ���ʮ���º�ʮ���£����������2004-1-10����ɣ�2003-13-10�����빫ʽ���㡣
	if month <= 2:
		year -= 1
		month += 12
	return ( day + 2 * month + 3 * ( month + 1 ) / 5 + year + year / 4 - year / 100 + year / 400 ) % 7

def parseSingleScheme( schemeString, min, max ):
	"""
	���������ļƻ�ʱ�����,
	��: 1,2,10-20,*/2,1-15/3,10/5

	@param schemeString: like as 1,2,10-20,*/2,1-15/3,10/5
	@param min: ��Сֵ��С�ڴ�ֵȡ��ֵ
	@param max: ���ֵ�����ڴ�ֵȡ��ֵ
	@return: list of int
	"""
	ret_val = []

	schemeString = schemeString.replace( "\\", "/" )
	schemes = schemeString.split( "," )
	for scheme in schemes:
		if len( scheme ) == 0:
			continue
		dividend = None
		if scheme == "*":
			# ֻҪ������"*",����ʾ��������������
			return range( min, max + 1 )
		elif scheme.isdigit():					# set of 0 and 9
			ret_val.append( int( scheme ) )
			continue
		elif "/" in scheme:					# find dividend from */2 or 3-18/3
			try:
				scheme, dividend = scheme.split( "/" )
			except ValueError, errstr:
				ERROR_MSG( "ValueError: ", errstr, "scheme = ", schemeString )
				return []
			if dividend.isdigit():
				dividend = int( dividend )
				if dividend <= 0:
					ERROR_MSG( "devidend must be greater than 0. scheme = ", schemeString )
					return []
			else:
				ERROR_MSG( "devidend must be an integer. scheme = ", schemeString )
				return []
			if scheme == "*":						# */2
				ret_val.extend( [ e for e in xrange( min, max + 1 ) if e % dividend == 0 ] )
				continue

		if "-" in scheme:						# 3-18 or 3-18/3
			try:
				minV, maxV = scheme.split( "-" )
			except ValueError, errstr:
				ERROR_MSG( "ValueError: ", errstr, "scheme = ", schemeString )
				return []
			try:
				minV = int( minV )
				maxV = int( maxV )
			except ValueError, errstr:
				ERROR_MSG( "ValueError: ", errstr, "scheme = ", schemeString )
				return []
			if minV < min: minV = min
			if maxV > max: maxV = max
			if dividend is not None:
				ret_val.extend( [ e for e in xrange( minV, maxV + 1 ) if e % dividend == 0 ] )
			else:
				ret_val.extend( range( minV, maxV + 1 ) )
		elif scheme.isdigit():					# 10/2, �����������Ӧ��֧�֣���Ϊ����������
			ret_val.append( int( scheme ) / dividend )
			continue
		else:									# abc/3 ???
			ERROR_MSG( "invalid scheme. scheme = ", schemeString )
			return []

	datas = list( set( ret_val ) )		# �������б��ӵ�hash_setȥ���࣬Ȼ�����±���б�
	datas.sort()						# ����С���������Ը���Ĳ���

	# ���˵����� [min, max] ֮���ֵ
	for index in xrange( len( datas ) - 1, -1, -1 ):
		if datas[index] < min or datas[index] > max:
			datas.pop( index )
	return datas

class SchemeTypeTime( object ):
	"""
	"""
	def __init__( self, hourSchemeString = None, minuteSchemeString = None ):
		self._hours = []
		self._minutes = []
		if hourSchemeString is None or minuteSchemeString is None:
			return
		self.init( hourSchemeString, minuteSchemeString )

	def init( self, hourSchemeString, minuteSchemeString ):
		"""
		��ʼ�������ļƻ�ʱ�����,
		"""
		self._hours = parseSingleScheme( hourSchemeString, 0, 23 )
		self._minutes = parseSingleScheme( minuteSchemeString, 0, 59 )

	def find( self, hour, minute ):
		"""
		������ӽ��Ҵ���ָ��������ʱ�䡣
		@return: �����ҵ���ֵ(int)������Ҳ����򷵻�None
		"""
		hourO = hour

		def findFunc( dataList, value ):
			if not len( dataList ):
				return None

			if value is None:
				try:
					return dataList[0]
				except IndexError:
					return None	# ֻ�г����ʱ����п����ǿ��б���˻��ʺܵ�
			for e in dataList:
				if e >= value: return e
			return None

		while True:
			hour = findFunc( self._hours, hour )
			if hour is None:
				return None, None
			minute = findFunc( self._minutes, minute )
			if minute is None:
				if hour == hourO:
					hour += 1
				minute = None
			else:
				return hour, minute

	def valid( self ):
		"""
		��������Ƿ������Ч�����ݡ�
		"""
		return len( self._hours ) and len( self._minutes )

class SchemeTypeDate( object ):
	def __init__( self, monthSchemeString = None, daySchemeString = None, wdaySchemeString = None ):
		self._wdays = []
		self._days = []
		self._months = []
		if monthSchemeString is None or daySchemeString is None or wdaySchemeString is None:
			return
		self.init( monthSchemeString, daySchemeString, wdaySchemeString )

	def init( self, monthSchemeString, daySchemeString, wdaySchemeString ):
		"""
		"""
		self._months = parseSingleScheme( monthSchemeString, 1, 12 )
		self._days = parseSingleScheme( daySchemeString, 1, 31 )
		self._wdays = parseSingleScheme( wdaySchemeString, 0, 7 )

		# ʹ��time.localtime()���������ڱ�ʾ��ʽΪ��0 - 6������һ�������죩
		# ��ˣ�Ϊ�˷����������ڱȶԣ�������Ҫ��0�滻��7���ٰ��б���������ֵ���μ�һ
		if self._wdays[0] == 0:
			self._wdays.pop(0)
			if self._wdays[-1] < 7:
				self._wdays.append( 7 )
		self._wdays = [ e - 1 for e in self._wdays ]
		assert len( self._wdays ) <= 7, self._wdays

	def find( self, year, month = None, day = None ):
		"""
		������ӽ��Ҵ���ָ���������ڡ�
		@return: (year, month, day) or (None, None, None)
		"""
		yearE = year
		monthE = month
		if month is None:
			dayE = None
		else:
			dayE = day
		while True:
			oldMonthE = monthE
			monthE = self.findMonth( monthE )
			if monthE is None:
				yearE += 1
				# ��������ϴ����硰* * 31 4 *�����������ã�
				# ���п���������ѭ���������Ҫ��һ�´���
				# ��8��ԭ������������Ĺ������£��Ա�����
				# ��* * 29 2 *����������ȷ�ļ���Żᴥ��һ
				# �ε�ʱ�䱻���Ե�����Ȼ�������������ó���
				# �Ŀ����Լ��ͣ���
				# ע��������ȫ��������4�������ꡣ
				if yearE > year + 8:
					return None, None, None
				dayE = None
				continue
			elif monthE != oldMonthE:
				# �����˾͵����������������
				dayE = None

			dayE = self.findDay( yearE, monthE, dayE )
			if dayE is None:
				monthE += 1
			else:
				if dayE <= 28:
					return yearE, monthE, dayE

				# ������ڿ��µ�����
				# ���磺2��31��Ҳ����3��2�ţ����꣩��Ҳ����3��3�ţ�
				# �����磺4��31����5��1��
				if time.localtime( time.mktime( ( yearE, monthE, dayE, 0, 0, 0, 0, 0, 0 ) ) )[1] == monthE:
					return yearE, monthE, dayE	# ����û�п��£����ǿ���ֱ��ʹ��
				else:
					monthE += 1
					dayE = None

	def findMonth( self, month = None ):
		"""
		"""
		if month is None:
			return self._months[0]
		for monthE in self._months:
			if monthE >= month: return monthE
		return None

	def findDay( self, year, month, day = None ):
		"""
		������ӽ��Ҵ���ָ������(value)����ֵ��
		@return: �����ҵ���ֵ(int)������Ҳ����򷵻�None
		"""
		dayIgnore = len( self._days ) == 31
		wdayIgnore = len( self._wdays ) == 7

		# ������Ϊ��������������ڶ���ȫ��ƥ�䣨len == max����
		# �Ǿ����κ�������ƥ�䣬���ԣ����day��ΪNone�����ֱ�ӷ��ء�
		# �����dayΪNone����һ������ÿ�µĵ�һ�졣
		if dayIgnore and wdayIgnore:
			if day is None:
				return 1
			else:
				return day

		# ���dayΪ��*��������Ժ��Զ������жϣ���Ϊ��һ����true����˸�Ϊ��wday�����ɹ���ʧ��
		if dayIgnore:
			if day is None:
				day = 1
			while day <= 31:
				wday = calculateWeekDay( year, month, day )
				if wday in self._wdays:
					return day
				day += 1
			return None
		# ���wdayΪ��*��������Ժ��Զ������жϣ���Ϊ��һ����true����˸�Ϊ��day�����ɹ���ʧ��
		elif wdayIgnore:
			if day is None:
				return self._days[0]
			while day <= 31:
				if day in self._days:
					return day
				day += 1
			return None
		# Note:  The  day  of  a command's execution can be specified by two fields -- day of month, and day of week.
  		# If both fields are restricted (ie, aren't *), the command will be run when either field matches the current time.
  		else:
  			# �������ڵ����⣬���û��ָ����ʼ���ڣ������ÿ�µĵ�һ�쿪ʼѭ���ж�
  			if day is None:
  				day = 1
  			while day <= 31:
  				if day in self._days:
  					return day

				wday = calculateWeekDay( year, month, day )
				if wday in self._wdays:
					return wday

  				day += 1

	def valid( self ):
		"""
		��������Ƿ������Ч�����ݡ�
		"""
		return len( self._wdays ) and len( self._days ) and len( self._months )



class Scheme( object ):
	"""
	timer scheme
	"""
	def __init__( self, schemeString = "" ):
		"""
		@param schemeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@param baseMailbox: MAILBOX, see also callbackName param
		@param callbackName: string, ��ʱ�䵽��ʱ��ʹ�ô����ִ�baseMailbox�����л�ȡ�ص��ӿڲ����á�
		"""
		self._schemeString = ""
		self._dateScheme = SchemeTypeDate()
		self._timeScheme = SchemeTypeTime()

		if len( schemeString ):
			self.init( schemeString )

	def init( self, schemeString ):
		"""
		@param schemeString: string, like as: 0-59/2 0-23 1-31 1-12 0-7
		@return: bool
		"""
		self._schemeString = schemeString
		try:
			minute, hour, day, month, wday = schemeString.split()
		except ValueError, errstr:
			ERROR_MSG( "ValueError: ", errstr, "scheme = ", schemeString )
			return False

		self._dateScheme.init( month, day, wday )
		self._timeScheme.init( hour, minute )

		if self._dateScheme.valid() and self._timeScheme.valid():
			return True

		ERROR_MSG( "invalid scheme string.", schemeString )
		return False

	def calculateNext( self, year, month, day, hour, minute ):
		"""
		�Ը�������Ϊ��ʼʱ�䣬������һ�δ���ʱ�䡣
		@return: int32; time of second
		"""
		yearO = year
		monthO = month
		dayO = day
		while True:
			year, month, day = self._dateScheme.find( year, month, day )
			# �����ϣ�������ȷyear��month��dayһ����ΪNone��
			# ��ˣ������ĳ������������⣬ֱ�ӷ���һ��N���ֵ��
			# ������Զ�޷�������
			if year is None:
				return ERROR_TIME

			# ����һ�����ҵ�һ�����ڣ����ǣ����ܻ��������������
			# �ҵ������ڲ��ǲ���������������£�
			# ����Ӧ����hour��minute��ͷ����
			if dayO != day or monthO != month or yearO != year:
				hour = minute = None
			hour, minute = self._timeScheme.find( hour, minute )
			if hour is None:
				day += 1
				hour = None
				minute = None
			else:
				return int( time.mktime( ( year, month, day, hour, minute, 0, 0, 0, 0 ) ) )


class clientScheme( Scheme ):
	def __init__(  self, schemeString = "" ):
		Scheme.__init__( self, schemeString )


	def getDayTable( self, year, month, day ):
		"""
		���ָ����Ļ
		return�� list of list of int like as [ [ hour, minute ], ... ]
		"""
		table = []

		hour = 0
		minute = 0

		while True:
			t = self.calculateNext( year, month, day, hour, minute )
			if t == ERROR_TIME:
				return table

			yearE, monthE, dayE, hourE, minuteE = time.localtime( t )[:5]
			hour = hourE
			minute = minuteE

			if yearE != year or monthE != month or dayE != day:
				return table

			table.append( [ hour, minute ] )
			minute += 1








def test_Scheme():
	s = Scheme()
	assert s.init( "*/3 1,2,5-12 * 12,1-10/5 0-7" ) == True
	assert s.init( "*/3, 1,2,5-12, *, 12,1-10/5, *," ) == True
	assert s.init( "a/3 1,2,5-12 * 12,1-10/5 0-7" ) == False
	assert s.init( "*/3 a,2,5-12 * 12,1-10/5 0-7" ) == False
	assert s.init( "*/3 1,2,a-z * 12,1-10/5 0-7" ) == False
	assert s.init( "*/3 1,2,5-12 b 12,1-10/5 0-7" ) == False


	t = time.time()
	assert s.init( "*/3 1,2,5-12 1,7,9 12,1-10/5 *" ) == True
	#s.valid( month, day, hour, minute )
	assert s.calculateNext( 2009, 5, 7, 10, 1 ) != ERROR_TIME

	assert s.init( "* 1,2,5-12 1,7,9 12,1-10/5 1-6" ) == True
	assert s.calculateNext( 2009, 5, 7, 10, 31 ) != ERROR_TIME
	assert s.calculateNext( 2009, 5, 2, 10, 32 ) != ERROR_TIME
	assert s.calculateNext( 2009, 8, 17, 10, 33 ) != ERROR_TIME

	assert s.init( "* * * * *" ) == True
	assert s.calculateNext( 2009, 5, 7, 10, 33 ) != ERROR_TIME

	assert s.init( "* 1,2,5-12 1,7,9 12,1-10/5 0-6" ) == True
	assert s.calculateNext( 2009, 5, 7, 10, 32 ) != ERROR_TIME
	assert s.calculateNext( 2009, 8, 22, 10, 33 ) != ERROR_TIME

	assert s.init( "* 1,2,5-12 1,7,9 12,1-10/5 0-7" ) == True
	assert s.calculateNext( 2009, 5, 7, 10, 32 ) != ERROR_TIME
	assert s.calculateNext( 2009, 8, 22, 10, 33 ) != ERROR_TIME

	assert s.init( "* 1,2,5-12 1,7,9 12,1-10/5 1-7" ) == True
	assert s.calculateNext( 2009, 5, 7, 10, 32 ) != ERROR_TIME
	assert s.calculateNext( 2009, 8, 22, 10, 33 ) != ERROR_TIME

	assert s.init( "3,10,15 3,8,12 2,9,11 * *" ) == True
	time.localtime( s.calculateNext( 2009, 5, 9, 10, 5 ) )[:6] == ( 2009, 5, 9, 8, 10, 0 )
	assert time.localtime( s.calculateNext( 2009, 5, 10, 10, 5 ) )[:6] == ( 2009, 5, 11, 3, 3, 0 )

	assert s.init( "0 12 * * *" ) == True
	assert time.localtime( s.calculateNext( 2009, 8, 21, 12, 1 ) )[:6] != ( 2009, 8, 21, 12, 0, 0 )
	assert time.localtime( s.calculateNext( 2009, 8, 21, 12, 0 ) )[:6] == ( 2009, 8, 21, 12, 0, 0 )

	assert s.init( "0 12 * * 1-5" ) == True
	assert time.localtime( s.calculateNext( 2009, 8, 20, 13, 0 ) )[:6] == ( 2009, 8, 21, 12, 0, 0 )
	assert time.localtime( s.calculateNext( 2009, 8, 22, 0, 0 ) )[:6] == ( 2009, 8, 24, 12, 0, 0 )

	assert s.init( "* * 31 4 *" ) == True
	assert s.calculateNext( 2009, 8, 21, 13, 21 ) == ERROR_TIME

	assert s.init( "* * 29 2 *" ) == True
	assert s.calculateNext( 2009, 8, 21, 13, 21 ) != ERROR_TIME

	assert s.init( "* * 30 2 *" ) == True
	assert s.calculateNext( 2009, 8, 21, 13, 21 ) == ERROR_TIME

	assert s.init("0 12 * * 1-5") == True
	assert time.localtime( s.calculateNext( 2009, 8, 26, 11, 55 ) )[:6] == ( 2009, 8, 26, 12, 0, 0 )

	assert s.init( "0 12,18,23 1-7 10 *" ) == True
	assert s.calculateNext( 2010, 9, 30, 10, 10 ) == time.mktime( ( 2010, 10, 1, 12, 0, 0, 0, 0, 0 ) )

	print "time.time() - t:", time.time() - t
	print "Scheme test ok."

# test class Scheme
if __name__ == "__main__":
	test_Scheme()

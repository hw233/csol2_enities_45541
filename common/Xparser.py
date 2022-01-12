# -*- coding: gb18030 -*-
#
"""
"""
# $Id: Xparser.py,v 1.2 2005-08-19 08:23:44 phw Exp $

def lstripLines( string, chars ):
	"""
	删除所有行头与chars里指定字符相同的字符
	
	@param string: 要处理的源字符串
	@type  string: str
	@param  chars: 要删除的字符集合，例："\t \n\r"
	@type   chars: str
	@return:       返回处理过以后的字符串
	"""
	return "".join( [ e.lstrip( chars ) for e in string.splitlines(True) ] )

def rstripLines( string, chars ):
	"""
	删除所有行尾与chars里指定字符相同的字符
	
	@param string: 要处理的源字符串
	@type  string: str
	@param  chars: 要删除的字符集合，例："\t \n\r"
	@type   chars: str
	@return:       返回处理过以后的字符串
	"""
	return "".join( [ e.rstrip( chars ) for e in string.splitlines(True) ] )

def stripLines( string, chars ):
	"""
	删除所有行头行尾与chars里指定字符相同的字符
	
	@param string: 要处理的源字符串
	@type  string: str
	@param  chars: 要删除的字符集合，例："\t \n\r"
	@type   chars: str
	@return:       返回处理过以后的字符串
	"""
	return "".join( [ e.strip( chars ) for e in string.splitlines(True) ] )

class Xparser:
	"""
	简单的字符串解析器；
	它解释的字符串格式很像xml的格式，因此称其为XParser。
	"""
	def parseString( self, string ):
		"""
		解板对话里的关键字；这是一个很简单的解释器。
		
		@param string: 需要解释的字符串
		@type  string: str
		@return: 无
		"""
		state = 0
		posB = posE = 0
		while state != -1:
			if state == 0:
				state = 1
				posE = string.find( "[", posB )
				if posE == -1:
					posE = len( string )
					state = -1
				if posB < posE:
					self.characterDataHandler( string[posB:posE] )
				posB = posE + 1
			elif state == 1:	# ]
				state = 0
				posE = string.find( "]", posB )
				if posE == -1:
					raise "string format not right after %i col." % posB
					
				substr = string[posB:posE]
				if substr[0] == "/":	# 第一个字符是"/"则表示结束一个标识
					assert substr[-1] != "/"
					self.endElementHandler( substr[1:] )
				else:
					if substr[-1] == "/":
						hasEnd = True
						substr = substr[:-1]
					else:
						hasEnd = False
					tagList = substr.split( "=" )	# 切割参数
					se = tagList[0].strip( " \t" )
					if len( tagList ) == 1:
						self.startElementHandler( se, "" )
					else:
						self.startElementHandler( se, tagList[1].strip( " \t" ) )
					if hasEnd:
						self.endElementHandler( se )
				posB = posE + 1
		# end of while ...
	### end of method: parseString ###
	
	def startElementHandler( self, name, attrs ):
		"""
		开始一个元素(标识)
		
		@param  name: 开始一个标识
		@type   name: string
		@param attrs: 标识附加属性
		@type  attrs: string
		@return: 无
		"""
		raise "we must implement this method."
	
	def endElementHandler( self, name ):
		"""
		结束一个元素(标识)
		
		@param  name: 结果一个标识
		@type   name: string
		@return: 无
		"""
		raise "we must implement this method."
	
	def characterDataHandler( self, data ):
		"""
		字符串处理
		
		@param  name: 标识以外的数据
		@type   name: string
		@return: 无
		"""
		raise "we must implement this method."

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/07/29 02:41:35  phw
# 解释类似于以下内容的字符串中"[]"包含的内容的解释器底层。
#
# 	\\t小样的，别在我面前晃
# fkldjlldf[MENU=xiangshi]想死？[/MENU]
# 	eths[MENU=xianghuo]想活？[/MENU]idghs
# 小心我把你给咔嚓了...
#
#

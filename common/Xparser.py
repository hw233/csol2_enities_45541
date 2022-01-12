# -*- coding: gb18030 -*-
#
"""
"""
# $Id: Xparser.py,v 1.2 2005-08-19 08:23:44 phw Exp $

def lstripLines( string, chars ):
	"""
	ɾ��������ͷ��chars��ָ���ַ���ͬ���ַ�
	
	@param string: Ҫ�����Դ�ַ���
	@type  string: str
	@param  chars: Ҫɾ�����ַ����ϣ�����"\t \n\r"
	@type   chars: str
	@return:       ���ش�����Ժ���ַ���
	"""
	return "".join( [ e.lstrip( chars ) for e in string.splitlines(True) ] )

def rstripLines( string, chars ):
	"""
	ɾ��������β��chars��ָ���ַ���ͬ���ַ�
	
	@param string: Ҫ�����Դ�ַ���
	@type  string: str
	@param  chars: Ҫɾ�����ַ����ϣ�����"\t \n\r"
	@type   chars: str
	@return:       ���ش�����Ժ���ַ���
	"""
	return "".join( [ e.rstrip( chars ) for e in string.splitlines(True) ] )

def stripLines( string, chars ):
	"""
	ɾ��������ͷ��β��chars��ָ���ַ���ͬ���ַ�
	
	@param string: Ҫ�����Դ�ַ���
	@type  string: str
	@param  chars: Ҫɾ�����ַ����ϣ�����"\t \n\r"
	@type   chars: str
	@return:       ���ش�����Ժ���ַ���
	"""
	return "".join( [ e.strip( chars ) for e in string.splitlines(True) ] )

class Xparser:
	"""
	�򵥵��ַ�����������
	�����͵��ַ�����ʽ����xml�ĸ�ʽ����˳���ΪXParser��
	"""
	def parseString( self, string ):
		"""
		���Ի���Ĺؼ��֣�����һ���ܼ򵥵Ľ�������
		
		@param string: ��Ҫ���͵��ַ���
		@type  string: str
		@return: ��
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
				if substr[0] == "/":	# ��һ���ַ���"/"���ʾ����һ����ʶ
					assert substr[-1] != "/"
					self.endElementHandler( substr[1:] )
				else:
					if substr[-1] == "/":
						hasEnd = True
						substr = substr[:-1]
					else:
						hasEnd = False
					tagList = substr.split( "=" )	# �и����
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
		��ʼһ��Ԫ��(��ʶ)
		
		@param  name: ��ʼһ����ʶ
		@type   name: string
		@param attrs: ��ʶ��������
		@type  attrs: string
		@return: ��
		"""
		raise "we must implement this method."
	
	def endElementHandler( self, name ):
		"""
		����һ��Ԫ��(��ʶ)
		
		@param  name: ���һ����ʶ
		@type   name: string
		@return: ��
		"""
		raise "we must implement this method."
	
	def characterDataHandler( self, data ):
		"""
		�ַ�������
		
		@param  name: ��ʶ���������
		@type   name: string
		@return: ��
		"""
		raise "we must implement this method."

#
# $Log: not supported by cvs2svn $
# Revision 1.1  2005/07/29 02:41:35  phw
# �����������������ݵ��ַ�����"[]"���������ݵĽ������ײ㡣
#
# 	\\tС���ģ���������ǰ��
# fkldjlldf[MENU=xiangshi]������[/MENU]
# 	eths[MENU=xianghuo]��[/MENU]idghs
# С���Ұ����������...
#
#

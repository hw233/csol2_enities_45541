# -*- coding: utf-8 -*-

#skid.txt   ���� datatools �л�ȡ�ļ���id

from temp import skillConfig as sc

outfile1 = "����û�У�������.txt"
outfile2 = "�����У�����û��.txt"

def notInConfig():
	f = open( "temp/skid.txt", "r")
	ids = f.readlines()
	f.close()
	l = []
	for id in ids:
		sk = "Datas_"+id[0:-1]
		if not hasattr( sc, sk ):
			l.append( id )
	
	f = open( outfile2, "w" )
	f.writelines( l )
	f.close()



def notInTools():
	f = open( "temp/skid.txt", "r")
	ids = f.readlines()
	f.close()
	l = []
	for i in dir( sc ):
		if "Datas_" in i:
			id = i.split("_")[1]
			if not id+"\n" in ids:
				l.append(id+"\n")

	f = open( outfile1, "w" )
	f.writelines( l )
	f.close()
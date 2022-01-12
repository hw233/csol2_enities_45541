# -*- coding: utf-8 -*-
#1,��ȷ��ָ���û��Ļ�������MF_ROOT·���Ƿ���ȷ,ȷ��MF_ROOT/bigworld/tools/server/control_cluster.py����
#2,������ű��ŵ�entities/cell/testĿ¼��
#3,�༭linux�ƻ�����ÿ���賿1��ִ��һ��
#crontab -u csol -e
#0 1 * * * python /home/hsq/mf181/bigworld/tools/server/control_cluster.py runscript cellapp01 `echo "import sys;sys.path.append('entities/cell/test');import start_test;reload(start_test);start_test.run('entities/cell/test')" > /tmp/tstart.py` /tmp/tstart.py
#4,��д���Խű�Ҫ�ڲ��Խű����������������
#runfunc = [test1, test3, test2]
#�������ű�֪���Ǹ���������ִ��
import os
import imp
import traceback 
def run(path):
    print "BEGIN TEST ......"
    fileList = os.listdir(path)
    for i in fileList:
        if i.endswith(".py"):
            filepath = path + "/" + i
            filepath = filepath.replace("\\", "/")

            try:
                module = imp.load_source(i[0:-3], filepath) 
            except  Exception, e:
                print traceback.format_exc() 
                print "ERROR LOAD SOURCE [%s]" % filepath,
                continue

            if hasattr(module, "runfunc"):
                for func in module.runfunc:
                    print "START TEST [%s,%s]" % (module.__file__, func.__name__)
                    try:
                        if func():
                            print "RUN IS OK .."
                        else:
                            print "HAS ERROR .."
                    except Exception, e:
                        print traceback.format_exc() 
                        print "EXCEPT [%s,%s]" % (module.__file__, func.__name__)

                    print "FINISH TEST [%s,%s]" % (module.__file__, func.__name__)
    print "END TEST ......"

#if __name__ == "__main__":
#    run_test()

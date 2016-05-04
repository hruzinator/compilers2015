import os
print '-Testing bad file-'
os.system('coverage run -p main.py foobar.pas')
print '-Running comprehensiveSource.pas-'
os.system('coverage run -p main.py ./test/comprehensiveSource.pas')
os.system('mv lineListing.txt ./test/comprehensiveSourceLineListing.txt')
print '-Running proj34Test.pas-'
os.system('coverage run -p main.py ./test/proj34Test.pas')
os.system('mv lineListing.txt ./test/test1LineListing.txt')
print '-Running proj34Test-2.pas-'
os.system('coverage run -p main.py ./test/proj34Test-2.pas')
os.system('mv lineListing.txt ./test/test2LineListing.txt')
print '-Running proj34Test-MyTests.pas-'
os.system('coverage run -p main.py ./test/proj34Test-MyTests.pas')
os.system('mv lineListing.txt ./test/myTestLineListing.txt')
os.system('coverage combine')
os.system('coverage report -m --include parser.py')
os.system('coverage html')

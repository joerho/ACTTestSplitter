import glob
import os

CONST_PATH_TO_ACT_TESTS = "/Users/joerho/ModusDropBox/Dropbox/Modus Teachers (Shared)/1 ACT/ REAL ACT TESTS/Single File"

def actpreparse(fileName):
	allTestPaths = glob.glob(os.path.join(CONST_PATH_TO_ACT_TESTS, "*.pdf"))
	allTests = list()
	for test in allTestPaths:
		(head, tail) = os.path.split(test)
		allTests.append(tail)

	allTests.sort()
	with open('{}.txt'.format(fileName), 'w+') as inputFile:
		inputFile.write(';\n'.join(allTests))

actpreparse("inputdata")
actpreparse("testnames")



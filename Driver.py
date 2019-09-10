import sys
from actparser import actparse

def main(argv):
	with open(argv[0], "r") as pdfList:
		line = pdfList.readline()
		while line:
			line = line.rstrip().split(';')
			actparse(line)
			line = pdfList.readline()
			



if __name__ == '__main__':
	main(sys.argv[1:])
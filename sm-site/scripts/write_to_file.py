import sys

if __name__ == "__main__":
	f = open("speed-limit.txt", "w")
	f.write(sys.argv[1])
	f.close()

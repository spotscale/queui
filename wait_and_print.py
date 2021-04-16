import sys
import time

if __name__ == "__main__":
    print("doing some heavy calculations!")
    time.sleep(5)
    print("Message: " + str(sys.argv[1]))

import random
#from multiprocessing import Process, Value, Semaphore
from lithops.multiprocessing import Process, Value, Semaphore
import time

def prepareSleigh():
    print("Santa Claus: preparing sleigh")


def helpElves():
    print("Santa Claus: helping elves")


def getHitched(reindeer_c):
    print("This is reindeer ", reindeer_c)


def getHelp(elves_c):
    print("This is elve", elves_c)


def santa(elves_c, reindeer_c, santaSem, elfTex, reindeerSem, mutex, num_years, max_years):
    print("Santa Claus: Hoho, here I am")
    while num_years.value != max_years.value:
        if num_years.value == max_years.value:
            break
        santaSem.acquire()
        mutex.acquire()
        if reindeer_c.value >= 9:
            prepareSleigh()
            for i in range(9):
                reindeerSem.release()
            print("Santa Claus: make all kids in the world happy")
            with reindeer_c.get_lock():
                reindeer_c.value -= 9
            time.sleep(4)
            with num_years.get_lock():
                num_years.value += 1
        elif elves_c.value == 3:
            helpElves()
        mutex.release()
        if num_years.value == max_years.value:
            for i in range(20):
                santaSem.release()
            for i in range(20):
                mutex.release()
            for i in range(20):
                reindeerSem.release()
            for i in range(20):
                elfTex.release()
            print("----------------- Christmas ended! ----------------------")


def reindeer(reindeer_c, santaSem, reindeerSem, mutex, num_years, max_years):
    while num_years.value != max_years.value:
        if num_years.value == max_years.value:
            break
        mutex.acquire()
        with reindeer_c.get_lock():
            reindeer_c.value += 1
        if reindeer_c.value == 9:
            santaSem.release()
        mutex.release()
        getHitched(reindeer_c.value)
        print("Reindeer", reindeer_c.value, "getting hitched")
        if num_years.value == max_years.value:
            break
        reindeerSem.acquire()
        time.sleep(random.randint(2, 3))


def elves(elves_c, santaSem, elfTex, mutex, num_years, max_years):
    while num_years.value != max_years.value:
        if num_years.value == max_years.value:
            break
        elfTex.acquire()
        mutex.acquire()
        with elves_c.get_lock():
            elves_c.value += 1
        if elves_c.value == 3:
            santaSem.release()
        else:
            elfTex.release()
        mutex.release()
        getHelp(elves_c.value)
        time.sleep(random.randint(2, 5))
        if num_years.value == max_years.value:
            break
        mutex.acquire()
        with elves_c.get_lock():
            elves_c.value -= 1
        if elves_c.value == 0:
            elfTex.release()
        mutex.release()
        print("Elve", elves_c.value, "at work")


def main():
    elves_c = Value('i', 0)
    reindeer_c = Value('i', 0)
    num_years = Value('i', 0)
    max_years = Value('i', 2)

    santaSem = Semaphore()
    reindeerSem = Semaphore()
    elfTex = Semaphore()
    mutex = Semaphore(1)
    
    elfThread = []  # threads for elves
    reindThread = []  # threads from reindeers

    thread = Process(target=santa, args=(elves_c, reindeer_c, santaSem, elfTex, reindeerSem, mutex, num_years, max_years,))  # main thread for SantaClaus
    thread.start()  # starting the thread
    for i in range(9):
        reindThread.append(Process(target=reindeer, args=(reindeer_c, santaSem, reindeerSem, mutex, num_years, max_years,)))
    for j in range(9):
        elfThread.append(Process(target=elves, args=(elves_c, santaSem, elfTex, mutex, num_years, max_years,)))
    for t in elfThread:
        t.start()
    for t in reindThread:
        t.start()
    for t in elfThread:
        t.join()
    for t in reindThread:
        t.join()
    thread.join()

if __name__ == "__main__":
    main()
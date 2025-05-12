from csidh import CSIDHCW as CSIDH
from csidh.search import *
import chipwhisperer as cw
import time
import os
import sys
import logging

from tqdm.notebook import trange
import random
import secrets

N_ITERS = 5
POPSIZE = 100

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, encoding="utf-8")

seed = random.randint(0, 2**32)
random.seed(seed)

def algo_search(csidh):
    """Parameter search using own algorithm"""

    population = generate_population(POPSIZE)
    N_scanned = []

    logger.info("Starting GA")
    t0 = tgen = time.time()
    for i in range(N_ITERS):
        logger.info("Iteration {}".format(i + 1))
        fits = evaluate_batch(csidh, population)
        population = selection_roulette(population, elite_size=3)
        logger.info(fits)
        logger.info("Mean={}, max={}".format(np.mean(fits), np.max(fits)))
        logger.info(
            "Iteration took {:.2f}s, total {:.2f}".format(
                time.time() - tgen, time.time() - t0
            )
        )
        tgen = time.time()

    t1 = time.time()
    N_scanned.append(len(cache))

    logger.info("Time elapsed GA/total: {}/{} s".format(t1 - t0, t1 - t0))
    logger.info("Scanned points GA/total: {}/{}".format(N_scanned[0], sum(N_scanned)))
    logger.info(" speed: {}s per point".format((t1 - t0) / N_scanned[-1]))

    write_cache_to_file("cache.json", cache, N_ITERS, POPSIZE, seed)


def main():
    logger.setLevel(logging.DEBUG)
    # Path to the CSIDH torget source code
    PATH = "/home/xjaros2/Documents/git/csidh-setup/csidh-target/src/"
    attack_type = "A2"

    # Initialize the CSIDH wrapper
    csidh = CSIDH(PATH, attack_type=attack_type)

    csidh.setup()

    csidh.flash_target()

    # Capture the first public key
    csidh.scope.arm()
    csidh.action()
    ret = csidh.scope.capture()
    if ret:
        logging.info("Timeout happened during acquisition")
    EXPECTED_PUBLIC = csidh.public_with_errors
    EXT_OFFSET_MAX = csidh.scope.adc.trig_count
    print(f"{EXPECTED_PUBLIC=}")
    print(f"{EXT_OFFSET_MAX=}")

    csidh.voltage_glitching_setup()

    Unit.is_husky = True
    # Setup unit parameter ranges
    Unit.OFFSET_MIN = 2500
    Unit.OFFSET_MAX = 3000
    Unit.OFFSET_RANGE = Unit.OFFSET_MAX - Unit.OFFSET_MIN

    Unit.WIDTH_MIN = 2500
    Unit.WIDTH_MAX = 3000
    Unit.WIDTH_RANGE = Unit.WIDTH_MAX - Unit.WIDTH_MIN

    Unit.EXT_OFFSET_MIN = 0
    Unit.EXT_OFFSET_MAX =  EXT_OFFSET_MAX
    Unit.EXT_OFFSET_RANGE = Unit.EXT_OFFSET_MAX - Unit.EXT_OFFSET_MIN

    Unit.REPEAT_MIN = 4
    Unit.REPEAT_MAX = 6
    Unit.repeat_range = Unit.REPEAT_MAX - Unit.REPEAT_MIN

    print("seed: {}".format(seed))
    algo_search(csidh)
    print("seed: {}".format(seed))


if __name__ == "__main__":
    main()

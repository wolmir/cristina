"""High scores."""

from const import NUM_LEVELS

_FNAME = 'highscores.txt'

_DEFAULT = {}

# named constant for if the level hasn't been finished yet
NO_SCORE = -1

for i in range(1, NUM_LEVELS + 1):
    # nsaved, nmoves
    _DEFAULT[i] = (NO_SCORE, NO_SCORE)

# the current state of the high scores, keys are level numbers
scores = {}

def load_high_scores():
    global scores
    try:
        f = open(_FNAME, 'r')
    except IOError:
        scores = _DEFAULT
        return
    for lin in f.readlines():
        lev, nsaved, nmoves = lin.split(',')
        scores[int(lev)] = (int(nsaved), int(nmoves))
    f.close()

def get_score_string(n):
    if (n == NO_SCORE):
        return '-'
    return str(n)

def get_score_strings_for_level(lev):
    sc = scores[lev]
    return get_score_string(sc[0]), get_score_string(sc[1])

def write_high_scores():
    try:
        f = open(_FNAME, 'w')
    except:
        return
    levs = scores.keys()
    levs.sort()
    for k in levs:
        score = scores[k]
        f.write('{0},{1},{2}\n'.format(k, score[0], score[1]))
    f.close()
    
def update_high_scores(level, sc):
    scores[level] = sc
    write_high_scores()

def is_better(level, new_score):
    """Return true if new_score is better than old score for level."""

    old_score = scores[level]
    if (new_score[0] > old_score[0]):
        # we saved more bits
        return True
    elif (new_score[0] == old_score[0]):
        if (new_score[1] < old_score[1]):
            # same number of bits saved, but in fewer moves
            return True
    return False

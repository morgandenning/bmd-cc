import logging, numpy as np, time

logger = logging.getLogger('PROCESS_GRAVITY')

def process_gravity(input):

    t = time.process_time()
    matrix = []
    for line in input.splitlines():
        matrix.append([x for x in line])

    matrix = np.array(matrix)
    as_cols = matrix.transpose()

    logger.info(f'Found Matrix of Size {matrix.shape}')

    for x, i in enumerate(as_cols):
        if (i == 'T').sum() > 0:
            l = list(i.ravel())
            t_loc = l.index('T')

            pre_count = (i[0:t_loc] == '.').sum() + ((i[0:t_loc] == ':').sum() * 2)
            post_count = (i[t_loc:] == '.').sum() + ((i[t_loc:] == ':').sum() * 2)

            pre_list = ([':'] * int(pre_count / 2)) + (['.'] * (pre_count % 2))
            post_list = ([':'] * int(post_count / 2)) + (['.'] * (post_count % 2))

            pre_list += [' '] * (t_loc - len(pre_list))
            pre_list.reverse()

            post_list += [' '] * ((len(i) - t_loc - len(pre_list)))
            post_list.reverse()

            l = np.array(pre_list + ['T'] + post_list)

        else:
            count = (i == '.').sum() + ((i == ':').sum() * 2)

            l = ([':'] * int(count / 2)) + (['.'] * (count % 2))
            l += [' '] * (len(i) - len(l))
            l.reverse()

        as_cols[x] = np.array(l)

    et = time.process_time() - t

    logger.info(f'World Processing Time: {et}')

    return as_cols.transpose(), et


def to_text(input):
    r = ""
    for i in input:
        for x in i:
            r += x
        r += "\n"

    return r


directory = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/'
for movie in ['AHKJ_rating_avg_movieA.txt', 'AHKJ_rating_avg_movieB.txt', 'AHKJ_rating_avg_movieC.txt']:

    with open(directory + movie, 'r') as file:
        content = file.readlines()
        content = [line.split('\n')[0] for line in content]

    pos = []
    neg = []
    for line in content:
        if float(line) > 0:
            pos.append(line)
            neg.append('0')
        if float(line) < 0:
            pos.append('0')
            neg.append(str(-float(line)))
        if float(line) == 0:
            pos.append('0')
            neg.append('0')

        movie_name = movie.split('.txt')[0]
        with open(f'{directory}{movie_name}_pos.txt', 'w') as file:
            for line in pos:
                file.write(f"{line}\n")
        with open(f'{directory}{movie_name}_neg.txt', 'w') as file:
            for line in neg:
                file.write(f"{line}\n")


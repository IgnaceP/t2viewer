
def printProgressBar(iteration, total,printBar = True,  prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if printBar:
        print('\r%s |%s| %s%% %s\r' % (prefix, bar, percent, suffix), end = printEnd)
    else:
        print('\r%s%% %s' % (percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

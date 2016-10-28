"""
Prepare RSC for parsing using existing tags
"""

def _makeline(plain):
    """
    Turn a TSV into a single line of space sep tokens
    with each token being word_pos
    """
    import pandas as pd
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
    nms = ['w', 'p', 'l', 'w2', 'a', 'b', 'c', 'd']
    df = pd.read_csv(StringIO(plain), sep='\t', header=None, names=nms)
    df = df.fillna('???')
    # lemma could be added here too
    underscore_sep = df['w'].str.cat([df['p']], sep='_')
    s = ' '.join(underscore_sep)
    #lin = underscore_sep.str.join(sep=' ')
    #print(lin)
    return s

def split_file(f):
    """
    Take the  large .vrt file and make separate files
    for each text, to improve speed of later ops
    """
    import os
    import re
    from corpkit.constants import OPENER
    outdir = 'splitfiles'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    s = 0
    with OPENER(f, 'r') as fo:
        for line in fo:
            if line.lstrip().startswith('<text id="'):
                namefind = re.compile('<text id="([0-9]+)"')
                name = re.search(namefind, line).group(1)

                outpath = os.path.join(outdir, '%s.txt' % name)
                outf = OPENER(outpath, 'w')
                s += 1
            outf.write(line)

def main(f='rsc_v2-0.vrt', indir='splitfiles'):
    import os
    import re
    import pandas as pd
    from corpkit.constants import OPENER
    
    # make the split file if not done already
    if not os.path.exists(indir):
        splitfiles(f)

    namefind = re.compile('<text id="([0-9]+)"')
    yearfind = re.compile(' year="([0-9]+)"')
    metafind = re.compile('(<text id=.*>)\s*')
    delim = '<text id="'
    selim = '<s no="'
    outdir = 'processed'

    files = [os.path.join(indir, f) for f in os.listdir(indir)]
    
    for n, fpath in enumerate(files, start=1):

        print('%d/%d' % (n, len(files)))

        with OPENER(fpath, 'r') as fo:
            text = fo.read()

        out = []
        name = re.search(namefind, text).group(1)
        name = name + '.txt'
        year = re.search(yearfind, text).group(1)
        outd = os.path.join(outdir, year)
        meta = re.search(metafind, text).group(1)
        meta = ' ' + meta.replace('text', 'metadata', 1)
        splt = [i for i in text.splitlines() if not i.startswith('<') and not i.endswith('>')]
        if not os.path.exists(outd):
            os.makedirs(outd)
        sents = [e+selim for e in '\n'.join(splt).split(selim) if e]
        for sent in sents:
            line = _makeline(sent)
            line = line + meta
            out.append(line.strip())
        as_s = '\n'.join(out)
        # bug here to fix, this is just a hack
        as_s = as_s.replace('._SENT', '._. %s\n' % meta)
        with OPENER(os.path.join(outd, name), 'w') as fo:
            fo.write(as_s) 

if __name__ == '__main__':
    main()

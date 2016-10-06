#!/usr/bin/python

"""
Convert jstor xml of RSC corpus to plain text with metadata in a single xml tags

Optionally, parse this using corpkit/corenlp

Usage: python convert_xml_to_corpkit.py
"""

def pre_process(indir='xml'):
    """
    Move folders to less redundant structure
    """
    d = {'abs_communicated/fla': 'abs_com_fla',
        'abs_printed/fla': 'abs_prt_fla',
        'proceedings/fla': 'pro_fla',
        'proceedings/nws': 'pro_nws',
        'transactions/brv': 'trn_brv',
        'transactions/fla': 'trn_fla'}
    import os
    import shutil
    for k, v in d.items():
        shutil.move(os.path.join(indir, k), os.path.join(indir, v))
    fs = [os.path.join(indir, i) for i in os.listdir(indir) if i not in d.values() and not i.startswith('.')]
    for f in fs:
        shutil.rmtree(f)

def format_langs_output(output_list):
    """
    Take langdetect result and give us the language and probability
    """
    found_english = True
    eng = next((i for i in output_list if i.lang.startswith('en')), False)
    if not eng:
        found_english = False
        lang, prob = output_list[0].lang, output_list[0].prob
    else:
        lang, prob = output_list[0].lang, eng.prob
    
    # bug? latin isn't detected well
    if lang == 'ca':
        lang == 'la'

    score = '%.3f' % float(prob)
    if not found_english:
        score = '0.000'        
    return lang, score

def turn_to_plaintext(corpus_dir='xml'):
    """
    turn  xml corpus into corpkit input
    takes about 5 minutes, most of which is lang detection
    also determines language so that we can remove baddies later
    """
    import os
    # just an os.walk/glob type function
    from corpkit.build import get_filepaths
    from lxml import etree as ET
    from langdetect import detect, detect_langs

    # make a new directory if need be
    corpus_dir = 'xml'
    outdir = '%s-form' % corpus_dir
    try:
        os.makedirs(outdir)
    except OSError:
        pass

    # this function pretty much just calls os.walk
    fs = get_filepaths(corpus_dir, 'xml')

    # parse metadata, put in corpkit format
    # write to same filepath in outdir
    for index, f in enumerate(fs, start=1):
        # progress info
        print("%.2f: %s" % ((index * 100.0 / len(fs)), f))
        # make new filename
        fpath, fname = os.path.split(f)
        outpath = fpath.replace(corpus_dir, outdir, 1)
        outname = fname.replace('.xml', '.txt')
        try:
            os.makedirs(outpath)
        except OSError:
            pass
        # get all the xml into a string
        root = ET.parse(f).getroot()
        metastring = ' <metadata '
        for k, v in sorted(root.items()):
            k = k.strip('"').strip("'").lstrip().rstrip()
            v = v.strip('"').strip("'").lstrip().rstrip()
            metastring += "%s='%s' " % (k, v)

        pages = ''
        # detect language
        langs = detect_langs('\n'.join([i.text for i in root if i.text]))
        lang, score = format_langs_output(langs)

        # pages don't end at sentence boundaries. join it all together
        for i, page in enumerate(root, start=1):
            if page.text:
                pagetext = page.text.replace('\n', ' ')
                pages += pagetext.rstrip('\n')
        
        metend = "lang='%s' engprob='%s'>\n" % (lang, score)
        pages += metastring + metend
            
        # write to file
        with open(os.path.join(outpath, outname), 'w') as fo:
            fo.write(pages.encode('utf-8'))
    return outdir

def move_and_parse(indir='xml-form'):
    """
    Use corpkit/CoreNLP to parse the corpus
    """
    import shutil
    import os
    from corpkit import Corpus, new_project    
    
    # make a new project and move into it
    new_project('rsc-proj')
    shutil.copytree('xml-form', 'rsc-proj/data')
    os.chdir('rsc-proj')
    corpus = Corpus('rsc-form')
    parsed = corpus.parse(metadata=True, speaker_segmentation=False,
                          multiprocess=15)



if __name__ == '__main__':
    indir = 'xml'
    pre_process(indir)
    out = turn_to_plaintext(indir)
    # parse it:
    # move_and_parse(out)

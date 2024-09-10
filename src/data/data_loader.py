import os
import sys
from os.path import join
import collections
from glob import glob, escape
from pathlib import Path
from itertools import chain
from tqdm import tqdm
import re


# ------------------------------------------------------------------------
# document loading routine
# ------------------------------------------------------------------------
def remove_pattern(doc, start_symbol, end_symbol, counter):
    #assert counter[start_symbol] == counter[end_symbol], 'wrong number of {}{} found'.format(start_symbol,end_symbol)
    search = True
    while search:
        start = doc.find(start_symbol)
        if start > -1:
            end = doc[start + 1:].find(end_symbol)
            doc = doc[:start] + doc[start + 1 + end + 1:]
        else:
            search = False
    return doc

def clean_texts(text):
    text = re.sub("\n+", " ", text)
    text = re.sub("\s+", " ", text)
    text = re.sub('\*.*?\*', "", text)
    text = re.sub('\{.*?\}', "", text)
    text = re.sub('[0-9]', "", text)
    text = re.sub("\n+", " ", text)
    text = re.sub("\s+", " ", text)
    text = text.lower()
    text = text.replace('v', 'u')
    text = text.replace('j', 'i')
    text = re.sub('\.\s+(?=\.)|\.\.+', "", text)
    text = re.sub("\n+", " ", text)
    text = re.sub("\s+", " ", text)
    text = re.sub("\(|\)|\[|\]", "", text)
    text = re.sub("\—|\–|\-|\_", "", text)
    text = re.sub("\‹|\›|\»|\«|\=|\/|\\|\~|\§|\*|\#|\@|\^|\“|\”|\‘|\’", "", text)
    text = re.sub("\&dagger;|\&amacr;|\&emacr;|\&imacr;|\&omacr;|\&umacr;|\&lsquo;|\&rsquo;|\&rang;|\&lang;|\&lsqb;", "", text)
    text = re.sub("\?|\!|\:|\;", ".", text)
    text = text.replace("'", "")
    text = text.replace('"', '')
    text = text.replace(".,", ".")
    text = text.replace(",.", ".")
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = re.sub('(\.)+', ".", text)
    text = re.sub('(\,)+', "", text)
    text = text.replace("á", "a")
    text = text.replace("é", "e")
    text = text.replace("í", "i")
    text = text.replace("ó", "o")
    text = text.replace("ç", "")
    text = re.sub("\n+", " ", text)
    text = re.sub("\s+", " ", text)
    return text


# removes citations in format:
#    *latino*
#    {volgare}
def  remove_citations(doc, clean_text=False):
    counter = collections.Counter(doc)
    doc = remove_pattern(doc, start_symbol='*', end_symbol='*', counter=counter)
    doc = remove_pattern(doc, start_symbol='{', end_symbol='}', counter=counter)

    doc = ' '.join(doc.split())
    doc = doc.lower()

    # if clean_text:
    #     clean_texts()
    return doc


def load_medlatin_singlecorpus(path, unknown_target=None, train_skip_prefix='Epistola'):
    """
    Function used to load the Corpus I and Corpus II for authorship attribution.
    The corpus is assumed to contain files named according to <author>_<text_name>.txt.
    :param path: the path containing the texts, each named as <author>_<text_name>.txt
    :param positive_author: the author that defines the positive class for verification
    :param unknown_target: if specified, is the path to the unknown document whose paternity is to be check (w.r.t.
    the positive_author)
    :param train_skip_prefix: specify a prefix for documents that should be skipped
    :return: a tuple containing the positive documents, negative documents, paths to positive documents, paths to
    negative documents, and the unknown document if that was specified (otherwise an empty list)
    """
    # load the training data (all documents but Epistolas 1 and 2)
    filenames = []
    authors = []
    documents = []
    ndocs=0
    dirs = os.listdir(path)
    for file in tqdm(dirs, total=len(dirs), desc='loading: ' + path):
        if file.startswith(train_skip_prefix):
            print('found a file that will be skipped: ', file)
            sys.exit(0)
        if f'{path}/{file}' == unknown_target: continue
        file_name = file.replace('.txt','')
        author, textname = file_name.split('_')
        text = open(join(path,file), encoding= "utf8").read()
        text = remove_citations(text)

        documents.append(text)
        filenames.append(file_name)
        authors.append(author)
        ndocs += 1

    return documents, authors, filenames


def load_medlatin_corpus(path, unknown_target=None, train_skip_prefix='Epistola'):
    docsEpi, authorsEpi, filesEpi = load_medlatin_singlecorpus(f'{path}/MedLatinEpi', unknown_target, train_skip_prefix)
    docsLit, authorsLit, filesLit = load_medlatin_singlecorpus(f'{path}/MedLatinLit', unknown_target, train_skip_prefix)
    docs = docsEpi+docsLit
    authors = authorsEpi+authorsLit
    filenames = filesEpi+filesLit
    return docs, authors, filenames


def load_quaestio_corpus(path):
    authors, documents, filenames = [], [], []
    dirs = glob(f'{path}/*/')
    for dirname in tqdm(dirs, total=len(dirs), desc='loading: ' + path):
        dir = Path(dirname)
        author = dir.name
        author = author.replace(' ', '')
        if '(' in author:
            author = author[:author.index('(')]
        if ']' in author:
            author = author[author.index(']')+1:]

        dirname = escape(dirname)
        # print(f'opening {dirname}')
        for doc in glob(f'{dirname}/*.txt'):
            doc = Path(doc)
            # print('\topening', doc.name)
            text = open(str(doc), 'rt').read()
            # print('\t\texerpt:', text[:50], '...')
            authors.append(author)
            documents.append(text)
            filenames.append(doc.name.replace('.txt', ''))

    return documents, authors, filenames


def load_corpus(path, remove_epistles=False, remove_test=True, remove_egloghe=False):
    filenames = []
    authors = []
    documents = []
    ndocs=0
    dirs = os.listdir(path)
    for file in tqdm(dirs, total=len(dirs), desc='loading: ' + path):
        if file.endswith('txt'):
            
            if remove_epistles:
                files_removed = 0
                if 'epistola' in file.lower():
                    print('removing', file)
                    files_removed += 1
                    continue
            
            if remove_egloghe:

                if 'egloga' in file.lower():
                    print('removing egloga', file)
                    continue

            if remove_test:
                if ' quaestio' in file.lower():
                    print('removing test document', file)
                    continue
            
            # if 'monarchie' in file.lower():
            #         print('removing document', file)
            #         continue
            

            # if 'monarchia_i' in file.lower() and 'monarchia_i.txt' not in file.lower():
            #         print('removing monarchia document', file)
            #         continue
            
            file_name = file.replace('.txt','')
            author, textname = file_name.split('-')
            text = open(join(path,file), encoding= "utf8", errors='ignore').read()

            #cleaning
            text = re.sub('\{[^{}]*\}', "", text)
            text = re.sub('\*[^**]*\*', "", text)
            text=text.lower()
            text=text.strip()
            text = text.replace('\x00', '') #remove null bytes
            text = re.sub('<\w>(.*?)</\w>', '\1', text)
            #text = remove_citations(text) # da rivedere
   
            documents.append(text)
            filenames.append(file_name)
            authors.append(author.strip())
            ndocs += 1
    print('Total documents:', len(documents))
    print('Total authors:', len(list(set(authors))))


    return documents, authors, filenames


def load_corpora(path, medlatinepi=True, medlatinlit=True, quaestio=True):
    #assert medlatinepi or medlatinlit or quaestio or medspanish, 'nothing to load, abort'
    outs = []
    if medlatinepi:
        outs.append(load_medlatin_singlecorpus(f'{path}/MedLatin/Corpora/MedLatinEpi'))
    if medlatinlit:
        outs.append(load_medlatin_singlecorpus(f'{path}/MedLatin/Corpora/MedLatinLit'))
    if quaestio:
        outs.append(load_quaestio_corpus(f'{path}/Progetto Quaestio')) 
    docs = list(chain.from_iterable(docs for docs, authors, filenames in outs))
    authors = list(chain.from_iterable(authors for docs, authors, filenames in outs))
    filenames = list(chain.from_iterable(filenames for docs, authors, filenames in outs))
    return docs, authors, filenames


if __name__ == '__main__':

    documents, authors, filenames = load_corpus('../../LatinCorpus')
    print(f'read {len(documents)} documents')
    print(f'#authors {len(set(authors))}')




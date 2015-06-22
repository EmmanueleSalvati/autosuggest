"""
Credits to this blogger for writing the code of ternary search trees:
http://hacktalks.blogspot.com/2012/03/implementing-auto-complete-with-ternary.html

Please Check This link For Theory Of TST :
# http://en.wikipedia.org/wiki/Ternary_search_tree

Each node contains 5 parts They are
self.ch => contains the character
self.flag => Flag to Check whether the node is an end character of a valid string
self.left, self.right => Links to the next nodes (Working similar to Binary
                                                  Search Tree)
# self.center => Link to the next valid character
"""

import json
import cPickle as pkl
import sys
import os.path
sys.setrecursionlimit(10000)


class Node:
    def __init__(self, ch, flag):
        """Constructor for Node Object"""

        self.ch = ch
        self.flag = flag
        self.left = 0
        self.right = 0
        self.center = 0

    def Add(self, string, node):
        """Function to add a string"""

        key = string[0]

        if node == 0:
            node = Node(key, 0)

        if key < node.ch:
            node.left = node.Add(string, node.left)
        elif key > node.ch:
            node.right = node.Add(string, node.right)
        else:
            if len(string) == 1:
                node.flag = 1
            else:
                node.center = node.Add(string[1:], node.center)

        return node

    def spdfs(self, match):
        """DFS for Ternary Search Tree"""

        if self.flag == 1:
            print match
            # print "Match : ", match

        if self.center == 0 and self.left == 0 and self.right == 0:
            return

        if self.center != 0:
            self.center.spdfs(match + self.center.ch)

        if self.right != 0:
            self.right.spdfs(match[:-1] + self.right.ch)

        if self.left != 0:
            self.left.spdfs(match[:-1]+self.left.ch)

    def simple(self, string):
        """ Function to search a string in the Ternary Search Tree"""

        temp = self
        i = 0
        while temp != 0:
            if string[i] < temp.ch:
                temp = temp.left
            elif string[i] > temp.ch:
                temp = temp.right
            else:
                i = i + 1
                if i == len(string):
                    return temp.flag
                temp = temp.center

        return 0

    def search(self, string, match):
        """Function to implement Auto complete search"""

        if len(string) > 0:
            key = string[0]

            if key < self.ch:
                if self.left == 0:
                    print "No Match Found"
                    return
                self.left.search(string, match)

            elif key > self.ch:
                if self.right == 0:
                    print("Not Match Found")
                    return
                self.right.search(string, match)

            else:
                if len(string) == 1:
                    if self.flag == 1:
                        print("Match ", match + self.ch)
                    if self.center != 0:
                        self.center.spdfs(match + self.ch + self.center.ch)
                    return 1
                self.center.search(string[1:], match + key)

        else:
            print("Invalid String")
            return


def fileparse(filename, node):
    """
    Parse the Input Dict file and build the TST
    """

    fd = open(filename)
    line = fd.readline().strip('\r\n')

    while line != '':
        node.Add(line, node)
        line = fd.readline().strip('\r\n')


def read_json(jsonfile='data/sample_conversations.json'):
    """reads the sample conversation and returns a corpus of statements"""

    corpus = []

    with open(jsonfile, 'r') as json_file:
        json_data = json.load(json_file)

        for issue in json_data['Issues']:
            messages = issue['Messages']
            for message in messages:
                corpus.append(message['Text'])

    return corpus


def write_data_corpus(filename, documents):
    """takes all the lines in the documents corpus and writes a text file"""

    with open(filename, 'wb') as f:
        for statement in documents:
            enc_statement = statement.encode('utf-8')
            f.write(enc_statement + '\n')


def num_iters(docs_file):
    """Simply returns the number of texts divided by 1000"""

    with open(docs_file, 'r') as docs:
        num_docs = len(docs.readlines())
        num_iters = num_docs/1000 + 1

    return num_iters


def split_data_corpus(filename):
    """Split the large file of all phrases into smaller chunks of 1000 lines
    each. Creates new files"""

    fid = 1
    with open(filename, 'r') as infile:
        f = open('%s-%s.txt' % (filename.strip('.txt'), fid), 'wb')
        for line, doc in enumerate(infile):
            f.write(doc)
            if not line % 1000 and line > 1:
                f.close()
                fid += 1
                f = open('%s-%s.txt' % (filename.strip('.txt'), fid),
                         'wb')
        f.close()


def write_partial_model(pkl_filename, doc_filename):
    """Writes one pickle file with a partial data model"""

    node = Node('', 0)
    print pkl_filename, doc_filename

    with open(doc_filename, 'r') as docs:
        for statement in docs:
            statement.strip('\r\n')
            node.Add(statement, node)

    pkl.dump(node, pkl_filename)


def write_data_model(doc_filename='data/documents.txt'):
    """data_tree is the ternary search tree.
    Function that dumps the tree into a pickle file"""

    numiters = num_iters(doc_filename) + 1
    print 'number of iterations:', numiters - 1

    pickles = ['data/data_model_%s.pkl' % i for i in range(1, numiters)]
    doc_filename = doc_filename.strip('.txt')
    files = ['%s-%s.txt' % (doc_filename, i) for i in range(1, numiters)]

    with open('data/data_model.pkl', 'wb') as pklfile:
        for i in range(numiters - 1):
            write_partial_model(pklfile, files[i])


def read_data_model(filename='data/data_model.pkl'):
    """Reads the ternary search tree from filename (a pickle file)
    returns the tree"""

    with open(filename, 'r') as pklfile:
        root = pkl.load(pklfile)

    return root


class ListStream:
    """Class used by generate_suggestions, to output the stdout to a list"""

    def __init__(self):
        self.data = []

    def write(self, s):
        self.data.append(s)

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__


def generate_suggestions(search_string):
    """Function to generate a suggestion from a sample string"""

    root = read_data_model('data/data_model.pkl')
    with ListStream() as x:
        root.search(search_string, '')
    print [s.strip('\n') for s in x.data if s != '\n']


if __name__ == '__main__':
    """This is to create the data structure

    Usage:

    python tst.py

    # to generate a suggestion
    from tst import generate_suggestions
    generate_suggestions('h')
    """

    root = Node('', 0)

    if not os.path.exists('data/documents.txt'):
        corpus = read_json()
        write_data_corpus('data/documents.txt', corpus)
        corpus_path = "data/documents.txt"
        fileparse(corpus_path, root)

    split_data_corpus('data/documents.txt')
    write_data_model()

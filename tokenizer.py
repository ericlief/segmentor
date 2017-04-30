
from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer
from nltk.tokenize.treebank import TreebankWordTokenizer
#from nltk.tokenize.stanford import StanfordTokenizer

#import io
import sys

t = TreebankWordTokenizer()
#t = MosesTokenizer()
#t = StanfordTokenizer()
#tokenized_output_file = sys.argv[1]

# with open(sys.argv[1], 'w') as f:
#
#     for sentence in sys.stdin:
#         tokens = t.tokenize(line, return_str=True)
#         f.write(tokens)

#cnt = 0
for sentence in sys.stdin:
   # if cnt >= 1000:
   #    break
    #tokens = t.tokenize(sentence, return_str=True)
    tokens = t.tokenize(sentence)
    sys.stdout.write(' '.join(tokens) + '\n')
    #sys.stdout.write(tokens + '\n') 
    #cnt += 1




# # Return list
# text = "This ain't funny. It's actually hillarious, yet double Ls. | [] < > [ ] & You're gonna shake it off? Don't?"
# expected_tokens = [u'This', u'ain', u'&apos;t', u'funny.', u'It', u'&apos;s', u'actually', u'hillarious', u',', u'yet', u'double', u'Ls.', u'&#124;', u'&#91;', u'&#93;', u'&lt;', u'&gt;', u'&#91;', u'&#93;', u'&amp;', u'You', u'&apos;re', u'gonna', u'shake', u'it', u'off', u'?', u'Don', u'&apos;t', u'?']
# expected_detokens = "This ain't funny. It's actually hillarious, yet double Ls. | [] < > [] & You're gonna shake it off? Don't?"
# tokens = t.tokenize(text)
# tokens == expected_detokens
# detokens = d.detokenize(tokens)
# detokens == expected_detokens
#
# # Return as string
# text = u'This, is a sentence with weird» symbols… appearing everywhere¿'
# expected_tokenized = u'This , is a sentence with weird » symbols … appearing everywhere ¿'
# tokens = t.tokenize(text, return_str=True)
# tokens == expected_detokens
# expected_detokenized = u'This, is a sentence with weird » symbols … appearing everywhere ¿'
# detokens = d.detokenize(tokens)
# detokens == expected_detokens



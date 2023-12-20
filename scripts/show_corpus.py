import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from api.debugging import pretty


for corpus in genaix.list_corpora():
  print(pretty(corpus))

print('------------')

#genaix.delete_corpus(corpus_id="ltsang-google")
#genaix.delete_corpus(corpus_id="ltsang-llama")
#genaix.delete_corpus(corpus_id="ltsang-llama-1")


for corpus in genaix.list_corpora():
  print(pretty(corpus))

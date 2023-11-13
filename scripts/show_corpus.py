import llama_index.vector_stores.google.generativeai.genai_extension as genaix
from api.debugging import pretty


for corpus in genaix.list_corpora():
  print(pretty(corpus))


# genaix.delete_corpus(corpus_id="ltsang-rag-comparision")

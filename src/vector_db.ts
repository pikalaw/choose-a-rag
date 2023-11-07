import {IVSDocument, VectorStorage} from 'vector-storage';
import {openAIApiKey} from './secret.js';

type Metadata = {
  filename: string;
};

const store = new VectorStorage<Metadata>({openAIApiKey});

export async function addDocuments(texts: string[], metadata: Metadata[]) {
  await store.addTexts(texts, metadata);
}

export interface Document {
  text: string;
  score: number;
}

export async function queryDocuments({
  query,
  k = 3,
}: {
  query: string;
  k: number;
}): Promise<Document[]> {
  const result = await store.similaritySearch({query, k});
  return result.similarItems.map(
    item =>
      ({
        text: item.text,
        score: item.score,
      }) satisfies Document
  );
}

export async function deleteDocuments() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const documents: IVSDocument<Metadata>[] = (store as any).documents;
  documents.length = 0;
  await addDocuments([], []);
}

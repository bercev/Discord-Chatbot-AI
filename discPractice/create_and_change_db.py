from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from uuid import uuid4
from dotenv import load_dotenv


# data path
load_dotenv()
CHROMA_PATH = "vector_db"

# main
def main() -> None:
    print("hello")
    dump_db_to_terminal()

# dump to see contents of database
def dump_db_to_terminal() -> None:

    # initializing variables
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=GPT4AllEmbeddings())
    all_messages = db.get().get('documents')
    all_metadatas = db.get().get('metadatas')
    for i in range(len(all_messages)):
        print(all_metadatas[i].get('source') + " said: " + all_messages[i])
        

# adding each message to the db
def add_to_db(texts, metadata, id) -> None:
    # reload the database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=GPT4AllEmbeddings())

    # add message to db in the form of a document
    db.add_documents(
        documents=[Document(
            page_content=texts,
            metadata=metadata,
            id=id
        )],
        ids=[str(uuid4())] # give document a randomly generated uuid
        )


# creating an empty db
def create_empty_db() -> None:
    db = Chroma(collection_name="chroma-vector-db", embedding_function=GPT4AllEmbeddings, persist_directory=CHROMA_PATH)

# calling main()
if __name__=="__main__":
    main()
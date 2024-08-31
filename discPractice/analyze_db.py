import argparse
from langchain_chroma import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import warnings
from langchain.schema import AIMessage
load_dotenv()

# handling paths
CHROMA_PATH = "vector_db"

# Convert warnings to exceptions
warnings.filterwarnings("ignore", category=UserWarning)
# prompt template
PROMPT_TEMPLATE = """
Answer the question based only on the following context which is given in a specific format of [Source] = is the person who sent the message, and [Message] = is the message from the Source

{context}

---

Answer the question based on the above context: {question}
"""

prompt_to_ask_for_context = PromptTemplate(template="""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as releveant.
It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \nGive a binary score 'yes' or 'no' score to indicate whether the document is relevant 
to the question. \n Provide the binary score as a JSON with a single key 'score' and no premable or explanation. 
<|eot_id|><|start_header_id|>user<|end_header_id|>
Here is the retrieved document: \n\n {document} \n\n
Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
""", input_variables=["question", "document"]
)

def dump() -> str:
    # initializing variables
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=GPT4AllEmbeddings())
    all_messages = db.get().get('documents')
    all_metadatas = db.get().get('metadatas')
    dump_str = ""
    for i in range(len(all_messages)):
        dump_str += all_metadatas[i].get('source') + " said: " + all_messages[i] + "\n"
    if len(dump_str) > 1900:
        return "DB too big. Printing what's possible: " + dump_str[0:1900]
    return dump_str
    
def query(msg) -> str:   
    query_text = msg

    # reload the db
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=GPT4AllEmbeddings())
    
    # search the db
    results = db.similarity_search_with_relevance_scores(query=query_text, k=3)

    # formatting context text and response text ahead of time:
    page_contents = []
    for doc, _score in results:
        page_contents.append("Source: " + doc.metadata.get('source') + "\t\tMessage: " + doc.page_content)
    context_text = "\n---\n".join(page_contents)
    response_text = ""
    
    # code shows that query is invalid for provided context/db, if the score is low, then ask the LLM the usability of context to answer the question.
    print(f"\t\t\t\t\t\tSCORE: {results[0][1]}")
    if len(results) == 0 or results[0][1] < 0.5: 
        print(f"\t\t\t\t\t\tUnable to find matching results... Asking LLM if context are usable/viable")
        ans = determine_validity_of_context(query_text, context_text)
        print(f"\t\t\t\t\t\tAnswer from LLM: {ans}")
        if ans.get('score') == 'no':
            return "Unable to get result, context not enough"
      
    # initializing LLM
    llm = ChatOllama(model="llama3", format= "str", temperature=0)

    # creating prompt template and printing
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # getting and returning the response from the LLM with the source
    response_text = llm.invoke(prompt)
    sources = [doc.metadata.get("source", None) for doc, _score in results] # getting sources from db
    if isinstance(response_text, AIMessage):
        response_text = response_text.content
    formatted_response = f"Response: {response_text}\nSources:\n{sources}"
    print(formatted_response)
    return formatted_response

# determines the validity of the documents, which is the input
def determine_validity_of_context(query_text, context_text):
    llm = ChatOllama(model="llama3", format="json", temperature=0) # creating llm
    retrieval_grader = prompt_to_ask_for_context | llm | JsonOutputParser() # invoking llm with prompt template
    ans = retrieval_grader.invoke({"question": query_text, "document": context_text}) # getting answer
    return ans

def main() -> None:
    print("anaylze_db.py")
    query("which color of people does <@771824555923996722>  hate?")

if __name__ == "__main__":
    main()
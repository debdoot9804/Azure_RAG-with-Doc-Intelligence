from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks



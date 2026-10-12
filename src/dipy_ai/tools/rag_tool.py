from pathlib import Path
from dipy_ai.config import GOOGLE_EMBEDDING_API_KEY, GOOGLE_EMBEDDING_MODEL, RAG_DATA_FOLDER, RAG_CHROMA_DB
from dipy_ai.tools import BaseTool
from langchain_community.document_loaders import   PyMuPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from  langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class RAGTool(BaseTool):
    def __init__(self, 
                name: str = "RAG Tool", 
                description: str = "A tool for retrieving information using Retrieval-Augmented Generation."):
        super().__init__(name, description)
        self._embedding = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL, api_key=GOOGLE_EMBEDDING_API_KEY)
        rag_data_folder = Path(RAG_DATA_FOLDER)
        if not any(rag_data_folder.glob("*.pdf")):
            raise FileNotFoundError(f"No PDF files found in RAG data folder: {rag_data_folder}")
        self._vector_store = Chroma(
            collection_name="rag_collection",
            embedding_function=self._embedding,
            persist_directory=RAG_CHROMA_DB,
            collection_metadata={"source": "rag_collection"}
        )
        if not self._vector_store.get(limit=1, include=[])["ids"]:
            self._text_chunks = self.load_pdfs()
            self._vector_store.add_documents(self._text_chunks)
            
    def load_pdfs(self):
        pdf_list = list(Path(RAG_DATA_FOLDER).glob("*.pdf"))
        text_chunks = []
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for i in pdf_list:
            try:
                py_pdf_loader = PyMuPDFLoader(i)
                py_pdf_docs = py_pdf_loader.load()
                text_chunks.extend(text_splitter.split_documents(py_pdf_docs))
            except Exception as e:
                print(f"Error loading PDF file {i}: {e}")
                continue
        return text_chunks
    
    def execute(self, *args, **kwargs):
        query = kwargs.get("query", "")
        if not query:
            return []
        docs = self._vector_store.similarity_search(query=query, k=5)
        return [
            {
                "text": doc.page_content,
            }
            for doc in docs
        ]

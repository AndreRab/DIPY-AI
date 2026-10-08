from pathlib import Path
from dipy_ai.config import RAG_DATA_FOLDER
from dipy_ai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader

class RAGTool(BaseTool):
    def __init__(self, 
                name: str = "RAG Tool", 
                description: str = "A tool for retrieving information using Retrieval-Augmented Generation."):
        super().__init__(name, description)

    def execute(self, *args, **kwargs):
        rag_data_folder = Path(RAG_DATA_FOLDER)
        if not any(rag_data_folder.glob("*.pdf")):
            raise FileNotFoundError(f"No PDF files found in RAG data folder: {rag_data_folder}")
        pdf_list = list(rag_data_folder.glob("*.pdf"))
        for i in pdf_list:
            try:
                py_pdf_loader = PyPDFLoader(i)
                py_pdf_docs = py_pdf_loader.load()
            except Exception as e:
                print(f"Error loading PDF file {i}: {e}")
                continue


from fastapi import APIRouter, UploadFile, File
import tempfile
from document_processor import DocumentProcessor
import os


documentRouter = APIRouter(
    prefix="/documents", tags=["documents"]
)  # Router for documents separate from the chat router

@documentRouter.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process the document
        from document_processor import document_processor
        result = await document_processor.process_document(tmp_file_path, file.filename)        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {"message": result}
        
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

import PyPDF2
import logging

class PDFProcessor:
    """
    Utility class for extracting text content from PDF files.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as string
        """
        try:
            text_content = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            # Clean up the text
            text_content = self._clean_text(text_content)
            
            self.logger.info(f"Successfully extracted {len(text_content)} characters from {pdf_path}")
            return text_content
            
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Remove null characters
        text = text.replace('\uf0b7', '•')  # Replace bullet symbols
        
        return text 
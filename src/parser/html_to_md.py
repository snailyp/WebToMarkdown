import html2text
import re
from src.utils.logger import get_logger


class HTML2Markdown:
    def __init__(self, ignore_links=False, bypass_tables=False):
        self.logger = get_logger(__name__)
        self.converter = html2text.HTML2Text()
        
        # Configure HTML2Text options
        self.converter.ignore_links = ignore_links
        self.converter.bypass_tables = bypass_tables
        self.converter.unicode_snob = True  # Use Unicode characters directly
        self.converter.body_width = 0  # Don't wrap text at a certain width
        self.converter.wrap_links = False  # Don't wrap links
        self.converter.mark_code = True  # Surround code with backticks
        
    def convert(self, html):
        """Convert HTML to Markdown with additional cleanup"""
        try:
            # Basic conversion
            markdown = self.converter.handle(html)
            
            # Clean up extra whitespace
            markdown = self._clean_whitespace(markdown)
            
            # Fix code blocks
            markdown = self._fix_code_blocks(markdown)
            
            # Fix list formatting
            markdown = self._fix_list_formatting(markdown)
            
            return markdown
            
        except Exception as e:
            self.logger.error(f"Error converting HTML to Markdown: {e}")
            # Fallback to basic conversion without enhancements
            return self.converter.handle(html)
            
    def _clean_whitespace(self, markdown):
        """Remove excessive blank lines and trailing whitespace"""
        # Replace multiple blank lines with at most two
        cleaned = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Remove trailing whitespace from each line
        cleaned = '\n'.join(line.rstrip() for line in cleaned.split('\n'))
        
        return cleaned
        
    def _fix_code_blocks(self, markdown):
        """Ensure code blocks are properly formatted"""
        # Convert sequences of 4+ backticks to standard 3 backticks
        fixed = re.sub(r'`{4,}', '```', markdown)
        
        # Ensure code blocks have language identifier or are blank
        lines = fixed.split('\n')
        in_code_block = False
        
        for i in range(len(lines)):
            if lines[i].startswith('```'):
                if not in_code_block and len(lines[i]) == 3:
                    # Opening code block without language
                    lines[i] = '```'
                in_code_block = not in_code_block
                
        return '\n'.join(lines)
        
    def _fix_list_formatting(self, markdown):
        """Ensure lists are properly formatted"""
        # Make sure there's a space after list markers
        fixed = re.sub(r'^(\s*[*+-])(\S)', r'\1 \2', markdown, flags=re.MULTILINE)
        
        # Fix numbered lists
        fixed = re.sub(r'^(\s*\d+\.)(\S)', r'\1 \2', fixed, flags=re.MULTILINE)
        
        return fixed

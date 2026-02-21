import json
import logging

logger = logging.getLogger(__name__)

def parse_notebook(content: str) -> str:
    """
    Parse .ipynb (Jupyter Notebook) cells and convert them into readable text strings.
    """
    try:
        notebook_data = json.loads(content)
        processed_content = []
        
        cells = notebook_data.get('cells', [])
        
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type', 'unknown')
            source = cell.get('source', [])
            
            if isinstance(source, list):
                cell_content = ''.join(source)
            else:
                cell_content = str(source)
            
            if not cell_content.strip():
                continue
            
            header = f"# Cell {i+1} - {cell_type.capitalize()}"
            processed_content.append(f"{header}\n{cell_content}\n{'#' + ('-' * 30)}")
            
        return '\n\n'.join(processed_content)
    
    except json.JSONDecodeError:
        logger.warning("Failed to decode JSON for notebook content.")
        return content
    except Exception as e:
        logger.error(f"Error processing notebook: {e}")
        return content

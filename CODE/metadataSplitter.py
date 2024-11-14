import numpy as np
from typing import Dict, List, Tuple, Optional

class MetadataProcessor:
    def __init__(self, layout_data: Dict):
        """
        Initialize metadata processor with plate layout information.
        
        Args:
            layout_data: Dictionary containing plate layout information including:
                - rows: Number of rows in plate
                - columns: Number of columns in plate
                - strains: Number of strains
                - strain_positions: Dictionary mapping strain index to (start_col, end_col)
        """
        self.rows = layout_data['rows']
        self.columns = layout_data['columns']
        self.num_strains = layout_data['strains']
        self.strain_positions = layout_data['strain_positions']
        
    def create_metadata(self, quantification_array: np.ndarray, 
                       strain_names: List[str],
                       threshold: float = 0,
                       small_area: float = 0,
                       blocksize: int = 11) -> Dict:
        """
        Create metadata dictionary from quantification array and strain information.
        
        Args:
            quantification_array: 2D numpy array containing quantification data
            strain_names: List of strain names in order
            threshold: Threshold value for image processing
            small_area: Minimum area size for contour detection
            blocksize: Block size for adaptive thresholding
            
        Returns:
            Dictionary containing metadata and split quantification data
        """
        if len(strain_names) != self.num_strains:
            raise ValueError(f"Expected {self.num_strains} strain names, got {len(strain_names)}")
            
        metadata = {
            'rows': self.rows,
            'columns': self.columns,
            'num_strains': self.num_strains,
            'threshold': threshold,
            'smallArea': small_area,
            'blocksize': blocksize,
            'IMGcontours': None,
            'IMGbinary': None,
            'IMGgrid': None
        }
        
        # Split quantification array by strain positions and add to metadata
        strain_data = self.split_array_by_strains(quantification_array)
        
        # Add strain names and their corresponding quantification data
        for i, (strain_name, quant_data) in enumerate(zip(strain_names, strain_data)):
            strain_key = f'strain{chr(65 + i)}'  # strainA, strainB, etc.
            quant_key = f'Quantification{chr(65 + i)}'
            metadata[strain_key] = strain_name
            metadata[quant_key] = quant_data
            
        return metadata
        
    def split_array_by_strains(self, array: np.ndarray) -> List[np.ndarray]:
        """
        Split a 2D array into sub-arrays based on strain positions.
        
        Args:
            array: 2D numpy array to split
            
        Returns:
            List of numpy arrays, one for each strain's section
        """
        if array.shape != (self.rows, self.columns):
            raise ValueError(f"Array shape {array.shape} doesn't match expected shape ({self.rows}, {self.columns})")
            
        strain_arrays = []
        for strain_idx in range(self.num_strains):
            start_col, end_col = self.strain_positions[strain_idx]
            strain_array = array[:, start_col:end_col + 1]
            strain_arrays.append(strain_array)
            
        return strain_arrays
    
    def reconstruct_array(self, strain_arrays: List[np.ndarray]) -> np.ndarray:
        """
        Reconstruct full array from strain sub-arrays.
        
        Args:
            strain_arrays: List of numpy arrays for each strain section
            
        Returns:
            Combined 2D numpy array
        """
        return np.hstack(strain_arrays)

    def validate_metadata(self, metadata: Dict) -> bool:
        """
        Validate metadata dictionary has all required fields.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = {
            'rows', 'columns', 'num_strains', 'threshold', 'smallArea', 
            'blocksize', 'IMGcontours', 'IMGbinary', 'IMGgrid'
        }
        
        # Check for strain fields
        for i in range(self.num_strains):
            strain_letter = chr(65 + i)
            required_fields.add(f'strain{strain_letter}')
            required_fields.add(f'Quantification{strain_letter}')
            
        return all(field in metadata for field in required_fields)

# Example usage:
def example_usage():
    # Sample layout data
    layout_data = {
        'rows': 8,
        'columns': 12,
        'strains': 3,
        'strain_positions': {
            0: (0, 3),   # Strain 1 in columns 0-3
            1: (4, 7),   # Strain 2 in columns 4-7
            2: (8, 11)   # Strain 3 in columns 8-11
        }
    }
    
    # Create processor
    processor = MetadataProcessor(layout_data)
    
    # Sample data
    quantification_array = np.random.random((8, 12))
    strain_names = ['Strain_1', 'Strain_2', 'Strain_3']
    
    # Create metadata
    metadata = processor.create_metadata(
        quantification_array=quantification_array,
        strain_names=strain_names,
        threshold=0.5,
        small_area=100,
        blocksize=11
    )
    
    # Validate metadata
    is_valid = processor.validate_metadata(metadata)
    print(f"Metadata is valid: {is_valid}")
    print(metadata)

example_usage()    
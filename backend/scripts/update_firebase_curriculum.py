import sys
import os
import json
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.curriculum_service import CurriculumService

def update_curriculum_data():
    """
    Reads local curriculums.json and updates Firebase Firestore.
    """
    print("Initializing Flask app context...")
    app = create_app()
    
    with app.app_context():
        service = CurriculumService()
        
        # Path to curriculums.json
        # Assuming script is in backend/scripts/
        base_dir = Path(__file__).parent.parent.parent
        json_path = base_dir / 'apps' / 'curriculum-navigator' / 'data' / 'curriculums.json'
        
        print(f"Reading data from: {json_path}")
        
        if not json_path.exists():
            print(f"Error: File not found at {json_path}")
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            print(f"Found {len(data)} curriculums to update.")
            
            for curriculum_id, curriculum_data in data.items():
                print(f"Updating {curriculum_id}...")
                
                # Ensure curriculum_id is set in the data
                curriculum_data['curriculum_id'] = curriculum_id
                
                success = service.create_or_update_curriculum(curriculum_id, curriculum_data)
                
                if success:
                    print(f"Successfully updated {curriculum_id}")
                else:
                    print(f"Failed to update {curriculum_id}")
                    
            print("Update complete.")
            
        except Exception as e:
            print(f"Error updating data: {e}")

if __name__ == '__main__':
    update_curriculum_data()

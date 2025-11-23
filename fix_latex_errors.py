import firebase_admin
from firebase_admin import credentials, firestore
import re

# Initialize Firebase (assuming it's already initialized in the environment or use default)
# Since we are running this as a standalone script in the same env as run_local.py, 
# we need to ensure creds are available. 
# However, run_local.py uses a service account or default creds. 
# We'll try default first, similar to backend/app.py but simpler.

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'my-mvp-backend', # Replace with actual project ID if known, or rely on env
    })

db = firestore.client()

def clean_text(text):
    if not isinstance(text, str):
        return text
    
    # 1. Remove \textit{...} -> ...
    text = re.sub(r'\\textit\{(.*?)\}', r'\1', text)
    
    # 2. Remove \textbf{...} -> ...
    text = re.sub(r'\\textbf\{(.*?)\}', r'\1', text)
    
    # 3. Remove \text{...} -> ...
    text = re.sub(r'\\text\{(.*?)\}', r'\1', text)

    # 4. Fix \% -> % (Simple approach: replace all \% with % in text context)
    # This might break \% inside math if it was intended, but usually % works fine in KaTeX too 
    # or the prompt will fix new ones. For existing text, 25\% is the main issue.
    # We will replace \% with % globally for now as it's the safest for readability.
    text = text.replace('\\%', '%')
    
    return text

def fix_questions():
    print("Starting database cleanup...")
    questions_ref = db.collection('questions')
    docs = questions_ref.stream()
    
    count = 0
    updated_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        needs_update = False
        
        # Check text_latex
        if 'text_latex' in data:
            new_text = clean_text(data['text_latex'])
            if new_text != data['text_latex']:
                data['text_latex'] = new_text
                needs_update = True
                
        # Check explanation
        if 'explanation' in data:
            new_exp = clean_text(data['explanation'])
            if new_exp != data['explanation']:
                data['explanation'] = new_exp
                needs_update = True
                
        # Check choices
        if 'choices' in data and isinstance(data['choices'], list):
            new_choices = []
            choices_changed = False
            for choice in data['choices']:
                if 'text' in choice:
                    new_choice_text = clean_text(choice['text'])
                    if new_choice_text != choice['text']:
                        choice['text'] = new_choice_text
                        choices_changed = True
                new_choices.append(choice)
            
            if choices_changed:
                data['choices'] = new_choices
                needs_update = True
        
        if needs_update:
            print(f"Updating document: {doc_id}")
            questions_ref.document(doc_id).set(data, merge=True)
            updated_count += 1
        
        count += 1
        
    print(f"Cleanup complete. Scanned {count} documents, updated {updated_count} documents.")

if __name__ == "__main__":
    fix_questions()

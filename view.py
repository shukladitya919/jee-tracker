import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tracker.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    title = db.Column(db.String(300))
    theory = db.Column(db.Boolean, default=False)
    revision_count = db.Column(db.Integer, default=0)
    # ... other fields

def check_data():
    with app.app_context():
        try:
            # Count total chapters
            total_chapters = Chapter.query.count()
            print(f"📊 Total chapters in database: {total_chapters}")
            
            # Count chapters with progress
            chapters_with_progress = Chapter.query.filter(
                (Chapter.theory == True) | 
                (Chapter.revision_count > 0)
            ).count()
            print(f"📈 Chapters with progress: {chapters_with_progress}")
            
            # Show some sample data
            print("\n🔍 Sample chapters with progress:")
            active_chapters = Chapter.query.filter(
                (Chapter.theory == True) | 
                (Chapter.revision_count > 0)
            ).limit(5).all()
            
            for ch in active_chapters:
                print(f"  - {ch.subject}: {ch.title} (Theory: {ch.theory}, Revisions: {ch.revision_count})")
                
            if total_chapters == 0:
                print("❌ Database appears to be empty or reset!")
            else:
                print("✅ Database has data and is persisting!")
                
        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == '__main__':
    check_data()

from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Use environment variable for database URL (important for Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tracker.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)  # Physics / Mathematics / Chemistry
    category = db.Column(db.String(50), nullable=False) # Category 1..4
    index_in_list = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    
    # Common actions for all subjects
    theory = db.Column(db.Boolean, default=False)
    revision_count = db.Column(db.Integer, default=0)
    pyqs = db.Column(db.Boolean, default=False)
    module_a = db.Column(db.Boolean, default=False)
    module_b = db.Column(db.Boolean, default=False)
    
    # Physics specific
    physics_galaxy = db.Column(db.Boolean, default=False)
    
    # Mathematics specific
    cengage = db.Column(db.Boolean, default=False)

    def progress_count(self):
        # Common actions for all subjects
        count = sum([
            self.theory,
            self.pyqs,
            self.module_a,
            self.module_b,
            self.revision_count > 0  # At least one revision
        ])
        
        # Subject-specific actions
        if self.subject == "Physics":
            count += sum([self.physics_galaxy])
        elif self.subject == "Mathematics":
            count += sum([self.cengage])
            
        return count
    
    def max_possible_progress(self):
        # Common actions count
        base_max = 5  # theory, pyqs, module_a, module_b, revision_count
        
        # Add subject-specific actions
        if self.subject == "Physics":
            return base_max + 1  # physics_galaxy
        elif self.subject == "Mathematics":
            return base_max + 1  # cengage
        return base_max

# New model for subject-level book completion
class SubjectBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False, unique=True)
    
    # Mathematics books
    pinkbook = db.Column(db.Boolean, default=False)
    yellowbook = db.Column(db.Boolean, default=False)
    play_with_graphs = db.Column(db.Boolean, default=False)
    
    # Chemistry books
    n_awasthi = db.Column(db.Boolean, default=False)
    ms_chauhan = db.Column(db.Boolean, default=False)

# Updated Seed data
SEED = {
  "Physics": [
    ("1", "Ray Optics"),
    ("1", "Electrostatics"),
    ("1", "Current Electricity"),
    ("1", "Magnetic Effects Of Current"),
    ("1", "Modern Physics"),
    ("2", "Thermodynamics"),
    ("2", "Rotational Motion"),
    ("2", "Mechanical Properties of Fluids"),
    ("2", "Semiconductors"),
    ("2", "Capacitance"),
    ("2", "Work Power Energy"),
    ("3", "Wave Optics"),
    ("3", "Electromagnetic Induction"),
    ("3", "Alternating Current"),
    ("3", "Gravitation"),
    ("3", "Kinetic Theory Of Gases"),
    ("3", "Oscillations"),
    ("4", "Center Of Mass And Momentum"),
    ("4", "Waves And Sound"),
    ("4", "Electromagnetic Waves"),
    ("4", "Kinematics"),
    ("4", "Laws Of Motion"),
    ("4", "Units And Dimensions"),
    ("4", "Experimental Physics"),
    ("4", "Calorimetry and Conduction"),
    ("4", "Properties of Solids"),
    ("4", "Heat Transfer"),
    ("4", "Magnetism")
    ],
  "Mathematics": [
    ("1", "Three Dimensional Geometry"),
    ("1", "Sequence And Series"),
    ("1", "Functions"),
    ("1", "Definite Integration"),
    ("1", "Probability"),
    ("2", "Differential Equations"),
    ("2", "Vector Algebra"),
    ("2", "Binomial Theorem"),
    ("2", "Matrices And Determinants"),
    ("2", "Complex Numbers"),
    ("2", "Area Under Curves"),
    ("2", "Straight Line"),
    ("3", "Parabola"),
    ("3", "Sets And Relations"),
    ("3", "Permutation And Combination"),
    ("3", "Circle"),
    ("3", "Quadratic Equations"),
    ("3", "Limits"),
    ("4", "Ellipse"),
    ("4", "Continuity And Differentiability"),
    ("4", "Hyperbola"),
    ("4", "Application Of Derivatives"),
    ("4", "Statistics"),
    ("4", "Inverse Trigonometric Functions"),
    ("4", "Indefinite Integration"),
    ("4", "Trigonometry"),
    ("4", "Differentiation")
  ],
  "Chemistry": [
    ("1", "Coordination Compounds"),
    ("1", "General Organic Chemistry"),
    ("1", "Chemical Bonding"),
    ("1", "D and F Block Elements"),
    ("1", "Chemical Thermodynamics"),
    ("1", "Electrochemistry"),
    ("2", "Hydrocarbons"),
    ("2", "Chemical Kinetics"),
    ("2", "Some Basic Principles of Organic Chemistry"),
    ("2", "Aldehyde, Ketones and Carboxylic Acids"),
    ("2", "Solutions"),
    ("2", "Biomolecules"),
    ("2", "Amines"),
    ("3", "Atomic Structure"),
    ("3", "P Block Elements"),
    ("3", "Halogen Containing Compounds"),
    ("3", "Chemical Equilibrium"),
    ("3", "Mole Concept"),
    ("4", "Periodicity"),
    ("4", "Alcohols Phenols And Ethers"),
    ("4", "Ionic Equilibrium"),
    ("4", "Redox Reactions"),
    ("4", "Purification and Characterisation of Organic Compounds"),
    ("4", "Qualitative Inorganic Chemistry")
    ]
}

def init_db():
    with app.app_context():
        db.create_all()
        # seed chapters
        for subject, items in SEED.items():
            for idx, (cat, title) in enumerate(items, start=1):
                # Check if chapter already exists to avoid duplicates
                existing = Chapter.query.filter_by(subject=subject, title=title).first()
                if not existing:
                    ch = Chapter(subject=subject, category=cat, index_in_list=idx, title=title)
                    db.session.add(ch)
        
        # Initialize subject books
        for subject in ["Physics", "Mathematics", "Chemistry"]:
            if not SubjectBooks.query.filter_by(subject=subject).first():
                subject_book = SubjectBooks(subject=subject)
                db.session.add(subject_book)
        
        db.session.commit()

# Initialize database before first request
@app.before_request
def before_first():
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

# Utility: get subject stats
def subject_stats(subject):
    chapters = Chapter.query.filter_by(subject=subject).order_by(Chapter.category, Chapter.index_in_list).all()
    total = len(chapters)
    if total == 0:
        return {"total":0, "completed":0, "percent":0}
    
    # Calculate progress percentage based on actual completion of all criteria
    max_marks_possible = sum(c.max_possible_progress() for c in chapters)
    marked = sum(c.progress_count() for c in chapters)
    percent = round((marked/max_marks_possible)*100) if max_marks_possible > 0 else 0
    
    # Get subject books
    subject_books = SubjectBooks.query.filter_by(subject=subject).first()
    
    return {
        "total": total, 
        "percent": percent, 
        "chapters": chapters,
        "marked": marked,
        "max_possible": max_marks_possible,
        "subject_books": subject_books
    }

@app.route('/')
def index():
    subjects = ["Physics", "Mathematics", "Chemistry"]
    stats = {s: subject_stats(s) for s in subjects}
    return render_template('index.html', stats=stats)

@app.route('/subject/<name>')
def subject_view(name):
    chapters = Chapter.query.filter_by(subject=name).order_by(Chapter.category, Chapter.index_in_list).all()
    # group by category
    categories = {}
    for c in chapters:
        categories.setdefault(c.category, []).append(c)
    # category progress
    cat_progress = {}
    for cat, chs in categories.items():
        max_marks = sum(c.max_possible_progress() for c in chs)
        marked = sum(c.progress_count() for c in chs)
        percent = round((marked/max_marks)*100) if max_marks > 0 else 0
        cat_progress[cat] = percent
    subj = subject_stats(name)
    return render_template('subject.html', subject=name, categories=categories, cat_progress=cat_progress, subj=subj)

@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.json
    ch_id = data.get('id')
    field = data.get('field')
    action = data.get('action', 'toggle')  # 'increment', 'decrement', or 'toggle'
    
    if ch_id:  # Chapter-specific toggle
        ch = Chapter.query.get(ch_id)
        if not ch:
            return jsonify({"ok":False}), 404
        
        # Handle different field types
        if field == 'revision_count':
            if action == 'increment':
                setattr(ch, field, ch.revision_count + 1)
            elif action == 'decrement' and ch.revision_count > 0:
                setattr(ch, field, ch.revision_count - 1)
            db.session.commit()
        elif field in ['theory', 'pyqs', 'module_a', 'module_b', 'physics_galaxy', 'cengage']:
            # Toggle boolean fields
            current = getattr(ch, field)
            setattr(ch, field, not current)
            db.session.commit()
        else:
            return jsonify({"ok":False}), 400
        
        # return updated percentages for subject and category
        subj = ch.subject
        subj_stats = subject_stats(subj)
        # category percent
        cat_chs = Chapter.query.filter_by(subject=subj, category=ch.category).all()
        max_marks = sum(c.max_possible_progress() for c in cat_chs)
        marked = sum(c.progress_count() for c in cat_chs)
        cat_percent = round((marked/max_marks)*100) if max_marks > 0 else 0
        
        return jsonify({
            "ok": True,
            "subject_percent": subj_stats['percent'],
            "category_percent": cat_percent,
            "chapter_progress": ch.progress_count(),
            "chapter_max": ch.max_possible_progress(),
            "revision_count": ch.revision_count
        })
    
    else:  # Subject-level book toggle
        subject = data.get('subject')
        field = data.get('field')
        subject_book = SubjectBooks.query.filter_by(subject=subject).first()
        if not subject_book:
            return jsonify({"ok":False}), 404
        
        if field in ['pinkbook', 'yellowbook', 'play_with_graphs', 'n_awasthi', 'ms_chauhan']:
            current = getattr(subject_book, field)
            setattr(subject_book, field, not current)
            db.session.commit()
            return jsonify({"ok": True})
        else:
            return jsonify({"ok":False}), 400

with app.app_context():
    init_db()

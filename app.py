from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# -----------------------
# Database configuration for Render persistence
# -----------------------
# Use /tmp directory which persists between deployments on Render
DB_PATH = '/tmp/tracker.db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------
# Models (keep your existing models)
# -----------------------
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    index_in_list = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    
    theory = db.Column(db.Boolean, default=False)
    revision_count = db.Column(db.Integer, default=0)
    pyqs = db.Column(db.Boolean, default=False)
    module_a = db.Column(db.Boolean, default=False)
    module_b = db.Column(db.Boolean, default=False)
    physics_galaxy = db.Column(db.Boolean, default=False)
    cengage = db.Column(db.Boolean, default=False)

    def progress_count(self):
        count = sum([
            self.theory,
            self.pyqs,
            self.module_a,
            self.module_b,
            self.revision_count > 0
        ])
        if self.subject == "Physics":
            count += self.physics_galaxy
        elif self.subject == "Mathematics":
            count += self.cengage
        return count

    def max_possible_progress(self):
        base = 5
        if self.subject in ["Physics", "Mathematics"]:
            return base + 1
        return base

class SubjectBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False, unique=True)
    pinkbook = db.Column(db.Boolean, default=False)
    yellowbook = db.Column(db.Boolean, default=False)
    play_with_graphs = db.Column(db.Boolean, default=False)
    n_awasthi = db.Column(db.Boolean, default=False)
    ms_chauhan = db.Column(db.Boolean, default=False)

# -----------------------
# Seed data (your existing seed data)
# -----------------------
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
        ("4","Trigonometry"), 
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

# -----------------------
# Initialize DB - Only seed if database is empty
# -----------------------
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if database is already populated
        existing_chapters = Chapter.query.first()
        if not existing_chapters:
            # Seed only if database is empty
            print("Seeding database for the first time...")
            for subject, items in SEED.items():
                for idx, (cat, title) in enumerate(items, start=1):
                    if not Chapter.query.filter_by(subject=subject, title=title).first():
                        db.session.add(Chapter(subject=subject, category=cat, index_in_list=idx, title=title))
                if not SubjectBooks.query.filter_by(subject=subject).first():
                    db.session.add(SubjectBooks(subject=subject))
            db.session.commit()
            print("Database seeded successfully!")
        else:
            print("Database already exists, skipping seed.")

# -----------------------
# Routes (your existing routes)
# -----------------------
@app.route('/')
def index():
    subjects = ["Physics", "Mathematics", "Chemistry"]
    stats = {}
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject=subject).all()
        total = len(chapters)
        if total == 0:
            stats[subject] = {"total": 0, "percent": 0}
        else:
            max_marks = sum(c.max_possible_progress() for c in chapters)
            marked = sum(c.progress_count() for c in chapters)
            percent = round((marked/max_marks)*100) if max_marks > 0 else 0
            stats[subject] = {"total": total, "percent": percent}
    return render_template('index.html', stats=stats)

@app.route('/subject/<name>')
def subject_view(name):
    chapters = Chapter.query.filter_by(subject=name).order_by(Chapter.category, Chapter.index_in_list).all()
    categories = {}
    for c in chapters:
        categories.setdefault(c.category, []).append(c)
    
    # Calculate category progress
    cat_progress = {}
    for cat, chs in categories.items():
        max_marks = sum(c.max_possible_progress() for c in chs)
        marked = sum(c.progress_count() for c in chs)
        percent = round((marked/max_marks)*100) if max_marks > 0 else 0
        cat_progress[cat] = percent
    
    # Calculate subject progress
    total_chapters = len(chapters)
    if total_chapters == 0:
        subj_progress = 0
    else:
        max_marks = sum(c.max_possible_progress() for c in chapters)
        marked = sum(c.progress_count() for c in chapters)
        subj_progress = round((marked/max_marks)*100) if max_marks > 0 else 0
    
    subject_books = SubjectBooks.query.filter_by(subject=name).first()
    
    return render_template('subject.html', 
                         subject=name, 
                         categories=categories, 
                         cat_progress=cat_progress,
                         subj={"total": total_chapters, "percent": subj_progress},
                         subject_books=subject_books)

@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.json
    ch_id = data.get('id')
    field = data.get('field')
    action = data.get('action', 'toggle')

    if ch_id:
        ch = Chapter.query.get(ch_id)
        if not ch:
            return jsonify({"ok": False}), 404
        
        if field == 'revision_count':
            if action == 'increment':
                ch.revision_count += 1
            elif action == 'decrement' and ch.revision_count > 0:
                ch.revision_count -= 1
        elif field in ['theory', 'pyqs', 'module_a', 'module_b', 'physics_galaxy', 'cengage']:
            setattr(ch, field, not getattr(ch, field))
        
        db.session.commit()
        
        # Calculate updated progress
        chapter_progress = ch.progress_count()
        chapter_max = ch.max_possible_progress()
        
        # Calculate category progress
        category_chapters = Chapter.query.filter_by(subject=ch.subject, category=ch.category).all()
        total_progress = sum(c.progress_count() for c in category_chapters)
        total_max = sum(c.max_possible_progress() for c in category_chapters)
        category_percent = round((total_progress/total_max)*100) if total_max > 0 else 0
        
        # Calculate subject progress
        subject_chapters = Chapter.query.filter_by(subject=ch.subject).all()
        subject_total_progress = sum(c.progress_count() for c in subject_chapters)
        subject_total_max = sum(c.max_possible_progress() for c in subject_chapters)
        subject_percent = round((subject_total_progress/subject_total_max)*100) if subject_total_max > 0 else 0
        
        return jsonify({
            "ok": True,
            "subject_percent": subject_percent,
            "category_percent": category_percent,
            "chapter_progress": chapter_progress,
            "chapter_max": chapter_max,
            "revision_count": ch.revision_count
        })
    
    else:  # Subject-level book toggle
        subject = data.get('subject')
        field = data.get('field')
        subject_book = SubjectBooks.query.filter_by(subject=subject).first()
        if not subject_book:
            return jsonify({"ok": False}), 404
        
        if field in ['pinkbook', 'yellowbook', 'play_with_graphs', 'n_awasthi', 'ms_chauhan']:
            current = getattr(subject_book, field)
            setattr(subject_book, field, not current)
            db.session.commit()
            return jsonify({"ok": True})
        else:
            return jsonify({"ok": False}), 400

# Initialize database when app starts
init_db()

# Remove the app.run() for Render deployment
if __name__ == '__main__':
    app.run(debug=True)of Fluids"),
        ("2", "Semiconductors"), ("2", "Capacitance"), ("2", "Work Power Energy"),
        ("3", "Wave Optics"), ("3", "Electromagnetic Induction"), ("3", "Alternating Current"),
        ("3", "Gravitation"), ("3", "Kinetic Theory Of Gases"), ("3", "Oscillations"),
        ("4", "Center Of Mass And Momentum"), ("4", "Waves And Sound"), ("4", "Electromagnetic Waves"),
        ("4", "Kinematics"), ("4", "Laws Of Motion"), ("4", "Units And Dimensions"),
        ("4", "Experimental Physics"), ("4", "Calorimetry and Conduction"),
        ("4", "Properties of Solids"), ("4", "Heat Transfer"), ("4", "Magnetism")
    ],
    "Mathematics": [
        ("1", "Three Dimensional Geometry"), ("1", "Sequence And Series"), ("1", "Functions"),
        ("1", "Definite Integration"), ("1", "Probability"),
        ("2", "Differential Equations"), ("2", "Vector Algebra"), ("2", "Binomial Theorem"),
        ("2", "Matrices And Determinants"), ("2", "Complex Numbers"), ("2", "Area Under Curves"),
        ("2", "Straight Line"),
        ("3", "Parabola"), ("3", "Sets And Relations"), ("3", "Permutation And Combination"),
        ("3", "Circle"), ("3", "Quadratic Equations"), ("3", "Limits"),
        ("4", "Ellipse"), ("4", "Continuity And Differentiability"), ("4", "Hyperbola"),
        ("4", "Application Of Derivatives"), ("4", "Statistics"), ("4", "Inverse Trigonometric Functions"),
        ("4", "Indefinite Integration"), ("4", "Trigonometry"), ("4", "Differentiation")
    ],
    "Chemistry": [
        ("1", "Coordination Compounds"), ("1", "General Organic Chemistry"), ("1", "Chemical Bonding"),
        ("1", "D and F Block Elements"), ("1", "Chemical Thermodynamics"), ("1", "Electrochemistry"),
        ("2", "Hydrocarbons"), ("2", "Chemical Kinetics"), ("2", "Some Basic Principles of Organic Chemistry"),
        ("2", "Aldehyde, Ketones and Carboxylic Acids"), ("2", "Solutions"), ("2", "Biomolecules"),
        ("2", "Amines"),
        ("3", "Atomic Structure"), ("3", "P Block Elements"), ("3", "Halogen Containing Compounds"),
        ("3", "Chemical Equilibrium"), ("3", "Mole Concept"),
        ("4", "Periodicity"), ("4", "Alcohols Phenols And Ethers"), ("4", "Ionic Equilibrium"),
        ("4", "Redox Reactions"), ("4", "Purification and Characterisation of Organic Compounds"),
        ("4", "Qualitative Inorganic Chemistry")
    ]
}

# -----------------------
# Initialize DB and seed
# -----------------------
def init_db():
    db.create_all()
    for subject, items in SEED.items():
        for idx, (cat, title) in enumerate(items, start=1):
            if not Chapter.query.filter_by(subject=subject, title=title).first():
                db.session.add(Chapter(subject=subject, category=cat, index_in_list=idx, title=title))
        if not SubjectBooks.query.filter_by(subject=subject).first():
            db.session.add(SubjectBooks(subject=subject))
    db.session.commit()

with app.app_context():
    init_db()

# -----------------------
# Routes
# -----------------------
@app.route('/')
def index():
    subjects = ["Physics", "Mathematics", "Chemistry"]
    stats = {s: len(Chapter.query.filter_by(subject=s).all()) for s in subjects}
    return render_template('index.html', stats=stats)

@app.route('/subject/<name>')
def subject_view(name):
    chapters = Chapter.query.filter_by(subject=name).order_by(Chapter.category, Chapter.index_in_list).all()
    categories = {}
    for c in chapters:
        categories.setdefault(c.category, []).append(c)
    return render_template('subject.html', subject=name, categories=categories)

@app.route('/toggle', methods=['POST'])
def toggle():
    data = request.json
    ch_id = data.get('id')
    field = data.get('field')
    action = data.get('action', 'toggle')

    if ch_id:
        ch = Chapter.query.get(ch_id)
        if not ch: return jsonify({"ok": False}), 404
        if field == 'revision_count':
            if action == 'increment': ch.revision_count += 1
            elif action == 'decrement' and ch.revision_count > 0: ch.revision_count -= 1
        elif field in ['theory','pyqs','module_a','module_b','physics_galaxy','cengage']:
            setattr(ch, field, not getattr(ch, field))
        db.session.commit()
        return jsonify({"ok": True, "progress": ch.progress_count()})
    else:
        subject = data.get('subject')
        subject_book = SubjectBooks.query.filter_by(subject=subject).first()
        if not subject_book: return jsonify({"ok": False}), 404
        if field in ['pinkbook','yellowbook','play_with_graphs','n_awasthi','ms_chauhan']:
            setattr(subject_book, field, not getattr(subject_book, field))
            db.session.commit()
            return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

# -----------------------
# Run App
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)
['percent'],
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

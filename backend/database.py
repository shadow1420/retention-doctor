import os
import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./retention_doctor.db")
# Fix Heroku/Render/Supabase legacy postgres:// URI scheme for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine with connection pooling for PostgreSQL and thread safety for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine_kwargs = {"connect_args": connect_args}
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    plan = Column(String(32), default="pro")  # 100% Free Creator Pro for Public Launch
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(255), default="Untitled Video")
    original_filename = Column(String(255), nullable=False)
    original_filepath = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    duration = Column(Float, default=0.0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    aspect_ratio = Column(String(16), default="16:9")  # "9:16", "16:9", "1:1", etc.
    fps = Column(Float, default=30.0)
    status = Column(String(32), default="uploaded")  # uploaded, analyzing, analyzed, fixing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="projects")
    analysis = relationship("Analysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    jobs = relationship("EditingJob", back_populates="project", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="project", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), unique=True, nullable=False)
    
    # Hook Evaluation
    hook_score = Column(Integer, default=0)  # 0 to 100
    hook_grade = Column(String(4), default="C")  # A, B, C, D
    hook_explanation = Column(Text, default="")
    hook_issues = Column(JSON, default=list)  # list of strings
    hook_recommendations = Column(JSON, default=list)  # list of strings
    alternative_hooks = Column(JSON, default=list)  # 5 generated hook ideas

    # Speech and Transcript
    transcript_text = Column(Text, default="")
    word_timestamps = Column(JSON, default=list)  # [{"word": "Hi", "start": 0.1, "end": 0.3}, ...]
    sentence_segments = Column(JSON, default=list)  # [{"text": "...", "start": 0.1, "end": 2.5}, ...]
    words_per_minute = Column(Float, default=0.0)
    filler_words = Column(JSON, default=list)  # [{"word": "um", "start": 1.2, "end": 1.5}, ...]

    # Dead-Air and Silence
    silence_intervals = Column(JSON, default=list)  # [{"start": 2.1, "end": 3.4, "duration": 1.3, "confidence": 0.95}]
    total_silence_duration = Column(Float, default=0.0)
    silence_percentage = Column(Float, default=0.0)

    # Visual Analysis
    scene_cuts = Column(JSON, default=list)  # [timestamp_1, timestamp_2, ...]
    static_scenes = Column(JSON, default=list)  # [{"start": 5.0, "end": 12.0, "duration": 7.0}]
    visual_dynamics_data = Column(JSON, default=dict)  # velocity score, ASL, boredom windows, B-roll prompts

    # Vocal Dynamics & Pitch/Energy
    vocal_data = Column(JSON, default=dict)  # vocal_energy_score, monotone_segments, emphasis_peaks

    # Social Media Safe Zone Framing
    safe_zone_data = Column(JSON, default=dict)  # safe_zone_score, framing_status, violations

    # Second-by-Second Predicted Retention Risk Curve
    retention_curve_data = Column(JSON, default=dict)  # curve, completion_rate, top_dropoffs
    
    # Combined Retention Risk Timeline
    retention_timeline = Column(JSON, default=list)
    # [{"timestamp": 0.0, "type": "weak_hook"|"silence"|"static_scene"|"filler"|"pace_drop", "severity": "high"|"med"|"low", "title": "...", "description": "..."}]

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="analysis")


class EditingJob(Base):
    __tablename__ = "editing_jobs"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    status = Column(String(32), default="queued")  # queued, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100%
    config = Column(JSON, default=dict)
    # { "remove_silence": True, "silence_threshold_sec": 0.6, "speech_padding_sec": 0.08,
    #   "dynamic_zoom": "medium", "audio_normalize": True, "burn_subtitles": True, "subtitle_style": "kinetic" }
    
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="jobs")
    export = relationship("Export", back_populates="job", uselist=False)


class Export(Base):
    __tablename__ = "exports"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False)
    job_id = Column(String(64), ForeignKey("editing_jobs.id"), nullable=False)
    output_filename = Column(String(255), nullable=False)
    output_filepath = Column(String(512), nullable=False)
    output_duration = Column(Float, default=0.0)
    file_size_bytes = Column(Integer, default=0)
    seconds_saved = Column(Float, default=0.0)
    silence_cut_seconds = Column(Float, default=0.0)
    cuts_count = Column(Integer, default=0)
    resolution = Column(String(32), default="1080p")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="exports")
    job = relationship("EditingJob", back_populates="export")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

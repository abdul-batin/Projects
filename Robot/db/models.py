"""SQLAlchemy ORM models for the robot planner database."""
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid


def generate_uuid():
    """Generate UUID string for primary keys."""
    return str(uuid.uuid4())


class Wall(Base):
    """Wall entity representing the area to be covered."""
    __tablename__ = "walls"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    geometry = Column(JSON, nullable=False)  # Store as [[x,y], [x,y], ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    obstacles = relationship("Obstacle", back_populates="wall", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="wall", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Wall(id={self.id}, name={self.name})>"


class Obstacle(Base):
    """Obstacle entity representing obstacles within a wall."""
    __tablename__ = "obstacles"

    id = Column(String, primary_key=True, default=generate_uuid)
    wall_id = Column(String, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # e.g., "window", "door", "furniture"
    geometry = Column(JSON, nullable=False)  # Store as [[x,y], [x,y], ...]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    wall = relationship("Wall", back_populates="obstacles")

    def __repr__(self):
        return f"<Obstacle(id={self.id}, type={self.type}, wall_id={self.wall_id})>"


class Plan(Base):
    """Plan entity representing a planning operation on a wall."""
    __tablename__ = "plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    wall_id = Column(String, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False)
    resolution = Column(Float, nullable=False)
    best_path_id = Column(String, nullable=True)  # Reference to best path
    status = Column(String, default="PENDING")  # PENDING, COMPLETED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    wall = relationship("Wall", back_populates="plans")
    paths = relationship("Path", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plan(id={self.id}, wall_id={self.wall_id}, status={self.status})>"


class Path(Base):
    """Path entity representing a candidate path from planning."""
    __tablename__ = "paths"

    id = Column(String, primary_key=True, default=generate_uuid)
    plan_id = Column(String, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    strategy = Column(String, nullable=False)  # "horizontal", "vertical", etc.
    path_data = Column(JSON, nullable=False)  # Store full path as list of coordinates
    coverage = Column(Float, nullable=False)
    path_length = Column(Integer, nullable=False)
    execution_status = Column(String, default="NOT_STARTED")  # NOT_STARTED, RUNNING, COMPLETED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plan = relationship("Plan", back_populates="paths")
    executions = relationship("Execution", back_populates="path", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Path(id={self.id}, strategy={self.strategy}, coverage={self.coverage})>"


class Execution(Base):
    """Execution entity representing the execution of a path."""
    __tablename__ = "executions"

    id = Column(String, primary_key=True, default=generate_uuid)
    path_id = Column(String, ForeignKey("paths.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="SENT")  # SENT, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Float, default=0.0)  # Percentage of path completed
    error_message = Column(Text, nullable=True)

    # Relationships
    path = relationship("Path", back_populates="executions")

    def __repr__(self):
        return f"<Execution(id={self.id}, path_id={self.path_id}, status={self.status})>"


class Grid(Base):
    """Grid entity for caching computed grids."""
    __tablename__ = "grids"

    id = Column(String, primary_key=True, default=generate_uuid)
    wall_id = Column(String, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False)
    resolution = Column(Float, nullable=False)
    grid_data = Column(JSON, nullable=False)  # Serialized numpy array
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Grid(id={self.id}, wall_id={self.wall_id}, resolution={self.resolution})>"

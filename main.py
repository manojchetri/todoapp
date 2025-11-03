from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class ToDo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

class ToDoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


class ToDoResponse(ToDoCreate):
    id: int

    class Config:
        orm_mode = True

app = FastAPI(title="Simple To-Do API")


@app.post("/tasks/", response_model=ToDoResponse)
def create_task(todo: ToDoCreate):
    db = SessionLocal()
    db_todo = ToDo(title=todo.title, description=todo.description, completed=todo.completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    db.close()
    return db_todo

@app.get("/tasks/", response_model=list[ToDoResponse])
def get_tasks():
    db = SessionLocal()
    todos = db.query(ToDo).all()
    db.close()
    return todos





@app.get("/tasks/{task_id}", response_model=ToDoResponse)
def get_task(task_id: int):
    db = SessionLocal()
    todo = db.query(ToDo).filter(ToDo.id == task_id).first()
    db.close()
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    return todo


@app.put("/tasks/{task_id}", response_model=ToDoResponse)
def update_task(task_id: int, todo: ToDoCreate):
    db = SessionLocal()
    db_todo = db.query(ToDo).filter(ToDo.id == task_id).first()
    if not db_todo:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    db.close()
    return db_todo


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    db_todo = db.query(ToDo).filter(ToDo.id == task_id).first()
    if not db_todo:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_todo)
    db.commit()
    db.close()
    return {"message": "Task deleted successfully"}

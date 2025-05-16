from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models import File as FileModel, User
from backend.app.api.auth import get_current_user
from backend.app.core.database import get_db
import os
from uuid import uuid4
from typing import List

router = APIRouter()

UPLOAD_DIR = 'uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post('/upload', status_code=201)
def upload_file(
    uploads: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    uploaded_files = []
    for upload in uploads:
        ext = os.path.splitext(upload.filename)[1]
        unique_name = f"{uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, 'wb') as f:
            f.write(upload.file.read())
        db_file = FileModel(
            filename=upload.filename,
            content_type=upload.content_type,
            user_id=current_user.id,
            path=file_path
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        uploaded_files.append({"id": db_file.id, "filename": db_file.filename, "upload_time": db_file.upload_time})
    return {"uploaded": uploaded_files}

@router.get('/list', status_code=200)
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).order_by(FileModel.upload_time.desc()).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "content_type": f.content_type,
            "upload_time": f.upload_time,
            "path": f.path
        }
        for f in files
    ] 
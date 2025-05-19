from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models import File as FileModel, User
from backend.app.api.auth import get_current_user
from backend.app.core.database import get_db
import os
from uuid import uuid4
from typing import List
from backend.app.services.conversion_service import FileConversionService
from fastapi.responses import FileResponse

router = APIRouter()

UPLOAD_DIR = 'uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

@router.post('/upload', status_code=201)
def upload_file(
    uploads: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    uploaded_files = []
    image_paths = []
    image_db_objs = []
    # First, save all files and collect image paths if batch
    for upload in uploads:
        ext = os.path.splitext(upload.filename)[1].lower()
        unique_name = f"{uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(file_path, 'wb') as f:
            f.write(upload.file.read())
        db_file = FileModel(
            filename=upload.filename,
            content_type=upload.content_type,
            user_id=current_user.id,
            path=file_path,
            conversion_status="pending"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        if ext in IMAGE_EXTS:
            image_paths.append(file_path)
            image_db_objs.append(db_file)
        else:
            # Convert non-image files immediately
            if ext in ['.pdf', '.txt', '.doc', '.docx']:
                try:
                    pptx_path = FileConversionService.convert_to_pptx(file_path, ext, UPLOAD_DIR)
                    db_file.converted_pptx_path = pptx_path
                    db_file.conversion_status = "success"
                except Exception as e:
                    db_file.conversion_status = f"failed: {e}"
            else:
                db_file.conversion_status = "not_applicable"
            db.commit()
        uploaded_files.append({"id": db_file.id, "filename": db_file.filename, "upload_time": db_file.upload_time, "conversion_status": db_file.conversion_status})
    # If there are images, convert all to one PPTX
    if image_paths:
        try:
            pptx_name = f"images_{uuid4().hex}.pptx"
            pptx_path = os.path.join(UPLOAD_DIR, pptx_name)
            FileConversionService.images_to_pptx(image_paths, pptx_path)
            # Update all image db objects with the same pptx path
            for db_file in image_db_objs:
                db_file.converted_pptx_path = pptx_path
                db_file.conversion_status = "success"
                db.commit()
        except Exception as e:
            for db_file in image_db_objs:
                db_file.conversion_status = f"failed: {e}"
                db.commit()
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
            "path": f.path,
            "converted_pptx_path": f.converted_pptx_path,
            "conversion_status": f.conversion_status
        }
        for f in files
    ]

@router.get('/download/{file_id}', status_code=200)
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.user_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=db_file.path,
        filename=db_file.filename,
        media_type=db_file.content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{db_file.filename}\""}
    )

@router.get('/download-pptx/{file_id}', status_code=200)
def download_converted_pptx(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.user_id == current_user.id).first()
    if not db_file or not db_file.converted_pptx_path:
        raise HTTPException(status_code=404, detail="Converted PPTX not found")
    pptx_filename = db_file.filename
    if not pptx_filename.lower().endswith('.pptx'):
        pptx_filename = pptx_filename.rsplit('.', 1)[0] + '.pptx'
    return FileResponse(
        path=db_file.converted_pptx_path,
        filename=pptx_filename,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        headers={"Content-Disposition": f"attachment; filename=\"{pptx_filename}\""}
    ) 
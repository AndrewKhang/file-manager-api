from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
import shutil
import os
from fastapi.responses import FileResponse
router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified !")
    db_file = models.File(
    filename=file.filename,
    file_path=f"uploads/{file.filename}",
    file_size=file.size,
    owner_id=current_user.id
)
    with open(f"uploads/{file.filename}", "wb") as f:  
        shutil.copyfileobj(file.file, f)  # stream file content to disk
    db.add(db_file)
    db.commit()
    db.refresh(db_file)  # sync db-generated fields (id, created_at) back to the object
    return {"id": db_file.id, "filename": db_file.filename, "file_size": db_file.file_size}

@router.get("/")
def get_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(models.File).all()
    return db.query(models.File).filter(models.File.owner_id == current_user.id).all()

@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
      raise HTTPException(status_code=404, detail="File not found !")
    if current_user.id != db_file.owner_id and current_user.role != "admin":
       raise HTTPException(status_code=403, detail="Permission denied !")
    if os.path.exists(db_file.file_path):  # skip if already deleted from disk
        os.remove(db_file.file_path)
    db.delete(db_file)
    db.commit()
    return {"message":"File deleted successfully!"}

@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): 
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
      raise HTTPException(status_code=404, detail="File not found !")
    if current_user.id != db_file.owner_id and current_user.role != "admin":
       raise HTTPException(status_code=403, detail="Permission denied !")
    return FileResponse(
    path=db_file.file_path,
    filename=db_file.filename,
    content_disposition_type="attachment"
)

@router.get("/{file_id}/preview")
def preview_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)): 
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
      raise HTTPException(status_code=404, detail="File not found !")
    if current_user.id != db_file.owner_id and current_user.role != "admin":
       raise HTTPException(status_code=403, detail="Permission denied !")
    return FileResponse(
    path=db_file.file_path,
    filename=db_file.filename,
    content_disposition_type="inline"
)
     
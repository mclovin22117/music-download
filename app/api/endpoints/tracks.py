"""
Track download endpoints.
"""
from fastapi import APIRouter, HTTPException
from app.models import TrackDownloadRequest, TaskResponse, TaskStatus, TaskStatusResponse
from app.workers.tasks import download_track_task

router = APIRouter()


@router.post("/download", response_model=TaskResponse)
async def download_track(request: TrackDownloadRequest):
    """
    Submit a track download task.
    
    Args:
        request: Track download request with Spotify or YouTube URL
    
    Returns:
        Task ID and status
    """
    try:
        # Enqueue the task
        task = download_track_task.delay(request.url)
        
        return TaskResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            message="Track download task has been queued"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a download task.
    
    Args:
        task_id: The task ID returned from the download endpoint
    
    Returns:
        Task status and result
    """
    from app.workers.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        status = TaskStatus.PENDING
    elif task.state == "STARTED":
        status = TaskStatus.PROCESSING
    elif task.state == "SUCCESS":
        status = TaskStatus.COMPLETED
    elif task.state == "FAILURE":
        status = TaskStatus.FAILED
    else:
        status = TaskStatus.PROCESSING
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        result=task.result if task.state == "SUCCESS" else None,
        error=str(task.info) if task.state == "FAILURE" else None
    )

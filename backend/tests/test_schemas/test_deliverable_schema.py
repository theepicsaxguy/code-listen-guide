"""Tests for deliverable schema validation."""

import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError

from backend.api.schemas.deliverable import (
    DeliverableType,
    DeliverableResponse,
    DeliverableListResponse,
)


class TestDeliverableType:
    """Tests for DeliverableType enum."""

    def test_deliverable_type_enum_values(self):
        """Test all deliverable type enum values."""
        assert DeliverableType.FULL_AUDIOBOOK == "full_audiobook"
        assert DeliverableType.CHAPTER_AUDIO == "chapter_audio"
        assert DeliverableType.SCRIPT_TEXT == "script_text"
        assert DeliverableType.METADATA_JSON == "metadata_json"
        assert DeliverableType.CHAPTER_MARKERS == "chapter_markers"
        assert DeliverableType.SCRIPTS_ARCHIVE == "scripts_archive"


class TestDeliverableResponse:
    """Tests for DeliverableResponse schema."""

    def test_valid_deliverable_response_full_audiobook(self):
        """Test creating deliverable response for full audiobook."""
        response_dict = {
            "id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "file_type": "full_audiobook",
            "s3_url": "https://s3.amazonaws.com/bucket/audiobook.mp3",
            "file_size_bytes": 50000000,
            "mime_type": "audio/mpeg",
            "filename": "full_audiobook.mp3",
            "duration_seconds": 3600,
            "created_at": datetime.utcnow(),
        }
        response = DeliverableResponse(**response_dict)
        assert response.file_type == "full_audiobook"
        assert response.file_size_bytes == 50000000
        assert response.duration_seconds == 3600

    def test_valid_deliverable_response_chapter_audio(self):
        """Test creating deliverable response for chapter audio."""
        response_dict = {
            "id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "file_type": "chapter_audio",
            "s3_url": "https://s3.amazonaws.com/bucket/chapter_1.mp3",
            "file_size_bytes": 5000000,
            "mime_type": "audio/mpeg",
            "filename": "chapter_1.mp3",
            "chapter_number": 1,
            "duration_seconds": 360,
            "created_at": datetime.utcnow(),
        }
        response = DeliverableResponse(**response_dict)
        assert response.chapter_number == 1
        assert response.file_type == "chapter_audio"

    def test_valid_deliverable_response_script(self):
        """Test creating deliverable response for script."""
        response_dict = {
            "id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "file_type": "script_text",
            "s3_url": "https://s3.amazonaws.com/bucket/script.txt",
            "file_size_bytes": 10000,
            "mime_type": "text/plain",
            "filename": "script.txt",
            "created_at": datetime.utcnow(),
        }
        response = DeliverableResponse(**response_dict)
        assert response.file_type == "script_text"
        assert response.chapter_number is None
        assert response.duration_seconds is None

    def test_deliverable_negative_file_size_rejected(self):
        """Test that negative file size is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DeliverableResponse(
                id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                file_type="full_audiobook",
                s3_url="https://s3.amazonaws.com/bucket/file.mp3",
                file_size_bytes=-100,
                mime_type="audio/mpeg",
                filename="file.mp3",
                created_at=datetime.utcnow(),
            )
        assert "negative" in str(exc_info.value).lower()

    def test_deliverable_excessive_file_size_rejected(self):
        """Test that excessive file size is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DeliverableResponse(
                id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                file_type="full_audiobook",
                s3_url="https://s3.amazonaws.com/bucket/file.mp3",
                file_size_bytes=6000000000,  # 6GB
                mime_type="audio/mpeg",
                filename="file.mp3",
                created_at=datetime.utcnow(),
            )
        assert "5GB" in str(exc_info.value)

    def test_deliverable_negative_duration_rejected(self):
        """Test that negative duration is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            DeliverableResponse(
                id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                file_type="chapter_audio",
                s3_url="https://s3.amazonaws.com/bucket/file.mp3",
                file_size_bytes=1000000,
                mime_type="audio/mpeg",
                filename="file.mp3",
                duration_seconds=-10,
                created_at=datetime.utcnow(),
            )
        assert "negative" in str(exc_info.value).lower()

    def test_deliverable_zero_duration_accepted(self):
        """Test that zero duration is accepted."""
        response = DeliverableResponse(
            id=uuid.uuid4(),
            job_id=uuid.uuid4(),
            file_type="chapter_audio",
            s3_url="https://s3.amazonaws.com/bucket/file.mp3",
            file_size_bytes=1000000,
            mime_type="audio/mpeg",
            filename="file.mp3",
            duration_seconds=0,
            created_at=datetime.utcnow(),
        )
        assert response.duration_seconds == 0


class TestDeliverableListResponse:
    """Tests for DeliverableListResponse schema."""

    def test_valid_deliverable_list(self):
        """Test creating deliverable list with valid data."""
        deliverables = [
            DeliverableResponse(
                id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                file_type="full_audiobook",
                s3_url="https://s3.amazonaws.com/bucket/full.mp3",
                file_size_bytes=50000000,
                mime_type="audio/mpeg",
                filename="full.mp3",
                created_at=datetime.utcnow(),
            ),
            DeliverableResponse(
                id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                file_type="chapter_audio",
                s3_url="https://s3.amazonaws.com/bucket/chapter_1.mp3",
                file_size_bytes=5000000,
                mime_type="audio/mpeg",
                filename="chapter_1.mp3",
                created_at=datetime.utcnow(),
            ),
        ]
        
        list_response = DeliverableListResponse(
            deliverables=deliverables,
            total_size_bytes=55000000,
            total_files=2,
            total_duration_seconds=4000,
        )
        
        assert len(list_response.deliverables) == 2
        assert list_response.total_size_bytes == 55000000
        assert list_response.total_files == 2
        assert list_response.total_duration_seconds == 4000

    def test_deliverable_list_empty(self):
        """Test creating empty deliverable list."""
        list_response = DeliverableListResponse(
            deliverables=[],
            total_size_bytes=0,
            total_files=0,
        )
        assert len(list_response.deliverables) == 0
        assert list_response.total_size_bytes == 0

    def test_deliverable_list_negative_total_size_rejected(self):
        """Test that negative total size is rejected."""
        with pytest.raises(ValidationError):
            DeliverableListResponse(
                deliverables=[],
                total_size_bytes=-100,
                total_files=0,
            )

    def test_deliverable_list_negative_total_files_rejected(self):
        """Test that negative total files is rejected."""
        with pytest.raises(ValidationError):
            DeliverableListResponse(
                deliverables=[],
                total_size_bytes=0,
                total_files=-1,
            )

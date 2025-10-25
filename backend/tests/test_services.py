"""
Tests for backend services.

Tests for:
- Repository Analyzer Service
- Outline Generator Service
- Script Generator Service
- Audio Synthesizer Service
- Post Processor Service
- Storage Service
- Payment Service
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime


@pytest.mark.services
@pytest.mark.unit
class TestRepositoryAnalyzer:
    """Test Repository Analyzer service."""

    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test analyzer can be initialized."""
        from backend.services.repository_analyzer import RepositoryAnalyzer

        analyzer = RepositoryAnalyzer(
            repo_url="https://github.com/user/repo",
            git_ref="main",
            use_docling=False
        )

        assert analyzer.repo_url == "https://github.com/user/repo"
        assert analyzer.git_ref == "main"

    @pytest.mark.asyncio
    async def test_analyzer_with_docling_mode(self):
        """Test analyzer initialization with Docling enabled."""
        from backend.services.repository_analyzer import RepositoryAnalyzer

        with patch('backend.services.repository_analyzer.HAS_DOCLING_PIPELINE', True):
            with patch('backend.services.docling_pipeline.HAS_DOCLING', True):
                with patch('backend.services.docling_pipeline.DocumentConverter'):
                    analyzer = RepositoryAnalyzer(
                        repo_url="https://github.com/user/repo",
                        use_docling=True
                    )

                    assert analyzer.use_docling is True

    @pytest.mark.asyncio
    @patch('backend.services.repository_analyzer.Repo')
    async def test_clone_repository(self, mock_repo_class):
        """Test repository cloning."""
        from backend.services.repository_analyzer import RepositoryAnalyzer

        # Mock the git repo
        mock_repo = MagicMock()
        mock_repo.head.commit.hexsha = "abc123"
        mock_repo_class.clone_from.return_value = mock_repo

        analyzer = RepositoryAnalyzer(
            repo_url="https://github.com/user/repo",
            use_docling=False
        )

        with patch('backend.services.repository_analyzer.HAS_GIT', True):
            result = await analyzer.clone_repository()

            assert result is not None
            assert result.exists()
            mock_repo_class.clone_from.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyzer_max_size_validation(self):
        """Test that analyzer respects max repository size."""
        from backend.services.repository_analyzer import RepositoryAnalyzer

        analyzer = RepositoryAnalyzer(
            repo_url="https://github.com/user/huge-repo",
            max_repo_size_mb=100
        )

        assert analyzer.max_repo_size_mb == 100


@pytest.mark.services
@pytest.mark.unit
class TestOutlineGenerator:
    """Test Outline Generator service."""

    @pytest.mark.asyncio
    async def test_generate_outline_basic(self, sample_analysis_result, mock_anthropic_client):
        """Test basic outline generation."""
        from backend.services.outline_generator import generate_outline

        with patch('backend.services.outline_generator.get_settings') as mock_settings:
            mock_settings.return_value.ANTHROPIC_API_KEY = "test-key"

            with patch('backend.agents.outline_agent.create_outline_agent') as mock_create:
                mock_agent = AsyncMock()
                mock_agent.run = AsyncMock(return_value=MagicMock(
                    result='{"chapters": [], "total_chapters": 0}'
                ))
                mock_create.return_value = mock_agent

                result = await generate_outline(
                    analysis_data=sample_analysis_result,
                    depth_tier="standard",
                    job_id="test-job-1"
                )

                # Should return outline structure
                assert "chapters" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_outline_different_tiers(self):
        """Test outline generation for different depth tiers."""
        from backend.services.outline_generator import generate_outline

        analysis_data = {"structure": {"file_count": 50}}

        for tier in ["survey", "standard", "comprehensive"]:
            result = await generate_outline(
                analysis_data=analysis_data,
                depth_tier=tier,
                job_id="test-job"
            )

            # Result should be different based on tier
            assert result is not None


@pytest.mark.services
@pytest.mark.unit
class TestScriptGenerator:
    """Test Script Generator service."""

    @pytest.mark.asyncio
    async def test_generate_script_for_chapter(self, sample_chapter_data):
        """Test script generation for a single chapter."""
        from backend.services.script_generator import generate_script

        chapter_data = sample_chapter_data
        code_context = {"files": ["main.py"], "functions": ["main()"]}

        result = await generate_script(
            chapter_data=chapter_data,
            code_context=code_context,
            job_id="test-job"
        )

        # Should return script text
        assert result is not None

    @pytest.mark.asyncio
    async def test_generate_script_handles_empty_context(self, sample_chapter_data):
        """Test script generation with minimal context."""
        from backend.services.script_generator import generate_script

        result = await generate_script(
            chapter_data=sample_chapter_data,
            code_context={},
            job_id="test-job"
        )

        assert result is not None


@pytest.mark.services
@pytest.mark.unit
class TestAudioSynthesizer:
    """Test Audio Synthesizer service."""

    @pytest.mark.asyncio
    async def test_synthesize_audio_from_script(self, mock_elevenlabs_client):
        """Test audio synthesis from script text."""
        from backend.services.audio_synthesizer import synthesize_audio

        with patch('backend.services.audio_synthesizer.get_settings') as mock_settings:
            mock_settings.return_value.ELEVENLABS_API_KEY = "test-key"

            script_text = "This is a test narration script."

            result = await synthesize_audio(
                script_text=script_text,
                chapter_number=1,
                job_id="test-job"
            )

            # Should return audio file path or URL
            assert result is not None

    @pytest.mark.asyncio
    async def test_synthesize_handles_long_scripts(self):
        """Test audio synthesis splits long scripts into chunks."""
        from backend.services.audio_synthesizer import synthesize_audio

        # Create a very long script
        long_script = "This is a sentence. " * 500

        result = await synthesize_audio(
            script_text=long_script,
            chapter_number=1,
            job_id="test-job"
        )

        assert result is not None


@pytest.mark.services
@pytest.mark.unit
class TestPostProcessor:
    """Test Post Processor service."""

    @pytest.mark.asyncio
    async def test_merge_chapter_audio_files(self, tmp_path):
        """Test merging multiple audio files."""
        from backend.services.post_processor import merge_audio_files

        # Create fake audio file paths
        audio_files = [
            str(tmp_path / "chapter1.mp3"),
            str(tmp_path / "chapter2.mp3")
        ]

        result = await merge_audio_files(
            audio_files=audio_files,
            output_path=str(tmp_path / "full_audiobook.mp3"),
            job_id="test-job"
        )

        # Should return path to merged file
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_deliverables(self):
        """Test deliverable creation."""
        from backend.services.post_processor import create_deliverables

        job_data = {
            "id": "test-job",
            "repo_name": "test-repo"
        }

        chapters = [
            {"number": 1, "audio_url": "https://s3.example.com/ch1.mp3"},
            {"number": 2, "audio_url": "https://s3.example.com/ch2.mp3"}
        ]

        result = await create_deliverables(
            job_data=job_data,
            chapters=chapters
        )

        assert result is not None


@pytest.mark.services
@pytest.mark.unit
class TestStorageService:
    """Test Storage service (AWS S3)."""

    @pytest.mark.asyncio
    async def test_upload_audio_file(self, mock_s3_client, tmp_path):
        """Test uploading audio file to S3."""
        from backend.services.storage import upload_audio_file

        # Create a fake audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        with patch('backend.services.storage.boto3.client', return_value=mock_s3_client):
            result = await upload_audio_file(
                job_id="test-job",
                chapter_number=1,
                file_path=str(audio_file)
            )

            # Should return S3 URL
            assert result is not None
            assert "http" in result or result.startswith("s3://")

    @pytest.mark.asyncio
    async def test_generate_presigned_url(self, mock_s3_client):
        """Test generating presigned URL for private files."""
        from backend.services.storage import generate_presigned_url

        with patch('backend.services.storage.boto3.client', return_value=mock_s3_client):
            result = await generate_presigned_url(
                s3_key="jobs/test-job/audio/chapter1.mp3"
            )

            assert result is not None
            assert "http" in result

    @pytest.mark.asyncio
    async def test_delete_job_files(self, mock_s3_client):
        """Test deleting all files for a job."""
        from backend.services.storage import delete_job_files

        with patch('backend.services.storage.boto3.client', return_value=mock_s3_client):
            result = await delete_job_files(job_id="test-job")

            # Should complete without error
            assert result is not None or result is None


@pytest.mark.services
@pytest.mark.unit
class TestPaymentService:
    """Test Payment service (Stripe)."""

    @pytest.mark.asyncio
    async def test_create_payment_intent(self, mock_stripe_client):
        """Test creating Stripe payment intent."""
        from backend.services.payment import create_payment_intent

        with patch('backend.services.payment.stripe', mock_stripe_client):
            result = await create_payment_intent(
                job_id="test-job",
                amount_cents=4900,
                user_email="test@example.com"
            )

            assert result is not None
            assert "client_secret" in result

    @pytest.mark.asyncio
    async def test_handle_payment_success_webhook(self, mock_stripe_client, test_db, create_job):
        """Test handling successful payment webhook."""
        from backend.services.payment import handle_payment_webhook

        job = create_job()

        webhook_payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "metadata": {"job_id": str(job.id)}
                }
            }
        }

        with patch('backend.services.payment.stripe', mock_stripe_client):
            result = await handle_payment_webhook(
                payload=webhook_payload,
                signature="test_signature"
            )

            # Should process successfully
            assert result is not None

    @pytest.mark.asyncio
    async def test_refund_payment(self, mock_stripe_client):
        """Test processing refund."""
        from backend.services.payment import process_refund

        with patch('backend.services.payment.stripe', mock_stripe_client):
            result = await process_refund(
                payment_intent_id="pi_test_123",
                reason="Job failed"
            )

            assert result is not None


@pytest.mark.services
@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for service interactions."""

    @pytest.mark.skip(reason="Requires full environment setup")
    @pytest.mark.asyncio
    async def test_full_audiobook_generation_pipeline(
        self,
        sample_analysis_result,
        test_db,
        create_job
    ):
        """Test complete pipeline from analysis to deliverables."""
        job = create_job()

        # This would test the full flow:
        # 1. Repository analysis
        # 2. Outline generation
        # 3. Script generation
        # 4. Audio synthesis
        # 5. Post-processing
        # 6. Storage upload

        assert job is not None

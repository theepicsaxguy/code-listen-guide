"""
Token estimation service for accurate cost calculation before job creation.

Implements real token counting using tiktoken for LLM tokens and character
counting for TTS, replacing placeholder estimates with actual calculations.
"""

import logging
from typing import Dict, List, Optional
import tiktoken

logger = logging.getLogger(__name__)


class TokenEstimator:
    """
    Estimate tokens and costs for LLM and TTS operations.
    
    Uses tiktoken for accurate token counting based on OpenAI's encoding.
    Calculates costs based on current API pricing for Claude and OpenAI TTS.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize token estimator.
        
        Args:
            model: Model name for token encoding (default: gpt-4)
        """
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base if model not found
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))
    
    def estimate_llm_tokens(self, file_contents: List[str], depth_tier: str = "standard") -> int:
        """
        Estimate tokens for code analysis and script generation.
        
        Args:
            file_contents: List of file content strings
            depth_tier: Depth tier (survey, standard, comprehensive)
            
        Returns:
            Estimated total LLM tokens needed
        """
        total_tokens = 0
        
        # Count tokens in all file contents
        for content in file_contents:
            total_tokens += self.count_tokens(content)
        
        # Add overhead for prompts and agent instructions
        # Outline generation: ~2000 tokens
        # Script generation per chapter: ~1000 tokens system prompt
        # Multi-turn dialogue: ~500 tokens per turn overhead
        
        tier_multipliers = {
            "survey": 1.3,      # Less detailed analysis
            "standard": 1.5,    # Standard overhead
            "comprehensive": 2.0,  # More detailed, longer conversations
        }
        
        multiplier = tier_multipliers.get(depth_tier, 1.5)
        return int(total_tokens * multiplier)
    
    def estimate_tts_chars(self, script_word_count: int) -> int:
        """
        Estimate TTS characters needed.
        
        Args:
            script_word_count: Estimated word count of generated scripts
            
        Returns:
            Estimated TTS characters
        """
        # Average: ~5 characters per word (including spaces and punctuation)
        return script_word_count * 5
    
    def estimate_script_length(
        self,
        file_count: int,
        depth_tier: str = "standard"
    ) -> int:
        """
        Estimate total word count of generated scripts.
        
        Args:
            file_count: Number of files to be analyzed
            depth_tier: Depth tier
            
        Returns:
            Estimated word count
        """
        # Base words per file by tier
        words_per_file = {
            "survey": 300,       # High-level overview
            "standard": 500,     # Detailed explanation
            "comprehensive": 800,  # Deep dive with examples
        }
        
        base_words = words_per_file.get(depth_tier, 500)
        return file_count * base_words
    
    def calculate_llm_cost(self, tokens: int) -> int:
        """
        Calculate LLM cost in cents.
        
        Uses Claude 3.5 Sonnet pricing:
        - Input: $3/MTok
        - Output: $15/MTok
        - Average: ~$9/MTok (assuming 50/50 split)
        
        Args:
            tokens: Total token count
            
        Returns:
            Cost in cents
        """
        # Average cost per million tokens (cents)
        cost_per_mtok = 900  # $9/MTok
        
        cost_cents = (tokens / 1_000_000) * cost_per_mtok
        return int(cost_cents)
    
    def calculate_tts_cost(self, chars: int) -> int:
        """
        Calculate TTS cost in cents.
        
        Uses OpenAI TTS pricing:
        - HD quality: $15/1M characters
        
        Args:
            chars: Total character count
            
        Returns:
            Cost in cents
        """
        # Cost per million characters (cents)
        cost_per_mchars = 1500  # $15/1M chars
        
        cost_cents = (chars / 1_000_000) * cost_per_mchars
        return int(cost_cents)
    
    def estimate_job_cost(
        self,
        file_contents: List[str],
        depth_tier: str = "standard",
        selected_files: Optional[List[str]] = None,
        excluded_patterns: Optional[List[str]] = None,
    ) -> Dict:
        """
        Calculate complete cost estimate for a job.
        
        Args:
            file_contents: List of file content strings
            depth_tier: Depth tier
            selected_files: User-selected files (or None for all)
            excluded_patterns: Exclusion patterns
            
        Returns:
            Dictionary with detailed cost breakdown
        """
        # Estimate LLM tokens
        llm_tokens = self.estimate_llm_tokens(file_contents, depth_tier)
        
        # Estimate script length
        file_count = len(file_contents)
        script_words = self.estimate_script_length(file_count, depth_tier)
        
        # Estimate TTS characters
        tts_chars = self.estimate_tts_chars(script_words)
        
        # Calculate costs
        llm_cost_cents = self.calculate_llm_cost(llm_tokens)
        tts_cost_cents = self.calculate_tts_cost(tts_chars)
        total_cost_cents = llm_cost_cents + tts_cost_cents
        
        # Estimate duration (150 words per minute average narration)
        duration_minutes = script_words / 150
        
        # Estimate number of episodes (20-30 min each, use 25 as average)
        estimated_episodes = max(1, int(duration_minutes / 25))
        
        return {
            "llm_tokens": llm_tokens,
            "tts_chars": tts_chars,
            "llm_cost_cents": llm_cost_cents,
            "tts_cost_cents": tts_cost_cents,
            "total_cost_cents": total_cost_cents,
            "estimated_duration_minutes": int(duration_minutes),
            "estimated_episodes": estimated_episodes,
            "file_count": file_count,
        }

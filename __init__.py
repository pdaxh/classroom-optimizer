"""
Classroom Optimizer

AI-powered seating optimization tool for teachers.
Uses Google ADK for AI interaction and OR-Tools for constraint satisfaction.
"""

__version__ = "0.1.0"
__author__ = "Daniel"

from .agents.agent import root_agent

__all__ = ["root_agent"]


"""Exercise service handling business logic for listening exercises."""
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import pyodbc
from app.models.exercise import ListeningItem, Question, AssessmentAttempt


class ExerciseService:
    """Handles exercise-related business logic and database operations."""
    
    @staticmethod
    def get_all_listening_items(cursor: pyodbc.Cursor, 
                               limit: int = 100) -> List[ListeningItem]:
        """Retrieve all listening items with their questions and topics."""
        query = """
            SELECT * FROM listening_items 
            WHERE is_deleted = 0 
            ORDER BY item_id
        """
        if limit:
            query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
        
        cursor.execute(query)
        items = [ListeningItem.from_db_row(row) for row in cursor.fetchall()]
        
        for item in items:
            item.topics = ExerciseService._get_item_topics(cursor, item.item_id)
            item.questions = ExerciseService._get_item_questions(cursor, item.item_id)
        
        return items
    
    @staticmethod
    def get_listening_item_by_id(cursor: pyodbc.Cursor, 
                                 item_id: int) -> Optional[ListeningItem]:
        """Retrieve a specific listening item with questions and topics."""
        query = """
            SELECT * FROM listening_items 
            WHERE item_id = ? AND is_deleted = 0
        """
        cursor.execute(query, (item_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        item = ListeningItem.from_db_row(row)
        item.topics = ExerciseService._get_item_topics(cursor, item_id)
        item.questions = ExerciseService._get_item_questions(cursor, item_id)
        
        return item
    
    @staticmethod
    def _get_item_topics(cursor: pyodbc.Cursor, item_id: int) -> List[str]:
        """Retrieve topics associated with a listening item."""
        query = """
            SELECT t.name 
            FROM topics t
            INNER JOIN item_topics it ON t.topic_id = it.topic_id
            WHERE it.item_id = ?
        """
        cursor.execute(query, (item_id,))
        return [row.name for row in cursor.fetchall()]
    
    @staticmethod
    def _get_item_questions(cursor: pyodbc.Cursor, item_id: int) -> List[Question]:
        """Retrieve questions for a listening item."""
        query = """
            SELECT q.*, s.name as skill_name
            FROM listening_questions q
            INNER JOIN skills s ON q.skill_id = s.skill_id
            WHERE q.item_id = ? AND q.is_deleted = 0
            ORDER BY q.order_index
        """
        cursor.execute(query, (item_id,))
        return [Question.from_db_row(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create_assessment_attempt(cursor: pyodbc.Cursor, 
                                 user_id: int,
                                 item_id: int) -> int:
        """Create a new assessment attempt record."""
        query = """
            INSERT INTO assessment_attempts 
            (user_id, blueprint_id, attempt_mode, start_time, status, 
             settings, settings_version, created_at)
            OUTPUT INSERTED.attempt_id
            VALUES (?, 1, 'practice', ?, 'in_progress', '{}', 1, ?)
        """
        now = datetime.utcnow()
        cursor.execute(query, (user_id, now, now))
        result = cursor.fetchone()
        return result.attempt_id
    
    @staticmethod
    def submit_exercise_answers(
        cursor: pyodbc.Cursor,
        user_id: int,
        item_id: int,
        answers: Dict[int, str]
    ) -> Tuple[int, List[Dict], List[Dict]]:
        """Process exercise submission and calculate results."""
        attempt_id = ExerciseService.create_assessment_attempt(cursor, user_id, item_id)
        
        questions = ExerciseService._get_item_questions(cursor, item_id)
        
        results = []
        correct_count = 0
        skill_stats = {}
        
        for question in questions:
            selected_answer = answers.get(question.question_id, "")
            is_correct = selected_answer.upper() == question.correct_answer.upper()
            
            if is_correct:
                correct_count += 1
            
            ExerciseService._save_item_response(
                cursor, attempt_id, question.question_id, 
                selected_answer, is_correct
            )
            
            results.append({
                "question_id": question.question_id,
                "selected_answer": selected_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation
            })
            
            if question.skill_name not in skill_stats:
                skill_stats[question.skill_name] = {"correct": 0, "total": 0}
            skill_stats[question.skill_name]["total"] += 1
            if is_correct:
                skill_stats[question.skill_name]["correct"] += 1
        
        percentage = (correct_count / len(questions) * 100) if questions else 0
        
        ExerciseService._update_attempt_status(
            cursor, attempt_id, correct_count, percentage
        )
        
        skill_results = ExerciseService._save_skill_results(
            cursor, attempt_id, skill_stats
        )
        
        return attempt_id, results, skill_results
    
    @staticmethod
    def _save_item_response(cursor: pyodbc.Cursor, attempt_id: int,
                           question_id: int, selected_answer: str,
                           is_correct: bool) -> None:
        """Save individual question response."""
        query = """
            INSERT INTO item_responses 
            (attempt_id, question_id, selected_answer, is_correct, 
             response_time_ms, answered_at, created_at)
            VALUES (?, ?, ?, ?, 0, ?, ?)
        """
        now = datetime.utcnow()
        cursor.execute(query, (attempt_id, question_id, selected_answer, 
                              is_correct, now, now))
    
    @staticmethod
    def _update_attempt_status(cursor: pyodbc.Cursor, attempt_id: int,
                              raw_score: int, percentage: float) -> None:
        """Update assessment attempt with final scores."""
        query = """
            UPDATE assessment_attempts 
            SET status = 'completed', 
                raw_score = ?, 
                scaled_score = ?,
                end_time = ?,
                updated_at = ?
            WHERE attempt_id = ?
        """
        now = datetime.utcnow()
        scaled_score = int(percentage)
        cursor.execute(query, (raw_score, scaled_score, now, now, attempt_id))
    
    @staticmethod
    def _save_skill_results(cursor: pyodbc.Cursor, attempt_id: int,
                           skill_stats: Dict) -> List[Dict]:
        """Save skill-based results for the attempt."""
        skill_results = []
        
        for skill_name, stats in skill_stats.items():
            skill_id = ExerciseService._get_skill_id_by_name(cursor, skill_name)
            percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            query = """
                INSERT INTO skill_results 
                (attempt_id, skill_id, correct_count, total_count, percentage, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (attempt_id, skill_id, stats["correct"], 
                                 stats["total"], percentage, datetime.utcnow()))
            
            skill_results.append({
                "skill_name": skill_name,
                "correct_count": stats["correct"],
                "total_count": stats["total"],
                "percentage": round(percentage, 2)
            })
        
        return skill_results
    
    @staticmethod
    def _get_skill_id_by_name(cursor: pyodbc.Cursor, skill_name: str) -> int:
        """Get skill ID by skill name."""
        query = "SELECT skill_id FROM skills WHERE name = ?"
        cursor.execute(query, (skill_name,))
        row = cursor.fetchone()
        return row.skill_id if row else 1
    
    @staticmethod
    def get_user_completed_exercises(cursor: pyodbc.Cursor, 
                                     user_id: int) -> List[Dict]:
        """Retrieve completed exercises for a user."""
        query = """
            SELECT 
                aa.attempt_id,
                li.item_id as exercise_id,
                CONCAT('Exercise ', li.item_id) as title,
                aa.end_time as completed_at,
                aa.raw_score as score,
                aa.scaled_score as percentage
            FROM assessment_attempts aa
            INNER JOIN blueprint_items bi ON aa.blueprint_id = bi.blueprint_id
            INNER JOIN listening_items li ON bi.item_id = li.item_id
            WHERE aa.user_id = ? AND aa.status = 'completed'
            ORDER BY aa.end_time DESC
        """
        cursor.execute(query, (user_id,))
        return [dict(zip([column[0] for column in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    @staticmethod
    def mark_exercise_complete(cursor: pyodbc.Cursor, 
                               user_id: int, 
                               exercise_id: int) -> bool:
        """Mark an exercise as completed for a user."""
        query = """
            UPDATE assessment_attempts 
            SET status = 'completed', 
                end_time = ?,
                updated_at = ?
            WHERE user_id = ? 
            AND attempt_id IN (
                SELECT TOP 1 attempt_id 
                FROM assessment_attempts 
                WHERE user_id = ? 
                ORDER BY start_time DESC
            )
        """
        now = datetime.utcnow()
        cursor.execute(query, (now, now, user_id, user_id))
        return cursor.rowcount > 0


exercise_service = ExerciseService()

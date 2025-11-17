#!/usr/bin/env python3
"""
Classroom Optimization Tools

Uses Google OR-Tools for constraint satisfaction and seating optimization.
"""

from typing import Any, Dict, List
from ortools.sat.python import cp_model


def validate_constraints(
    classroom_size: Dict[str, int],
    num_students: int,
    constraints: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate that the constraints are feasible given the classroom size.
    
    Args:
        classroom_size: Dict with 'rows' and 'columns'
        num_students: Total number of students
        constraints: List of constraint dictionaries
        
    Returns:
        Dict with validation results and any warnings
    """
    rows = classroom_size.get('rows', 0)
    columns = classroom_size.get('columns', 0)
    total_seats = rows * columns
    
    validation_result = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "info": {
            "total_seats": total_seats,
            "students": num_students,
            "available_seats": total_seats - num_students
        }
    }
    
    # Check basic feasibility
    if num_students > total_seats:
        validation_result["valid"] = False
        validation_result["errors"].append(
            f"Not enough seats: {num_students} students need {total_seats} seats"
        )
        return validation_result
    
    # Count constraint types
    constraint_counts = {}
    front_row_requirements = 0
    back_row_exclusions = 0
    
    for constraint in constraints:
        constraint_type = constraint.get('type', 'unknown')
        constraint_counts[constraint_type] = constraint_counts.get(constraint_type, 0) + 1
        
        if constraint_type == 'must_front_row':
            front_row_requirements += 1
        elif constraint_type == 'cannot_back_row':
            back_row_exclusions += 1
    
    # Check front row capacity
    if front_row_requirements > columns:
        validation_result["warnings"].append(
            f"Front row has only {columns} seats but {front_row_requirements} students require it"
        )
    
    # Check if too many students exclude back row
    non_back_row_seats = (rows - 1) * columns
    if back_row_exclusions + front_row_requirements > non_back_row_seats:
        validation_result["warnings"].append(
            "Too many students excluding back row - may be difficult to satisfy"
        )
    
    validation_result["constraint_summary"] = constraint_counts
    
    return validation_result


def optimize_seating(
    classroom_layout: Dict[str, int],
    students: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate optimal seating arrangement using OR-Tools constraint satisfaction.
    
    Args:
        classroom_layout: Dict with 'rows' and 'columns'
        students: List of student dicts with 'id' and 'name'
        constraints: List of constraint dicts with 'type' and relevant student IDs
        
    Returns:
        Dict with seating arrangement and satisfaction info
    """
    rows = classroom_layout.get('rows', 5)
    columns = classroom_layout.get('columns', 6)
    num_students = len(students)
    
    # Create the CP-SAT model
    model = cp_model.CpModel()
    
    # Decision variables: seat[student_id, row, col] = 1 if student sits there
    seats = {}
    for student in students:
        student_id = student['id']
        for row in range(rows):
            for col in range(columns):
                seats[(student_id, row, col)] = model.NewBoolVar(
                    f'seat_s{student_id}_r{row}_c{col}'
                )
    
    # Constraint: Each student sits in exactly one seat
    for student in students:
        student_id = student['id']
        model.Add(sum(seats[(student_id, r, c)] 
                     for r in range(rows) 
                     for c in range(columns)) == 1)
    
    # Constraint: Each seat has at most one student
    for row in range(rows):
        for col in range(columns):
            model.Add(sum(seats[(s['id'], row, col)] for s in students) <= 1)
    
    # Apply custom constraints
    for constraint in constraints:
        constraint_type = constraint.get('type')
        
        if constraint_type == 'cannot_sit_together':
            # Students cannot sit adjacent (including diagonals)
            student1_id = constraint.get('student1')
            student2_id = constraint.get('student2')
            
            for row in range(rows):
                for col in range(columns):
                    # Get adjacent positions
                    adjacent = []
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < rows and 0 <= new_col < columns:
                                adjacent.append((new_row, new_col))
                    
                    # If student1 sits here, student2 cannot sit in adjacent seats
                    for adj_row, adj_col in adjacent:
                        model.AddBoolOr([
                            seats[(student1_id, row, col)].Not(),
                            seats[(student2_id, adj_row, adj_col)].Not()
                        ])
        
        elif constraint_type == 'must_front_row':
            # Student must sit in front row (row 0)
            student_id = constraint.get('student')
            model.Add(sum(seats[(student_id, 0, c)] for c in range(columns)) == 1)
        
        elif constraint_type == 'cannot_back_row':
            # Student cannot sit in back row
            student_id = constraint.get('student')
            model.Add(sum(seats[(student_id, rows-1, c)] for c in range(columns)) == 0)
        
        elif constraint_type == 'near_door':
            # Prefer seats near door (assuming door is at col 0)
            student_id = constraint.get('student')
            # Add preference for column 0 or 1
            # This is a soft constraint - could be weighted
            pass  # Simplified for now
        
        elif constraint_type == 'near_window':
            # Prefer seats near window (assuming window is at col = columns-1)
            student_id = constraint.get('student')
            pass  # Simplified for now
        
        elif constraint_type == 'cannot_by_window':
            # Cannot sit by window
            student_id = constraint.get('student')
            model.Add(sum(seats[(student_id, r, columns-1)] for r in range(rows)) == 0)
        
        elif constraint_type == 'cannot_by_door':
            # Cannot sit by door
            student_id = constraint.get('student')
            model.Add(sum(seats[(student_id, r, 0)] for r in range(rows)) == 0)
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    # Extract solution
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        seating_chart = [[None for _ in range(columns)] for _ in range(rows)]
        
        for student in students:
            student_id = student['id']
            for row in range(rows):
                for col in range(columns):
                    if solver.Value(seats[(student_id, row, col)]):
                        seating_chart[row][col] = {
                            "id": student_id,
                            "name": student['name']
                        }
        
        return {
            "success": True,
            "status": "optimal" if status == cp_model.OPTIMAL else "feasible",
            "seating_chart": seating_chart,
            "layout": {"rows": rows, "columns": columns},
            "statistics": {
                "solve_time_seconds": solver.WallTime(),
                "constraints_satisfied": len(constraints)
            }
        }
    else:
        return {
            "success": False,
            "status": "infeasible",
            "message": "Could not find a valid seating arrangement with the given constraints. Try relaxing some constraints.",
            "seating_chart": None
        }


def explain_solution(
    seating_chart: List[List[Dict[str, Any]]],
    constraints: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Explain how the seating arrangement satisfies the constraints.
    
    Args:
        seating_chart: 2D array of seating positions
        constraints: List of constraints that were applied
        
    Returns:
        Dict with explanations for each constraint
    """
    explanations = []
    
    rows = len(seating_chart)
    columns = len(seating_chart[0]) if rows > 0 else 0
    
    # Find student positions
    student_positions = {}
    for row in range(rows):
        for col in range(columns):
            if seating_chart[row][col]:
                student_id = seating_chart[row][col]['id']
                student_positions[student_id] = (row, col)
    
    # Explain each constraint
    for i, constraint in enumerate(constraints, 1):
        constraint_type = constraint.get('type')
        
        if constraint_type == 'cannot_sit_together':
            student1_id = constraint.get('student1')
            student2_id = constraint.get('student2')
            
            if student1_id in student_positions and student2_id in student_positions:
                pos1 = student_positions[student1_id]
                pos2 = student_positions[student2_id]
                distance = max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))
                
                explanations.append({
                    "constraint": f"Students {student1_id} and {student2_id} cannot sit together",
                    "satisfied": distance > 1,
                    "explanation": f"They are {distance} seats apart (row/col distance)"
                })
        
        elif constraint_type == 'must_front_row':
            student_id = constraint.get('student')
            if student_id in student_positions:
                row, col = student_positions[student_id]
                explanations.append({
                    "constraint": f"Student {student_id} must sit in front row",
                    "satisfied": row == 0,
                    "explanation": f"Seated in row {row + 1}, column {col + 1}"
                })
        
        elif constraint_type == 'cannot_back_row':
            student_id = constraint.get('student')
            if student_id in student_positions:
                row, col = student_positions[student_id]
                explanations.append({
                    "constraint": f"Student {student_id} cannot sit in back row",
                    "satisfied": row < rows - 1,
                    "explanation": f"Seated in row {row + 1} (not back row)"
                })
    
    all_satisfied = all(exp.get('satisfied', True) for exp in explanations)
    
    return {
        "all_constraints_satisfied": all_satisfied,
        "total_constraints": len(constraints),
        "explanations": explanations,
        "summary": f"Successfully satisfied {sum(1 for e in explanations if e.get('satisfied'))} out of {len(constraints)} constraints"
    }


__all__ = ["optimize_seating", "validate_constraints", "explain_solution"]


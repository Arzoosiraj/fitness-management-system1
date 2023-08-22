import ast
from flask import render_template, session, request, redirect, url_for, Blueprint, flash, make_response
from ..database import db
from .models import Workout, Exercise
import json
from werkzeug.security import generate_password_hash, check_password_hash
from fitness_management.user.routes import login_required, get_current_user
from flask import abort


workout_bp = Blueprint("workout_bp", __name__)


@workout_bp.route('/create_workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    current_user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            workout = Workout(title=title, user_id=current_user.id)
            db.session.add(workout)
            db.session.commit()
            flash(f'New Workout Has Been Created', 'success')
            return redirect(url_for('workout_bp.list_workouts'))
    return render_template('workout_planner/create_workout.html', current_user=current_user)


@workout_bp.route('/workout/<int:id>', methods=['GET', 'POST'])
def workout_detail(id):
    current_user = get_current_user()
    workout = Workout.query.get_or_404(id)
    if workout.user_id != current_user.id:
        abort(403)  # Forbidden access
    if request.method == 'POST':
        name = request.form.get('name')
        sets = request.form.get('sets')
        reps = request.form.get('reps')
        if name and sets and reps:
            exercise = Exercise(name=name, sets=sets, reps=reps, workout_id=id)
            db.session.add(exercise)
            db.session.commit()
            flash(f'New Exercise Has Been Created', 'success')
            return redirect(url_for('workout_bp.workout_detail', id=id))
    return render_template('workout_planner/workout_detail.html', workout=workout, current_user=current_user)


@workout_bp.route("/updateexercise/<int:exercise_id>/<int:workout_id>", methods=['GET', 'POST'])
@login_required
def updateexercise(exercise_id, workout_id):
    workout = Workout.query.get_or_404(workout_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    if request.method == 'POST':
        exercise.name = request.form.get("name")
        exercise.sets = request.form.get("sets")
        exercise.reps = request.form.get("reps")
        flash(f'Your Exercise has been updated', 'success')
        db.session.commit()
        return redirect(url_for('workout_bp.workout_detail', id=workout_id))
    return render_template('workout_planner/updateexercise.html', exercise=exercise, workout=workout)


@workout_bp.route("/delete_exercise/<int:exercise_id>/<int:workout_id>", methods=['GET', 'POST'])
@login_required
def delete_exercise(exercise_id, workout_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    flash(f'The Exercise {exercise.name} has been deleted', 'warning')
    db.session.commit()
    return redirect(url_for('workout_bp.workout_detail', id=workout_id))


@workout_bp.route("/updateworkout/<int:workout_id>", methods=['GET', 'POST'])
@login_required
def updateworkout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if request.method == 'POST':
        workout.title = request.form.get("title")
        flash(f'Your Workout has been updated', 'success')
        db.session.commit()
        return redirect(url_for('workout_bp.list_workouts'))
    return render_template('workout_planner/updateworkout.html', workout=workout)


@workout_bp.route("/delete_workout/<int:workout_id>", methods=['GET', 'POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    flash(f'The workout {workout.title} has been deleted', 'warning')
    db.session.commit()
    return redirect(url_for('workout_bp.list_workouts'))


@workout_bp.route('/list_workouts')
@login_required
def list_workouts():
    current_user = get_current_user()
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    return render_template('workout_planner/list_workouts.html', workouts=workouts)

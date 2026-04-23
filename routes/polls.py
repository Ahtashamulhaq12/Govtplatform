from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Poll, PollOption, VotedState, User

polls_bp = Blueprint('polls', __name__, url_prefix='/polls')

@polls_bp.route('/')
def index():
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    # For each poll, determine if current user has voted
    voted_polls = []
    if current_user.is_authenticated:
        votes = VotedState.query.filter_by(user_id=current_user.id, entity_type='poll').all()
        voted_polls = [v.entity_id for v in votes]
        
    return render_template('polls/index.html', polls=polls, voted_polls=voted_polls)

@polls_bp.route('/vote/<int:option_id>', methods=['POST'])
@login_required
def vote(option_id):
    option = PollOption.query.get_or_404(option_id)
    poll_id = option.poll_id
    
    # Check if voted
    voted = VotedState.query.filter_by(user_id=current_user.id, entity_type='poll', entity_id=poll_id).first()
    if voted:
        flash('You have already voted on this poll.', 'warning')
        return redirect(url_for('polls.index'))
        
    option.votes += 1
    vs = VotedState(user_id=current_user.id, entity_type='poll', entity_id=poll_id)
    db.session.add(vs)
    
    current_user.points += 2
    
    db.session.commit()
    flash('Poll vote recorded!', 'success')
    return redirect(url_for('polls.index'))

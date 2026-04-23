from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Candidate, VotedState, User

elections_bp = Blueprint('elections', __name__, url_prefix='/elections')

@elections_bp.route('/')
def index():
    candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
    # Check if user has voted
    has_voted = False
    if current_user.is_authenticated:
        has_voted = VotedState.query.filter_by(user_id=current_user.id, entity_type='election').first() is not None
    return render_template('elections/index.html', candidates=candidates, has_voted=has_voted)

@elections_bp.route('/vote/<int:candidate_id>', methods=['POST'])
@login_required
def vote(candidate_id):
    # Check if already voted
    voted = VotedState.query.filter_by(user_id=current_user.id, entity_type='election').first()
    if voted:
        flash('You have already voted in this election.', 'warning')
        return redirect(url_for('elections.index'))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.votes += 1
    
    # Record the vote
    vs = VotedState(user_id=current_user.id, entity_type='election', entity_id=candidate.id)
    db.session.add(vs)
    
    # Reward user for participating
    current_user.points += 5
    
    db.session.commit()
    flash('Your vote has been successfully cast!', 'success')
    return redirect(url_for('elections.index'))

@elections_bp.route('/api/results')
def api_results():
    candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
    data = {
        'labels': [c.name for c in candidates],
        'votes': [c.votes for c in candidates],
        'parties': [c.party for c in candidates]
    }
    return jsonify(data)

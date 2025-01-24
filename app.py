from flask import Flask, render_template, request, redirect, url_for, flash, session
import json

app = Flask(__name__)
app.secret_key = 'clave_secreta_123'  # Necesario para las sesiones y mensajes flash

class ScoreTracker:
    def __init__(self, players, max_score):
        self.players = {player: 0 for player in players}
        self.max_score = max_score
        self.round = 0
        self.game_over = False
        self.losers = []

    def add_scores(self, scores):
        for player, score in scores.items():
            self.players[player] += int(score)
        self.round += 1
        self.check_winner()

    def check_winner(self):
        self.losers = [player for player, score in self.players.items() if score >= self.max_score]
        if self.losers:
            self.game_over = True
        return self.losers

    def to_dict(self):
        return {
            'players': self.players,
            'max_score': self.max_score,
            'round': self.round,
            'game_over': self.game_over,
            'losers': self.losers
        }

    @classmethod
    def from_dict(cls, data):
        game = cls([], data['max_score'])
        game.players = data['players']
        game.round = data['round']
        game.game_over = data['game_over']
        game.losers = data['losers']
        return game

@app.route('/')
def index():
    if 'game' in session:
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    try:
        num_players = int(request.form['num_players'])
        max_score = int(request.form['max_score'])
        
        if num_players < 2:
            flash('Debe haber al menos 2 jugadores', 'error')
            return redirect(url_for('index'))
        
        if max_score <= 0:
            flash('El puntaje máximo debe ser mayor a 0', 'error')
            return redirect(url_for('index'))
        
        players = []
        for i in range(num_players):
            player_name = request.form[f'player_{i}']
            if player_name.strip():
                players.append(player_name)
        
        game = ScoreTracker(players, max_score)
        session['game'] = json.dumps(game.to_dict())
        return redirect(url_for('game'))
    
    except ValueError:
        flash('Por favor, ingrese valores numéricos válidos', 'error')
        return redirect(url_for('index'))

@app.route('/game')
def game():
    if 'game' not in session:
        return redirect(url_for('index'))
    
    game_data = json.loads(session['game'])
    game = ScoreTracker.from_dict(game_data)
    return render_template('game.html', game=game)

@app.route('/add_scores', methods=['POST'])
def add_scores():
    if 'game' not in session:
        return redirect(url_for('index'))
    
    game_data = json.loads(session['game'])
    game = ScoreTracker.from_dict(game_data)
    
    scores = {}
    for player in game.players:
        try:
            score = int(request.form[f'score_{player}'])
            if score < 0:
                flash('Los puntajes no pueden ser negativos', 'error')
                return redirect(url_for('game'))
            scores[player] = score
        except ValueError:
            flash('Por favor, ingrese valores numéricos válidos', 'error')
            return redirect(url_for('game'))
    
    game.add_scores(scores)
    session['game'] = json.dumps(game.to_dict())
    return redirect(url_for('game'))

@app.route('/reset')
def reset():
    session.pop('game', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
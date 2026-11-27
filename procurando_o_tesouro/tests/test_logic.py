import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.player import Player
from entities.diamond import Diamond
from entities.trap import Trap, TrapType
from entities.clue import Clue
from world.map_generator import MapGenerator
from world.board import Board
from systems.scoring_system import ScoringSystem
from systems.turn_system import TurnSystem
from systems.movement_system import MovementSystem

def mk(n=2):
    return [Player(i, f"P{i}", (1,1,1)) for i in range(n)]

def test_map():
    b = Board(MapGenerator.build_board(6, 6))
    assert b.rows == 6 and b.cols == 6
    assert b.total_cells == 36

def test_diamond():
    for _ in range(20):
        d = Diamond.random()
        assert 1 <= d.carats <= 10

def test_diamond_score():
    p = mk()
    s = ScoringSystem(p)
    s.on_diamond(0, Diamond(carats=7))
    assert p[0].carats == 7

def test_deadend():
    p = mk()
    s = ScoringSystem(p)
    s.on_dead_end(0, Trap(TrapType.DEAD_END))
    assert p[0].carats == -10

def test_hideout():
    p = mk()
    s = ScoringSystem(p)
    s.on_hideout(0, Trap(TrapType.HIDEOUT))
    assert p[0].invisible is True
    assert p[1].carats == -5

def test_clue():
    p = mk()
    s = ScoringSystem(p)
    s.on_clue(0, Clue())
    assert p[0].carats == 3

def test_turns():
    p = mk(3)
    t = TurnSystem(p, 4)
    assert t.current_player.id == 0
    t.advance()
    assert t.current_player.id == 1
    t.advance()
    assert t.current_player.id == 2

def test_movement():
    b = Board(MapGenerator.build_board(6, 6))
    p = mk()
    p[0].row = 0; p[0].col = 0
    m = MovementSystem(b, p)
    assert not m.is_valid(p[0], -1, 0)
    assert m.is_valid(p[0], 1, 0)
    assert not m.is_valid(p[0], 1, 1)

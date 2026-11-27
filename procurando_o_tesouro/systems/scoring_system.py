from __future__ import annotations
from config.settings import settings

class ScoringSystem:
    def __init__(self, players):
        self.players = players
        self.last_message = ""

    def _find(self, pid):
        for p in self.players:
            if p.id == pid: return p
        raise ValueError("Jogador nao encontrado")

    def on_diamond(self, pid, diamond):
        p = self._find(pid)
        p.add_carats(diamond.carats)
        p.diamonds_found += 1
        diamond.collected = True
        diamond.discovered = True
        diamond.discovered_by = pid
        self.last_message = f"{p.name} encontrou diamante de {diamond.carats} ct!"

    def on_dead_end(self, pid, trap):
        p = self._find(pid)
        p.add_carats(-settings.TRAP_DEADEND_PENALTY)
        p.traps_found += 1
        trap.discovered = True
        trap.discovered_by = pid
        self.last_message = f"{p.name} caiu em um tunel sem saida! -{settings.TRAP_DEADEND_PENALTY} ct"

    def on_hideout(self, pid, trap):
        p = self._find(pid)
        p.traps_found += 1
        p.set_invisible(settings.INVISIBILITY_TURNS)
        trap.discovered = True
        trap.discovered_by = pid
        for o in self.players:
            if o.id != pid: o.add_carats(-settings.TRAP_HIDEOUT_OPPONENT_PENALTY)
        self.last_message = f"{p.name} ficou invisivel! Oponentes -{settings.TRAP_HIDEOUT_OPPONENT_PENALTY} ct"

    def on_clue(self, pid, clue):
        p = self._find(pid)
        p.add_carats(settings.CLUE_BONUS)
        clue.discovered = True
        clue.discovered_by = pid
        self.last_message = f"{p.name} achou Prossiga! +{settings.CLUE_BONUS} ct"

    def ranking(self):
        return sorted(self.players, key=lambda p: p.carats, reverse=True)

    def winners(self):
        if not self.players: return []
        best = max(p.carats for p in self.players)
        return [p for p in self.players if p.carats == best]

# Procurando o Tesouro

Jogo 3D de exploracao de mina em Python com PygameCE + PyOpenGL.

## Instalar

    pip install -r requirements.txt

## Rodar

    python main.py

## Controles

- Setas: mover jogador
- Mouse arrastar: girar camera
- Scroll: zoom
- W/A/S/D: mover camera
- R: resetar camera
- ESC: pausar

## Regras

- Tabuleiro 6x6
- Diamante: +1 a +10 ct
- Tunel sem saida: -10 ct
- Esconderijo secreto: jogador invisivel 1 turno, oponentes -5 ct
- Pista Prossiga: +3 ct

## Testes

    pytest tests/
